import * as React from 'react'
import {fetchApi, formatSize} from '../utils'
import HideInStatic from '../components/common/HideInStatic'
import {useAppSelector} from "../ducks";
import {useEffect} from "react";

export default function Footer() {
    const version = useAppSelector(state => state.backendState.version);
    let {
        mode, intercept, showhost, upstream_cert, rawtcp, http2, websocket, anticache, anticomp,
        stickyauth, stickycookie, stream_large_bodies, listen_host, listen_port, server, ssl_insecure,filter_body_content, performance_switch, traffic_control
    } = useAppSelector(state => state.options);

    return (
        <footer style={{"fontSize":16}}>
            {mode && (mode.length !== 1 || mode[0] !== "regular") && (
                <span className="label label-success">{mode.join(",")}</span>
            )}
            {intercept && (
                <span className="label label-success">Intercept: {intercept}</span>
            )}
            {filter_body_content && (
                <span className="label label-danger">捕获接口响应（筛选用）</span>
            )}
            {traffic_control && (
                <span className="label label-danger">弱网模拟</span>
            )}
            {showhost && (
                <span className="label label-success">抓取静态资源</span>
            )}
            {!upstream_cert && (
                <span className="label label-success">no-upstream-cert</span>
            )}
            {!rawtcp && (
                <span className="label label-success">no-raw-tcp</span>
            )}
            {!http2 && (
                <span className="label label-success">no-http2</span>
            )}
            {!websocket && (
                <span className="label label-success">no-websocket</span>
            )}
            {anticache && (
                <span className="label label-success">anticache</span>
            )}
            {anticomp && (
                <span className="label label-success">anticomp</span>
            )}
            {stickyauth && (
                <span className="label label-success">stickyauth: {stickyauth}</span>
            )}
            {stickycookie && (
                <span className="label label-success">stickycookie: {stickycookie}</span>
            )}
            {stream_large_bodies && (
                <span className="label label-success">stream: {stream_large_bodies}</span>
            )}
            {performance_switch && (
                <span className="label label-danger">性能分析中</span>
            )}
           <div className="pull-right">
                <HideInStatic>

                    {
                        server && (
                            <span className="label label-primary" title="HTTP Proxy Server Address">

                            （推荐使用）PAC代理地址：<span suppressContentEditableWarning={true} contentEditable="true">http://{window.location.hostname || "*"}/pac/{listen_port}</span>
                            </span>
                        )
                    }
                    {
                        server && (
                            <span className="label label-default" title="HTTP Proxy Server Address">
                            代理地址：<span suppressContentEditableWarning={true} contentEditable="true">{window.location.hostname || "*"}:{listen_port}</span>
                            </span>
                        )
                    }
                </HideInStatic>
                <span className="label label-default" title="Mitmproxy Version">
            (*^▽^*) Enjoy It~
            </span>
            </div>
        </footer>
    )
}
