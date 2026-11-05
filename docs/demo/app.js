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
      steps: ["Hover an edge", "Pick its length", "Choose the value"],
      explanations: [
        "The edge under the cursor turns yellow. These rectangles are synthetic examples.",
        "The first selected edge turns magenta. Its length becomes the numeric input.",
        "A second parallel edge changes the value to spacing. With a single edge, keep its length instead.",
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
      steps: ["Start a wire", "Enter a width", "Confirm"],
      explanations: [
        "Start the native command. This example begins with a narrow provisional segment.",
        "Press J and enter or pick a width. The magenta contour previews the pending value.",
        "Confirmation updates the width. Native Wire remains active for subsequent points.",
      ],
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
      steps: ["Place a corner", "Enter X,Y", "Confirm"],
      explanations: [
        "Place the first corner with native Rectangle. The illustration fixes the upper-right quadrant.",
        "Press J and enter width,height. Both dimensions appear in the preview.",
        "Confirm to complete the rectangle. In the real tool, omitted dimensions retain the context-specific extent.",
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
      steps: ["Place the start", "Set the length", "Save the ruler"],
      explanations: [
        "Start Measurement with K and place the first point. The scene uses a horizontal direction.",
        "Press J, then type or pick a length. The line previews the second endpoint.",
        "Confirm to save the ruler and finish Measurement. Diagonal lengths can be approximated by the manufacturing grid.",
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
      steps: ["Select an edge", "Set final size", "Confirm"],
      explanations: [
        "Use native partial Stretch to select the right edge. The left edge is the fixed boundary.",
        "Press J and enter the final X extent. The magenta contour shows the resized rectangle.",
        "The final width is applied. Whole-object or multiple-object Stretch uses displacement instead; Shift+J is also relative.",
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
      steps: ["Choose a reference", "Enter X,Y", "Confirm"],
      explanations: [
        "The cross marks this example's reference point at (10, 9). Native commands may use a different selected reference.",
        "J interprets X,Y as a delta. Shift+J interprets it as the target position of the reference point.",
        "Confirm to place the geometry at the target. The selected reference point, rather than a particular corner, defines the position.",
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
      steps: ["Start Copy", "Set N", "Set J distance", "Place copies"],
      explanations: [
        "Select the source and start native Copy. The source remains in place.",
        "Press N and confirm a positive integer. This sets the Step copy count without placing anything.",
        "Transfer to J and enter the displacement. Each target is a successive multiple of the same pitch.",
        "Confirm J to place the copies. The copy count resets after placement; entering or canceling the assist also resets it.",
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
      steps: ["Enter offset", "Pick pivot", "Choose a side", "Confirm"],
      explanations: [
        "Select one rectangle with no command active and press Shift+J. Enter a positive offset.",
        "Choose a pivot rectangle or four bounding edges, then press Enter or Space. This example uses the source boundary itself.",
        "Move inside or outside to preview the result. This demo's selector stands in for that pointer direction.",
        "Confirm to resize the source. In Virtuoso, an inset that collapses a dimension is rejected.",
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
      steps: ["Inspect the layout", "Use cleanup", "Objects removed"],
      explanations: [
        "Steiners are normally invisible. Crossed markers reveal their synthetic positions in this illustration.",
        "Use the routing-node and broom toolbar action in an editable layout. It also works while Numeric Assist is toggled off.",
        "The objects are removed and their count is reported in CIW. Shapes stay in place and the cellview is not saved automatically.",
      ],
    },
  ];
  let tool = tools[1],
    step = 0,
    progress = 1,
    values = {},
    playing = false,
    timer = 0,
    started = 0;
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
  function cursor(x, y, label, color = C.magenta) {
    const a = X(x),
      b = Y(y);
    const width = label.length * 8 + 20;
    const labelX = Math.min(Math.max(18, a + 20), 880 - width);
    const labelY = Math.max(34, b - 28);
    return `<path data-role="pointer" data-x="${x}" data-y="${y}" d="M${a} ${b}l0 22 6-6 5 10 5-2-5-10 9-1Z" fill="#f7f2e3" stroke="${C.bg}" stroke-width="2"/><rect x="${labelX}" y="${labelY - 20}" width="${width}" height="30" rx="4" fill="#243643" stroke="${color}"/>${text(labelX + 10, labelY + 1, label, color, 13)}`;
  }
  function base() {
    return `<defs><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="${C.grid}" stroke-width=".75"/></pattern></defs><rect width="900" height="460" fill="${C.bg}"/><rect x="30" y="25" width="840" height="395" fill="url(#grid)"/>${line(60, 380, 850, 380, "#3b505f", 1)}${line(90, 410, 90, 45, "#3b505f", 1)}${text(48, 407, "0", C.faint, 11)}${text(849, 403, "X", C.faint, 11)}${text(74, 40, "Y", C.faint, 11)}${text(830, 443, "µm", C.faint, 11)}${[10, 20, 30, 40].map((n) => text(X(n), 399, String(n), C.faint, 11, "middle")).join("")}`;
  }
  function phaseSpec(index = step) {
    let hotkey = "",
      input = null,
      confirm = false,
      events = [];
    const valueText = Array.isArray(values.value)
      ? values.value.map(f).join(",")
      : f(values.value ?? 0);
    if (
      ["width", "rectangle", "measure", "stretch", "move"].includes(tool.id) &&
      index === 1
    ) {
      hotkey =
        tool.id === "move" && values.mode === "absolute" ? "Shift+J" : "J";
      input = valueText;
    } else if (tool.id === "copy" && (index === 1 || index === 2)) {
      hotkey = index === 1 ? "N" : "J";
      input = index === 1 ? String(values.count) : valueText;
      confirm = index === 1;
    } else if (tool.id === "contour" && index === 0) {
      hotkey = "Shift+J";
      input = valueText;
      confirm = true;
    }
    const event = (key, start, type = "key", character = "") => ({
      key,
      start,
      end: start + 180,
      type,
      character,
    });
    let duration = 1900;
    if (input !== null) {
      events.push(event(hotkey, 180));
      [...input].forEach((character, i) =>
        events.push(event(character, 550 + i * 260, "character", character)),
      );
      const end = 550 + input.length * 260;
      if (confirm) events.push(event("Enter", end + 200, "confirm"));
      duration = end + (confirm ? 850 : 550);
    } else if (tool.id === "pick") {
      if (index === 1) events.push(event("Click", 300, "select"));
      if (index === 2 && values.kind === "spacing")
        events.push(event("Click", 1400, "select"));
    } else if (tool.id === "contour" && index === 1) {
      events = [
        event("Shift+J", 120),
        event("Click", 1700, "select"),
        event("Enter", 2150, "confirm"),
      ];
      duration = 2700;
    } else if (tool.id === "cleanup") {
      if (index === 1) events.push(event("Cleanup", 1250, "select"));
    } else if (index === tool.steps.length - 1) {
      events.push(event("Enter", 350, "confirm"));
    } else if (index === 0) {
      if (tool.id === "measure") events.push(event("K", 180));
      if (["rectangle", "measure", "stretch", "move", "copy"].includes(tool.id))
        events.push(event("Click", 1250, "select"));
    }
    return { duration, events, input };
  }
  function phaseState() {
    const spec = phaseSpec(),
      time = Math.max(0, Math.min(1, progress)) * spec.duration;
    const occurred = spec.events.filter((event) => time >= event.start);
    return {
      ...spec,
      time,
      typed: occurred
        .filter((event) => event.type === "character")
        .map((event) => event.character)
        .join(""),
      pressed: occurred.findLast((event) => time < event.end)?.key || "",
      selected: occurred.some((event) => event.type === "select"),
      confirmed: occurred.some((event) => event.type === "confirm"),
    };
  }
  function renderInput(animation) {
    const occurred = animation.events.filter(
      (event) => animation.time >= event.start,
    );
    const recent = occurred.slice(-6);
    const pointerPhase =
      (tool.id === "pick" && step !== 1) ||
      (tool.id === "stretch" && step === 0) ||
      (tool.id === "contour" && step === 1);
    const hint =
      animation.input !== null
        ? "INPUT"
        : recent.length
          ? "ACTION"
          : pointerPhase
            ? "POINTER"
            : "READY";
    const idle = pointerPhase
      ? progress >= 0.55
        ? "Target reached"
        : "Move to target"
      : tool.id === "contour" && step === 2
        ? values.side + " preview"
        : tool.id === "cleanup"
          ? "Inspect geometry"
          : "Native command active";
    const typed =
      animation.input !== null
        ? animation.typed
        : recent.length
          ? recent.at(-1).key
          : idle;
    $("input-strip").innerHTML =
      `<span class="input-label">${hint}</span><div class="key-history">${recent.map((event) => `<span class="keycap ${animation.time < event.end ? "pressed" : ""}">${esc(event.key)}</span>`).join("")}</div><span class="typed-value" data-typed="${esc(animation.typed)}">${esc(typed || " ")}<span class="typing-caret">${animation.input !== null && animation.typed !== animation.input ? "▏" : ""}</span></span>`;
    $("input-strip").dataset.pressed = animation.pressed;
  }
  function approach(from, to, fraction) {
    const t = Math.max(0, Math.min(1, fraction / 0.55));
    const eased = t * t * (3 - 2 * t);
    return [
      from[0] + (to[0] - from[0]) * eased,
      from[1] + (to[1] - from[1]) * eased,
    ];
  }
  function geometry() {
    const animation = phaseState(),
      q = Math.max(0, Math.min(1, progress));
    const finalStep = step === tool.steps.length - 1;
    const done =
      finalStep &&
      (!animation.events.some((event) => event.type === "confirm") ||
        animation.confirmed);
    let v = values.value,
      n = values.count,
      hasInput = true;
    if (animation.input !== null) {
      if (Array.isArray(v)) {
        const parts = animation.typed.split(","),
          x = Number(parts[0]);
        hasInput = parts[0].trim() !== "" && Number.isFinite(x);
        const fallbackY =
          tool.id === "rectangle" ? 6 : values.mode === "absolute" ? 9 : 0;
        const y =
          parts.length > 1 &&
          parts[1].trim() &&
          Number.isFinite(Number(parts[1]))
            ? Number(parts[1])
            : fallbackY;
        v = [
          hasInput
            ? x
            : tool.id === "rectangle"
              ? 10
              : values.mode === "absolute"
                ? 10
                : 0,
          y,
        ];
        if (tool.id === "rectangle" && (v[0] <= 0 || v[1] <= 0))
          hasInput = false;
      } else {
        const number = Number(animation.typed);
        hasInput =
          animation.typed.trim() !== "" &&
          Number.isFinite(number) &&
          number > 0;
        if (tool.id === "copy" && step === 1) n = hasInput ? number : 1;
        else
          v = hasInput
            ? number
            : tool.id === "width"
              ? 0.6
              : tool.id === "stretch"
                ? 10
                : tool.id === "measure"
                  ? 9
                  : 0;
      }
    }
    const entry =
      animation.input !== null
        ? animation.typed || "▏"
        : Array.isArray(v)
          ? v.map(f).join(",")
          : f(v ?? 0);
    let s = base(),
      result = "",
      caption = tool.steps[step];
    if (tool.id === "pick") {
      s += rect(8, 5, 12, 4) + rect(8, 12, 12, 4);
      if (step === 0) {
        const point = approach([29, 18], [17, 9], q),
          reached = q >= 0.55;
        if (reached)
          s += `<g data-role="hover-highlight">${line(X(8), Y(9), X(20), Y(9), C.yellow, 4)}</g>`;
        s += cursor(
          ...point,
          reached ? "EDGE CANDIDATE" : "MOVE TO THE EDGE",
          reached ? C.yellow : C.text,
        );
        result = reached
          ? "Pointer on edge → highlight"
          : "Approaching edge · no highlight";
      } else if (step === 1) {
        s += line(
          X(8),
          Y(9),
          X(20),
          Y(9),
          animation.selected ? C.magenta : C.yellow,
          4,
        );
        if (animation.selected) s += dim(8, 10.5, 20, 10.5, "12 µm");
        s += cursor(
          17,
          9,
          animation.selected ? "12 | EDGE LENGTH" : "CLICK THE EDGE",
        );
        result = animation.selected
          ? "Picked length: 12 µm"
          : "Click to select the edge";
      } else if (values.kind === "length") {
        s +=
          line(X(8), Y(9), X(20), Y(9), C.magenta, 4) +
          dim(8, 10.5, 20, 10.5, "12 µm") +
          cursor(17, 9, "12 | EDGE LENGTH");
        result = "Picked length: 12 µm";
      } else {
        const point = approach([17, 9], [17, 12], q),
          reached = q >= 0.55;
        s += line(X(8), Y(9), X(20), Y(9), C.magenta, 4);
        if (reached)
          s += `<g data-role="hover-highlight">${line(X(8), Y(12), X(20), Y(12), animation.selected ? C.magenta : C.yellow, 4)}</g>`;
        if (animation.selected) s += vdim(23, 9, 12, "3 µm");
        s += cursor(
          ...point,
          animation.selected
            ? "3 | EDGE SPACING"
            : reached
              ? "PARALLEL EDGE"
              : "MOVE TO SECOND EDGE",
          animation.selected ? C.magenta : reached ? C.yellow : C.text,
        );
        result = animation.selected
          ? "Picked spacing: 3 µm"
          : reached
            ? "Second edge reached → highlight"
            : "Approaching parallel edge";
      }
    } else if (tool.id === "width") {
      const width = done ? v : 0.6;
      s += rect(5, 10 - width / 2, 29, width);
      if (step && !done && hasInput)
        s += rect(5, 10 - v / 2, 29, v, {
          color: C.magenta,
          fill: "#e989f115",
        });
      if (step && hasInput)
        s += vdim(
          36,
          10 - v / 2,
          10 + v / 2,
          `${f(v)} µm`,
          done ? C.geometry : C.magenta,
        );
      s += cursor(
        31,
        10 + (step ? v : 0.6) / 2,
        step ? `${entry} | WIRE WIDTH` : "NATIVE WIRE · J",
        step ? C.magenta : C.text,
      );
      result = step
        ? hasInput
          ? `Width = ${f(v)} µm`
          : "Press J, then type a width"
        : "Current width: 0.6 µm";
    } else if (tool.id === "rectangle") {
      const [w, h] = v;
      s +=
        cross(8, 4) +
        (step === 0 ? text(X(8), Y(4) + 30, "first corner", C.faint, 12) : "");
      if (step && hasInput)
        s +=
          rect(8, 4, w, h, {
            color: done ? C.geometry : C.magenta,
            fill: done ? C.fill : "#e989f115",
          }) +
          dim(8, 2.3, 8 + w, 2.3, `${f(w)} µm`) +
          vdim(10 + w, 4, 4 + h, `${f(h)} µm`);
      else
        s += rect(8, 4, 10, 6, { color: C.faint, fill: "none", dash: "5 5" });
      s += cursor(
        8 + (step ? w : 10),
        4 + (step ? h : 6),
        step ? `${entry} | RECTANGLE` : "FIRST CORNER · J",
        step ? C.magenta : C.text,
      );
      result =
        step && hasInput
          ? `${f(w)} × ${f(h)} µm`
          : "Place the first corner, then enter X,Y";
    } else if (tool.id === "measure") {
      s +=
        rect(6, 5, 8, 3, { opacity: 0.3 }) +
        rect(28, 12, 5, 5, { opacity: 0.3 }) +
        cross(5, 10);
      const end = 5 + (step && hasInput ? v : 9);
      s += dim(
        5,
        10,
        end,
        10,
        step && hasInput ? `${f(v)} µm` : "direction",
        done ? C.geometry : step ? C.magenta : C.faint,
      );
      s +=
        line(X(5), Y(10) - 8, X(5), Y(10) + 8, C.geometry) +
        line(
          X(end),
          Y(10) - 8,
          X(end),
          Y(10) + 8,
          done ? C.geometry : C.magenta,
        );
      if (!done)
        s += cursor(
          end,
          10,
          step ? `${entry} | MEASUREMENT LENGTH` : "START → DIRECTION · J",
        );
      else s += text(X(5), Y(7), "Saved two-point ruler", C.geometry, 14);
      result = done
        ? `Ruler saved: ${f(v)} µm`
        : step
          ? `Preview length: ${f(v)} µm`
          : "K → first point";
    } else if (tool.id === "stretch") {
      s += rect(7, 6, 10, 7, {
        color: done ? C.faint : C.geometry,
        fill: done ? "none" : C.fill,
        dash: done ? "5 6" : "",
      });
      if (step && hasInput)
        s += rect(7, 6, v, 7, {
          color: done ? C.geometry : C.magenta,
          fill: done ? C.fill : "#e989f115",
        });
      s +=
        line(X(7), Y(5), X(7), Y(15), C.yellow, 2, "4 5") +
        text(X(7), Y(17), "fixed boundary", C.yellow, 12);
      const edge = step ? 7 + v : 17;
      if (step || q >= 0.55)
        s += `<g data-role="hover-highlight">${line(X(edge), Y(6), X(edge), Y(13), step || animation.selected ? C.magenta : C.yellow, 4)}</g>`;
      s += dim(7, 3.7, edge, 3.7, `${f(step ? v : 10)} µm`);
      const point = step ? [edge, 9.5] : approach([27, 18], [17, 9.5], q);
      s += cursor(
        ...point,
        step
          ? `${entry} | STRETCH LENGTH`
          : q >= 0.55
            ? "SELECT ONE EDGE · J"
            : "MOVE TO THE EDGE",
      );
      result = step ? `Final X extent: ${f(v)} µm` : "Original X extent: 10 µm";
    } else if (tool.id === "move") {
      const [a, b] = v,
        tx = values.mode === "absolute" ? a : 10 + a,
        ty = values.mode === "absolute" ? b : 9 + b;
      s +=
        rect(6.5, 6.5, 7, 5, {
          color: done ? C.faint : C.geometry,
          fill: done ? "none" : C.fill,
          dash: done ? "5 6" : "",
        }) +
        cross(10, 9, C.yellow) +
        text(X(6.5), Y(4.5), "reference (10, 9)", C.faint, 12);
      if (step && hasInput)
        s +=
          line(X(10), Y(9), X(tx), Y(ty), C.magenta, 1.5, "5 5") +
          rect(tx - 3.5, ty - 2.5, 7, 5, {
            color: done ? C.geometry : C.magenta,
            fill: done ? C.fill : "#e989f115",
          }) +
          cross(tx, ty, C.magenta);
      s += cursor(
        step ? tx : 10,
        step ? ty : 9,
        step
          ? `${entry} | ${values.mode === "absolute" ? "POSITION" : "DELTA"}`
          : "PICK A REFERENCE",
      );
      result =
        step && hasInput
          ? `Reference → (${f(tx)}, ${f(ty)}) µm`
          : "Reference at (10, 9) µm";
    } else if (tool.id === "copy") {
      s +=
        rect(3, 8, 4, 5) + text(X(5), Y(6), "source", C.geometry, 12, "middle");
      if (step >= 2 && hasInput) {
        for (let i = 1; i <= n; i++)
          s +=
            rect(3 + i * v, 8, 4, 5, {
              color: done ? C.geometry : C.magenta,
              fill: done ? C.fill : "#e989f115",
            }) +
            text(
              X(5 + i * v),
              Y(6),
              String(i),
              done ? C.geometry : C.magenta,
              13,
              "middle",
            );
        s += dim(5, 4, 5 + v, 4, `${f(v)} µm / copy`);
      }
      s += cursor(
        step >= 2 ? 5 + v : 5,
        14,
        step === 0
          ? "NATIVE COPY · N"
          : step === 1
            ? `${entry} | COPY COUNT`
            : `${entry} | COPY DISTANCE [${n} copies]`,
      );
      result =
        step < 2
          ? step === 0
            ? "Source selected"
            : `Count = ${n}; nothing placed`
          : done
            ? `${n} copies placed; source retained`
            : hasInput
              ? `${n} preview targets at ${f(v)} µm pitch`
              : "Press J, then type the displacement";
    } else if (tool.id === "contour") {
      const d = values.side === "outside" ? v : -v;
      const hover = step === 1 && q >= 0.55;
      s += `<g ${hover ? 'data-role="hover-highlight"' : ""}>${rect(11, 6, 18, 9, { color: hover ? (animation.selected ? C.magenta : C.yellow) : done ? C.faint : C.geometry, fill: done ? "none" : C.fill, dash: done ? "5 6" : "" })}</g>`;
      if (step >= 2)
        s +=
          rect(11 - d, 6 - d, 18 + 2 * d, 9 + 2 * d, {
            color: done ? C.geometry : C.magenta,
            fill: done ? C.fill : "#e989f115",
          }) + dim(11 - d, 3 - d, 11, 3 - d, `${f(v)} µm`);
      if (hover)
        s += text(
          X(20),
          Y(17),
          "PIVOT BOUNDARY",
          animation.selected ? C.magenta : C.yellow,
          13,
          "middle",
        );
      const point =
        step === 1
          ? approach([34, 20], [20, 15], q)
          : step >= 2
            ? [30 + d, 16 + d]
            : [34, 20];
      s += cursor(
        ...point,
        step === 0
          ? `${entry} | CONTOUR OFFSET`
          : step === 1
            ? hover
              ? "PICK PIVOT · ENTER"
              : "MOVE TO THE PIVOT"
            : `${f(v)} | CONTOUR ${values.side.toUpperCase()}`,
      );
      result =
        step >= 2
          ? `${values.side} offset: ${f(v)} µm`
          : step === 1
            ? animation.selected
              ? "Source boundary chosen as pivot"
              : "Approach, then select the pivot"
            : hasInput
              ? `Offset = ${f(v)} µm`
              : "Shift+J → enter an offset";
    } else if (tool.id === "cleanup") {
      s +=
        rect(5, 5, 10, 4) +
        rect(28, 13, 9, 4) +
        `<path d="M${X(15)} ${Y(7)}H${X(22)}V${Y(15)}H${X(28)}" stroke="${C.geometry}" stroke-width="8" fill="none"/>`;
      const points = [
        [22, 7],
        [22, 15],
        [18, 7],
        [25, 15],
        [12, 7],
        [32, 15],
      ];
      if (!done)
        for (let i = 0; i < n; i++) {
          const [x, y] = points[i];
          s +=
            `<circle cx="${X(x)}" cy="${Y(y)}" r="12" fill="${C.bg}" stroke="${step ? C.magenta : C.yellow}" stroke-dasharray="3 3"/>` +
            cross(x, y, step ? C.magenta : C.yellow);
        }
      s += text(
        450,
        80,
        done
          ? "DRAWN GEOMETRY PRESERVED"
          : "STEINER MARKERS REVEALED FOR ILLUSTRATION",
        done ? C.geometry : C.yellow,
        13,
        "middle",
      );
      if (step === 1) s += cursor(34, 8, "TOOLBAR · CLEANUP");
      if (done)
        s += text(
          450,
          330,
          `${n} Steiner objects removed`,
          C.geometry,
          16,
          "middle",
        );
      result = done
        ? `${n} removed · cellview not saved`
        : `${n} synthetic Steiner objects`;
    }
    return { svg: s, result, caption, animation };
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
    $("scene-phase").textContent =
      `${String(step + 1).padStart(2, "0")} / ${view.caption}`;
    $("step-counter").textContent = `${step + 1} / ${tool.steps.length}`;
    if ($("explanation").textContent !== tool.explanations[step])
      $("explanation").textContent = tool.explanations[step];
    document.querySelectorAll(".step").forEach((button, i) => {
      button.classList.toggle("active", i === step);
      button.setAttribute("aria-pressed", String(i === step));
    });
    $("next").disabled = step === tool.steps.length - 1;
    $("play").textContent = playing ? "Ⅱ Pause" : "▶ Play";
  }
  function stop() {
    playing = false;
    cancelAnimationFrame(timer);
  }
  function setStep(next) {
    stop();
    step = Math.max(0, Math.min(tool.steps.length - 1, next));
    progress = 1;
    render();
  }
  function load(id) {
    stop();
    tool = tools.find((t) => t.id === id) || tools[1];
    step = 0;
    progress = 0;
    const raw = defaults();
    values = parse(raw);
    renderFields(values);
    $("error").textContent = "";
    $("tool-category").textContent = tool.category;
    $("tool-title").textContent = tool.name;
    $("key-badge").textContent = tool.key;
    $("tool-description").textContent = tool.description;
    $("scene-name").textContent = tool.name.toUpperCase();
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
    document
      .querySelector(`.tool[data-tool="${tool.id}"]`)
      .scrollIntoView({ block: "nearest", inline: "nearest" });
    render();
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
    try {
      const raw = Object.fromEntries(new FormData($("settings")));
      values = parse(raw);
      renderFields(values);
      $("error").textContent = "";
      setStep(tool.id === "copy" || tool.id === "contour" ? 2 : 1);
    } catch (error) {
      $("error").textContent = error.message;
    }
  }
  $("settings").addEventListener("submit", apply);
  $("settings").addEventListener("change", (event) => {
    if (event.target.tagName === "SELECT") apply();
  });
  $("play").addEventListener("click", () => {
    if (playing) {
      stop();
      render();
      return;
    }
    playing = true;
    step = 0;
    progress = 0;
    started = performance.now();
    render();
    function tick(now) {
      let remaining = now - started;
      step = 0;
      while (
        step < tool.steps.length - 1 &&
        remaining >= phaseSpec(step).duration
      ) {
        remaining -= phaseSpec(step).duration;
        step += 1;
      }
      const duration = phaseSpec(step).duration;
      progress = Math.min(1, remaining / duration);
      if (step === tool.steps.length - 1 && remaining >= duration) {
        stop();
        progress = 1;
        render();
        return;
      }
      render();
      timer = requestAnimationFrame(tick);
    }
    timer = requestAnimationFrame(tick);
  });
  if (new URLSearchParams(location.search).has("export"))
    document.body.classList.add("export");
  load(location.hash.slice(1));
  // Deterministic frames for documentation capture and offline browser checks.
  window.NumericDemo = {
    tools: tools.map(({ id, steps }) => ({ id, steps: [...steps] })),
    show(id, frame, overrides = {}, fraction = 1) {
      load(id);
      const raw = { ...defaults(), ...overrides };
      values = parse(raw);
      renderFields(values);
      step = Math.max(0, Math.min(tool.steps.length - 1, frame));
      progress = fraction;
      render();
      return $("scene-result").textContent;
    },
    get timeline() {
      return tool.steps.map((_, index) => phaseSpec(index));
    },
    get state() {
      return {
        tool: tool.id,
        step,
        playing,
        animation: phaseState(),
        values: JSON.parse(JSON.stringify(values)),
      };
    },
  };
})();
