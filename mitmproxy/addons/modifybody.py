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
        auto_increment_id = random.randint(0, 99)  # 在函数的开始定义自增ID

        def replace_path(path):
            # 使用正则表达式替换所有的 [index]，["xxx"]，['xxx'] 或者 [*] 实例
            path = re.sub(r'(\[\d+\]|\[".*?"\]|\[\'*?\'\]|\[\*\])', r'->\1', path)

            return path
        def set_nested_item(obj, path, value):
            nonlocal auto_increment_id  # 使用 nonlocal 而不是 global
            if len(path) == 1:
                # 检查replacement_str是否包含{}
                if '{}' in value:
                    value = value.replace('{}', str(auto_increment_id))
                    auto_increment_id += 1  # 自增ID
                key = path[0]
                if '[' in key and ']' in key:
                    key, index = key.rstrip(']').split('[')
                    if index == '*':
                        for i in range(len(obj[key])):
                            obj[key][i] = value
                    else:
                        index = int(index)  # 将索引转换为整数
                        obj[key][index] = value
                elif key == '*':
                    for i in range(len(obj)):
                        obj[i] = value
                else:
                    obj[key] = value
            else:
                key = path[0]
                if '[' in key and ']' in key:
                    key, index = key.rstrip(']').split('[')
                    if index == '*':
                        if key:
                            for i in range(len(obj[key])):
                                set_nested_item(obj[key][i], path[1:], value)
                        else:
                            for i in range(len(obj)):
                                set_nested_item(obj[i], path[1:], value)
                    else:
                        index = int(index)  # 将索引转换为整数
                        if key:
                            set_nested_item(obj[key][index], path[1:], value)
                        else:
                            set_nested_item(obj[index], path[1:], value)
                elif key == '*':
                    for i in range(len(obj)):
                        set_nested_item(obj[i], path[1:], value)
                else:
                    set_nested_item(obj[key], path[1:], value)

        for spec in self.replacements:
            if spec.matches(flow):
                try:
                    replacement = spec.read_replacement()
                except OSError as e:
                    ctx.log.warn(f"Could not read replacement file: {e}")
                    continue

                if flow.response:
                    content = flow.response.content

                    if not spec.subject.startswith(b'JSON->'):
                        content = re.sub(spec.subject, replacement, content, flags=re.DOTALL)

                    subject_str = spec.subject.decode('utf-8')
                    replacement_str = replacement.decode('utf-8')
                    # 检查replacement_str是否包含{}
                    if '{}' in replacement_str:
                        replacement_str = replacement_str.replace('{}', str(auto_increment_id))
                        auto_increment_id += 1  # 自增ID
                    unicode_escape_subject = json.dumps(subject_str)[1:-1]
                    unicode_escape_replacement = json.dumps(replacement_str)[1:-1]

                    unicode_escape_subject_bytes = escaped_str_to_bytes(unicode_escape_subject)
                    unicode_escape_replacement_bytes = escaped_str_to_bytes(unicode_escape_replacement)

                    if unicode_escape_subject_bytes in content:
                        ctx.log.info(f"在响应内容中，将 {subject_str} 替换为 {replacement_str}。URL: {flow.request.url}")
                        content = content.replace(unicode_escape_subject_bytes, unicode_escape_replacement_bytes)

                    if flow.response.headers.get('Content-Type', '').lower().startswith('application/json'):
                        try:
                            json_content = json.loads(content.decode('utf-8'))
                        except json.JSONDecodeError:
                            ctx.log.warn("Failed to decode JSON content.")
                            return

                        try:
                            if replacement_str.lower() == 'true':
                                replacement_value = True
                            elif replacement_str.lower() == 'false':
                                replacement_value = False
                            elif replacement_str.replace('.', '', 1).isdigit():
                                replacement_value = float(replacement_str)
                                if replacement_value.is_integer():
                                    replacement_value = int(replacement_value)
                            elif replacement_str.startswith('"') and replacement_str.endswith('"'):
                                replacement_value = replacement_str[1:-1]
                            elif replacement_str.startswith("'") and replacement_str.endswith("'"):
                                replacement_value = replacement_str[1:-1]
                            else:
                                replacement_value = replacement_str
                        except ValueError:
                            replacement_value = replacement_str

                        if subject_str.startswith('JSON->'):
                            subject_str = replace_path(subject_str)
                            path_parts = subject_str.split('->')[1:]
                            try:
                                set_nested_item(json_content, path_parts, replacement_value)
                            except (KeyError, IndexError):
                                ctx.log.warn(f"JSON path not found: {subject_str}")

                            content = json.dumps(json_content).encode()
                    flow.response.content = content
                else:
                    # 对请求内容进行类似的替换，如果需要的话
                    if not spec.subject.startswith(b'JSON->'):
                        flow.request.content = re.sub(spec.subject, replacement, flow.request.content, flags=re.DOTALL)