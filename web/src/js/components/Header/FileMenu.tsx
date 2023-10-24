import * as React from "react"
import {useDispatch} from 'react-redux'
import FileChooser from '../common/FileChooser'
import Dropdown, {Divider, MenuItem} from '../common/Dropdown'
import * as flowsActions from '../../ducks/flows'
import HideInStatic from "../common/HideInStatic";


export default React.memo(function FileMenu() {
    const dispatch = useDispatch();
    return (
        <Dropdown className="pull-left special" text="菜单" options={{"placement": "bottom-start"}}>
            <li>
                <FileChooser
                    icon="fa-folder-open"
                    text="&nbsp;打开工作副本..."
                    onClick={
                        // stop event propagation: we must keep the input in DOM for upload to work.
                        e => e.stopPropagation()
                    }
                    onOpenFile={file => {
                        dispatch(flowsActions.upload(file));
                        document.body.click(); // "restart" event propagation
                    }}
                />
            </li>
            <MenuItem onClick={() => dispatch(flowsActions.download())}>
                <i className="fa fa-fw fa-floppy-o"/>&nbsp;保存工作副本...
            </MenuItem>
            <MenuItem onClick={() => confirm('Delete all flows?') && dispatch(flowsActions.clear())}>
                <i className="fa fa-fw fa-trash"/>&nbsp;清空请求
            </MenuItem>
            <HideInStatic>
                <Divider/>
                {/*<li>*/}
                {/*    <a href="http://mitm.it/" target="_blank">*/}
                {/*        <i className="fa fa-fw fa-external-link"/>&nbsp;Install Certificates...*/}
                {/*    </a>*/}
                {/*</li>*/}
                <li>
                    <a href="https://ty-vs.66rpg.com/?folder=/data/ty" target="_blank">
                        <i className="fa fa-fw fa-external-link"/>&nbsp;远程文件管理
                    </a>
                </li>
            </HideInStatic>
        </Dropdown>
    )
});
