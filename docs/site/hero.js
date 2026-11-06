/* Animate the home hero: type X/Y stretch values, preview the corner, repeat. */
(() => {
  "use strict";

  const svg = document.querySelector(".hero-art svg");
  if (!svg) return;

  const byId = (id) => svg.querySelector("#" + id);
  const base = { x: 196, y: 156, width: 160, height: 112 };
  const bottom = base.y + base.height;
  const scale = { x: 4, y: 2.4 };
  const steps = [
    { x: 18, y: 12 },
    { x: 34, y: 7 },
    { x: 26, y: 20 },
  ];

  const preview = byId("hero-preview");
  const handle = byId("hero-handle");
  const xLine = byId("hero-dim-x-line");
  const yLine = byId("hero-dim-y-line");
  const xLabel = byId("hero-x-label");
  const yLabel = byId("hero-y-label");
  const xInput = byId("hero-x-input");
  const yInput = byId("hero-y-input");
  const caret = byId("hero-caret");
  const pointer = byId("hero-pointer");

  let shown = { x: 0, y: 0 };

  function draw(dx, dy) {
    const right = base.x + base.width + dx * scale.x;
    const top = bottom - base.height - dy * scale.y;
    preview.setAttribute("y", top);
    preview.setAttribute("width", right - base.x);
    preview.setAttribute("height", bottom - top);
    handle.setAttribute("x", right - 4);
    handle.setAttribute("y", top - 4);
    const baseRight = base.x + base.width;
    xLine.setAttribute("d", `M${baseRight} 292H${right}`);
    xLine.style.opacity = dx ? 1 : 0;
    xLabel.setAttribute("x", (baseRight + right) / 2);
    xLabel.textContent = dx ? `${dx} µm` : "";
    yLine.setAttribute("d", `M${right + 20} ${base.y}V${top}`);
    yLine.style.opacity = dy ? 1 : 0;
    yLabel.setAttribute("x", right + 34);
    yLabel.setAttribute("y", (base.y + top) / 2 + 4);
    yLabel.textContent = dy ? `${dy} µm` : "";
    pointer.setAttribute("transform", `translate(${right - 3} ${top - 3})`);
  }

  const caretX = (text) => caret.setAttribute("x", 326 + text.length * 9.6);

  function setInputs(xText, yText) {
    xInput.textContent = xText;
    yInput.textContent = yText;
    caretX(xText);
  }

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function tween(from, to, duration) {
    return new Promise((resolve) => {
      const start = performance.now();
      const tick = (now) => {
        const t = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        draw(
          Math.round(from.x + (to.x - from.x) * eased),
          Math.round(from.y + (to.y - from.y) * eased),
        );
        if (t < 1) requestAnimationFrame(tick);
        else resolve();
      };
      requestAnimationFrame(tick);
    });
  }

  async function playStep(target) {
    setInputs("", "");
    await tween(shown, { x: 0, y: 0 }, 420);
    shown = { x: 0, y: 0 };
    await wait(260);
    let xText = "";
    for (const digit of String(target.x)) {
      xText += digit;
      xInput.textContent = xText;
      caretX(xText);
      const value = Number(xText);
      await tween(shown, { x: value, y: shown.y }, 200);
      shown.x = value;
      await wait(120);
    }
    await wait(240);
    let yText = "";
    for (const digit of String(target.y)) {
      yText += digit;
      yInput.textContent = yText;
      const value = Number(yText);
      await tween(shown, { x: shown.x, y: value }, 200);
      shown.y = value;
      await wait(120);
    }
    await wait(1900);
  }

  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) {
    setInputs(String(steps[0].x), String(steps[0].y));
    draw(steps[0].x, steps[0].y);
    return;
  }

  draw(0, 0);
  setInputs("", "");
  (async () => {
    await wait(700);
    for (;;) {
      for (const step of steps) await playStep(step);
    }
  })();
})();
