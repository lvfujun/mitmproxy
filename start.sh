#!/bin/bash
ls -lsh /certs/
cat /certs/66cgyouxi.pem
cat /etc/main_hosts >> /etc/hosts
CMD="mitmweb \
     --certs *.66rpg.com=/certs/66cgyouxi.pem \
     --certs *.cgyouxi.com=/certs/66cgyouxi.pem \
     --certs *.muccybook.com=/certs/muxi.pem \
     --certs *.muccygame.com=/certs/muccygame.pem \
     --certs *.muccyapi.com=/certs/muccyapi.pem \
     --certs *.dreamwanman.com=/certs/dreamwanman.pem \
     --certs muccybook.com=/certs/muxi.pem \
     --certs *.wanman66.com=/certs/wanman.pem \
     --certs wanman66.com=/certs/wanman.pem \
     --certs *.wanmanqc.com=/certs/wanmanqc.pem \
     --certs *.qingchengwanman.com=/certs/qingchengwanman.pem \
     --ssl-insecure \
     --allow-hosts api.cgyouxi.com \
     --allow-hosts japi.cgyouxi.com \
     --allow-hosts mxapi \
     --allow-hosts miniapi \
     --allow-hosts c2.cgyouxi.com \
     --allow-hosts muccyapi \
     --allow-hosts muccybook \
     --allow-hosts muccygame \
     --allow-hosts wanman66 \
     --allow-hosts dreamwanman \
     --allow-hosts wanmanqc \
     --allow-hosts qingchengwanman \
     --allow-hosts (.+?).66rpg.com \
     --listen-host $LISTEN_HOST \
     --listen-port $LISTEN_PORT \
     --web-host $WEB_HOST \
     --web-port $WEB_PORT \
     --set upstream_cert=false \
     --set tls_version_client_min=UNBOUNDED \
     --no-http2 \
     --set stream_large_bodies=10m \
     -s /script/my_custom.py"

if [ -n "$MODE" ]
then
  CMD="$CMD --mode $MODE"
fi
exec $CMD