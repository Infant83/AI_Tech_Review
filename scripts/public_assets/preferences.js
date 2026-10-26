/* Hub-only preferences. Never reads or changes reader/device credentials. */
(() => {
  "use strict";
  const root = document.documentElement;
  const language = root.dataset.hubLanguage;
  if (language !== "ko" && language !== "en") return;
  const home = document.querySelector("[data-hub-home]");
  if (!home) return;
  let base;
  try {
    const url = new URL(home.getAttribute("href"), location.href);
    if (url.origin !== location.origin) return;
    base = new URL("./", url);
  } catch (_) { return; }
  const paths = new Set([base.pathname, base.pathname + "index.html", base.pathname.slice(0, -1),
    base.pathname + "en", base.pathname + "en/", base.pathname + "en/index.html"]);
  if (!paths.has(location.pathname)) return;
  const key = "atr.reader.preferences.v1";
  const themes = new Set(["light", "dark", "system"]);
  const validLanguage = value => value === "ko" || value === "en";
  function parse(raw) {
    try {
      if (typeof raw !== "string" || raw.length > 1024) return {};
      const value = JSON.parse(raw);
      if (!value || typeof value !== "object" || Array.isArray(value)) return {};
      return {readerLanguage: validLanguage(value.readerLanguage) ? value.readerLanguage : null,
        readerTheme: themes.has(value.readerTheme) ? value.readerTheme : "light"};
    } catch (_) { return {}; }
  }
  let preferences = {};
  try { preferences = parse(localStorage.getItem(key)); } catch (_) { /* Reading still works. */ }
  preferences.readerTheme = themes.has(preferences.readerTheme) ? preferences.readerTheme : "light";
  function persist() {
    try { localStorage.setItem(key, JSON.stringify(preferences)); return true; }
    catch (_) { return false; }
  }
  const media = typeof matchMedia === "function" ? matchMedia("(prefers-color-scheme: dark)") : null;
  function applyTheme() {
    const dark = preferences.readerTheme === "dark" || (preferences.readerTheme === "system" && media && media.matches);
    root.dataset.theme = dark ? "dark" : "light";
    root.dataset.themePreference = preferences.readerTheme;
    root.style.colorScheme = dark ? "dark" : "light";
  }
  applyTheme();
  const current = new URL(location.href);
  const explicit = current.searchParams.get("lang");
  if (validLanguage(explicit)) { preferences.readerLanguage = explicit; persist(); }
  const requested = validLanguage(explicit) ? explicit : (language === "ko" && preferences.readerLanguage === "en" ? "en" : language);
  function destination(value) {
    const target = new URL(value === "en" ? "en/" : "./", base);
    target.search = location.search;
    target.searchParams.set("lang", value);
    target.hash = location.hash;
    return target;
  }
  if (requested !== language) {
    location.replace(destination(requested).href);
    return;
  }
  if (media) {
    const changed = () => { if (preferences.readerTheme === "system") applyTheme(); };
    if (typeof media.addEventListener === "function") media.addEventListener("change", changed);
    else if (typeof media.addListener === "function") media.addListener(changed);
  }
  function bind() {
    const en = language === "en";
    const labels = en ? {light:"Light",dark:"Dark",system:"Device setting",appearance:"Appearance",saved:"Preferences saved.",temporary:"Applied for this visit."}
      : {light:"밝게",dark:"어둡게",system:"기기 설정",appearance:"화면 테마",saved:"선택을 저장했습니다.",temporary:"이번 방문에 적용했습니다."};
    const themeControls = document.querySelectorAll("[data-hub-theme]");
    function refresh() {
      themeControls.forEach(control => { control.value = preferences.readerTheme; });
      document.querySelectorAll(".hub-appearance summary").forEach(summary => {
        const label = labels.appearance + ": " + labels[preferences.readerTheme];
        summary.setAttribute("aria-label", label); summary.setAttribute("title", label);
      });
    }
    function notice(saved) {
      document.querySelectorAll("[data-hub-preference-status]").forEach(node => { node.textContent = saved ? labels.saved : labels.temporary; });
    }
    document.querySelectorAll("[data-hub-language-select]").forEach(control => {
      control.value = language;
      control.addEventListener("change", () => {
        if (!validLanguage(control.value)) { control.value = language; return; }
        preferences.readerLanguage = control.value;
        notice(persist());
        if (control.value !== language) {
          window.dispatchEvent(new Event("hub:before-language-change"));
          location.assign(destination(control.value).href);
        }
      });
    });
    themeControls.forEach(control => control.addEventListener("change", () => {
      preferences.readerTheme = themes.has(control.value) ? control.value : "light";
      preferences.readerLanguage = language;
      applyTheme(); refresh(); notice(persist());
    }));
    document.querySelectorAll(".hub-appearance").forEach(details => {
      document.addEventListener("click", event => { if (!details.contains(event.target)) details.open = false; });
      details.addEventListener("keydown", event => {
        if (event.key === "Escape") { details.open = false; details.querySelector("summary").focus(); }
      });
    });
    window.addEventListener("storage", event => {
      if (event.key !== key) return;
      const next = parse(event.newValue);
      preferences = {readerLanguage: next.readerLanguage || null, readerTheme: next.readerTheme || "light"};
      applyTheme(); refresh();
    });
    refresh();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind, {once:true});
  else bind();
})();
