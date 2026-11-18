// Recording only: shows a person's identity under a bot's on screen. Display-only; nothing is sent.
// make-patch.py writes the name map into CONFIG below.
(() => {
  const CONFIG = __CONFIG__;
  if (!CONFIG.hosts.includes(location.hostname)) return;
  const RULES = CONFIG.replace.map((r) => ({ re: new RegExp(r.pattern, "gi"), to: r.to }));
  const AVATAR_IDS = CONFIG.avatar_ids || [];
  const KEEP = CONFIG.keep_selectors || "";
  const HIDE_TYPING = CONFIG.hide_typing_in || "";
  const BADGE =
    "data:image/svg+xml;utf8," +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="32" fill="#1f2937"/>' +
        `<text x="32" y="41" font-family="Segoe UI,Arial,sans-serif" font-size="24" font-weight="600" fill="#fff" text-anchor="middle">${CONFIG.badge || "BOT"}</text></svg>`,
    );

  const hits = (s) => RULES.some((r) => { r.re.lastIndex = 0; return r.re.test(s); });
  const fix = (s) => RULES.reduce((acc, r) => acc.replace(r.re, r.to), s);
  const keep = (el) => !!el && !!KEEP && !!el.closest(KEEP);
  // "@Name" is a mention of the real person reviewing; it stays as it is.
  const isMention = (node) => /@\s*$/.test(node.previousSibling?.textContent ?? "") || /(^|\s)@\S/.test(node.nodeValue);

  function fixText(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const found = [];
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (hits(n.nodeValue) && !keep(n.parentElement) && !isMention(n)) found.push(n);
    }
    for (const n of found) n.nodeValue = fix(n.nodeValue);
  }

  function fixAttrs() {
    for (const el of document.querySelectorAll("[aria-label],[title],[alt]")) {
      if (keep(el)) continue;
      for (const a of ["aria-label", "title", "alt"]) {
        const v = el.getAttribute(a);
        if (v && hits(v)) el.setAttribute(a, fix(v));
      }
    }
    for (const img of document.querySelectorAll("img")) {
      if (keep(img)) continue;
      const src = img.getAttribute("src") || "";
      if (AVATAR_IDS.some((id) => src.includes(id)) && src !== BADGE) {
        img.setAttribute("src", BADGE);
        img.removeAttribute("srcset");
      }
    }
  }

  // Input values are not reported by mutation records, so they are polled.
  function fixInputs() {
    for (const input of document.querySelectorAll("input")) {
      if (!keep(input) && hits(input.value || "")) input.value = fix(input.value);
    }
    // A people picker shows what is typed into it; hide that text so a search by name stays off camera.
    if (HIDE_TYPING) {
      for (const input of document.querySelectorAll(HIDE_TYPING)) {
        input.style.color = input.value ? "transparent" : "";
        input.spellcheck = false;
      }
    }
  }

  const run = () => { if (document.body) { fixText(document.body); fixAttrs(); fixInputs(); } };
  let queued = false;
  const schedule = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; run(); });
  };
  const start = () => {
    run();
    new MutationObserver(schedule).observe(document.documentElement, {
      subtree: true, childList: true, characterData: true, attributes: true,
      attributeFilter: ["src", "title", "aria-label", "alt"],
    });
    setInterval(fixInputs, 200);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
