!function(t) {
    function e(t, e, r) {
        var a = t.getLineHandle(e.line)
            , i = e.ch - 1
            , l = r && r.afterCursor;
        null == l && (l = /(^| )cm-fat-cursor($| )/.test(t.getWrapperElement().className));
        var h = !l && 0 <= i && o[a.text.charAt(i)] || o[a.text.charAt(++i)];
        if (!h)
            return null;
        var s = ">" == h.charAt(1) ? 1 : -1;
        if (r && r.strict && 0 < s != (i == e.ch))
            return null;
        var u = t.getTokenTypeAt(c(e.line, i + 1))
            , f = n(t, c(e.line, i + (0 < s ? 1 : 0)), s, u || null, r);
        return null == f ? null : {
            from: c(e.line, i),
            to: f && f.pos,
            match: f && f.ch == h.charAt(0),
            forward: 0 < s
        }
    }
    function n(t, e, n, r, a) {
        for (var i, l = a && a.maxScanLineLength || 1e4, h = a && a.maxScanLines || 1e3, s = [], u = a && a.bracketRegex ? a.bracketRegex : /[(){}[\]]/, f = 0 < n ? Math.min(e.line + h, t.lastLine() + 1) : Math.max(t.firstLine() - 1, e.line - h), g = e.line; g != f; g += n)
            if (i = t.getLine(g)) {
                var m = 0 < n ? 0 : i.length - 1
                    , d = 0 < n ? i.length : -1;
                if (!(i.length > l))
                    for (g == e.line && (m = e.ch - (0 > n ? 1 : 0)); m != d; m += n) {
                        var k = i.charAt(m);
                        if (u.test(k) && (void 0 === r || t.getTokenTypeAt(c(g, m + 1)) == r)) {
                            var p = o[k];
                            if (">" == p.charAt(1) == 0 < n)
                                s.push(k);
                            else {
                                if (!s.length)
                                    return {
                                        pos: c(g, m),
                                        ch: k
                                    };
                                s.pop()
                            }
                        }
                    }
            }
        return g - n != (0 < n ? t.lastLine() : t.firstLine()) && null
    }
    function r(t, n, r) {
        for (var a, o = t.state.matchBrackets.maxHighlightLineLength || 1e3, l = [], h = t.listSelections(), s = 0; s < h.length; s++)
            if ((a = h[s].empty() && e(t, h[s].head, r)) && t.getLine(a.from.line).length <= o) {
                var u = a.match ? "CodeMirror-matchingbracket" : "CodeMirror-nonmatchingbracket";
                l.push(t.markText(a.from, c(a.from.line, a.from.ch + 1), {
                    className: u
                })),
                a.to && t.getLine(a.to.line).length <= o && l.push(t.markText(a.to, c(a.to.line, a.to.ch + 1), {
                    className: u
                }))
            }
        if (l.length) {
            i && t.state.focused && t.focus();
            var f = function() {
                t.operation(function() {
                    for (var t = 0; t < l.length; t++)
                        l[t].clear()
                })
            };
            if (!n)
                return f;
            setTimeout(f, 800)
        }
    }
    function a(t) {
        t.operation(function() {
            t.state.matchBrackets.currentlyHighlighted && (t.state.matchBrackets.currentlyHighlighted(),
                t.state.matchBrackets.currentlyHighlighted = null),
                t.state.matchBrackets.currentlyHighlighted = r(t, !1, t.state.matchBrackets)
        })
    }
    var i = /MSIE \d/.test(navigator.userAgent) && (null == document.documentMode || 8 > document.documentMode)
        , c = t.Pos
        , o = {
        "(": ")>",
        ")": "(<",
        "[": "]>",
        "]": "[<",
        "{": "}>",
        "}": "{<"
    };
    t.defineOption("matchBrackets", !1, function(e, n, r) {
        r && r != t.Init && (e.off("cursorActivity", a),
        e.state.matchBrackets && e.state.matchBrackets.currentlyHighlighted && (e.state.matchBrackets.currentlyHighlighted(),
            e.state.matchBrackets.currentlyHighlighted = null)),
        n && (e.state.matchBrackets = "object" == typeof n ? n : {},
            e.on("cursorActivity", a))
    }),
        t.defineExtension("matchBrackets", function() {
            r(this, !0)
        }),
        t.defineExtension("findMatchingBracket", function(t, n, r) {
            return (r || "boolean" == typeof n) && (r ? (r.strict = n,
                n = r) : n = n ? {
                strict: !0
            } : null),
                e(this, t, n)
        }),
        t.defineExtension("scanForBracket", function(t, e, r, a) {
            return n(this, t, e, r, a)
        })
}(CodeMirror);
