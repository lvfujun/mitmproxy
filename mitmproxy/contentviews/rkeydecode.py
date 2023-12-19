import re
import json
from collections.abc import Iterator
from functools import lru_cache
from typing import Any, Optional

from mitmproxy.contentviews import base
from base64 import urlsafe_b64decode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Base64URL解码函数
def base64url_decode2(plain_text):
    base64url = plain_text.replace('-', '+').replace('_', '/').replace('!', '=')
    padding = '=' * ((4 - len(base64url) % 4) % 4)
    return urlsafe_b64decode(base64url + padding)

# RSA解密函数
def decrypt(eb64_cry, private_key_pem):
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,
        backend=default_backend()
    )
    decoded_data = base64url_decode2(eb64_cry)
    decrypted = private_key.decrypt(
        decoded_data,
        padding.PKCS1v15()
    )
    return decrypted

# XOR解密函数
def xor_string(data: bytes, key: bytes) -> bytes:
    data_len = len(data)
    off = 0
    key_cursor = 0
    k_len = len(key) - 1
    decrypted_data = bytearray(data)

    while off < data_len:
        decrypted_data[off] = data[off] ^ key[key_cursor]
        off += 1
        key_cursor = (key_cursor + (off & 0xF)) & k_len

    return bytes(decrypted_data)
#
# # 示例私钥和加密数据
private_key_pem = b"""-----BEGIN RSA PRIVATE KEY-----
MIIEoQIBAAKCAQBgb8ErKBB8U46IblJydeySayCOTsTHVJ5qMqKpLriN6FgDOFAe
SkNJI7aQ95bOgoxY4bu6HY4QN5MS9AaWoL8aomZnPSKC67eD/sdSz2gddk2r9jXT
DyOEf9QPiHsdmQF5wAipsWoCjBNeFmmZTDTg3RlDcjRDZ6zPj6LJrWmXnRKAN3vU
JrzUMYMlVJhx8xgROyUAh1MK7vFexyQCaUut8eV+lyT9pAgQ7OTVCPDTfAWgb5rs
UonKERbwmSPqdxjLjqz+xIWnBLWA1X42tJxJ613sBypXSglv2Gogcyonc6FO8EmR
v5U48cw4MK6XN+Nls3wCmlMLoXn3dxLANpJ7AgMBAAECggEAI+6f+BeWhOyRSC5r
E/Dyc9/sonmhAnB6EjHJv+YDqARxfsmluJONHJxs8vj9vPaRmrCJRSCsBUjfyQkZ
x1gfvKnUJBV4XXW8zDbLSAS103x4FmHHzlturXj/p8X/sZiIHzg5Qhkz2b0dnkoV
kKP/c+WN+z57UL45eqEXU7QEixPrJ8OCRpk58O4ziLeYXCR2R8Jby1FBMwIBS+mk
uEGFi81OmINFzx0IyaRswKbPSnalLQpfd24+DhJry6N9EpC8vEfmVUV2b0AuW4Tv
YaNW2/qTYTjnA/0OKn6foDPhEP3swFWYmVVtCGp5yUa6HJk5BjMpVwp9J1sfOBxz
JDrF6QKBgQCofEP03n7NaAuPI3w1R6hD0OsGGEuv4Rjj8McIDNlnSXCekATWcVZk
/hRzIuYGLY+PxrSgLbQiys8w9abdFOor/mz9AsFGxB2+zzXLT91AHgzI9ToTysC6
tNu0xsX+kv7JHZeFd6thzL873IFoIt9m3kCw8ulmBgKOZlYwLM3YhQKBgQCShw1+
p8nq5FIa+crfhl850HzenUjviLNRJPYnUxWHeQM1BxrHi9KaH7z2XZHIHLbnOVCA
l17+AAnoGOqIRcJF6Xuxi3EF3mtS3oBP1fcsNJOpe5Afi4ontF0arS8PSTHIibhd
9eOdp6/UrsBsIRdwfUxdcTYzzHNayQ/oznQu/wKBgBLtMq0VOWVVpMbFk7RgglRr
6Zrbq9TsEmG4sIME/n8Nzurg/sogHTZnHGD6sKBNCe16wtujhrLJ2ZCEZ+Q57zxV
7mRVpOSQL085868NH6uONJ12frmucwwGORALrD42wQxSmKzTjpsD5w+Qa7EJCdOC
b/3wq6tcTXk1ocTzo4QJAoGAWsVtN7QL4waUUn/CDNy6Kx+b63B2WWVO6IrELrJK
mQT/Vp9TGKDm03Gr5tcqU1RufilEVJTxVNqDSJP+3nKQmiy84szmNGOICuspg8uh
9nGPtCOGsfQInvYd40O77nVCcN/YJeUIn4bc5x1muNV7JsWIRC65DDewkmISB/+1
e9MCgYBmeN7vPEmKEbCrg6ttOWaI5xC8OnEG2qZPUldotY0Sez8EatrGft1of13E
tXjHnOfahHz9ZGUT4bNLS0BORZ2NNE6rArFtr55l+y84tkB5i7yqVmBh2vPGLNRm
gF2cOCeObRy8+ikD4TGk6tOkPJyeiiXRGF4o38tRNfNugp+S/g==
-----END RSA PRIVATE KEY-----"""
#

PARSE_ERROR = object()


@lru_cache(1)
def parse_json(s: bytes) -> Any:
    try:
        return json.loads(s.decode("utf-8"))
    except ValueError:
        return PARSE_ERROR


def format_json(data: Any) -> Iterator[base.TViewLine]:
    encoder = json.JSONEncoder(indent=4, sort_keys=True, ensure_ascii=False)
    current_line: base.TViewLine = []
    for chunk in encoder.iterencode(data):
        if "\n" in chunk:
            rest_of_last_line, chunk = chunk.split("\n", maxsplit=1)
            # rest_of_last_line is a delimiter such as , or [
            current_line.append(("text", rest_of_last_line))
            yield current_line
            current_line = []
        if re.match(r'\s*"', chunk):
            current_line.append(("json_string", chunk))
        elif re.match(r"\s*\d", chunk):
            current_line.append(("json_number", chunk))
        elif re.match(r"\s*(true|null|false)", chunk):
            current_line.append(("json_boolean", chunk))
        else:
            current_line.append(("text", chunk))
    yield current_line


class ViewRKEY(base.View):
    name = "rkey-decoded"

    def __call__(self, data, **metadata):
        type = "R-KEY-JSON"
        rKey = metadata['flow'].request.query.get('r-key')
        if rKey and metadata['content_type']:
            if "application/jsonp" in metadata['content_type']:
                type = "JSONP"
                matchObj = re.match(r'^[\w]+\((\{.*\})\);', data.decode("utf-8"), re.M | re.I)
                if matchObj is not None and matchObj.group(1) is not None:
                    data = matchObj.group(1).encode("utf-8")
                    type = "JSONP"
            elif "application/json" in metadata['content_type']:
                # 支持JSONP
                matchObj = re.match(r'^[\w].+?\((.+)\)$', data.decode("utf-8"), re.M | re.I)
                if matchObj is not None and matchObj.group(1) is not None:
                    data = matchObj.group(1).encode("utf-8")
                    type = "JSONP"


            r_key_encrypted = rKey  # 这里替换为加密的r-key
            # 首先尝试解析JSON字符串
            json_content = data
            try:
                json_data = json.loads(json_content.decode('utf-8'))
            except json.JSONDecodeError as e:
                print("解析JSON时出错:", str(e))
                return

            # 从解析好的JSON数据中提取encrypted_base64url_msg
            encrypted_base64url_msg = json_data.get('encrypt_data')
            if not encrypted_base64url_msg:
                return
            # 解密r-key
            try:
                r_key_decrypted = decrypt(r_key_encrypted, private_key_pem)
            except Exception as exc:
                print("r-key解密过程中出错:", str(exc))
                raise

            # Base64URL解码encrypt_data
            decoded_data = base64url_decode2(encrypted_base64url_msg)

            # 使用解密的r-key和XOR解密encrypt_data
            decrypted_data = xor_string(decoded_data, r_key_decrypted)
            data = decrypted_data.decode("utf-8")
        else:
            return
        if data is not PARSE_ERROR:
            return type, data

    def render_priority(
            self, data: bytes, *, content_type: Optional[str] = None, **metadata
    ) -> float:
        # Safely access the flow object from metadata
        flow = metadata.get('flow')
        if flow and content_type and b"encrypt_data" in data:
            # Now, safely access the request object from the flow
            request = getattr(flow, 'request', None)
            if request:
                # Safely get the URL from the request object
                url = getattr(request, 'url', '')
                # Check if 'r-key' is present in the URL
                if 'r-key' in url:
                    return 1
        return 0