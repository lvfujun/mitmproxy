import React, { RefObject, useEffect } from "react";

type ContentLinesRendererProps = {
    lines: [style: string, text: string][][],
    rawJson: string,
    maxLines: number
    description: string,
    showMore: () => void
}

const LineRenderer: React.FC<ContentLinesRendererProps> = React.memo(
    function LineRenderer({lines, rawJson, description = "", maxLines, showMore}) {
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

function utf8_to_b64(str: string): string {
    return window.btoa(unescape(encodeURIComponent(str)));
}

function b64_to_utf8(str: string): string {
    return decodeURIComponent(escape(window.atob(str)));
}

function FrameWrapper(rawJson: string) {
    const ref: RefObject<HTMLIFrameElement> = React.useRef(null);
    const [height, setHeight] = React.useState("0px");

    // Declare a state variable to hold the focused element before iframe load
    const [focusedElementBeforeIframeLoaded, setFocusedElementBeforeIframeLoaded] = React.useState<Element | null>(null);

    useEffect(() => {
        // Save the current focused element when iframe starts to load
        setFocusedElementBeforeIframeLoaded(document.activeElement);
    }, []);

    const onLoad = () => {
        let height = 0;
        let count = 0;
        const timer = setInterval(function () {
            count++;
            if (count > 1000) {
                clearInterval(timer)
                return;
            }
            try {
                const jfContentHeight = ref.current?.contentWindow?.document.getElementById("jfContent")?.offsetHeight;
                if (jfContentHeight == 0) {
                    return;
                }
                const safeJfContentHeight = jfContentHeight || 0;
                if (height != safeJfContentHeight + 100) {
                    height = safeJfContentHeight + 100
                    setHeight(height + "px");
                }
            } catch (e) {
                clearInterval(timer)
            }
        }, 25)

        // Return focus to the previously focused element
        if (focusedElementBeforeIframeLoaded) {
            (focusedElementBeforeIframeLoaded as HTMLElement).focus();
        }
    };

    localStorage.setItem("rawJson", rawJson)

    return (
        <iframe
            ref={ref}
            onLoad={onLoad}
            id="myFrame"
            src={"/json-format?my_json=1"}
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
    );
}

function QueryLineRenderer(lines: [string, string][][], maxLines: number, showMore: () => void): JSX.Element {
    return <pre>
                {lines.map((line, i) =>
                    i === maxLines
                        ? <button key="showmore" onClick={showMore}
                                  className="btn btn-xs btn-info">
                            <i className="fa fa-angle-double-down" aria-hidden="true"/> Show more
                        </button>
                        : <div key={i}>
                            {line.map(([style, text], j) => <span key={j} className={style}>{text}</span>)}
                        </div>
                )}
            </pre>
}

export default LineRenderer;
