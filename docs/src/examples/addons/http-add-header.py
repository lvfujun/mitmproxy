"""Add an HTTP header to each response."""
from mitmproxy import ctx

import redis
redisObject = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)

class AddHeader:
    def __init__(self):
        self.num = 0

    def request(self, flow):
        token = redisObject.get(ctx.options.listen_port)
        ctx.log.alert("测试一下1")
        ctx.log.info("测试一下2")
        ctx.log.error("测试一下3")
        ctx.log.warn("测试一下4")
        ctx.log.debug("测试一下5")
        flow.request.headers["X-Fake-Token"] = str(token)
        print(ctx.options.listen_port)

    def response(self, flow):
        print(str(flow.incId))
addons = [AddHeader()]
