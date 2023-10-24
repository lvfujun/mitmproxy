import * as React from "react";
import {useDispatch} from "react-redux"
import * as eventLogActions from "../../ducks/eventLog"
import * as commandBarActions from "../../ducks/commandBar"
import {useAppDispatch, useAppSelector} from "../../ducks"
import * as optionsActions from "../../ducks/options"
import {useEffect, useState} from "react";


type MenuToggleProps = {
    value: boolean
    onChange: (e: React.ChangeEvent) => void
    children: React.ReactNode
}

export function MenuToggle({value, onChange, children}: MenuToggleProps) {
    return (
        <div className="menu-entry">
            <label>
                <input type="checkbox"
                       checked={value}
                       onChange={onChange}/>
                {children}
            </label>
        </div>
    )
}

type OptionsToggleProps = {
    name: optionsActions.Option,
    children: React.ReactNode
}

export function OptionsToggle({name, children}: OptionsToggleProps) {
    const dispatch = useAppDispatch();
    const value = useAppSelector((state) => state.options[name]);
    const [firstClick, setFirstClick] = useState(false);
    const [autoOffTimer, setAutoOffTimer] = useState<any>(null);

    // // 首次进入页面时就开始计时
    // useEffect(() => {
    //     if (name == "filter_body_content" && value) {
    //         const timerId = setTimeout(() => {
    //             dispatch(optionsActions.update(name, false));
    //             alert('"捕获接口响应（筛选用）"已关闭');
    //         }, 90000);
    //         setAutoOffTimer(timerId);
    //
    //         return () => {
    //             // clearTimeout(timerId);
    //         };
    //     }
    // }, []); // 注意这里的空数组，它使得这个 useEffect 只在首次渲染后运行

    // 当用户首次点击开关时，显示提示
    const handleOnChange = () => {
        // 清除首次进入页面时的定时器
        clearTimeout(autoOffTimer);
        setAutoOffTimer(null);

        if (name == 'filter_body_content') {
            if (!firstClick && value == false) {
                // alert('📢️ 注意：启用此选项会使网络抓包速度变慢，以及占用大量网络流量，请在需要的时候再开启。\n⏲️ 该选项在开启后将在90秒后自动关闭。\n🔍 请注意，即使关闭了此选项，你仍然可以搜索已经捕获的内容，但不会捕获新的请求内容。');
                alert('📢️ 注意：启用此选项会使网络抓包速度变慢一些，请在需要的时候开启');
                setFirstClick(true);
            }
        }

        dispatch(optionsActions.update(name, !value));
    };

    if (name == "filter_body_content") {
        // useEffect(() => {
        //     if (value && firstClick) {
        //         const timerId = setTimeout(() => {
        //             dispatch(optionsActions.update(name, false));
        //             alert('"捕获接口响应（筛选用）"已关闭');
        //         }, 90000);
        //
        //         return () => {
        //             // clearTimeout(timerId);
        //         };
        //     }
        // }, [value, name, dispatch, firstClick]);
    }

    return (
        <MenuToggle
            value={!!value}
            onChange={handleOnChange}
        >
            {children}
        </MenuToggle>
    );
}

export function EventlogToggle() {
    const dispatch = useDispatch(),
        visible = useAppSelector(state => state.eventLog.visible);

    return (
        <MenuToggle
            value={visible}
            onChange={() => dispatch(eventLogActions.toggleVisibility())}
        >
            显示事件日志
        </MenuToggle>
    )
}

export function CommandBarToggle() {
    const dispatch = useDispatch(),
        visible = useAppSelector(state => state.commandBar.visible);

    return (
        <MenuToggle
            value={visible}
            onChange={() => dispatch(commandBarActions.toggleVisibility())}
        >
            显示命令栏
        </MenuToggle>
    )
}
