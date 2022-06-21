import re
from collections.abc import Sequence

from mitmproxy import ctx, exceptions
from mitmproxy.addons.modifyheaders import parse_modify_spec, ModifySpec


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
                    flow.response.content = re.sub(
                        spec.subject,
                        replacement,
                        flow.response.content,
                        flags=re.DOTALL,
                    )
                else:
                    flow.request.content = re.sub(
                        spec.subject, replacement, flow.request.content, flags=re.DOTALL
                    )
