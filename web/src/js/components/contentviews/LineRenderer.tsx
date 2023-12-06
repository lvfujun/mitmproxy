import React, {useEffect, useState, useRef, RefObject} from "react";

type ContentLinesRendererProps = {
    lines: [style: string, text: string][][],
    rawJson: string,
    maxLines: number
    description: string,
    showMore: () => void
}

const LineRenderer: React.FC<ContentLinesRendererProps> = React.memo(
    function LineRenderer({ lines, rawJson, description = "", maxLines, showMore }) {
        if (!Array.isArray(lines) || lines.length === 0) {
            return null;
        }

        const safeDescription = description || "";
        if (safeDescription.indexOf("JSON") !== -1) {
            return FrameWrapper(rawJson)
        } else {
            return QueryLineRenderer(lines, maxLines, showMore)
        }
    }
);

function FrameWrapper(rawJson: string) {
    const ref: RefObject<HTMLIFrameElement> = React.useRef(null);
    const [height, setHeight] = React.useState("0px");
    const [divContent, setDivContent] = useState<string>('');
    const [divWidth, setDivWidth] = useState<string>('auto');

    useEffect(() => {
        window.addEventListener("message", (event) => {
            if (typeof event.data === 'object') {
                if (event.data.frameHeight) {
                    setHeight(`${event.data.frameHeight + 100}px`);
                }
                if (typeof event.data.statusBarContent === 'string') {
                    if (event.data.isHide) {
                        setDivContent('');
                    } else {
                        setDivContent(event.data.statusBarContent.replaceAll('.', '->'));
                    }
                }
            }
        }, false);
    }, []);

    const [focusedElementBeforeIframeLoaded, setFocusedElementBeforeIframeLoaded] = React.useState<Element | null>(null);

    useEffect(() => {
        setFocusedElementBeforeIframeLoaded(document.activeElement);
    }, []);

    useEffect(() => {
        function handleResize() {
            const contentView = document.querySelector('.contentview');
            if (contentView) {
                const width = contentView.getBoundingClientRect().width;
                setDivWidth(width);
            }
        }

        window.addEventListener('resize', handleResize);
        handleResize();

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    const onLoad = () => {
        if (focusedElementBeforeIframeLoaded) {
            (focusedElementBeforeIframeLoaded as HTMLElement).focus();
        }
    };

    localStorage.setItem("rawJson", rawJson)

    return (
        <>
            <iframe
                ref={ref}
                onLoad={onLoad}
                id="myFrame"
                src={"/json-format?my_json=1&v=2"}
                width="100%"
                height={height}
                scrolling="no"
                frameBorder="0"
                style={{
                    maxWidth: "100%",
                    width: "100%",
                    overflow: "auto",
                }}
            ></iframe>
            {divContent &&
                <div
                    style={{
                        position: 'fixed',
                        bottom: '25px',
                        width: divWidth, // Use divWidth state
                        background: '#f5f5f5',
                        borderTop: '1px solid #f4f4f4',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        padding: '2px 0px 2px 2px',
                        zIndex: '10',
                        fontFamily: 'font-family',
                        color: "#666",
                        marginLeft: '-10px',
                    }}
                    dangerouslySetInnerHTML={{ __html: divContent }}
                />
            }
        </>
    );
}

function QueryLineRenderer(lines: [string, string][][], maxLines: number, showMore: () => void): JSX.Element {
    return <pre>
        {lines.map((line, i) =>
            i === maxLines
                ? <button key="showmore" onClick={showMore}
                    className="btn btn-xs btn-info">
                    <i className="fa fa-angle-double-down" aria-hidden="true" /> Show more
                </button>
                : <div key={i}>
                    {line.map(([style, text], j) => <span key={j} className={style}>{text}</span>)}
                </div>
        )}
    </pre>
}

export default LineRenderer;
