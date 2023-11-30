import {fetchApi} from "../utils"
import * as optionsEditorActions from "./ui/optionsEditor"
import {defaultState, Option, OptionsState} from "./_options_gen";
import {AppThunk} from "./index";

export const RECEIVE = 'OPTIONS_RECEIVE'
export const UPDATE = 'OPTIONS_UPDATE'
export const REQUEST_UPDATE = 'REQUEST_UPDATE'

export {Option, defaultState}

export default function reducer(state = defaultState, action): OptionsState {
    switch (action.type) {
        case RECEIVE:
            let s = <OptionsState>{};
            // @ts-ignore
            for (const [name, {value}] of Object.entries(action.data)) {
                s[name] = value
            }
            return s;

        case UPDATE:
            let s2 = {...state}
            // @ts-ignore
            for (const [name, {value}] of Object.entries(action.data)) {
                s2[name] = value
            }
            return s2

        default:
            return state
    }
}

export async function pureSendUpdate(option: Option, value, dispatch) {
    try {
        const response = await fetchApi.put('/options', {[option]: value});
        if (response.status === 200) {
            if (dispatch) {
                dispatch(optionsEditorActions.updateSuccess(option))
            }
        } else {
            throw await response.text()
        }
    } catch (error) {
        dispatch(optionsEditorActions.updateError(option, error))
    }
}

let sendUpdate = pureSendUpdate; // _.throttle(pureSendUpdate, 500, {leading: true, trailing: true})
let delayTime = 1000; // 延迟时间
let timerId: ReturnType<typeof setTimeout> | null = null;
export function update(name: Option, value: any): AppThunk {
    return dispatch => {
        dispatch(optionsEditorActions.startUpdate(name, value))
        // 增加防抖节流
        if (timerId) {
            clearTimeout(timerId);
        }
        let list = ['allow_hosts', 'block_list', 'map_local', 'map_remote', 'modify_body', 'modify_headers', 'performance_switch']

        if (list.includes(name)) {
            timerId = setTimeout(function () {
                sendUpdate(name, value, dispatch);
            }, delayTime);
        } else {
            sendUpdate(name, value, dispatch);
        }

        if (name == "showhost") {
            alert('📢注意：如果你使用的PAC代理模式，将不会立即生效（约1分钟左右生效），如果需要立即生效请重新开关一下被代理设备的代理设置，或者断开wifi重新链接，如果需要即时生效，请将被代理设备代理切换为普通代理模式')
            if (value == true) {
                sendUpdate("allow_hosts", ["api.cgyouxi.com", "japi.cgyouxi.com", "mxapi", "miniapi", "cgyouxi.com", "muccybook", "muccyapi", "wanman66", "dreamwanman", "wanmanqc", "qingchengwanman", "(.+?).66rpg.com"], null);
            } else {
                sendUpdate("allow_hosts", ["api.cgyouxi.com", "japi.cgyouxi.com", "mxapi", "miniapi", "c2.cgyouxi.com", "muccybook", "muccyapi", "wanman66", "dreamwanman", "wanmanqc", "qingchengwanman", "(.+?).66rpg.com"], null);
            }
        }
    }
}

export function save() {
    return dispatch => fetchApi('/options/save', {method: 'POST'})
}

export function addInterceptFilter(example) {
    return (dispatch, getState) => {
        let intercept = getState().options.intercept;
        if (intercept && intercept.includes(example)) {
            return
        }
        if (!intercept) {
            intercept = example
        } else {
            intercept = `${intercept} | ${example}`
        }
        dispatch(update("intercept", intercept));
    }
}

