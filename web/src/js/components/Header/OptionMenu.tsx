import * as React from "react";
import {CommandBarToggle, EventlogToggle, OptionsToggle} from "./MenuToggle"
import Button from "../common/Button"
import DocsLink from "../common/DocsLink"
import HideInStatic from "../common/HideInStatic";
import * as modalActions from "../../ducks/ui/modal"
import { useAppDispatch } from "../../ducks";

OptionMenu.title = '配置'

export default function OptionMenu() {
    const dispatch = useAppDispatch()
    const openOptions = () => modalActions.setActiveModal('OptionModal')

    return (
        <div>
            <HideInStatic>
                <div className="menu-group">
                    <div className="menu-content">
                        <Button title="Open Options" icon="fa-cogs text-primary"
                                onClick={() => dispatch(openOptions())}>
                            高级选项 <sup>alpha</sup>
                        </Button>
                    </div>
                    <div className="menu-legend">选项编辑</div>
                </div>

                <div className="menu-group">
                    <div className="menu-content">
                        <OptionsToggle name="anticache">
                            停用缓存（强刷每个请求） <DocsLink resource="overview-features/#anticache"/>
                        </OptionsToggle>
                        <OptionsToggle name="showhost">
                            抓取静态资源（图片、引擎资源等）
                        </OptionsToggle>
                        <OptionsToggle name="filter_body_content">
                            捕获接口响应（筛选用）
                        </OptionsToggle>
                    </div>
                    <div className="menu-legend">快速选项</div>
                </div>
            </HideInStatic>

            <div className="menu-group">
                <div className="menu-content">
                    <EventlogToggle/>
                    <CommandBarToggle/>
                </div>
                <div className="menu-legend">视图选项</div>
            </div>
        </div>
    )
}
