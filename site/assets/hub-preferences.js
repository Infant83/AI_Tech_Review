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
  const languageKey = "atr.reader.language.v1";
  const themeKey = "atr.reader.theme.v1";
  const legacyKey = "atr.reader.preferences.v1";
  const validLanguage = value => value === "ko" || value === "en";
  const validTheme = value => value === "light" || value === "dark";
  let storage;
  try { storage = localStorage; } catch (_) { /* Reading still works. */ }
  function read(key) {
    try { return storage ? storage.getItem(key) : undefined; }
    catch (_) { return undefined; }
  }
  function persist(key, value) {
    try { if (!storage) return false; storage.setItem(key, value); return true; }
    catch (_) { return false; }
  }
  function legacyPreferences(raw) {
    try {
      if (typeof raw !== "string" || raw.length > 1024) return {};
      const value = JSON.parse(raw);
      return value && typeof value === "object" && !Array.isArray(value) ? value : {};
    } catch (_) { return {}; }
  }
  let savedLanguage = read(languageKey), savedTheme = read(themeKey);
  // A choice already stored under its own key always takes precedence. Migrate
  // each missing field independently, without rewriting either setting later.
  if (savedLanguage === null || savedTheme === null) {
    const legacy = legacyPreferences(read(legacyKey));
    if (savedLanguage === null && validLanguage(legacy.readerLanguage)) {
      savedLanguage = legacy.readerLanguage;
      persist(languageKey, savedLanguage);
    }
    if (savedTheme === null && (validTheme(legacy.readerTheme) || legacy.readerTheme === "system")) {
      savedTheme = legacy.readerTheme;
      if (savedTheme === "system") {
        let dark = false;
        try { dark = typeof matchMedia === "function" && matchMedia("(prefers-color-scheme: dark)").matches; } catch (_) { /* Default to light. */ }
        savedTheme = dark ? "dark" : "light";
      }
      persist(themeKey, savedTheme);
    }
  }
  let theme = validTheme(savedTheme) ? savedTheme : "light";
  function applyTheme() {
    root.dataset.theme = theme;
    root.dataset.themePreference = theme;
    root.style.colorScheme = theme;
  }
  applyTheme();
  const current = new URL(location.href);
  const explicit = current.searchParams.get("lang");
  if (validLanguage(explicit)) { savedLanguage = explicit; persist(languageKey, explicit); }
  const requested = validLanguage(explicit) ? explicit : (language === "ko" && savedLanguage === "en" ? "en" : language);
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
  function bind() {
    const en = language === "en";
    const labels = en ? {english:"English",dark:"Dark theme",toKorean:"Switch to Korean",toEnglish:"Switch to English",toLight:"Switch to light theme",toDark:"Switch to dark theme",saved:"Preference saved.",temporary:"Applied for this visit."}
      : {english:"영어",dark:"어두운 화면",toKorean:"한국어로 전환",toEnglish:"영어로 전환",toLight:"밝은 화면으로 전환",toDark:"어두운 화면으로 전환",saved:"선택을 저장했습니다.",temporary:"이번 방문에 적용했습니다."};
    const themeControls = document.querySelectorAll("[data-hub-theme-toggle]");
    const languageControls = document.querySelectorAll("[data-hub-language-toggle]");
    function refresh() {
      themeControls.forEach(control => {
        control.setAttribute("aria-checked", theme === "dark" ? "true" : "false");
        control.setAttribute("aria-label", labels.dark);
        control.setAttribute("title", theme === "dark" ? labels.toLight : labels.toDark);
      });
      languageControls.forEach(control => {
        control.setAttribute("aria-checked", en ? "true" : "false");
        control.setAttribute("aria-label", labels.english);
        control.setAttribute("title", en ? labels.toKorean : labels.toEnglish);
      });
    }
    function notice(saved) {
      document.querySelectorAll("[data-hub-preference-status]").forEach(node => { node.textContent = saved ? labels.saved : labels.temporary; });
    }
    languageControls.forEach(control => control.addEventListener("click", () => {
      const next = en ? "ko" : "en";
      notice(persist(languageKey, next));
      window.dispatchEvent(new Event("hub:before-language-change"));
      location.assign(destination(next).href);
    }));
    themeControls.forEach(control => control.addEventListener("click", () => {
      theme = theme === "dark" ? "light" : "dark";
      const saved = persist(themeKey, theme);
      applyTheme(); refresh(); notice(saved);
    }));
    window.addEventListener("storage", event => {
      if (event.storageArea && event.storageArea !== storage) return;
      if (event.key !== themeKey && event.key !== null) return;
      theme = event.key === themeKey && validTheme(event.newValue) ? event.newValue : "light";
      applyTheme(); refresh();
    });
    refresh();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind, {once:true});
  else bind();
})();
