import {selectTab} from "./flow"
import * as flowsActions from "../flows"
import * as modalActions from "./modal"
import {tabsForFlow} from "../../components/FlowView";
import {runCommand} from "../../utils"
import * as flowActions from "../flows";

// 定制快捷键
export function onKeyDown(e: KeyboardEvent) {
    //console.debug("onKeyDown", e)
    // 由于浏览器本身有很多快捷键，所以不拦截功能键，防止冲突
    if (e.ctrlKey || e.metaKey) {
        return () => {
        }
    }
    const key = e.key;
    e.preventDefault()
    return (dispatch, getState) => {

        const flows = getState().flows,
            flow = flows.byId[getState().flows.selected[0]]

        switch (key) {
            case "k":
            case "ArrowUp":
                dispatch(flowsActions.selectRelative(flows, -1))
                break

            case "j":
            case "ArrowDown":
                dispatch(flowsActions.selectRelative(flows, +1))
                break

            case " ":
            case "PageDown":
                dispatch(flowsActions.selectRelative(flows, +10))
                break

            case "PageUp":
                dispatch(flowsActions.selectRelative(flows, -10))
                break

            case "End":
                dispatch(flowsActions.selectRelative(flows, +1e10))
                break

            case "Home":
                dispatch(flowsActions.selectRelative(flows, -1e10))
                break

            case "Escape":
                if (getState().ui.modal.activeModal) {
                    dispatch(modalActions.hideModal())
                } else {
                    dispatch(flowsActions.select(undefined))
                }
                break

            case "ArrowLeft": {
                if (!flow) break
                let tabs = tabsForFlow(flow),
                    currentTab = getState().ui.flow.tab,
                    nextTab = tabs[(Math.max(0, tabs.indexOf(currentTab)) - 1 + tabs.length) % tabs.length]
                dispatch(selectTab(nextTab))
                break
            }

            case "Tab":
            case "ArrowRight": {
                if (!flow) break
                let tabs = tabsForFlow(flow),
                    currentTab = getState().ui.flow.tab,
                    nextTab = tabs[(Math.max(0, tabs.indexOf(currentTab)) + 1) % tabs.length]
                dispatch(selectTab(nextTab))
                break
            }

            case "d": {
                if (!flow) {
                    return
                }
                dispatch(flowsActions.remove(flow))
                break
            }

            case "n": {
                runCommand("view.flows.create", "get", "https://example.com/")
                break
            }

            case "D": {
                if (!flow) {
                    return
                }
                dispatch(flowsActions.duplicate(flow))
                break
            }
            case "q": {
                if (flow) {
                    if (flow.marked) {
                        dispatch(flowActions.update(flow, {marked: ''}))
                    } else {
                        dispatch(flowActions.update(flow, {marked: ':red_circle:'}))
                    }
                }
                break
            }
            case "A": {
                dispatch(flowsActions.resumeAll())
                break
            }

            case "r": {
                if (flow) {
                    dispatch(flowsActions.replay(flow))
                }
                break
            }

            case "v": {
                if (flow && flow.modified) {
                    dispatch(flowsActions.revert(flow))
                }
                break
            }

            case "z": {
                if (flow && flow.intercepted) {
                    dispatch(flowsActions.kill(flow))
                }
                break
            }

            case "Z": {
                dispatch(flowsActions.killAll())
                break
            }

            case "x": {
                dispatch(flowsActions.clear())
                break
            }

            default:
                return
        }
    }
}
