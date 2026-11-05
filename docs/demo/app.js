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
  const exporting = new URLSearchParams(location.search).has("export");
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
  for (const item of tools) {
    item.phases = plans[item.id];
    item.steps = item.phases.map((p) => p.title);
    item.explanations = item.phases.map((p) => p.description);
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
      ? "Done."
      : animation.input !== null
        ? animation.typed || " "
        : recent.at(-1)?.key || animation.title;
    $("input-strip").innerHTML =
      `<span class="input-label">${animation.input !== null ? "INPUT" : "ACTION"}</span><div class="key-history">${recent.map((event) => `<span class="keycap ${animation.time < event.end ? "pressed" : ""}">${esc(event.key)}</span>`).join("")}</div><span class="typed-value" data-typed="${esc(animation.typed)}">${esc(currentAction)}<span class="typing-caret">${animation.input !== null && animation.typed !== animation.input ? "▏" : ""}</span></span>`;
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
        result = `Picked ${second ? "spacing" : "length"}: ${size} µm → Stretch preview on the right`;
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
        result = `Width = ${f(v)} µm${done ? " · native Path continues" : " · preview"}`;
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
        result = `${f(v[0])} × ${f(v[1])} µm${done ? " · rectangle completed" : " · preview"}`;
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
        result = `${done ? "Ruler saved" : "Preview length"}: ${f(v)} µm`;
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
        result = `Final X extent: ${f(v)} µm · opposite edge fixed`;
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
        result = `Reference → (${f(x)}, ${f(y)}) µm`;
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
          ? `${n} copies placed; source retained`
          : `${n} preview targets at ${f(v)} µm pitch`;
      else if (id === "count") result = `Count = ${n}; nothing placed`;
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
        result = `${values.side} offset: ${f(v)} µm · pivot can also be four edges`;
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
      s += `<g data-role="cleanup-button"><rect x="${X(36)}" y="${Y(22)}" width="112" height="48" rx="5" fill="#2b3d4b" stroke="${C.faint}"/>${text(X(39.7), Y(20) + 4, "Cleanup", C.text, 14, "middle")}</g>`;
      result = removed
        ? `${n} Steiner objects removed · cellview not saved`
        : `${n} synthetic Steiner objects · markers revealed for illustration`;
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
          throw new Error("Choose one of the listed modes.");
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
            `${field.label}: use ${field.min}–${field.max}${field.step === 1 ? " as a whole number" : ""}.`,
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
        throw new Error("Enter two numbers as X,Y for this scene.");
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
        throw new Error("Use the scene ranges shown below the input.");
      parsed.value = pair;
    }
    return parsed;
  }
  function renderFields(raw) {
    $("fields").innerHTML = tool.fields
      .map(
        (field) =>
          `<label for="field-${field.key}">${esc(field.label)}</label>${field.options ? `<select id="field-${field.key}" name="${field.key}">${field.options.map(([value, label]) => `<option value="${value}" ${String(raw[field.key]) === value ? "selected" : ""}>${esc(label)}</option>`).join("")}</select>` : `<input id="field-${field.key}" name="${field.key}" ${field.min === undefined ? 'type="text"' : `type="number" min="${field.min}" max="${field.max}" step="${field.step}"`} value="${esc(raw[field.key])}" aria-describedby="hint-${field.key}" autocomplete="off" spellcheck="false"><small class="field-hint" id="hint-${field.key}">${esc(field.hint)}</small>`}`,
      )
      .join("");
  }
  function render() {
    const view = geometry();
    renderInput(view.animation);
    $("scene").innerHTML =
      `<title>${esc(tool.name)} — ${esc(tool.steps[step])}</title>` + view.svg;
    $("scene").setAttribute("aria-label", `${tool.name}: ${view.result}`);
    $("scene-result").textContent = view.result;
    $("scene-description").textContent = view.description;
    $("scene-phase").textContent =
      `${String(step + 1).padStart(2, "0")} / ${view.caption}`;
    $("step-counter").textContent = holding
      ? "Done."
      : `${step + 1} / ${tool.steps.length}`;
    if ($("explanation").textContent !== view.description)
      $("explanation").textContent = view.description;
    document.querySelectorAll(".step").forEach((button, i) => {
      button.classList.toggle("active", i === step);
      button.setAttribute("aria-pressed", String(i === step));
    });
    $("next").disabled = step === tool.steps.length - 1;
    $("play").textContent = playing
      ? "Ⅱ Pause"
      : position >= totalDuration()
        ? "↺ Replay"
        : "▶ Play";
    $("loop").textContent = loop ? "↻ Loop on" : "↻ Loop off";
    $("loop").setAttribute("aria-pressed", String(loop));
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
  // Motion scales with speed. The deliberate pause between loops is always 3 real seconds.
  function advance(milliseconds) {
    const total = totalDuration();
    let remaining = milliseconds;
    while (remaining > 0) {
      if (position < total) {
        const consumed = Math.min(remaining, (total - position) / speed);
        position = Math.min(total, position + consumed * speed);
        remaining -= consumed;
        if (position < total) break;
      }
      if (!loop) {
        holding = false;
        stop();
        break;
      }
      holding = true;
      const consumed = Math.min(remaining, LOOP_WAIT - holdElapsed);
      holdElapsed += consumed;
      remaining -= consumed;
      if (holdElapsed < LOOP_WAIT) break;
      position = 0;
      holdElapsed = 0;
      holding = false;
    }
    locate();
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
  function load(id, autoplay = !exporting) {
    stop();
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
    $("tool-category").textContent = tool.category;
    $("tool-title").textContent = tool.name;
    $("key-badge").textContent = tool.key;
    $("tool-description").textContent = tool.description;
    $("scene-name").textContent =
      `${String(tools.indexOf(tool) + 1).padStart(2, "0")} / ${tool.name.toUpperCase()}`;
    $("reference").href = `guide.html#${tool.anchor}`;
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
    render();
    if (autoplay) play();
  }
  $("tools").innerHTML = tools
    .map(
      (t, i) =>
        `<button type="button" class="tool" data-tool="${t.id}" aria-pressed="false"><span class="index">${String(i + 1).padStart(2, "0")}</span>${t.name}</button>`,
    )
    .join("");
  $("tools").addEventListener("click", (event) => {
    const button = event.target.closest("[data-tool]");
    if (button) {
      if (location.hash.slice(1) === button.dataset.tool)
        load(button.dataset.tool);
      else location.hash = button.dataset.tool;
    }
  });
  window.addEventListener("hashchange", () => load(location.hash.slice(1)));
  $("steps").addEventListener("click", (event) => {
    const button = event.target.closest("[data-step]");
    if (button) setStep(Number(button.dataset.step));
  });
  $("next").addEventListener("click", () => setStep(step + 1));
  $("reset").addEventListener("click", () => load(tool.id));
  function apply(event) {
    if (event) event.preventDefault();
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
    if (playing) {
      advance(performance.now() - lastTick);
      stop();
      render();
    } else play();
  });
  $("speed").addEventListener("change", () => {
    if (playing) {
      const now = performance.now();
      advance(now - lastTick);
      lastTick = now;
    }
    speed = Number($("speed").value);
    render();
  });
  $("loop").addEventListener("click", () => {
    loop = !loop;
    if (!loop && holding) {
      holding = false;
      holdElapsed = 0;
      stop();
    }
    render();
  });
  if (exporting) document.body.classList.add("export");
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
        holding,
        holdElapsed,
        loopWait: LOOP_WAIT,
        animation: phaseState(),
        values: JSON.parse(JSON.stringify(values)),
      };
    },
  };
})();
