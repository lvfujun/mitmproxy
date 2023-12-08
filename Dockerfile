# 使用一个包含 Python 和 mitmproxy 的基础镜像
FROM python:3.9
USER root
ENV http_proxy=http://192.168.0.132:7890
ENV https_proxy=http://192.168.0.132:7890
ENV PYTHONOPTIMIZE=2
VOLUME /certs
VOLUME /script

WORKDIR /taiyi-proxy
RUN pip install requests
COPY . .
RUN pip install .
WORKDIR /
# 设置启动命令
RUN chmod +x /taiyi-proxy/start.sh
# 安装 tc
RUN apt-get update && apt-get install -y iproute2 && apt-get install iperf && apt-get install iputils-ping
CMD /taiyi-proxy/start.sh