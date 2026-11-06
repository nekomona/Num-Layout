/* Illustrative geometry only. This page does not connect to Virtuoso. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const numeric = (key, label, value, min, max, hint, step = "any") => ({
    key,
    label,
    value,
    min,
    max,
    hint,
    step,
  });
  const choice = (key, label, value, options) => ({
    key,
    label,
    value,
    options,
  });
  const tools = [
    {
      id: "pick",
      name: "Pick a dimension",
      category: "READ THE GEOMETRY",
      key: "J + edge picks",
      description:
        "Take a value from an edge, or pick a second parallel edge to measure the space between them.",
      anchor: "j-number-entry",
      fields: [
        choice("kind", "Measure", "spacing", [
          ["spacing", "Parallel-edge spacing"],
          ["length", "One edge length"],
        ]),
      ],
    },
    {
      id: "width",
      name: "Path / Wire width",
      category: "DRAW WITH A DIMENSION",
      key: "J",
      description:
        "Set the width while a native Path or Wire command is active. See the new contour before confirming.",
      anchor: "j-number-entry",
      fields: [numeric("value", "Width", 2, 0.2, 5, "Scene range: 0.2–5 µm")],
    },
    {
      id: "rectangle",
      name: "Rectangle",
      category: "TWO DIMENSIONS, ONE ENTRY",
      key: "J · X,Y",
      description:
        "Enter width and height together. After the first corner, the rectangle follows the cursor's quadrant.",
      anchor: "xy-input-and-absolute-position",
      fields: [
        {
          key: "value",
          label: "Width, height",
          value: "12,6",
          hint: "Scene range: width 2–28, height 2–15 µm",
        },
      ],
    },
    {
      id: "measure",
      name: "Measurement",
      category: "A RULER THAT REACHES",
      key: "K → J",
      description:
        "Give a new two-point ruler an exact length along the chosen direction.",
      anchor: "j-number-entry",
      fields: [
        numeric("value", "Ruler length", 20, 4, 35, "Scene range: 4–35 µm"),
      ],
    },
    {
      id: "stretch",
      name: "Stretch",
      category: "SET THE FINAL EXTENT",
      key: "Partial Stretch → J",
      description:
        "Resize one selected edge to a final dimension while the opposite side stays fixed.",
      anchor: "j-number-entry",
      fields: [
        numeric("value", "Final X extent", 18, 4, 28, "Scene range: 4–28 µm"),
      ],
    },
    {
      id: "move",
      name: "Move",
      category: "DELTA OR DESTINATION",
      key: "J / Shift+J",
      description:
        "Choose a relative displacement or an absolute reference-point position, then preview the target.",
      anchor: "xy-input-and-absolute-position",
      fields: [
        choice("mode", "Coordinate mode", "relative", [
          ["relative", "J · relative X,Y"],
          ["absolute", "Shift+J · absolute X,Y"],
        ]),
        {
          key: "value",
          label: "X,Y",
          value: "12,6",
          hint: "Relative: −8–20, −7–10. Absolute: 4–36, 3–20 µm.",
        },
      ],
    },
    {
      id: "copy",
      name: "Copy + count",
      category: "ONE PITCH, MANY COPIES",
      key: "N → J",
      description:
        "Set a positive integer count with N, then use J to set the per-copy displacement. Preview every Step target.",
      anchor: "copy-count-n",
      fields: [
        numeric(
          "count",
          "Number of copies",
          3,
          1,
          4,
          "Scene range: 1–4 copies",
          1,
        ),
        numeric(
          "value",
          "Per-copy displacement",
          9,
          5,
          10,
          "Scene range: 5–10 µm; direction is horizontal",
        ),
      ],
    },
    {
      id: "contour",
      name: "Contour",
      category: "OFFSET A BOUNDARY",
      key: "Idle selection → Shift+J",
      description:
        "Resize a selected rectangle around a pivot. Set the offset, pick the pivot, then choose inside or outside.",
      anchor: "contour-a-rectangle",
      fields: [
        numeric("value", "Offset", 2, 0.5, 3, "Scene range: 0.5–3 µm"),
        choice("side", "Direction", "outside", [
          ["outside", "Outside"],
          ["inside", "Inside"],
        ]),
      ],
    },
    {
      id: "cleanup",
      name: "Steiner cleanup",
      category: "CLEAR INVISIBLE OBJECTS",
      key: "Toolbar · cleanup",
      description:
        "Remove invisible Steiner objects from the edited layout while keeping the drawn geometry.",
      anchor: "toolbar-and-previews",
      fields: [
        numeric(
          "count",
          "Example Steiner objects",
          4,
          2,
          6,
          "Markers are revealed here only for explanation",
          1,
        ),
      ],
    },
  ];
  const UI = {
    en: {
      title: "Numeric Layout Assist · Interactive lab",
      description:
        "Explore Numeric Layout Assist: interactive illustrations of precise widths, positions, copies, and contours in Virtuoso Layout.",
      skip: "Skip to demonstration",
      home: "Numeric Layout Assist home",
      resources: "Resources",
      language: "Language",
      guide: "User guide ↗",
      homeLink: "Project home ↗",
      license: "MIT license ↗",
      builtFor: "BUILT FOR VIRTUOSO LAYOUT",
      hero: "Precision,<br><span>at your cursor.</span>",
      heroCopy:
        "Pick a dimension. Type a value.<br>Preview the result before you commit.",
      numericEntry: "numeric entry",
      absolute: "absolute / contour",
      copyCount: "copy count",
      explore: "EXPLORE THE TOOLS <span>01—09</span>",
      chooseTool: "Choose a tool",
      aside: "Every scene uses synthetic geometry.<br>Explore freely.",
      illustrative: "ILLUSTRATIVE DEMO",
      animatedInput: "Animated input",
      play: "▶ Play",
      pause: "Ⅱ Pause",
      replay: "↺ Replay",
      next: "Next step →",
      reset: "↺ Reset",
      loopOn: "↻ Loop on",
      loopOff: "↻ Loop off",
      loopTitle: "Wait 3 seconds between loops",
      showcaseOn: "⇄ Showcase on",
      showcaseOff: "⇄ Showcase off",
      showcaseTitle: "Automatically advance through every tool",
      speed: "Speed",
      steps: "Demonstration steps",
      tryValue: "TRY A VALUE",
      apply: "Apply & replay ↗",
      autoReplay:
        "Changes replay automatically: choose an option, press Enter, leave the input, or pause typing for 3 seconds.",
      whatHappens: "WHAT HAPPENS",
      candidate: "Candidate",
      preview: "Selection / preview",
      geometry: "Geometry",
      reference: "Read the tool guide ↗",
      principles: "A SMALL HABIT. A PRECISE EDIT.",
      principle1: "Pick or type",
      principle1Copy:
        "Measure existing geometry, or enter the dimension you already know.",
      principle2: "See the target",
      principle2Copy:
        "Magenta previews show the intended result before confirmation.",
      principle3: "Stay in the flow",
      principle3Copy:
        "Numeric entry works with the native drawing and editing command.",
      footer:
        'Interactive illustrations, not a live Virtuoso session. Native snapping and command behavior are described in the <a id="footer-guide-link" href="guide.html">guide</a>.',
      overview: "Project overview ↗",
      noscript:
        'Enable JavaScript for interactive demonstrations, or read the <a href="guide.html">complete user guide</a>.',
      workspace: "Interactive tool demonstrations",
      done: "Done.",
      input: "INPUT",
      action: "ACTION",
      syntheticScene: "Synthetic layout demonstration",
      choiceError: "Choose one of the listed modes.",
      rangeError: "Use the scene ranges shown below the input.",
      xyError: "Enter two numbers as X,Y for this scene.",
      wholeNumber: " as a whole number",
    },
    zh: {
      title: "Numeric Layout Assist · 交互演示",
      description:
        "体验 Numeric Layout Assist：在 Virtuoso Layout 中精确输入宽度、位置、副本数量和轮廓偏移的交互演示。",
      skip: "跳到演示",
      home: "Numeric Layout Assist 首页",
      resources: "资源",
      language: "语言",
      guide: "使用指南 ↗",
      homeLink: "项目首页 ↗",
      license: "MIT 许可证 ↗",
      builtFor: "专为 VIRTUOSO LAYOUT 设计",
      hero: "精确，<br><span>就在光标边。</span>",
      heroCopy: "选择尺寸，输入数值。<br>提交前先看结果。",
      numericEntry: "数值输入",
      absolute: "绝对定位 / 轮廓",
      copyCount: "复制数量",
      explore: "探索工具 <span>01—09</span>",
      chooseTool: "选择工具",
      aside: "所有场景均使用合成几何。<br>请自由体验。",
      illustrative: "示意演示",
      animatedInput: "动画输入",
      play: "▶ 播放",
      pause: "Ⅱ 暂停",
      replay: "↺ 重播",
      next: "下一步 →",
      reset: "↺ 重置",
      loopOn: "↻ 单页循环",
      loopOff: "↻ 本页单次",
      loopTitle: "每轮结束后等待 3 秒",
      showcaseOn: "⇄ 循环展示：开",
      showcaseOff: "⇄ 循环展示：关",
      showcaseTitle: "自动依次播放全部工具",
      speed: "速度",
      steps: "演示步骤",
      tryValue: "尝试数值",
      apply: "应用并重播 ↗",
      autoReplay:
        "修改后会自动重播：选择选项、按 Enter、离开输入框，或停止输入 3 秒。",
      whatHappens: "会发生什么",
      candidate: "候选",
      preview: "选择 / 预览",
      geometry: "几何",
      reference: "阅读使用指南 ↗",
      principles: "一个小习惯，一次精确编辑。",
      principle1: "量取或键入",
      principle1Copy: "尺寸可以从版图上拾取，也可以直接输入已知值。",
      principle2: "先看结果",
      principle2Copy: "洋红色预览会在确认前显示即将产生的变化。",
      principle3: "继续当前操作",
      principle3Copy: "不必退出正在使用的绘制或编辑命令。",
      footer:
        '页面中的场景为合成示意，不是实时 Virtuoso 会话。Virtuoso 的捕捉和命令行为见 <a id="footer-guide-link" href="guide.zh-CN.html">使用指南</a>。',
      overview: "项目概览 ↗",
      noscript:
        '启用 JavaScript 以运行交互演示，或阅读<a href="guide.zh-CN.html">完整使用指南</a>。',
      workspace: "交互式工具演示",
      done: "完成。",
      input: "输入",
      action: "操作",
      syntheticScene: "合成版图演示",
      choiceError: "请选择列表中的一项。",
      rangeError: "请输入下方标注范围内的数值。",
      xyError: "请按 X,Y 输入两个数值。",
      wholeNumber: "，且必须为整数",
    },
  };
  const zhTools = {
    pick: {
      name: "选择尺寸",
      category: "从版图读取尺寸",
      description: "拾取边的长度；再选一条平行边，可改为测量两边间距。",
      anchor: "j-数值输入",
      fields: {
        kind: {
          label: "测量方式",
          options: { spacing: "平行边间距", length: "单边长度" },
        },
      },
    },
    width: {
      name: "Path / Wire 宽度",
      category: "用尺寸绘制",
      description: "在 Path 或 Wire 命令中直接设置宽度，确认前先看轮廓预览。",
      anchor: "j-数值输入",
      fields: {
        value: { label: "宽度", hint: "场景范围：0.2–5 µm" },
      },
    },
    rectangle: {
      name: "矩形",
      category: "两个尺寸，一次输入",
      description:
        "一次输入宽高。放下第一个角点后，矩形会随光标在当前象限展开。",
      anchor: "xy-输入与绝对位置",
      fields: {
        value: {
          label: "宽度、高度",
          hint: "场景范围：宽度 2–28，高度 2–15 µm",
        },
      },
    },
    measure: {
      name: "测量",
      category: "让标尺落到精确长度",
      description: "沿选定方向为新的两点标尺指定精确长度。",
      anchor: "j-数值输入",
      fields: {
        value: { label: "标尺长度", hint: "场景范围：4–35 µm" },
      },
    },
    stretch: {
      name: "拉伸",
      category: "设置最终范围",
      description: "把选中的边拉到指定尺寸，对边保持不动。",
      anchor: "j-数值输入",
      fields: {
        value: { label: "最终 X 范围", hint: "场景范围：4–28 µm" },
      },
    },
    move: {
      name: "移动",
      category: "位移或目标位置",
      description:
        "按相对距离移动，或把参考点放到绝对坐标；放置前可先看目标位置。",
      anchor: "xy-输入与绝对位置",
      fields: {
        mode: {
          label: "坐标模式",
          options: { relative: "J · 相对 X,Y", absolute: "Shift+J · 绝对 X,Y" },
        },
        value: {
          label: "X,Y",
          hint: "相对：−8–20，−7–10。绝对：4–36，3–20 µm。",
        },
      },
    },
    copy: {
      name: "复制 + 数量",
      category: "一个间距，多个副本",
      description:
        "用 N 设定副本数量，再用 J 设定间距；所有 Step 目标都会先预览。",
      anchor: "copy-数量n",
      fields: {
        count: { label: "副本数量", hint: "场景范围：1–4 个副本" },
        value: { label: "每份位移", hint: "场景范围：5–10 µm，方向为水平" },
      },
    },
    contour: {
      name: "轮廓偏移",
      category: "偏移边界",
      description: "以 pivot 为基准调整矩形：先定偏移，再选 pivot 和内外方向。",
      anchor: "为矩形做-contour",
      fields: {
        value: { label: "偏移量", hint: "场景范围：0.5–3 µm" },
        side: { label: "方向", options: { outside: "外侧", inside: "内侧" } },
      },
    },
    cleanup: {
      name: "Steiner 清理",
      category: "清除不可见对象",
      description: "删除当前版图中的不可见 Steiner 对象，同时保留已绘制几何。",
      anchor: "工具栏与预览",
      fields: {
        count: {
          label: "示例 Steiner 对象数",
          hint: "标记仅在此演示中显示以便说明",
        },
      },
    },
  };
  const params = new URLSearchParams(location.search);
  const exporting = params.has("export");
  const readLanguage = () => {
    try {
      return localStorage.getItem("numeric-layout-assist-language");
    } catch {
      return null;
    }
  };
  const requestedLanguage = params.get("lang")?.toLowerCase();
  const browserLanguage = (
    navigator.languages?.[0] ||
    navigator.language ||
    "en"
  ).toLowerCase();
  let lang = exporting
    ? "en"
    : requestedLanguage?.startsWith("zh")
      ? "zh"
      : requestedLanguage?.startsWith("en")
        ? "en"
        : readLanguage() || (browserLanguage.startsWith("zh") ? "zh" : "en");
  if (!exporting && requestedLanguage) {
    try {
      localStorage.setItem("numeric-layout-assist-language", lang);
    } catch {
      /* Storage may be disabled. */
    }
  }
  const isZh = () => lang === "zh";
  const ui = (key) => UI[lang][key];
  const tr = (en, zh) => (isZh() ? zh : en);
  const toolText = (item, key) => (isZh() ? zhTools[item.id][key] : item[key]);
  const fieldInfo = (field) =>
    isZh() ? zhTools[tool.id].fields[field.key] : null;
  const fieldLabel = (field) => fieldInfo(field)?.label ?? field.label;
  const fieldHint = (field) => fieldInfo(field)?.hint ?? field.hint;
  const fieldOptions = (field) =>
    field.options.map(([value, label]) => [
      value,
      fieldInfo(field)?.options?.[value] ?? label,
    ]);
  function syncLanguageData() {
    for (const item of tools) {
      item.phases = item.phasesEn.map((p) => ({
        ...p,
        title: isZh() ? p.titleZh : p.title,
        description: isZh() ? p.descriptionZh : p.description,
      }));
      item.steps = item.phases.map((p) => p.title);
      item.explanations = item.phases.map((p) => p.description);
    }
  }
  function applyStaticLanguage() {
    document.documentElement.lang = isZh() ? "zh-CN" : "en";
    document.title = ui("title");
    $("page-description").setAttribute("content", ui("description"));
    $("skip-link").textContent = ui("skip");
    $("brand").setAttribute("aria-label", ui("home"));
    $("resource-nav").setAttribute("aria-label", ui("resources"));
    $("language-switch").setAttribute("aria-label", ui("language"));
    document.querySelectorAll("[data-language]").forEach((button) => {
      const active = button.dataset.language === (isZh() ? "zh" : "en");
      button.setAttribute("aria-pressed", String(active));
    });
    $("guide-link").textContent = ui("guide");
    $("guide-link").href = isZh() ? "guide.zh-CN.html" : "guide.html";
    $("home-link").textContent = ui("homeLink");
    $("home-link").href = isZh()
      ? "../site/index.zh-CN.html"
      : "../site/index.html";
    $("license-link").textContent = ui("license");
    $("built-for").innerHTML =
      `<span class="signal-dot"></span> ${ui("builtFor")}`;
    $("hero-title").innerHTML = ui("hero");
    $("hero-copy").innerHTML = ui("heroCopy");
    $("key-entry-label").textContent = ui("numericEntry");
    $("key-absolute-label").textContent = ui("absolute");
    $("key-copy-label").textContent = ui("copyCount");
    $("explore-heading").innerHTML = ui("explore");
    $("tools").setAttribute("aria-label", ui("chooseTool"));
    $("aside-note").innerHTML = ui("aside");
    $("illustration-label").textContent = ui("illustrative");
    $("input-strip").setAttribute("aria-label", ui("animatedInput"));
    $("steps").setAttribute("aria-label", ui("steps"));
    $("try-heading").textContent = ui("tryValue");
    $("apply-button").textContent = ui("apply");
    $("auto-replay-hint").textContent = ui("autoReplay");
    $("what-heading").textContent = ui("whatHappens");
    $("legend-candidate").textContent = ui("candidate");
    $("legend-preview").textContent = ui("preview");
    $("legend-geometry").textContent = ui("geometry");
    $("reference-label").textContent = ui("reference");
    $("principles-eyebrow").textContent = ui("principles");
    $("principle-one-title").textContent = ui("principle1");
    $("principle-one-copy").textContent = ui("principle1Copy");
    $("principle-two-title").textContent = ui("principle2");
    $("principle-two-copy").textContent = ui("principle2Copy");
    $("principle-three-title").textContent = ui("principle3");
    $("principle-three-copy").textContent = ui("principle3Copy");
    $("footer-note").innerHTML = ui("footer");
    $("overview-link").textContent = ui("overview");
    $("overview-link").href = isZh()
      ? "../../README.zh-CN.md"
      : "../../README.md";
    const noscript = document.querySelector("noscript");
    if (noscript) noscript.innerHTML = ui("noscript");
    $("workspace").setAttribute("aria-label", ui("workspace"));
    $("loop").title = ui("loopTitle");
    $("showcase").title = ui("showcaseTitle");
    $("speed-label").textContent = ui("speed");
  }
  const LOOP_WAIT = 3000;
  const ACTION_HOLD = 1200;
  let tool = tools[1],
    step = 0,
    progress = 0,
    values = {},
    playing = false,
    timer = 0,
    lastTick = 0,
    position = 0,
    speed = 1,
    loop = true,
    showcase = true,
    holding = false,
    holdElapsed = 0,
    inputTimer = 0;
  const C = {
    bg: "#17232e",
    grid: "#283946",
    geometry: "#82d2c9",
    fill: "#2b575c",
    yellow: "#efcf72",
    magenta: "#e989f1",
    faint: "#637c8c",
    text: "#c9dce7",
  };
  const X = (x) => 90 + x * 15,
    Y = (y) => 380 - y * 15;
  const round4 = (n) => Number(n.toFixed(4));
  const f = (n) => round4(n).toString();
  const esc = (s) =>
    String(s).replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const text = (x, y, value, color = C.text, size = 15, anchor = "start") =>
    `<text x="${x}" y="${y}" fill="${color}" font-size="${size}" text-anchor="${anchor}" font-family="Consolas, monospace">${esc(value)}</text>`;
  const line = (x1, y1, x2, y2, color = C.faint, width = 2, dash = "") =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
  function rect(
    x,
    y,
    w,
    h,
    { color = C.geometry, fill = C.fill, dash = "", opacity = 1 } = {},
  ) {
    return `<rect x="${X(x)}" y="${Y(y + h)}" width="${w * 15}" height="${h * 15}" fill="${fill}" stroke="${color}" stroke-width="2" opacity="${opacity}" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
  }
  function dim(x1, y1, x2, y2, label, color = C.magenta) {
    const a = X(x1),
      b = Y(y1),
      c = X(x2),
      d = Y(y2);
    return `${line(a, b, c, d, color, 1.4)}<path d="M${a + 5} ${b - 4}L${a} ${b}L${a + 5} ${b + 4} M${c - 5} ${d - 4}L${c} ${d}L${c - 5} ${d + 4}" fill="none" stroke="${color}" stroke-width="1.4"/>${text((a + c) / 2, (b + d) / 2 - 11, label, color, 14, "middle")}`;
  }
  function vdim(x, y1, y2, label, color = C.magenta) {
    const a = X(x),
      b = Y(y1),
      d = Y(y2);
    return `${line(a, b, a, d, color, 1.4)}<path d="M${a - 4} ${b - 5}L${a} ${b}L${a + 4} ${b - 5} M${a - 4} ${d + 5}L${a} ${d}L${a + 4} ${d + 5}" fill="none" stroke="${color}" stroke-width="1.4"/>${text(a + 12, (b + d) / 2 + 5, label, color, 14)}`;
  }
  function cross(x, y, color = C.yellow) {
    return (
      line(X(x) - 6, Y(y), X(x) + 6, Y(y), color) +
      line(X(x), Y(y) - 6, X(x), Y(y) + 6, color)
    );
  }
  function cursor(x, y, label = "", color = C.magenta) {
    const a = X(x),
      b = Y(y);
    const width = label.length * 8 + 20;
    const labelX = Math.min(Math.max(18, a + 20), 880 - width);
    const labelY = Math.max(34, b - 28);
    return `<path data-role="pointer" data-x="${x}" data-y="${y}" d="M${a} ${b}l0 22 6-6 5 10 5-2-5-10 9-1Z" fill="#f7f2e3" stroke="${C.bg}" stroke-width="2"/>${label ? `<g data-role="balloon"><rect x="${labelX}" y="${labelY - 20}" width="${width}" height="30" rx="4" fill="#243643" stroke="${color}"/>${text(labelX + 10, labelY + 1, label, color, 13)}</g>` : ""}`;
  }
  function base() {
    return `<defs><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="${C.grid}" stroke-width=".75"/></pattern></defs><rect width="900" height="460" fill="${C.bg}"/><rect x="30" y="25" width="840" height="395" fill="url(#grid)"/>${line(60, 380, 850, 380, "#3b505f", 1)}${line(90, 410, 90, 45, "#3b505f", 1)}${text(48, 407, "0", C.faint, 11)}${text(849, 403, "X", C.faint, 11)}${text(74, 40, "Y", C.faint, 11)}${text(830, 443, "µm", C.faint, 11)}${[10, 20, 30, 40].map((n) => text(X(n), 399, String(n), C.faint, 11, "middle")).join("")}`;
  }
  const HOME = [44, 2];
  const phase = (id, title, description, point, extra = {}) => ({
    id,
    title,
    description,
    point,
    ...extra,
  });
  const plans = {
    pick: [
      phase(
        "start",
        "Start Stretch",
        "S → click the lower edge of the small rectangle at upper right.",
        [39, 16],
        { key: "S", select: true },
      ),
      phase(
        "activate",
        "Start J",
        "J starts numeric entry for the selected Stretch edge.",
        [39, 16],
        { key: "J" },
      ),
      phase(
        "first",
        "Pick an edge",
        "Move onto an edge, then click to use its length in the Stretch preview.",
        [17, 9],
        { select: true, hover: true },
      ),
      phase(
        "second",
        "Choose the value",
        "Pick a second parallel edge for spacing, or keep the first edge's length.",
        [17, 12],
        { select: true, hover: true },
      ),
      phase(
        "confirm",
        "Apply dimension",
        "Enter applies the picked dimension to the rectangle being stretched.",
        [17, 12],
        { confirm: true },
      ),
    ],
    width: [
      phase(
        "start",
        "Start Path",
        "P → click the short path to pick it up and extend it.",
        [5, 10],
        { key: "P", select: true },
      ),
      phase(
        "aim",
        "Pull a segment",
        "Pull right to preview a narrow path segment before setting its width.",
        [31, 10],
      ),
      phase(
        "input",
        "Enter width",
        "J → type the width. The entire extended path changes width, including the original segment.",
        [31, 10],
        { input: "value", key: "J" },
      ),
      phase(
        "confirm",
        "Apply width",
        "Enter applies the width; native Path remains active for the next point.",
        [31, 10],
        { confirm: true },
      ),
    ],
    rectangle: [
      phase(
        "start",
        "Start Rectangle",
        "R → click the first corner of the new rectangle.",
        [8, 4],
        { key: "R", select: true },
      ),
      phase(
        "aim",
        "Pull the corner",
        "Move into the upper-right quadrant to preview the rectangle.",
        [18, 10],
      ),
      phase(
        "input",
        "Enter X,Y",
        "J → type width,height, one character at a time.",
        [18, 10],
        { input: "value", key: "J" },
      ),
      phase(
        "confirm",
        "Complete rectangle",
        "Enter confirms both dimensions and completes the rectangle.",
        [18, 10],
        { confirm: true },
      ),
    ],
    measure: [
      phase(
        "start",
        "Start Measurement",
        "K → click the starting point. No ruler exists before this click.",
        [5, 10],
        { key: "K", select: true },
      ),
      phase(
        "aim",
        "Choose direction",
        "Pull the mouse right to give the new ruler a horizontal direction.",
        [14, 10],
      ),
      phase(
        "input",
        "Enter length",
        "J → type the length to preview an exact second endpoint.",
        [14, 10],
        { input: "value", key: "J" },
      ),
      phase(
        "confirm",
        "Save ruler",
        "Enter saves the two-point ruler and finishes Measurement.",
        [14, 10],
        { confirm: true },
      ),
    ],
    stretch: [
      phase(
        "start",
        "Start Stretch",
        "S → click the right edge. The opposite edge stays fixed.",
        [17, 9.5],
        { key: "S", select: true, hover: true },
      ),
      phase(
        "input",
        "Set final size",
        "J → type the final X extent to resize the selected edge.",
        [17, 9.5],
        { input: "value", key: "J" },
      ),
      phase(
        "confirm",
        "Apply size",
        "Enter applies the final extent. Whole-object Stretch instead uses displacement.",
        [17, 9.5],
        { confirm: true },
      ),
    ],
    move: [
      phase(
        "start",
        "Start Move",
        "M → click the object. This scene uses its center as the reference point.",
        [10, 9],
        { key: "M", select: true },
      ),
      phase(
        "input",
        "Enter X,Y",
        "J sets a relative delta; Shift+J sets an absolute reference-point position.",
        [10, 9],
        { input: "value", key: "J" },
      ),
      phase(
        "confirm",
        "Place object",
        "Enter places the object at the previewed reference-point position.",
        [10, 9],
        { confirm: true },
      ),
    ],
    copy: [
      phase(
        "start",
        "Start Copy",
        "C → click the first object. The source stays in place.",
        [5, 10.5],
        { key: "C", select: true },
      ),
      phase(
        "aim",
        "Pull a preview",
        "Pull right to show the initial native Copy preview before pressing N.",
        [12, 10.5],
      ),
      phase(
        "count",
        "Set count",
        "N → type a positive integer → Enter. No copies are placed yet.",
        [12, 10.5],
        { input: "count", key: "N", confirm: true },
      ),
      phase(
        "input",
        "Set pitch",
        "J → type the per-copy displacement to preview every Step target.",
        [12, 10.5],
        { input: "value", key: "J" },
      ),
      phase(
        "confirm",
        "Place copies",
        "Enter places the copies at successive multiples of the pitch.",
        [12, 10.5],
        { confirm: true },
      ),
    ],
    contour: [
      phase(
        "start",
        "Select rectangle",
        "Select one rectangle with no native drawing command active.",
        [20, 10],
        { select: true },
      ),
      phase(
        "input",
        "Enter offset",
        "Shift+J → type a positive offset → Enter to choose a pivot.",
        [34, 20],
        { input: "value", key: "Shift+J", confirm: true },
      ),
      phase(
        "pivot",
        "Pick pivot",
        "Shift+J selects a pivot rectangle. You can also pick four bounding edges with J.",
        [20, 15],
        { key: "Shift+J", select: true, confirm: true, hover: true },
      ),
      phase(
        "side",
        "Choose side",
        "Move inside or outside the pivot to choose the contour direction.",
        [34, 18],
      ),
      phase(
        "confirm",
        "Resize rectangle",
        "Enter resizes the selected rectangle around the chosen pivot.",
        [34, 18],
        { confirm: true },
      ),
    ],
    cleanup: [
      phase(
        "start",
        "Inspect layout",
        "Steiner objects are normally invisible; markers reveal them here for explanation.",
        HOME,
      ),
      phase(
        "cleanup",
        "Use cleanup",
        "Click the routing-node and broom toolbar action in an editable layout.",
        [39, 20],
        { key: "Cleanup", select: true },
      ),
      phase(
        "confirm",
        "Objects removed",
        "CIW reports the removed count. Drawn shapes remain; the cellview is not saved.",
        [39, 20],
      ),
    ],
  };
  const phaseZh = {
    pick: [
      ["开始 Stretch", "S → 点击右上方小矩形的下边。"],
      ["启动 J", "J 打开数值输入，用于修改已选中的 Stretch 边。"],
      ["选择边", "将指针移到边上并点击，用其长度更新 Stretch 预览。"],
      ["选择数值", "选择第二条平行边测量间距，或保留第一条边的长度。"],
      ["应用尺寸", "按 Enter 将拾取的尺寸应用到正在拉伸的矩形。"],
    ],
    width: [
      ["开始 Path", "P → 点击短路径以选中并延长它。"],
      ["拉出线段", "向右拖动指针，先预览窄 Path 段。"],
      ["输入宽度", "J → 输入宽度；整条延长后的 Path（包括原段）会一起变化。"],
      ["应用宽度", "按 Enter 应用宽度；Path 命令继续保持活动。"],
    ],
    rectangle: [
      ["开始 Rectangle", "R → 点击新矩形的第一个角点。"],
      ["拉出角点", "移动到右上方象限，预览矩形范围。"],
      ["输入 X,Y", "J → 依次输入宽度和高度。"],
      ["完成矩形", "按 Enter 确认两个尺寸并完成矩形。"],
    ],
    measure: [
      ["开始 Measurement", "K → 点击起点；在此之前不会出现标尺。"],
      ["选择方向", "向右拖动鼠标，为新标尺确定水平方向。"],
      ["输入长度", "J → 输入长度，预览精确的第二端点。"],
      ["保存标尺", "按 Enter 保存两点标尺并结束 Measurement。"],
    ],
    stretch: [
      ["开始 Stretch", "S → 点击右边；对边保持固定。"],
      ["设置最终尺寸", "J → 输入最终 X 范围，调整选中边。"],
      ["应用尺寸", "按 Enter 应用最终范围；整体对象的 Stretch 使用位移。"],
    ],
    move: [
      ["开始 Move", "M → 点击对象；此场景以对象中心作为参考点。"],
      ["输入 X,Y", "J 使用相对位移；Shift+J 使用参考点的绝对位置。"],
      ["放置对象", "按 Enter 将对象放到预览的参考点位置。"],
    ],
    copy: [
      ["开始 Copy", "C → 点击第一个对象；源对象保持原位。"],
      ["拉出预览", "向右拖动，在按 N 前显示初始 Copy 预览。"],
      ["设置数量", "N → 输入正整数 → Enter；此时尚未放置副本。"],
      ["设置间距", "J → 输入每份位移，预览每个 Step 目标。"],
      ["放置副本", "按 Enter 后，副本会按该间距的连续倍数放置。"],
    ],
    contour: [
      ["选择矩形", "没有正在运行的绘图命令时，选择一个矩形。"],
      ["输入偏移", "Shift+J → 输入正偏移 → Enter，随后选择 pivot。"],
      ["选择 pivot", "Shift+J 选择 pivot 矩形；也可用 J 选择四条边界边。"],
      ["选择方向", "将指针移到 pivot 内侧或外侧，选择轮廓方向。"],
      ["调整矩形", "按 Enter 围绕所选 pivot 调整矩形。"],
    ],
    cleanup: [
      ["检查版图", "Steiner 通常不可见；这里显示标记以便说明。"],
      ["清理 Steiner", "在可编辑版图中点击路由节点与扫帚工具栏按钮。"],
      ["对象已删除", "CIW 会报告删除数量；图形保留，cellview 不会自动保存。"],
    ],
  };
  for (const item of tools) {
    item.phases = plans[item.id];
    item.steps = item.phases.map((p) => p.title);
    item.explanations = item.phases.map((p) => p.description);
    item.phasesEn = plans[item.id];
    item.phases.forEach((p, index) => {
      p.titleZh = phaseZh[item.id][index][0];
      p.descriptionZh = phaseZh[item.id][index][1];
    });
  }
  function pointAt(index) {
    const p = tool.phases[index];
    if (!p) return HOME;
    if (
      tool.id === "pick" &&
      values.kind === "length" &&
      ["second", "confirm"].includes(p.id)
    )
      return [17, 9];
    if (
      tool.id === "contour" &&
      ["side", "confirm"].includes(p.id) &&
      values.side === "inside"
    )
      return [24, 11];
    return p.point;
  }
  function phaseSpec(index = step) {
    const p = tool.phases[index];
    const event = (key, start, type = "key", character = "") => ({
      key,
      start,
      end: start + 180,
      type,
      character,
    });
    const key =
      tool.id === "move" && p.input && values.mode === "absolute"
        ? "Shift+J"
        : p.key;
    let duration = 1900,
      events = [],
      input = null;
    const from = pointAt(index - 1),
      to = pointAt(index);
    const moving = from.some((value, axis) => value !== to[axis]);
    const moveStart =
      moving && key && !p.input && key !== "Cleanup"
        ? 180 + 180 + ACTION_HOLD
        : 0;
    const moveDuration = moving ? 1000 : 0;
    if (p.input) {
      const value = values[p.input];
      input = Array.isArray(value) ? value.map(f).join(",") : f(value);
      const keyAt = moving ? moveDuration + 300 : 180;
      const firstDigit = keyAt + 180 + ACTION_HOLD;
      events.push(event(key, keyAt));
      [...input].forEach((character, i) =>
        events.push(
          event(character, firstDigit + i * 260, "character", character),
        ),
      );
      if (p.confirm)
        events.push(event("Enter", events.at(-1).end + ACTION_HOLD, "confirm"));
      duration = events.at(-1).end + ACTION_HOLD;
    } else {
      if (key && key !== "Cleanup") events.push(event(key, 180));
      const skipPick =
        tool.id === "pick" && p.id === "second" && values.kind === "length";
      if (p.select && !skipPick)
        events.push(
          event(
            key === "Cleanup" ? "Cleanup" : "Click",
            moveStart + moveDuration + 300,
            "select",
          ),
        );
      if (p.confirm) {
        events.push(
          event(
            "Enter",
            p.select ? events.at(-1).end + ACTION_HOLD : 350,
            "confirm",
          ),
        );
      }
      duration =
        Math.max(moveStart + moveDuration, events.at(-1)?.end || 0) +
        ACTION_HOLD;
      if (!moving && !events.length) duration = 1900;
    }
    const returnStart = index === tool.phases.length - 1 ? duration : null;
    if (returnStart !== null) duration += 1400;
    return {
      ...p,
      duration,
      events,
      input,
      from,
      to,
      moveStart,
      moveDuration,
      returnStart,
    };
  }
  function phaseState() {
    const spec = phaseSpec(),
      time = Math.max(0, Math.min(1, progress)) * spec.duration;
    const occurred = spec.events.filter((event) => time >= event.start);
    return {
      ...spec,
      time,
      arrived: time >= spec.moveStart + spec.moveDuration,
      finished: spec.returnStart !== null && time >= spec.returnStart,
      typed: occurred
        .filter((event) => event.type === "character")
        .map((event) => event.character)
        .join(""),
      pressed: occurred.findLast((event) => time < event.end)?.key || "",
      activated: occurred.some((event) => event.type === "key"),
      selected: occurred.some((event) => event.type === "select"),
      confirmed: occurred.some((event) => event.type === "confirm"),
    };
  }
  function renderInput(animation) {
    const recent = animation.events
      .filter((event) => animation.time >= event.start)
      .slice(-8);
    const currentAction = animation.finished
      ? ui("done")
      : animation.input !== null
        ? animation.typed || " "
        : recent.at(-1)?.key || animation.title;
    $("input-strip").innerHTML =
      `<span class="input-label">${ui(animation.input !== null ? "input" : "action")}</span><div class="key-history">${recent.map((event) => `<span class="keycap ${animation.time < event.end ? "pressed" : ""}">${esc(event.key)}</span>`).join("")}</div><span class="typed-value" data-typed="${esc(animation.typed)}">${esc(currentAction)}<span class="typing-caret">${animation.input !== null && animation.typed !== animation.input ? "▏" : ""}</span></span>`;
    $("input-strip").dataset.pressed = animation.pressed;
  }
  function approach(from, to, fraction) {
    const t = Math.max(0, Math.min(1, fraction)),
      eased = t * t * (3 - 2 * t);
    return [
      from[0] + (to[0] - from[0]) * eased,
      from[1] + (to[1] - from[1]) * eased,
    ];
  }
  function geometry() {
    const a = phaseState(),
      id = a.id,
      point = a.finished
        ? approach(a.to, HOME, (a.time - a.returnStart) / 1400)
        : approach(
            a.from,
            a.to,
            a.moveDuration ? (a.time - a.moveStart) / a.moveDuration : 1,
          );
    const index = (name) => tool.phases.findIndex((p) => p.id === name);
    const after = (name) => index(name) >= 0 && step > index(name);
    const done =
      after("confirm") || (id === "confirm" && (!a.confirm || a.confirmed));
    const selected = after("start") || a.selected;
    const startedInput = after("input") || (id === "input" && a.activated);
    const entry =
      id === "input" || id === "count"
        ? a.typed
        : Array.isArray(values.value)
          ? values.value.map(f).join(",")
          : f(values.value ?? 0);
    let v = values.value,
      n = values.count,
      hasInput = true;
    if (a.input !== null) {
      if (Array.isArray(v)) {
        const parts = a.typed.split(",");
        const fallback =
          tool.id === "rectangle"
            ? [10, 6]
            : values.mode === "absolute"
              ? [10, 9]
              : [0, 0];
        v = fallback.map((value, i) =>
          parts[i]?.trim() && Number.isFinite(Number(parts[i]))
            ? Number(parts[i])
            : value,
        );
        hasInput = !!parts[0]?.trim() && Number.isFinite(Number(parts[0]));
        if (tool.id === "rectangle" && v.some((value) => value <= 0))
          hasInput = false;
      } else {
        const number = Number(a.typed);
        hasInput = !!a.typed.trim() && Number.isFinite(number) && number > 0;
        if (id === "count") n = hasInput ? number : 1;
        else
          v = hasInput
            ? number
            : { width: 0.6, stretch: 10, measure: 9 }[tool.id] || 0;
      }
    }
    let s = base(),
      label = "",
      result = a.description;
    const numericLabel = (mode) => (entry ? `${entry}  |  ${mode}` : mode);
    const previewStyle = {
      color: done ? C.geometry : C.magenta,
      fill: done ? C.fill : "#e989f115",
    };
    const hover = (content) => `<g data-role="hover-highlight">${content}</g>`;
    if (tool.id === "pick") {
      const first = after("first") || (id === "first" && a.selected);
      const second =
        values.kind === "spacing" &&
        (after("second") || (id === "second" && a.selected));
      const size = second ? 3 : first ? 12 : 4;
      s += rect(8, 5, 12, 4) + rect(8, 12, 12, 4);
      s += rect(35, 16, 8, 4, { opacity: done ? 0.25 : 1 });
      if (selected) {
        s += `<g data-role="stretch-preview" data-size="${size}">${rect(35, 20 - size, 8, size, previewStyle)}</g>`;
        if (first)
          s += vdim(
            45,
            20 - size,
            20,
            `${size} µm`,
            done ? C.geometry : C.magenta,
          );
      }
      if (first) s += line(X(8), Y(9), X(20), Y(9), C.magenta, 4);
      if (second)
        s +=
          line(X(8), Y(12), X(20), Y(12), C.magenta, 4) +
          vdim(23, 9, 12, "3 µm");
      if (
        ["first", "second"].includes(id) &&
        a.arrived &&
        !(id === "second" && values.kind === "length")
      )
        s += hover(
          line(
            X(8),
            Y(id === "first" ? 9 : 12),
            X(20),
            Y(id === "first" ? 9 : 12),
            a.selected ? C.magenta : C.yellow,
            4,
          ),
        );
      const active = after("activate") || (id === "activate" && a.activated);
      if (active && !done)
        label = first
          ? `${size} [${second ? "2 edges" : "1 edge"}]  |  STRETCH LENGTH`
          : "STRETCH LENGTH";
      if (first)
        result = tr(
          `Picked ${second ? "spacing" : "length"}: ${size} µm → Stretch preview on the right`,
          `已拾取${second ? "间距" : "长度"}：${size} µm → 右侧 Stretch 预览已更新`,
        );
    } else if (tool.id === "width") {
      if (selected) {
        const end = id === "start" ? 5 : id === "aim" ? point[0] : 31;
        const width = startedInput && hasInput ? v : 0.6;
        s += `<g data-role="extended-path">${rect(
          2,
          10 - width / 2,
          end - 2,
          width,
          startedInput ? previewStyle : { color: C.faint, fill: "none" },
        )}</g>`;
        if (startedInput && hasInput)
          s += vdim(
            34,
            10 - v / 2,
            10 + v / 2,
            `${f(v)} µm`,
            done ? C.geometry : C.magenta,
          );
      } else s += rect(2, 9.7, 3, 0.6);
      if (startedInput && !done) label = numericLabel("PATH WIDTH");
      if (startedInput && hasInput)
        result = tr(
          `Width = ${f(v)} µm${done ? " · native Path continues" : " · preview"}`,
          `宽度 = ${f(v)} µm${done ? " · Path 命令继续保持活动" : " · 预览"}`,
        );
    } else if (tool.id === "rectangle") {
      if (selected) s += cross(8, 4);
      if (after("start")) {
        const [w, h] =
          startedInput && hasInput
            ? v
            : id === "aim"
              ? [point[0] - 8, point[1] - 4]
              : [10, 6];
        s += rect(
          8,
          4,
          w,
          h,
          startedInput ? previewStyle : { color: C.faint, fill: "none" },
        );
        if (startedInput && hasInput)
          s +=
            dim(8, 2.3, 8 + w, 2.3, `${f(w)} µm`) +
            vdim(10 + w, 4, 4 + h, `${f(h)} µm`);
      }
      if (startedInput && !done) label = numericLabel("RECT SIZE X,Y");
      if (startedInput && hasInput)
        result = `${f(v[0])} × ${f(v[1])} µm${tr(done ? " · rectangle completed" : " · preview", done ? " · 矩形已完成" : " · 预览")}`;
    } else if (tool.id === "measure") {
      s +=
        rect(6, 5, 8, 3, { opacity: 0.3 }) +
        rect(28, 12, 5, 5, { opacity: 0.3 });
      if (selected) s += cross(5, 10);
      if (after("start")) {
        const length =
          startedInput && hasInput ? v : id === "aim" ? point[0] - 5 : 9;
        s += `<g data-role="ruler">${dim(5, 10, 5 + length, 10, `${f(length)} µm`, done ? C.geometry : startedInput ? C.magenta : C.faint)}</g>`;
      }
      if (startedInput && !done) label = numericLabel("MEASUREMENT LENGTH");
      if (startedInput && hasInput)
        result = tr(
          `${done ? "Ruler saved" : "Preview length"}: ${f(v)} µm`,
          `${done ? "标尺已保存" : "预览长度"}：${f(v)} µm`,
        );
    } else if (tool.id === "stretch") {
      s += rect(7, 6, 10, 7, { opacity: done ? 0.25 : 1 });
      if (startedInput && hasInput)
        s +=
          rect(7, 6, v, 7, previewStyle) +
          dim(7, 3.7, 7 + v, 3.7, `${f(v)} µm`);
      if (id === "start" && a.arrived)
        s += hover(
          line(X(17), Y(6), X(17), Y(13), a.selected ? C.magenta : C.yellow, 4),
        );
      if (startedInput && !done) label = numericLabel("STRETCH LENGTH");
      if (startedInput && hasInput)
        result = tr(
          `Final X extent: ${f(v)} µm · opposite edge fixed`,
          `最终 X 范围：${f(v)} µm · 对边固定`,
        );
    } else if (tool.id === "move") {
      if (!done) {
        s += `<g data-role="move-source">${rect(6.5, 6.5, 7, 5)}</g>`;
        if (selected) s += cross(10, 9);
      }
      if (startedInput && hasInput) {
        const [x, y] = values.mode === "absolute" ? v : [10 + v[0], 9 + v[1]];
        if (!done)
          s +=
            line(X(10), Y(9), X(x), Y(y), C.magenta, 1.5, "5 5") +
            cross(x, y, C.magenta);
        s += `<g data-role="move-target">${rect(x - 3.5, y - 2.5, 7, 5, previewStyle)}</g>`;
        result = tr(
          `Reference → (${f(x)}, ${f(y)}) µm`,
          `参考点 → (${f(x)}, ${f(y)}) µm`,
        );
      }
      if (startedInput && !done)
        label = numericLabel(
          values.mode === "absolute"
            ? `MOVE ABSOLUTE ${entry.includes(",") ? "X,Y" : "X"}`
            : entry.includes(",")
              ? "MOVE DELTA X,Y"
              : "MOVE DISTANCE",
        );
    } else if (tool.id === "copy") {
      s += rect(3, 8, 4, 5);
      if (after("start")) {
        const pitch =
          startedInput && hasInput ? v : id === "aim" ? point[0] - 5 : 7;
        const count =
          after("count") || (id === "count" && a.confirmed) ? values.count : 1;
        for (let i = 1; i <= count; i++)
          s += `<g data-role="copy-preview">${rect(3 + i * pitch, 8, 4, 5, previewStyle)}</g>`;
        if (startedInput && hasInput)
          s += dim(5, 5, 5 + v, 5, `${f(v)} µm / copy`);
      }
      if (id === "count" && a.activated && !a.confirmed)
        label = numericLabel("COPY COUNT");
      if (startedInput && !done)
        label = numericLabel(
          `COPY DISTANCE${values.count > 1 ? ` [${values.count} copies]` : ""}`,
        );
      if (startedInput && hasInput)
        result = done
          ? tr(
              `${n} copies placed; source retained`,
              `已放置 ${n} 个副本；源对象保留`,
            )
          : tr(
              `${n} preview targets at ${f(v)} µm pitch`,
              `${n} 个预览目标，间距 ${f(v)} µm`,
            );
      else if (id === "count")
        result = tr(
          `Count = ${n}; nothing placed`,
          `数量 = ${n}；尚未放置副本`,
        );
    } else if (tool.id === "contour") {
      const inside = done
        ? values.side === "inside"
        : point[0] > 11 && point[0] < 29 && point[1] > 6 && point[1] < 15;
      const d = inside ? -v : v;
      const hovering = id === "pivot" && a.arrived;
      const source = rect(11, 6, 18, 9, {
        color: hovering ? (a.selected ? C.magenta : C.yellow) : C.geometry,
        opacity: done ? 0.25 : 1,
      });
      s += hovering ? hover(source) : source;
      if (after("pivot") || (id === "pivot" && a.confirmed))
        s += rect(11 - d, 6 - d, 18 + 2 * d, 9 + 2 * d, previewStyle);
      if (id === "input" && a.activated)
        label = a.confirmed
          ? `PIVOT EDGE  ${f(v)}  [0/4 edges]`
          : numericLabel("CONTOUR OFFSET");
      if (id === "pivot")
        label = a.confirmed
          ? `CONTOUR OUTSIDE  ${f(v)}`
          : `PIVOT ${a.activated ? "RECT" : "EDGE"}  ${f(v)}  [0/4 edges]`;
      if (["side", "confirm"].includes(id) && !done) {
        const inside =
          point[0] > 11 && point[0] < 29 && point[1] > 6 && point[1] < 15;
        label = `CONTOUR ${inside ? "INSIDE" : "OUTSIDE"}  ${f(v)}`;
      }
      if (after("pivot"))
        result = tr(
          `${values.side} offset: ${f(v)} µm · pivot can also be four edges`,
          `${values.side === "inside" ? "向内" : "向外"}偏移：${f(v)} µm · pivot 也可以取四条边`,
        );
    } else {
      s +=
        rect(5, 5, 10, 4) +
        rect(28, 13, 9, 4) +
        `<path d="M${X(15)} ${Y(7)}H${X(22)}V${Y(15)}H${X(28)}" stroke="${C.geometry}" stroke-width="8" fill="none"/>`;
      const removed = after("cleanup") || (id === "cleanup" && a.selected);
      if (!removed)
        for (const [x, y] of [
          [22, 7],
          [22, 15],
          [18, 7],
          [25, 15],
          [12, 7],
          [32, 15],
        ].slice(0, n))
          s +=
            `<circle cx="${X(x)}" cy="${Y(y)}" r="12" fill="${C.bg}" stroke="${C.yellow}" stroke-dasharray="3 3"/>` +
            cross(x, y);
      s += `<g data-role="cleanup-button"><rect x="${X(36)}" y="${Y(22)}" width="112" height="48" rx="5" fill="#2b3d4b" stroke="${C.faint}"/>${text(X(39.7), Y(20) + 4, tr("Cleanup", "清理"), C.text, 14, "middle")}</g>`;
      result = removed
        ? tr(
            `${n} Steiner objects removed · cellview not saved`,
            `已删除 ${n} 个 Steiner 对象 · cellview 未保存`,
          )
        : tr(
            `${n} synthetic Steiner objects · markers revealed for illustration`,
            `${n} 个合成 Steiner 对象 · 标记仅用于示意`,
          );
    }
    s += cursor(...point, label);
    return {
      svg: s,
      result,
      caption: a.title,
      description: a.description,
      animation: a,
    };
  }

  function defaults() {
    return Object.fromEntries(
      tool.fields.map((field) => [field.key, field.value]),
    );
  }
  function parse(raw) {
    const parsed = { ...raw };
    for (const field of tool.fields) {
      if (field.options) {
        if (!field.options.some(([v]) => v === raw[field.key]))
          throw new Error(ui("choiceError"));
        continue;
      }
      if (field.min !== undefined) {
        const original = Number(raw[field.key]);
        const value = round4(original);
        if (
          String(raw[field.key]).trim() === "" ||
          !Number.isFinite(value) ||
          value < field.min ||
          value > field.max ||
          (field.step === 1 && !Number.isInteger(original))
        )
          throw new Error(
            `${fieldLabel(field)}: ${field.min}–${field.max}${field.step === 1 ? ui("wholeNumber") : ""}.`,
          );
        parsed[field.key] = value;
      }
    }
    if (tool.id === "rectangle" || tool.id === "move") {
      const parts = String(raw.value).split(",");
      if (
        parts.length !== 2 ||
        parts.some(
          (p) => !p.trim() || !/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(p.trim()),
        )
      )
        throw new Error(ui("xyError"));
      const pair = parts.map((part) => round4(Number(part)));
      let limits =
        tool.id === "rectangle"
          ? [
              [2, 28],
              [2, 15],
            ]
          : raw.mode === "absolute"
            ? [
                [4, 36],
                [3, 20],
              ]
            : [
                [-8, 20],
                [-7, 10],
              ];
      if (
        pair.some(
          (v, i) => !Number.isFinite(v) || v < limits[i][0] || v > limits[i][1],
        )
      )
        throw new Error(ui("rangeError"));
      parsed.value = pair;
    }
    return parsed;
  }
  function renderFields(raw) {
    $("fields").innerHTML = tool.fields
      .map(
        (field) =>
          `<label for="field-${field.key}">${esc(fieldLabel(field))}</label>${
            field.options
              ? `<select id="field-${field.key}" name="${field.key}">${fieldOptions(
                  field,
                )
                  .map(
                    ([value, label]) =>
                      `<option value="${value}" ${String(raw[field.key]) === value ? "selected" : ""}>${esc(label)}</option>`,
                  )
                  .join("")}</select>`
              : `<input id="field-${field.key}" name="${field.key}" ${field.min === undefined ? 'type="text"' : `type="number" min="${field.min}" max="${field.max}" step="${field.step}"`} value="${esc(raw[field.key])}" aria-describedby="hint-${field.key}" autocomplete="off" spellcheck="false"><small class="field-hint" id="hint-${field.key}">${esc(fieldHint(field))}</small>`
          }`,
      )
      .join("");
  }
  function render() {
    const view = geometry();
    renderInput(view.animation);
    $("scene").innerHTML =
      `<title>${esc(toolText(tool, "name"))} — ${esc(tool.steps[step])}</title>` +
      view.svg;
    $("scene").setAttribute(
      "aria-label",
      `${toolText(tool, "name")}: ${view.result}`,
    );
    $("scene-result").textContent = view.result;
    $("scene-description").textContent = view.description;
    $("scene-phase").textContent =
      `${String(step + 1).padStart(2, "0")} / ${view.caption}`;
    $("step-counter").textContent = holding
      ? ui("done")
      : `${step + 1} / ${tool.steps.length}`;
    if ($("explanation").textContent !== view.description)
      $("explanation").textContent = view.description;
    document.querySelectorAll(".step").forEach((button, i) => {
      button.classList.toggle("active", i === step);
      button.setAttribute("aria-pressed", String(i === step));
    });
    $("next").disabled = step === tool.steps.length - 1;
    $("play").textContent = playing
      ? ui("pause")
      : position >= totalDuration()
        ? ui("replay")
        : ui("play");
    $("next").textContent = ui("next");
    $("reset").textContent = ui("reset");
    $("loop").textContent = loop ? ui("loopOn") : ui("loopOff");
    $("loop").setAttribute("aria-pressed", String(loop));
    $("showcase").textContent = showcase ? ui("showcaseOn") : ui("showcaseOff");
    $("showcase").setAttribute("aria-pressed", String(showcase));
    $("loop").title = ui("loopTitle");
    $("showcase").title = ui("showcaseTitle");
  }
  function totalDuration() {
    return tool.phases.reduce((sum, _, i) => sum + phaseSpec(i).duration, 0);
  }
  function locate() {
    let rest = position;
    step = 0;
    while (step < tool.phases.length - 1 && rest >= phaseSpec(step).duration) {
      rest -= phaseSpec(step).duration;
      step++;
    }
    progress = Math.min(1, rest / phaseSpec(step).duration);
  }
  function stop() {
    playing = false;
    cancelAnimationFrame(timer);
  }
  // Motion scales with speed. Each loop or showcase pause is always 3 real seconds.
  function advance(milliseconds) {
    let remaining = milliseconds;
    let switched = false;
    while (remaining > 0) {
      const total = totalDuration();
      if (position < total) {
        const consumed = Math.min(remaining, (total - position) / speed);
        position = Math.min(total, position + consumed * speed);
        remaining -= consumed;
        if (position < total) break;
      }
      if (!showcase && !loop) {
        holding = false;
        stop();
        break;
      }
      holding = true;
      const consumed = Math.min(remaining, LOOP_WAIT - holdElapsed);
      holdElapsed += consumed;
      remaining -= consumed;
      if (holdElapsed < LOOP_WAIT) break;
      holdElapsed = 0;
      holding = false;
      if (showcase) {
        const current = tools.indexOf(tool);
        resetTool(tools[(current + 1) % tools.length].id);
        switched = true;
      } else {
        position = 0;
        locate();
      }
    }
    if (!holding) locate();
    return switched;
  }
  function tick(now) {
    advance(now - lastTick);
    lastTick = now;
    render();
    if (playing) timer = requestAnimationFrame(tick);
  }
  function play() {
    if (position >= totalDuration() && !holding) {
      position = 0;
      locate();
    }
    playing = true;
    lastTick = performance.now();
    render();
    timer = requestAnimationFrame(tick);
  }
  function disableShowcase() {
    if (!showcase) return;
    showcase = false;
    render();
  }
  function setStep(next, fraction = 1) {
    stop();
    step = Math.max(0, Math.min(tool.steps.length - 1, next));
    progress = Math.max(0, Math.min(1, fraction));
    position =
      tool.phases
        .slice(0, step)
        .reduce((sum, _, i) => sum + phaseSpec(i).duration, 0) +
      progress * phaseSpec(step).duration;
    holding = false;
    holdElapsed = 0;
    render();
  }
  function resetTool(id) {
    clearTimeout(inputTimer);
    tool = tools.find((t) => t.id === id) || tools[1];
    step = 0;
    progress = 0;
    position = 0;
    holdElapsed = 0;
    holding = false;
    loop = true;
    values = parse(defaults());
    renderFields(values);
    $("error").textContent = "";
    renderToolChrome();
  }
  function renderToolChrome() {
    $("tool-category").textContent = toolText(tool, "category");
    $("tool-title").textContent = toolText(tool, "name");
    $("key-badge").textContent = tool.key;
    $("tool-description").textContent = toolText(tool, "description");
    $("scene-name").textContent =
      `${String(tools.indexOf(tool) + 1).padStart(2, "0")} / ${toolText(tool, "name").toUpperCase()}`;
    $("reference").href =
      `${isZh() ? "guide.zh-CN.html" : "guide.html"}#${isZh() ? zhTools[tool.id].anchor : tool.anchor}`;
    $("steps").innerHTML = tool.steps
      .map(
        (label, i) =>
          `<button type="button" class="step" data-step="${i}" aria-pressed="false"><span class="step-num">${String(i + 1).padStart(2, "0")}</span>${esc(label)}</button>`,
      )
      .join("");
    document.querySelectorAll(".tool").forEach((b) => {
      b.classList.toggle("active", b.dataset.tool === tool.id);
      b.setAttribute("aria-pressed", String(b.dataset.tool === tool.id));
    });
    requestAnimationFrame(updateToolMarker);
  }
  function load(id, autoplay = !exporting) {
    stop();
    resetTool(id);
    render();
    if (autoplay) play();
  }
  function setLanguage(next, persist = true) {
    if (!["en", "zh"].includes(next) || next === lang) return;
    lang = next;
    if (persist) {
      try {
        localStorage.setItem("numeric-layout-assist-language", lang);
      } catch {
        /* Storage may be disabled. */
      }
    }
    syncLanguageData();
    applyStaticLanguage();
    renderTools();
    renderToolChrome();
    renderFields(values);
    render();
  }
  function renderTools() {
    $("tools").innerHTML =
      `<span class="tool-marker" id="tool-marker" aria-hidden="true"></span>` +
      tools
        .map(
          (item, i) =>
            `<button type="button" class="tool ${item.id === tool?.id ? "active" : ""}" data-tool="${item.id}" aria-pressed="${item.id === tool?.id}"><span class="index">${String(i + 1).padStart(2, "0")}</span>${esc(toolText(item, "name"))}</button>`,
        )
        .join("");
    requestAnimationFrame(updateToolMarker);
  }
  function updateToolMarker() {
    const marker = $("tool-marker");
    const active = document.querySelector(`.tool[data-tool="${tool?.id}"]`);
    if (!marker || !active) return;
    marker.style.width = `${active.offsetWidth}px`;
    marker.style.height = `${active.offsetHeight}px`;
    marker.style.transform = `translate(${active.offsetLeft}px, ${active.offsetTop}px)`;
    marker.dataset.markerTool = tool.id;
    const nav = $("tools");
    if (nav.scrollWidth > nav.clientWidth)
      nav.scrollTo({
        left: Math.max(0, active.offsetLeft - 8),
        behavior: "smooth",
      });
  }
  $("tools").addEventListener("click", (event) => {
    const button = event.target.closest("[data-tool]");
    if (button) {
      disableShowcase();
      if (location.hash.slice(1) === button.dataset.tool)
        load(button.dataset.tool);
      else location.hash = button.dataset.tool;
    }
  });
  window.addEventListener("hashchange", () => {
    disableShowcase();
    load(location.hash.slice(1));
  });
  $("steps").addEventListener("click", (event) => {
    const button = event.target.closest("[data-step]");
    if (button) {
      disableShowcase();
      setStep(Number(button.dataset.step));
    }
  });
  $("next").addEventListener("click", () => {
    disableShowcase();
    setStep(step + 1);
  });
  $("reset").addEventListener("click", () => {
    disableShowcase();
    load(tool.id);
  });
  function apply(event) {
    if (event) event.preventDefault();
    disableShowcase();
    clearTimeout(inputTimer);
    try {
      const parsed = parse(Object.fromEntries(new FormData($("settings"))));
      const changed = JSON.stringify(values) !== JSON.stringify(parsed);
      values = parsed;
      for (const field of tool.fields)
        $("field-" + field.key).value = Array.isArray(values[field.key])
          ? values[field.key].map(f).join(",")
          : values[field.key];
      $("error").textContent = "";
      if (changed || event?.type === "submit") {
        loop = true;
        setStep(0, 0);
        play();
      }
    } catch (error) {
      $("error").textContent = error.message;
    }
  }
  $("settings").addEventListener("submit", apply);
  $("settings").addEventListener("change", (event) => {
    if (event.target.tagName === "SELECT") apply();
  });
  $("fields").addEventListener("input", (event) => {
    if (event.target.tagName !== "INPUT") return;
    clearTimeout(inputTimer);
    inputTimer = setTimeout(() => apply(), 3000);
  });
  $("fields").addEventListener("focusout", (event) => {
    if (event.target.tagName === "INPUT") apply();
  });
  $("play").addEventListener("click", () => {
    disableShowcase();
    if (playing) {
      advance(performance.now() - lastTick);
      stop();
      render();
    } else play();
  });
  $("speed").addEventListener("change", () => {
    disableShowcase();
    if (playing) {
      const now = performance.now();
      advance(now - lastTick);
      lastTick = now;
    }
    speed = Number($("speed").value);
    render();
  });
  $("loop").addEventListener("click", () => {
    disableShowcase();
    loop = !loop;
    if (!loop && holding) {
      holding = false;
      holdElapsed = 0;
      stop();
    }
    render();
  });
  $("showcase").addEventListener("click", () => {
    showcase = !showcase;
    if (showcase) {
      holding = false;
      holdElapsed = 0;
      if (!playing || position >= totalDuration()) {
        position = 0;
        locate();
        play();
        return;
      }
    }
    render();
  });
  $("capture").addEventListener("pointerdown", disableShowcase);
  document
    .querySelector(".controls")
    ?.addEventListener("pointerdown", disableShowcase);
  $("language-switch").addEventListener("click", (event) => {
    const button = event.target.closest("[data-language]");
    if (button) setLanguage(button.dataset.language);
  });
  window.addEventListener("resize", updateToolMarker);
  if (exporting) document.body.classList.add("export");
  syncLanguageData();
  applyStaticLanguage();
  renderTools();
  load(location.hash.slice(1));
  // Capture uses the same timeline as playback, without a running animation clock.
  window.NumericDemo = {
    tools: tools.map(({ id, steps, phases }) => ({
      id,
      steps: [...steps],
      phases: phases.map((p) => p.id),
    })),
    show(id, frame, overrides = {}, fraction = 1) {
      load(id, false);
      showcase = false;
      values = parse({ ...defaults(), ...overrides });
      renderFields(values);
      setStep(frame, fraction);
      return $("scene-result").textContent;
    },
    advance(milliseconds) {
      stop();
      advance(milliseconds);
      render();
    },
    setLanguage(next) {
      setLanguage(next, false);
    },
    setShowcase(value) {
      showcase = Boolean(value);
      holding = false;
      holdElapsed = 0;
      render();
    },
    get timeline() {
      return tool.steps.map((_, index) => phaseSpec(index));
    },
    get state() {
      return {
        tool: tool.id,
        step,
        progress,
        position,
        total: totalDuration(),
        playing,
        speed,
        loop,
        showcase,
        language: lang,
        holding,
        holdElapsed,
        loopWait: LOOP_WAIT,
        animation: phaseState(),
        values: JSON.parse(JSON.stringify(values)),
      };
    },
  };
})();
