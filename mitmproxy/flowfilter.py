"""
    The following operators are understood:

        ~q          Request
        ~s          Response

    Headers:

        Patterns are matched against "name: value" strings. Field names are
        all-lowercase.

        ~a          Asset content-type in response. Asset content types are:
                        text/javascript
                        application/x-javascript
                        application/javascript
                        text/css
                        image/*
                        font/*
                        application/font-*
        ~h rex      Header line in either request or response
        ~hq rex     Header in request
        ~hs rex     Header in response

        ~b rex      Expression in the body of either request or response
        ~bq rex     Expression in the body of request
        ~bs rex     Expression in the body of response
        ~t rex      Shortcut for content-type header.

        ~d rex      Request domain
        ~m rex      Method
        ~u rex      URL
        ~c CODE     Response code.
        rex         Equivalent to ~u rex
"""

import functools
import json
import re
import sys
from collections.abc import Sequence
from typing import ClassVar, Protocol, Union
import pyparsing as pp

from mitmproxy import dns, flow, http, tcp
from mitmproxy.utils.strutils import escaped_str_to_bytes


def only(*types):
    def decorator(fn):
        @functools.wraps(fn)
        def filter_types(self, flow):
            if isinstance(flow, types):
                return fn(self, flow)
            return False

        return filter_types

    return decorator


class _Token:
    def dump(self, indent=0, fp=sys.stdout):
        print(
            "{spacing}{name}{expr}".format(
                spacing="\t" * indent,
                name=self.__class__.__name__,
                expr=getattr(self, "expr", ""),
            ),
            file=fp,
        )


class _Action(_Token):
    code: ClassVar[str]
    help: ClassVar[str]

    @classmethod
    def make(klass, s, loc, toks):
        return klass(*toks[1:])


class FErr(_Action):
    code = "e"
    help = "过滤发生错误的请求"

    def __call__(self, f):
        return True if f.error else False


class FMarked(_Action):
    code = "marked"
    help = "过滤所有被标记的请求"

    def __call__(self, f):
        return bool(f.marked)


class FHTTP(_Action):
    code = "http"
    help = "过滤所有http请求"

    @only(http.HTTPFlow)
    def __call__(self, f):
        return True


class FWebSocket(_Action):
    code = "websocket"
    help = "过滤所有websocket请求"

    @only(http.HTTPFlow)
    def __call__(self, f: http.HTTPFlow):
        return f.websocket is not None


class FTCP(_Action):
    code = "tcp"
    help = "过滤tcp请求"

    @only(tcp.TCPFlow)
    def __call__(self, f):
        return True


class FDNS(_Action):
    code = "dns"
    help = "过滤DNS请求"

    @only(dns.DNSFlow)
    def __call__(self, f):
        return True


class FReq(_Action):
    code = "q"
    help = "过滤所有未响应的请求"

    @only(http.HTTPFlow, dns.DNSFlow)
    def __call__(self, f):
        if not f.response:
            return True


class FResp(_Action):
    code = "s"
    help = "过滤所有有返回值的请求"

    @only(http.HTTPFlow, dns.DNSFlow)
    def __call__(self, f):
        return bool(f.response)


class FAll(_Action):
    code = "all"
    help = "过滤全部请求"

    def __call__(self, f: flow.Flow):
        return True


class _Rex(_Action):
    flags = 0
    is_binary = True

    def __init__(self, expr):
        self.expr = expr
        if self.is_binary:
            expr = expr.encode()
        try:
            self.re = re.compile(expr, self.flags)
        except Exception:
            raise ValueError("Cannot compile expression.")


def _check_content_type(rex, message):
    return any(
        name.lower() == b"content-type" and rex.search(value)
        for name, value in message.headers.fields
    )


class FAsset(_Action):
    code = "a"
    help = "仅过滤静态资源：CSS，JavaScript，图片，字体。"
    ASSET_TYPES = [
        re.compile(x)
        for x in [
            b"text/javascript",
            b"application/x-javascript",
            b"application/javascript",
            b"text/css",
            b"image/.*",
            b"font/.*",
            b"application/font.*",
        ]
    ]

    @only(http.HTTPFlow)
    def __call__(self, f):
        if f.response:
            for i in self.ASSET_TYPES:
                if _check_content_type(i, f.response):
                    return True
        return False


class FContentType(_Rex):
    code = "t"
    help = "Content-type header （例：~t image）"

    @only(http.HTTPFlow)
    def __call__(self, f):
        if _check_content_type(self.re, f.request):
            return True
        elif f.response and _check_content_type(self.re, f.response):
            return True
        return False


class FContentTypeRequest(_Rex):
    code = "tq"
    help = "Request Content-Type header（例：~tq json）"

    @only(http.HTTPFlow)
    def __call__(self, f):
        return _check_content_type(self.re, f.request)


class FContentTypeResponse(_Rex):
    code = "ts"
    help = "Response Content-Type header（例：~ts image）"

    @only(http.HTTPFlow)
    def __call__(self, f):
        if f.response:
            return _check_content_type(self.re, f.response)
        return False


class FHead(_Rex):
    code = "h"
    help = "Header （例：~h X-Request-Id）"
    flags = re.MULTILINE

    @only(http.HTTPFlow)
    def __call__(self, f):
        if f.request and self.re.search(bytes(f.request.headers)):
            return True
        if f.response and self.re.search(bytes(f.response.headers)):
            return True
        return False


class FHeadRequest(_Rex):
    code = "hq"
    help = "过滤请求 header（例：~hq x-sign）"
    flags = re.MULTILINE

    @only(http.HTTPFlow)
    def __call__(self, f):
        if f.request and self.re.search(bytes(f.request.headers)):
            return True


class FHeadResponse(_Rex):
    code = "hs"
    help = "过滤响应 header（例：~hs vpc-iapi-web-04）"
    flags = re.MULTILINE

    @only(http.HTTPFlow)
    def __call__(self, f):
        if f.response and self.re.search(bytes(f.response.headers)):
            return True


class FBod(_Rex):
    code = "b"
    help = "过滤接口内容（例：~b 限量卡）"
    flags = re.DOTALL

    @only(http.HTTPFlow, tcp.TCPFlow, dns.DNSFlow)
    def __call__(self, f):
        json_mime_types = ["application/json", "application/json-rpc", "application/jsonp"]

        if isinstance(f, http.HTTPFlow):
            # Handle HTTP response
            if f.response:
                content_type = f.response.headers.get('Content-Type', '').split(';')[0]
                if any(mime in content_type for mime in json_mime_types):
                    try:
                        content = f.response.get_content(strict=False)
                        # 新的JSONP格式
                        jsonp_pattern_new = rb'^[\w].+?\((.+)\)$'
                        match = re.match(jsonp_pattern_new, content)
                        if match:
                            json_content = match.group(1).decode("utf-8")
                        else:
                            json_content = json.loads(content)
                        if self.re.search(escaped_str_to_bytes(json.dumps(json_content, ensure_ascii=False))):
                            return True
                    except Exception as e:
                        print(e)
                elif f.response.raw_content and self.re.search(f.response.get_content(strict=False)):
                    return True
            # Handle HTTP request
            if f.request:
                content_type = f.request.headers.get('Content-Type', '').split(';')[0]
                if any(mime in content_type for mime in json_mime_types):
                    try:
                        content = f.request.get_content(strict=False)
                        json_content = json.loads(content)
                        if self.re.search(escaped_str_to_bytes(json.dumps(json_content, ensure_ascii=False))):
                            return True
                    except Exception as e:
                        print(e)
                elif f.request.raw_content and self.re.search(f.request.get_content(strict=False)):
                    return True
            # Handle websocket
            if f.websocket:
                for msg in f.websocket.messages:
                    if self.re.search(msg.content):
                        return True
        elif isinstance(f, tcp.TCPFlow):
            for msg in f.messages:
                if self.re.search(msg.content):
                    return True
        elif isinstance(f, dns.DNSFlow):
            if f.request and self.re.search(f.request.content):
                return True
            if f.response and self.re.search(f.response.content):
                return True
        return False


class FBodRequest(_Rex):
    code = "bq"
    help = "过滤请求内容（例：~bq xxx）"
    flags = re.DOTALL

    @only(http.HTTPFlow, tcp.TCPFlow, dns.DNSFlow)
    def __call__(self, f):
        if isinstance(f, http.HTTPFlow):
            if f.request and f.request.raw_content:
                if self.re.search(f.request.get_content(strict=False)):
                    return True
            if f.websocket:
                for msg in f.websocket.messages:
                    if msg.from_client and self.re.search(msg.content):
                        return True
        elif isinstance(f, tcp.TCPFlow):
            for msg in f.messages:
                if msg.from_client and self.re.search(msg.content):
                    return True
        elif isinstance(f, dns.DNSFlow):
            if f.request and self.re.search(f.request.content):
                return True


class FBodResponse(_Rex):
    code = "bs"
    help = "过滤响应内容（~bs 512700）"
    flags = re.DOTALL

    @only(http.HTTPFlow, tcp.TCPFlow, dns.DNSFlow)
    def __call__(self, f):
        json_mime_types = ["application/json", "application/json-rpc", "application/jsonp"]

        if isinstance(f, http.HTTPFlow):
            if f.response:
                content_type = f.response.headers.get('Content-Type', '').split(';')[0]
                if any(mime in content_type for mime in json_mime_types):
                    try:
                        content = f.response.get_content(strict=False)
                        # 新的JSONP格式
                        jsonp_pattern_new = rb'^[\w].+?\((.+)\)$'
                        match = re.match(jsonp_pattern_new, content)
                        if match:
                            json_content = match.group(1).decode("utf-8")
                        else:
                            json_content = json.loads(content)
                        if self.re.search(escaped_str_to_bytes(json.dumps(json_content, ensure_ascii=False))):
                            return True
                    except Exception as e:
                        print(e)
                elif f.response.raw_content and self.re.search(f.response.get_content(strict=False)):
                    return True
                if f.websocket:
                    for msg in f.websocket.messages:
                        if not msg.from_client and self.re.search(msg.content):
                            return True
        elif isinstance(f, tcp.TCPFlow):
            for msg in f.messages:
                if not msg.from_client and self.re.search(msg.content):
                    return True
        elif isinstance(f, dns.DNSFlow):
            if f.response and self.re.search(f.response.content):
                return True

class FMethod(_Rex):
    code = "m"
    help = "Method（例：~m get）"
    flags = re.IGNORECASE

    @only(http.HTTPFlow)
    def __call__(self, f):
        return bool(self.re.search(f.request.data.method))


class FDomain(_Rex):
    code = "d"
    help = "Domain（例：~d 66rpg）"
    flags = re.IGNORECASE
    is_binary = False

    @only(http.HTTPFlow)
    def __call__(self, f):
        return bool(
            self.re.search(f.request.host) or self.re.search(f.request.pretty_host)
        )


class FUrl(_Rex):
    code = "u"
    help = "PATH（例：game_info）"
    is_binary = False

    # FUrl is special, because it can be "naked".

    @classmethod
    def make(klass, s, loc, toks):
        if len(toks) > 1:
            toks = toks[1:]
        return klass(*toks)

    @only(http.HTTPFlow, dns.DNSFlow)
    def __call__(self, f):
        if not f or not f.request:
            return False
        if isinstance(f, http.HTTPFlow):
            return self.re.search(f.request.pretty_url)
        elif isinstance(f, dns.DNSFlow):
            return f.request.questions and self.re.search(f.request.questions[0].name)


class FSrc(_Rex):
    code = "src"
    help = "过滤请求来源IP"
    is_binary = False

    def __call__(self, f):
        if not f.client_conn or not f.client_conn.peername:
            return False
        r = f"{f.client_conn.peername[0]}:{f.client_conn.peername[1]}"
        return f.client_conn.peername and self.re.search(r)


class FDst(_Rex):
    code = "dst"
    help = "过滤目的地IP"
    is_binary = False

    def __call__(self, f):
        if not f.server_conn or not f.server_conn.address:
            return False
        r = f"{f.server_conn.address[0]}:{f.server_conn.address[1]}"
        return f.server_conn.address and self.re.search(r)


class FReplay(_Action):
    code = "replay"
    help = "过滤重复过的请求"

    def __call__(self, f):
        return f.is_replay is not None


class FReplayClient(_Action):
    code = "replayq"
    help = "过滤劫持过的请求"

    def __call__(self, f):
        return f.is_replay == "request"


class FReplayServer(_Action):
    code = "replays"
    help = "过滤劫持过响应内容的请求"

    def __call__(self, f):
        return f.is_replay == "response"


class FMeta(_Rex):
    code = "meta"
    help = "Flow metadata"
    flags = re.MULTILINE
    is_binary = False

    def __call__(self, f):
        m = "\n".join([f"{key}: {value}" for key, value in f.metadata.items()])
        return self.re.search(m)


class FMarker(_Rex):
    code = "marker"
    help = "Match marked flows with specified marker"
    is_binary = False

    def __call__(self, f):
        return self.re.search(f.marked)


class FComment(_Rex):
    code = "comment"
    help = "Flow comment"
    flags = re.MULTILINE
    is_binary = False

    def __call__(self, f):
        return self.re.search(f.comment)


class _Int(_Action):
    def __init__(self, num):
        self.num = int(num)


class FCode(_Int):
    code = "c"
    help = "匹配状态码（例：~c 200)"

    @only(http.HTTPFlow)
    def __call__(self, f):
        if f.response and f.response.status_code == self.num:
            return True


class FAnd(_Token):
    def __init__(self, lst):
        self.lst = lst

    def dump(self, indent=0, fp=sys.stdout):
        super().dump(indent, fp)
        for i in self.lst:
            i.dump(indent + 1, fp)

    def __call__(self, f):
        return all(i(f) for i in self.lst)


class FOr(_Token):
    def __init__(self, lst):
        self.lst = lst

    def dump(self, indent=0, fp=sys.stdout):
        super().dump(indent, fp)
        for i in self.lst:
            i.dump(indent + 1, fp)

    def __call__(self, f):
        return any(i(f) for i in self.lst)


class FNot(_Token):
    def __init__(self, itm):
        self.itm = itm[0]

    def dump(self, indent=0, fp=sys.stdout):
        super().dump(indent, fp)
        self.itm.dump(indent + 1, fp)

    def __call__(self, f):
        return not self.itm(f)


filter_unary: Sequence[type[_Action]] = [
    FAsset,
    FErr,
    FHTTP,
    FMarked,
    FReplay,
    FReplayClient,
    FReplayServer,
    FReq,
    FResp,
    FTCP,
    FDNS,
    FWebSocket,
    FAll,
]
filter_rex: Sequence[type[_Rex]] = [
    FBod,
    FBodRequest,
    FBodResponse,
    FContentType,
    FContentTypeRequest,
    FContentTypeResponse,
    FDomain,
    FDst,
    FHead,
    FHeadRequest,
    FHeadResponse,
    FMethod,
    FSrc,
    FUrl,
    FMeta,
    FMarker,
    FComment,
]
filter_int = [FCode]


def _make():
    # Order is important - multi-char expressions need to come before narrow
    # ones.
    parts = []
    for cls in filter_unary:
        f = pp.Literal(f"~{cls.code}") + pp.WordEnd()
        f.setParseAction(cls.make)
        parts.append(f)

    # This is a bit of a hack to simulate Word(pyparsing_unicode.printables),
    # which has a horrible performance with len(pyparsing.pyparsing_unicode.printables) == 1114060
    unicode_words = pp.CharsNotIn("()~'\"" + pp.ParserElement.DEFAULT_WHITE_CHARS)
    unicode_words.skipWhitespace = True
    regex = (
        unicode_words
        | pp.QuotedString('"', escChar="\\")
        | pp.QuotedString("'", escChar="\\")
    )
    for cls in filter_rex:
        f = pp.Literal(f"~{cls.code}") + pp.WordEnd() + regex.copy()
        f.setParseAction(cls.make)
        parts.append(f)

    for cls in filter_int:
        f = pp.Literal(f"~{cls.code}") + pp.WordEnd() + pp.Word(pp.nums)
        f.setParseAction(cls.make)
        parts.append(f)

    # A naked rex is a URL rex:
    f = regex.copy()
    f.setParseAction(FUrl.make)
    parts.append(f)

    atom = pp.MatchFirst(parts)
    expr = pp.infixNotation(
        atom,
        [
            (pp.Literal("!").suppress(), 1, pp.opAssoc.RIGHT, lambda x: FNot(*x)),
            (pp.Literal("&").suppress(), 2, pp.opAssoc.LEFT, lambda x: FAnd(*x)),
            (pp.Literal("|").suppress(), 2, pp.opAssoc.LEFT, lambda x: FOr(*x)),
        ],
    )
    expr = pp.OneOrMore(expr)
    return expr.setParseAction(lambda x: FAnd(x) if len(x) != 1 else x)


bnf = _make()


class TFilter(Protocol):
    pattern: str

    def __call__(self, f: flow.Flow) -> bool:
        ...  # pragma: no cover


def parse(s: str) -> TFilter:
    """
    Parse a filter expression and return the compiled filter function.
    If the filter syntax is invalid, `ValueError` is raised.
    """
    if not s:
        raise ValueError("Empty filter expression")
    try:
        flt = bnf.parseString(s, parseAll=True)[0]
        flt.pattern = s
        return flt
    except (pp.ParseException, ValueError) as e:
        raise ValueError(f"Invalid filter expression: {s!r}") from e


def match(flt: Union[str, TFilter], flow: flow.Flow) -> bool:
    """
    Matches a flow against a compiled filter expression.
    Returns True if matched, False if not.

    If flt is a string, it will be compiled as a filter expression.
    If the expression is invalid, ValueError is raised.
    """
    if isinstance(flt, str):
        flt = parse(flt)
    if flt:
        return flt(flow)
    return True


match_all: TFilter = parse("~all")
"""A filter function that matches all flows"""


help = []
for a in filter_unary:
    help.append((f"~{a.code}", a.help))
for b in filter_rex:
    help.append((f"~{b.code} regex", b.help))
for c in filter_int:
    help.append((f"~{c.code} int", c.help))
help.sort()
help.extend(
    [
        ("!", "unary not"),
        ("&", "and"),
        ("|", "or"),
        ("(...)", "grouping"),
    ]
)
