import React, { Component } from 'react'
import { fetchApi } from "../../utils";

type FilterDocsProps = {
    selectHandler: (cmd: string) => void,
}

type FilterDocsStates = {
    doc: {commands: string[][]}
}

export default class FilterDocs extends Component<FilterDocsProps, FilterDocsStates> {

    // @todo move to redux

    static xhr: Promise<any> | null
    static doc: {commands: string[][]}

    constructor(props, context) {
        super(props, context)
        this.state = { doc: FilterDocs.doc }
    }

    componentDidMount() {
        if (!FilterDocs.xhr) {
            FilterDocs.xhr = fetchApi('/filter-help').then(response => response.json())
            FilterDocs.xhr.catch(() => {
                FilterDocs.xhr = null
            })
        }
        if (!this.state.doc) {
            FilterDocs.xhr.then(doc => {
                FilterDocs.doc = doc
                this.setState({ doc })
            })
        }
    }

    render() {
        const { doc } = this.state
        return !doc ? (
            <i className="fa fa-spinner fa-spin"/>
        ) : (
            <table className="table table-condensed">
                <tbody>
                    {doc.commands.map(cmd => (
                        <tr key={cmd[1]} onClick={e => this.props.selectHandler(cmd[0].split(" ")[0] + " ")}>
                            <td>{cmd[0].replace(' ', '\u00a0')}</td>
                            <td>{cmd[1]}</td>
                        </tr>
                    ))}
                    <tr key="docs-link">
                        <td colSpan={2}>
                            <a href="http://wiki.66rpg.com/pages/viewpage.action?pageId=61734996"
                                target="_blank">
                                <i className="fa fa-external-link"/>
                            &nbsp; 使用文档 docs</a>
                        </td>
                    </tr>
                </tbody>
            </table>
        )
    }
}
