from collections.abc import Sequence
from typing import NamedTuple

from mitmproxy import ctx, exceptions, flowfilter, http, version
from mitmproxy.net.http.status_codes import NO_RESPONSE
from mitmproxy.net.http.status_codes import RESPONSES


class BlockSpec(NamedTuple):
    matches: flowfilter.TFilter
    status_code: int


def parse_spec(option: str) -> BlockSpec:
    """
    Parses strings in the following format, enforces number of segments:

        /flow-filter/status

    """
    sep, rem = option[0], option[1:]

    parts = rem.lower().split(sep, 2)
    if len(parts) != 2:
        raise ValueError("Invalid number of parameters (2 are expected)")
    flow_patt, status = parts
    try:
        status_code = int(status)
    except ValueError:
        raise ValueError(f"Invalid HTTP status code: {status}")
    flow_filter = flowfilter.parse(flow_patt)
    if not RESPONSES.get(status_code):
        raise ValueError(f"Invalid HTTP status code: {status}")

    return BlockSpec(matches=flow_filter, status_code=status_code)


class BlockList:
    def __init__(self):
        self.items: list[BlockSpec] = []

    def load(self, loader):
        loader.add_option(
            "block_list",
            Sequence[str],
            [],
            """
            屏蔽请求：
            例1：/game_info/404 搜索 url中包含game_info的请求直接响应404
            """,
        )

    def configure(self, updated):
        if "block_list" in updated:
            self.items = []
            for option in ctx.options.block_list:
                try:
                    spec = parse_spec(option)
                except ValueError as e:
                    raise exceptions.OptionsError(
                        f"Cannot parse block_list option {option}: {e}"
                    ) from e
                self.items.append(spec)

    def request(self, flow: http.HTTPFlow) -> None:
        if flow.response or flow.error or not flow.live:
            return

        for spec in self.items:
            if spec.matches(flow):
                flow.metadata["blocklisted"] = True
                if spec.status_code == NO_RESPONSE:
                    flow.kill()
                else:
                    flow.response = http.Response.make(
                        spec.status_code, headers={"Server": version.MITMPROXY}
                    )
