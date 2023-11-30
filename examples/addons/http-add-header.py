import threading
import time
from collections import deque
from datetime import datetime

from ping3 import ping

from mitmproxy import ctx
import json
import jieba

from mitmproxy.http import HTTPFlow

# class MyCustom:
#     def __init__(self):
#         self.num = 0
#     def sendMess(self, msg):
#         # 你复制的webhook地址
#         url = "https://open.feishu.cn/open-apis/bot/v2/hook/9dd0f1ac-b1f5-48b5-9c99-4980d3b74394"
#         payload_message = {
#             "msg_type": "text",
#             "content": {
#                 "text": msg
#             }
#         }
#         headers = {
#             'Content-Type': 'application/json'
#         }
#         ctx.log.error("msss")
#         response = requests.request("POST", url, headers=headers, data=json.dumps(payload_message))

#     def request(self, flow: HTTPFlow):
#         token = ctx.options.listen_port
#         ctx.log.alert("测试一下1")
#         ctx.log.info("测试一下2")
#         ctx.log.error("测试一下3")
#         ctx.log.warn("测试一下4")
#         ctx.log.debug("测试一下5")
#         # flow.request.headers["X-Fake-Token"] = str(token)
#         print(ctx.options.listen_port)

#     def response(self, flow: HTTPFlow):
#         return
#         try:
#             if "/mini/_nuxt/app.js" in flow.request.url or \
#             "/mini/_nuxt/vendors/app.js" in flow.request.url or \
#             "/mini/_nuxt/commons/app.js" in flow.request.url:
#                 flow.response.headers["Cache-Control"] = "max-age=3600"
#             ctx.log.error(flow.request.url)
#             rawJson = json.loads(str(flow.response.content, 'utf-8'))
#             content = str(json.loads(str(flow.response.content, 'utf-8')))
#             ctx.log.error(content)
#             port = ctx.options.listen_port
#             if "签名" in content:
#                 if "test-" in flow.request.url  or  "debug-" in flow.request.url:
#                     ctx.log.error(flow.request.url)
#                     ctx.log.error("签名失败")
#                     # self.sendMess("代理端口："+str(port)+"，发现请求,签名检查失败：\n"+flow.request.url+"\n返回内容："+content )
#                 # print(response.text)
#             # if rawJson['status'] < 1:
#                 # self.sendMess("代理端口："+str(port)+"，发现请求,返回值小于1\n"+flow.request.url+"\n返回内容："+content )
#         except Exception as e:
#             ctx.log.error(str(e))
# addons = [MyCustom()]


from mitmproxy import http
import pprint
import io

from mitmproxy.net.http import url


def print_rr(a):
    buf = io.StringIO()
    pprint.pprint(a, stream=buf)
    return buf.getvalue()
class BlockIP:
    def __init__(self):
        self.blocked_ip = "172.16.72.114"
    def request(self, flow: http.HTTPFlow) -> None:
        # 检查是否存在User-Agent头部
        if "User-Agent" not in flow.request.headers:
            # 检查请求协议是否为HTTP
            if flow.request.scheme == "http":
                # 将请求协议更改为HTTPS
                flow.request.scheme = "https"
                flow.request.port = 443
                # 添加一个提示信息
                print(f"Scheme changed to HTTPS for: {flow.request.url}")
        port = ctx.options.listen_port
        # if flow.client_conn.address[0] == self.blocked_ip:
        #     flow.kill()
        #     print(f"Blocked request from {self.blocked_ip}")
        # 禁止访问代理端口防止出现死循环
        # ctx.log.error(flow.request)
        # with open('/data/ty/yunhe/flow', 'a') as f:
            # f.write(print_rr(flow)+'\n')
        if "172.16.6.111:80" in flow.request.url:
            flow.kill()
            ctx.log.error(f"Blocked request from 172.16.6.111:80")
        if flow.request.host == "172.16.6.111" and flow.request.method == "HEAD":
            flow.kill()
        if "172.16.15.220:80" in flow.request.url:
            flow.kill()
            ctx.log.error(f"Blocked request from 172.16.15.220:80")
        if flow.request.host == "172.16.15.220" and flow.request.method == "HEAD":
            flow.kill()

    def responseheaders(self, flow):
        flow.response.stream = flow.response.headers.get('content-type', '').startswith('text/event-stream');
class ContentTypeModifier:
    def __init__(self):
        self.content_type_to_modify = 'text/json;charset=utf-8'
        self.target_content_type = 'application/json;charset=utf-8'

    def detect_image_type(self,data: bytes) -> str:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return "png"
        elif data[:2] == b"\xff\xd8":
            return "jpeg"
        elif data[:6] in (b"GIF87a", b"GIF89a"):
            return "gif"
        return ""
    def response(self, flow: http.HTTPFlow) -> None:
        # flow.comment = flow.response.content

        # ctx.log.info(f"Current value of my_option: {ctx.options.filter_body_content}")

        # 检查URL中是否包含"cfg.php"
        if "cfg.php" in flow.request.url:
            # 检查响应头中的content-type是否为"text/html"
            if flow.response.headers.get("content-type", "").startswith("text/html"):
                # 修改响应头的content-type为"application/json;charset=utf-8"
                flow.response.headers["content-type"] = "application/json;charset=utf-8"

        content_type_header = flow.response.headers.get('Content-Type', '')
        # flow.response.headers["ty-tips"] = "你好"
        if self.content_type_to_modify in content_type_header:
            flow.response.headers['Content-Type'] = self.target_content_type
            print(f"Modified Content-Type header from '{self.content_type_to_modify}' to '{self.target_content_type}'")
        content_type = flow.response.headers.get("Content-Type", "").lower()
        if content_type == "application/octet-stream":
            image_type = self.detect_image_type(flow.response.content)
            if image_type:
                flow.response.headers["Content-Type"] = f"image/{image_type}"
                ctx.log.info(f"Changed Content-Type to image/{image_type}")
        if "application/json" in flow.response.headers.get("Content-Type", "") and ctx.options.filter_body_content and '0.0.0.0' not in flow.request.url and '172.16.6.111' not in flow.request.url:
            try:
                json_content = json.loads(flow.response.content)
                keys_values = set()
                extract_keys_values(json_content, keys_values)

                unique_keys_values = process_keys_values(keys_values)
                # ctx.log.error(unique_keys_values)
                flow.comment = "".join(str(i) for i in unique_keys_values)
                # ctx.log.error(flow.request.url)
            except json.JSONDecodeError:
                pass

def extract_keys_values(obj, keys_values):
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys_values.add(k)
            extract_keys_values(v, keys_values)
    elif isinstance(obj, list):
        for item in obj:
            extract_keys_values(item, keys_values)
    else:
        keys_values.add(obj)

def process_keys_values(keys_values):
    result = set()
    for item in keys_values:
        if isinstance(item, str) and not any([item in other for other in keys_values if item != other and isinstance(other, str)]):
            result.add(item)
    return result


from mitmproxy import http
class AddPNGComment:
    def __init__(self):
        self.num = 0

    def response(self, flow: http.HTTPFlow) -> None:
        flow.comment = flow.response.headers["Content-Type"]
class WebDebugPlugin:
    def __init__(self):
        self.target_host = 'webdebug.66rpg.com'
        self.redirect_ip = '172.16.73.66'

    def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.host == 'm.66rpg.com' and flow.request.scheme == 'http':
            flow.request.scheme = 'https'
            flow.request.port = '443'
        uInfo = url.parse(flow.request.url)
        if flow.request.port == 8899:
            flow.request.host = self.redirect_ip
        if uInfo[1].decode('utf-8') == self.target_host:
            if flow.request.scheme == 'https':
                flow.request.scheme = 'http'
            flow.request.host = self.redirect_ip

    def response(self, flow: http.HTTPFlow) -> None:
        flow.response.headers["Access-Control-Allow-Origin"] = "*"
        if flow.response:
            content = flow.response.content
            if content:
                new_content = content.replace(b'172.16.73.66', b'webdebug.66rpg.com')
                # flow.response.content = new_content
import re

class InjectScriptPlugin:
    def __init__(self):
        self.script_to_inject = b'''
        <script>
            if (window.location.protocol == 'https:') {
                window.location.href = window.location.href.replace('https:', 'http:');
            }
        </script>
        <script src="//172.16.73.66:8080/target.js" embedded="false"></script>
        '''

    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.headers.get('Content-Type', '').startswith('text/html'):
            content = flow.response.content
            flow.response.headers["Access-Control-Allow-Origin"] = "*"
            content = re.sub(b'<!doctype html>', b'<!doctype html>' + self.script_to_inject, content, flags=re.IGNORECASE)
            flow.response.content = content

class PingMonitor(threading.Thread):
    def __init__(self, key, url='www.66rpg.com'):
        threading.Thread.__init__(self)
        self.key = key
        self.url = url
        self.delays_1min = deque(maxlen=60)
        self.delays_5min = deque(maxlen=5*60)
        self.delays_15min = deque(maxlen=15*60)
        self.loss_1min = deque(maxlen=60)
        self.loss_5min = deque(maxlen=5*60)
        self.loss_15min = deque(maxlen=15*60)
        self.stop_requested = False

    def ping_and_update(self):
        delay = ping(self.url)
        if delay is None:
            print(f'{self.key}: 请求超时。')
            self.loss_1min.append(1)
            self.loss_5min.append(1)
            self.loss_15min.append(1)
        else:
            delay_ms = delay * 1000  # 转换成毫秒
            self.delays_1min.append(delay_ms)
            self.delays_5min.append(delay_ms)
            self.delays_15min.append(delay_ms)
            self.loss_1min.append(0)
            self.loss_5min.append(0)
            self.loss_15min.append(0)
    def stop(self):
        self.stop_requested = True

    def print_average_and_loss(self):
        avg_1min = sum(self.delays_1min) / len(self.delays_1min) if self.delays_1min else None
        avg_5min = sum(self.delays_5min) / len(self.delays_5min) if self.delays_5min else None
        avg_15min = sum(self.delays_15min) / len(self.delays_15min) if self.delays_15min else None
        loss_rate_1min = sum(self.loss_1min) / len(self.loss_1min) * 100 if self.loss_1min else None
        loss_rate_5min = sum(self.loss_5min) / len(self.loss_5min) * 100 if self.loss_5min else None
        loss_rate_15min = sum(self.loss_15min) / len(self.loss_15min) * 100 if self.loss_15min else None
        # 获取当前时间并格式化为字符串
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ctx.log.performance(
            f'{current_time} - {self.key: <5}: 1分钟平均延迟: {avg_1min: <5.2f}ms, 丢包率: {loss_rate_1min: <3.2f}% | 5分钟平均延迟: {avg_5min: <5.2f}ms, 丢包率: {loss_rate_5min: <3.2f}% | 15分钟平均延迟: {avg_15min: <5.2f}ms, 丢包率: {loss_rate_15min: <3.2f}%'
        )
    def run(self):
        while not self.stop_requested:
            self.ping_and_update()
            time.sleep(1)
            if time.time() % 3 < 1:  # 每3秒执行一次
                self.print_average_and_loss()
monitor = PingMonitor('橙光内部', 'test-conf.66rpg.com')
class PingAddons:

    def configure(self, updates):
        global monitor
        # 获取当前时间并格式化为字符串
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "performance_switch" in updates:
            if ctx.options.performance_switch:
                ctx.log.performance(f'{current_time} - 开启网络分析')
                if not monitor.is_alive():  # 如果线程还没启动，则启动它
                    try:
                        monitor.start()
                    except Exception as e:
                        monitor = PingMonitor('橙光内部', 'test-conf.66rpg.com')
            else:
                ctx.log.performance(f'{current_time} - 关闭网络分析')
                if monitor.is_alive():  # 如果线程正在运行，则停止它
                    monitor.stop()
addons = [
    # InjectScriptPlugin(),
    BlockIP(),
    ContentTypeModifier(),
PingAddons()
    # WebDebugPlugin(),
    # AddPNGComment()
]
