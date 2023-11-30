import * as React from "react"
import {useEffect, useState} from "react";
import Splitter from './common/Splitter'
import FlowTable from './FlowTable'
import FlowView from './FlowView'
import CaptureSetup from "./CaptureSetup";
import {useAppSelector} from "../ducks";

export default function MainView() {
    const selection = useAppSelector(state => !!state.flows.byId[state.flows.selected[0]])
    const hasFlows = useAppSelector(state => state.flows.list.length > 0);
    const [hasSelection, setHasSelection] = useState(selection)

    useEffect(() => {
        setHasSelection(selection)
    }, [selection])

    return (
        <div className="main-view">
            {hasFlows ? <FlowTable openWindow={e => {
                if (selection) {
                    setHasSelection(true)
                }
            }}/> : <CaptureSetup/>}
            {hasSelection && selection && <Splitter key="splitter"/>}
            {hasSelection && selection && <FlowView key="flowDetails" closeWindow={e => setHasSelection(false)}/>}
        </div>
    )
}
