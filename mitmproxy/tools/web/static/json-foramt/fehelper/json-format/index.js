
let editor = {}
    , LOCAL_KEY_OF_LAYOUT = "local-layout-key"
    , JSON_LINT = "jsonformat:json-lint-switch"
    , EDIT_ON_CLICK = "jsonformat:edit-on-click"
    , AUTO_DECODE = "jsonformat:auto-decode";
new Vue({
    el: "#pageContainer",
    data: {
        defaultResultTpl: '<div class="x-placeholder"><img src="../json-format/json-demo.jpg" alt="json-placeholder"></div>',
        placeHolder: "",
        jsonFormattedSource: "",
        errorMsg: "",
        errorJsonCode: "",
        errorPos: "",
        jfCallbackName_start: "",
        jfCallbackName_end: "",
        jsonLintSwitch: !0,
        autoDecode: !1,
        fireChange: !0,
        overrideJson: !1
    },
    mounted: function() {
        this.placeHolder = this.defaultResultTpl,
            this.autoDecode = localStorage.getItem(AUTO_DECODE),
            this.autoDecode = "true" === this.autoDecode,
            this.jsonLintSwitch = "false" !== localStorage.getItem(JSON_LINT),
            this.overrideJson = "true" === localStorage.getItem(EDIT_ON_CLICK),
            this.changeLayout(localStorage.getItem(LOCAL_KEY_OF_LAYOUT)),
            (editor = CodeMirror.fromTextArea(this.$refs.jsonBox, {
                mode: "text/javascript",
                lineNumbers: !0,
                matchBrackets: !0,
                styleActiveLine: !0,
                lineWrapping: !0
            })).focus(),
            window._OnJsonItemClickByFH = (e=>{
                    this.overrideJson && this.disableEditorChange(e)
                }
            ),
            editor.on("change", (e,t)=>{
                    this.jsonFormattedSource = e.getValue().replace(/\n/gm, " "),
                    this.fireChange && this.format()
                }
            ),
        "chrome-extension:" === location.protocol && chrome.runtime.onMessage.addListener((e,t,o)=>("TAB_CREATED_OR_UPDATED" === e.type && e.content && e.event === location.pathname.split("/")[1] && (editor.setValue(e.content || this.defaultResultTpl),
            this.format()),
        o && o(),
            !0))
        editor.setValue(myJson)
    },
    methods: {
        format: function() {
            this.errorMsg = "",
                this.placeHolder = this.defaultResultTpl,
                this.jfCallbackName_start = "",
                this.jfCallbackName_end = "";
            let e = editor.getValue().replace(/\n/gm, " ");
            if (!e)
                return !1;
            let t = null
                , o = null;
            try {
                let s = /^([\w\.]+)\(\s*([\s\S]*)\s*\)$/gim.exec(e);
                null != s && (t = s[1],
                    e = s[2]),
                    o = JSON.parse(e)
            } catch (t) {
                try {
                    o = new Function("return " + e)()
                } catch (t) {
                    try {
                        if ("string" == typeof (o = new Function("return '" + e + "'")()))
                            try {
                                o = JSON.parse(o)
                            } catch (e) {
                                o = new Function("return " + o)()
                            }
                    } catch (e) {
                        this.errorMsg = e.message
                    }
                }
            }
            if (null != o && "object" == typeof o && !this.errorMsg.length) {
                try {
                    let t = document.querySelectorAll("[name=jsonsort]:checked")[0].value;
                    "0" !== t && (o = JsonABC.sortObj(o, parseInt(t), !0)),
                        e = JSON.stringify(o)
                } catch (e) {
                    this.errorMsg = e.message
                }
                this.errorMsg.length || (this.placeHolder = "",
                    this.$nextTick(()=>{
                            let o = /Firefox/.test(navigator.userAgent);
                            this.autoDecode ? (async()=>{
                                    let t = await JsonEnDecode.urlDecodeByFetch(e);
                                    e = JsonEnDecode.uniDecode(t),
                                        o ? Formatter.formatSync(e) : Formatter.format(e)
                                }
                            )() : o ? Formatter.formatSync(e) : Formatter.format(e),
                                this.jsonFormattedSource = e,
                                null != t ? (this.jfCallbackName_start = t + "(",
                                    this.jfCallbackName_end = ")") : (this.jfCallbackName_start = "",
                                    this.jfCallbackName_end = "")
                        }
                    ),
                    this.$nextTick(()=>{
                            this.updateWrapperHeight()
                        }
                    ))
            }
            return !this.errorMsg.length || (this.jsonLintSwitch ? this.lintOn() : (this.placeHolder = '<span class="x-error">' + this.errorMsg + "</span>",
                !1))
        },
        compress: function() {
            if (this.format()) {
                let e = this.jfCallbackName_start + this.jsonFormattedSource + this.jfCallbackName_end;
                this.disableEditorChange(e)
            }
        },
        autoDecodeFn: function() {
            this.$nextTick(()=>{
                    localStorage.setItem(AUTO_DECODE, this.autoDecode),
                        this.format()
                }
            )
        },
        uniEncode: function() {
            editor.setValue(JsonEnDecode.uniEncode(editor.getValue()))
        },
        uniDecode: function() {
            editor.setValue(JsonEnDecode.uniDecode(editor.getValue()))
        },
        urlDecode: function() {
            JsonEnDecode.urlDecodeByFetch(editor.getValue()).then(e=>editor.setValue(e))
        },
        updateWrapperHeight: function() {
            let e = localStorage.getItem(LOCAL_KEY_OF_LAYOUT)
                , t = document.querySelector("#pageContainer");
            t.style.height = "up-down" === e ? "auto" : Math.max(t.scrollHeight, document.body.scrollHeight) + "px"
        },
        changeLayout: function(e) {
            let t = document.querySelector("#pageContainer");
            "up-down" === e ? (t.classList.remove("layout-left-right"),
                t.classList.add("layout-up-down"),
                this.$refs.btnLeftRight.classList.remove("selected"),
                this.$refs.btnUpDown.classList.add("selected")) : (t.classList.remove("layout-up-down"),
                t.classList.add("layout-left-right"),
                this.$refs.btnLeftRight.classList.add("selected"),
                this.$refs.btnUpDown.classList.remove("selected")),
                localStorage.setItem(LOCAL_KEY_OF_LAYOUT, e),
                this.updateWrapperHeight()
        },
        setCache: function() {
            this.$nextTick(()=>{
                    localStorage.setItem(EDIT_ON_CLICK, this.overrideJson)
                }
            )
        },
        lintOn: function() {
            return this.$nextTick(()=>{
                    localStorage.setItem(JSON_LINT, this.jsonLintSwitch)
                }
            ),
            !editor.getValue().trim() || (this.$nextTick(()=>{
                    if (!this.jsonLintSwitch)
                        return;
                    let e = JsonLint.lintDetect(editor.getValue());
                    isNaN(e.line) || (this.placeHolder = '<div id="errorTips"><div id="tipsBox">错误位置：' + (e.line + 1) + "行，" + (e.col + 1) + '列；缺少字符或字符不正确</div><div id="errorCode">' + e.dom + "</div></div>")
                }
            ),
                !1)
        },
        disableEditorChange: function(e) {
            this.fireChange = !1,
                this.$nextTick(()=>{
                        editor.setValue(e),
                            this.$nextTick(()=>{
                                    this.fireChange = !0
                                }
                            )
                    }
                )
        },
        setDemo: function() {
            editor.setValue('{"BigIntSupported":995815895020119788889,"date":"20180322","message":"Success !","status":200,"city":"北京","count":632,"data":{"shidu":"34%","pm25":73,"pm10":91,"quality":"良","wendu":"5","ganmao":"极少数敏感人群应减少户外活动","yesterday":{"date":"21日星期三","sunrise":"06:19","high":"高温 11.0℃","low":"低温 1.0℃","sunset":"18:26","aqi":85,"fx":"南风","fl":"<3级","type":"多云","notice":"阴晴之间，谨防紫外线侵扰"},"forecast":[{"date":"22日星期四","sunrise":"06:17","high":"高温 17.0℃","low":"低温 1.0℃","sunset":"18:27","aqi":98,"fx":"西南风","fl":"<3级","type":"晴","notice":"愿你拥有比阳光明媚的心情"},{"date":"23日星期五","sunrise":"06:16","high":"高温 18.0℃","low":"低温 5.0℃","sunset":"18:28","aqi":118,"fx":"无持续风向","fl":"<3级","type":"多云","notice":"阴晴之间，谨防紫外线侵扰"},{"date":"24日星期六","sunrise":"06:14","high":"高温 21.0℃","low":"低温 7.0℃","sunset":"18:29","aqi":52,"fx":"西南风","fl":"<3级","type":"晴","notice":"愿你拥有比阳光明媚的心情"},{"date":"25日星期日","sunrise":"06:13","high":"高温 22.0℃","low":"低温 7.0℃","sunset":"18:30","aqi":71,"fx":"西南风","fl":"<3级","type":"晴","notice":"愿你拥有比阳光明媚的心情"},{"date":"26日星期一","sunrise":"06:11","high":"高温 21.0℃","low":"低温 8.0℃","sunset":"18:31","aqi":97,"fx":"西南风","fl":"<3级","type":"多云","notice":"阴晴之间，谨防紫外线侵扰"}]}}')
        }
    }
});
// 在需要观察的元素上创建一个新的 ResizeObserver 实例
// 将调整后的高度通过 postMessage 发送出去
const resizeObserver = new ResizeObserver(entries => {
    for (let entry of entries) {
        window.parent.postMessage({
            frameHeight: entry.contentRect.height
        }, '*');
    }
});

// 开始观察 "#jfContent" 元素
const observedElement = document.getElementById("jfContent");
if (observedElement) {
    resizeObserver.observe(observedElement);
}
