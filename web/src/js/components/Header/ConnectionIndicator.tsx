import * as React from "react";
import {ConnectionState} from "../../ducks/connection"
import {useAppSelector} from "../../ducks";


export default React.memo(function ConnectionIndicator() {

    const connState = useAppSelector(state => state.connection.state),
        message = useAppSelector(state => state.connection.message)

    switch (connState) {
        case ConnectionState.INIT:
            return <span className="connection-indicator init">连接中…</span>;
        case ConnectionState.FETCHING:
            return <span className="connection-indicator fetching">从服务器获取历史抓包信息…</span>;
        case ConnectionState.ESTABLISHED:
            return <span className="connection-indicator established">连接成功</span>;
        case ConnectionState.ERROR:
            return <span className="connection-indicator error"
                         title={message}>已失去连接，请刷新页面</span>;
        case ConnectionState.OFFLINE:
            return <span className="connection-indicator offline">已离线，请检查网络</span>;
        default:
            const exhaustiveCheck: never = connState;
            throw "unknown connection state";
    }
})
