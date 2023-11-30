!function(e) {
    "use strict";
    function t(e) {
        for (var t = 0; t < e.state.activeLines.length; t++)
            e.removeLineClass(e.state.activeLines[t], "wrap", "CodeMirror-activeline"),
                e.removeLineClass(e.state.activeLines[t], "background", "CodeMirror-activeline-background"),
                e.removeLineClass(e.state.activeLines[t], "gutter", "CodeMirror-activeline-gutter")
    }
    function i(e, i) {
        for (var n = [], r = 0; r < i.length; r++) {
            var a = i[r]
                , o = e.getOption("styleActiveLine");
            if ("object" == typeof o && o.nonEmpty ? a.anchor.line == a.head.line : a.empty()) {
                var s = e.getLineHandleVisualStart(a.head.line);
                n[n.length - 1] != s && n.push(s)
            }
        }
        (function(e, t) {
                if (e.length != t.length)
                    return !1;
                for (var i = 0; i < e.length; i++)
                    if (e[i] != t[i])
                        return !1;
                return !0
            }
        )(e.state.activeLines, n) || e.operation(function() {
            t(e);
            for (var i = 0; i < n.length; i++)
                e.addLineClass(n[i], "wrap", "CodeMirror-activeline"),
                    e.addLineClass(n[i], "background", "CodeMirror-activeline-background"),
                    e.addLineClass(n[i], "gutter", "CodeMirror-activeline-gutter");
            e.state.activeLines = n
        })
    }
    function n(e, t) {
        i(e, t.ranges)
    }
    e.defineOption("styleActiveLine", !1, function(r, a, o) {
        var s = o != e.Init && o;
        a == s || (s && (r.off("beforeSelectionChange", n),
            t(r),
            delete r.state.activeLines),
        a && (r.state.activeLines = [],
            i(r, r.listSelections()),
            r.on("beforeSelectionChange", n)))
    })
}(CodeMirror);
