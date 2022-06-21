import * as React from "react"
import Splitter from './common/Splitter'
import FlowTable from './FlowTable'
import FlowView from './FlowView'
import {useAppSelector} from "../ducks";
import {useEffect, useState} from "react";

export default function MainView() {
    const selection = useAppSelector(state => !!state.flows.byId[state.flows.selected[0]])
    const [hasSelection, setHasSelection] = useState(selection)
    useEffect(() => {
        setHasSelection(selection)
    }, [selection])
    return (
        <div className="main-view">
            <FlowTable openWindow={e=>{
                if (selection) {
                    setHasSelection(true)
                }
            }}/>
            {hasSelection && selection && <Splitter key="splitter"/>}
            {hasSelection && selection && <FlowView key="flowDetails" closeWindow={e=>setHasSelection(false)}/>}
        </div>
    )
}
