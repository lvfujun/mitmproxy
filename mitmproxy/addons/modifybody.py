import json
import re
from collections.abc import Sequence

from mitmproxy import ctx, exceptions
from mitmproxy.addons.modifyheaders import parse_modify_spec, ModifySpec
from mitmproxy.utils.strutils import escaped_str_to_bytes


class ModifyBody:
    def __init__(self):
        self.replacements: list[ModifySpec] = []

    def load(self, loader):
        loader.add_option(
            "modify_body",
            Sequence[str],
            [],
            """
            这个主要用来替换响应内容
            例1：/橙光/丸漫                    这个的意思是：替换所有url中响应内容搜索字符串橙光并替换为丸漫\n
            例2：/game_info/61414/512700      这个的意思是：找到url中包含 game_info 关键词的接口在这个接口的响应内容中搜索61414并替换为512700\n
            例3：/\/user/([game_info|user_info])/(?:61414)/xxxxx/  支持正则
            """,
        )

    def configure(self, updated):
        if "modify_body" in updated:
            self.replacements = []
            for option in ctx.options.modify_body:
                try:
                    spec = parse_modify_spec(option, True)
                except ValueError as e:
                    raise exceptions.OptionsError(
                        f"Cannot parse modify_body option {option}: {e}"
                    ) from e

                self.replacements.append(spec)

    def request(self, flow):
        if flow.response or flow.error or not flow.live:
            return
        self.run(flow)

    def response(self, flow):
        if flow.error or not flow.live:
            return
        self.run(flow)

    def run(self, flow):
        for spec in self.replacements:
            if spec.matches(flow):
                try:
                    replacement = spec.read_replacement()
                except OSError as e:
                    ctx.log.warn(f"Could not read replacement file: {e}")
                    continue

                if flow.response:
                    content = flow.response.content

                    # 执行原来的替换逻辑
                    content = re.sub(
                        spec.subject,
                        replacement,
                        content,
                        flags=re.DOTALL,
                    )

                    # 先将 subject 和 replacement 转换为 UTF-8 编码的字符串
                    subject_str = spec.subject.decode('utf-8')
                    replacement_str = replacement.decode('utf-8')
                    # 处理 Unicode 转义格式（例如 \uxxx）
                    unicode_escape_subject = json.dumps(subject_str)[1:-1]  # remove double quotes
                    unicode_escape_replacement = json.dumps(replacement_str)[1:-1]  # remove double quotes

                    unicode_escape_subject_bytes = escaped_str_to_bytes(unicode_escape_subject)
                    unicode_escape_replacement_bytes = escaped_str_to_bytes(unicode_escape_replacement)
                    if unicode_escape_subject_bytes in content:
                        ctx.log.info(
                            f"在响应内容中，将 {subject_str} 替换为 {replacement_str}。URL: {flow.request.url}")
                        content = content.replace(unicode_escape_subject_bytes, unicode_escape_replacement_bytes)
                    # else:
                    #     ctx.log.info(f"在响应内容中未找到 {subject_str}。URL: {flow.request.url}")
                    flow.response.content = content
                else:
                    # 对请求内容进行类似的替换，如果需要的话
                    flow.request.content = re.sub(
                        spec.subject, replacement, flow.request.content, flags=re.DOTALL
                    )