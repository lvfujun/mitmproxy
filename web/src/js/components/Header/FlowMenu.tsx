import * as React from "react";
import Button from "../common/Button"
import {canReplay, MessageUtils} from "../../flow/utils"
import HideInStatic from "../common/HideInStatic";
import {useAppDispatch, useAppSelector} from "../../ducks";
import * as flowActions from "../../ducks/flows"
import {
    duplicate as duplicateFlow,
    kill as killFlow,
    remove as removeFlow,
    replay as replayFlow,
    resume as resumeFlow,
    revert as revertFlow
} from "../../ducks/flows"
import Dropdown, {MenuItem} from "../common/Dropdown";
import {copy} from "../../flow/export";
import {Flow} from "../../flow";

FlowMenu.title = '请求列表'

export default function FlowMenu(): JSX.Element {
    const dispatch = useAppDispatch(),
        flow = useAppSelector(state => state.flows.byId[state.flows.selected[0]])

    if (!flow)
        return <div/>
    return (
        <div className="flow-menu">
            <HideInStatic>
                <div className="menu-group">
                    <div className="menu-content">
                        <Button title="[r]eplay flow" icon="fa-repeat text-primary"
                                onClick={() => dispatch(replayFlow(flow))}
                                disabled={!canReplay(flow)}
                        >
                            重放请求
                        </Button>
                        <Button title="[D]uplicate flow" icon="fa-copy text-info"
                                onClick={() => dispatch(duplicateFlow(flow))}>
                            克隆请求
                        </Button>
                        <Button disabled={!flow || !flow.modified} title="revert changes to flow [V]"
                                icon="fa-history text-warning" onClick={() => dispatch(revertFlow(flow))}>
                            Revert
                        </Button>
                        <Button title="[d]elete flow" icon="fa-trash text-danger"
                                onClick={() => dispatch(removeFlow(flow))}>
                            Delete
                        </Button>
                        <MarkButton flow={flow}/>
                    </div>
                    <div className="menu-legend">控制请求流</div>
                </div>
            </HideInStatic>

            <div className="menu-group">
                <div className="menu-content">
                    <DownloadButton flow={flow}/>
                    <ExportButton flow={flow}/>
                </div>
                <div className="menu-legend">复制为</div>
            </div>

            <HideInStatic>
                <div className="menu-group">
                    <div className="menu-content">
                        <Button disabled={!flow || !flow.intercepted} title="[a]ccept intercepted flow"
                                icon="fa-play text-success" onClick={() => dispatch(resumeFlow(flow))}>
                            继续
                        </Button>
                        <Button disabled={!flow || !flow.intercepted} title="kill intercepted flow [x]"
                                icon="fa-times text-danger" onClick={() => dispatch(killFlow(flow))}>
                            终止
                        </Button>
                    </div>
                    <div className="menu-legend">请求拦截/修改</div>
                </div>
            </HideInStatic>
        </div>
    )
}

// Reference: https://stackoverflow.com/a/63627688/9921431
const openInNewTab = (url) => {
  const newWindow = window.open(url, '_blank', 'noopener,noreferrer')
  if (newWindow) newWindow.opener = null
}

function DownloadButton({flow}: { flow: Flow }) {
    if (flow.type !== "http")
        return <Button icon="fa-download" onClick={() => 0} disabled>Download</Button>;

    if (flow.request.contentLength && !flow.response?.contentLength) {
        return <Button icon="fa-download"
                       onClick={() => openInNewTab(MessageUtils.getContentURL(flow, flow.request))}
        >Download</Button>
    }
    if (flow.response) {
        const response = flow.response;
        if (!flow.request.contentLength && flow.response.contentLength) {
            return <Button icon="fa-download"
                           onClick={() => openInNewTab(MessageUtils.getContentURL(flow, response))}
            >Download</Button>
        }
        if (flow.request.contentLength && flow.response.contentLength) {
            return <Dropdown text={
                <Button icon="fa-download" onClick={() => 1}>Download▾</Button>
            } options={{"placement": "bottom-start"}}>
                <MenuItem onClick={() => openInNewTab(MessageUtils.getContentURL(flow, flow.request))}>Download
                    request</MenuItem>
                <MenuItem onClick={() => openInNewTab(MessageUtils.getContentURL(flow, response))}>Download
                    response</MenuItem>
            </Dropdown>
        }
    }

    return null;
}

function ExportButton({flow}: { flow: Flow }) {
    return <Dropdown className="" text={
        <Button title="Export flow." icon="fa-clone" onClick={() => 1}
                disabled={flow.type !== "http"}>复制为▾</Button>
    } options={{"placement": "bottom-start"}}>
        <MenuItem onClick={() => copy(flow, "raw_request")}>Copy raw request</MenuItem>
        <MenuItem onClick={() => copy(flow, "raw_response")}>Copy raw response</MenuItem>
        <MenuItem onClick={() => copy(flow, "raw")}>Copy raw request and response</MenuItem>
        <MenuItem onClick={() => copy(flow, "curl")}>Copy as cURL</MenuItem>
        <MenuItem onClick={() => copy(flow, "httpie")}>Copy as HTTPie</MenuItem>
    </Dropdown>
}


const markers = {
    ":red_circle:": "🔴",
    ":orange_circle:": "🟠",
    ":yellow_circle:": "🟡",
    ":green_circle:": "🟢",
    ":large_blue_circle:": "🔵",
    ":purple_circle:": "🟣",
    ":brown_circle:": "🟤",
}
const markersZh = {
    ":red_circle:": "红色",
    ":orange_circle:": "橙色",
    ":yellow_circle:": "黄色",
    ":green_circle:": "绿色",
    ":large_blue_circle:": "蓝色",
    ":purple_circle:": "紫色",
    ":brown_circle:": "褐色",
}
function MarkButton({flow}: { flow: Flow }) {
    const dispatch = useAppDispatch();
    return <Dropdown className="" text={
        <Button title="mark flow" icon="fa-paint-brush text-success" onClick={() => 1}>标记▾</Button>
    } options={{"placement": "bottom-start"}}>
        <MenuItem onClick={() => dispatch(flowActions.update(flow, {marked: ""}))}>⚪ &nbsp;(no
            marker)</MenuItem>
        {Object.entries(markers).map(([name, sym]) =>
            <MenuItem
                key={name}
                onClick={() => dispatch(flowActions.update(flow, {marked: name}))}>
                {sym} &nbsp;{markersZh[name].replace(/[:_]/g, " ")}
            </MenuItem>
        )}
    </Dropdown>
}
