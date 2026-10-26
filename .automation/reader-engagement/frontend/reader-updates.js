/* Fresh documents and quiet, device-local recency cues; no notification backfill. */
(function () {
  "use strict";
  var configNode = document.getElementById("reader-engagement-config"), config;
  try { config = JSON.parse(configNode.textContent); } catch (_) { return; }
  if (!config || typeof config !== "object" || Array.isArray(config)) return;
  var scope = config.scope, version = config.pageVersion;
  if (typeof scope !== "string" || !/^\/(?:[A-Za-z0-9_-]+\/)+$/.test(scope) || !/^[a-f0-9]{64}$/.test(version || "") || !location.pathname.startsWith(scope)) return;
  var english = (document.documentElement.lang || "ko").startsWith("en");
  var labels = english ? { fresh: "New", updated: "Updated", available: "New content is available", refresh: "Refresh", open: "View latest", close: "Dismiss", pull: "Pull to refresh", release: "Release to refresh", busy: "Checking…", failed: "Could not refresh. Try again when online." }
    : { fresh: "새 글", updated: "업데이트", available: "새 내용이 있습니다", refresh: "새로고침", open: "새로 보기", close: "닫기", pull: "당겨서 새로고침", release: "놓으면 새로고침", busy: "확인 중…", failed: "새로 불러오지 못했습니다. 연결 후 다시 시도해 주세요." };
  var storageKey = "atr-seen-content:" + scope, week = 7 * 86400000;
  var seen = {}, manifest = null, pending = null, lastCheck = 0, navigating = false;
  var notice = null, noticeVersion = null, dismissed = null, pull = null, pullNode = null, expiryTimer = null;
  var standalone = navigator.standalone === true || (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches);
  function path(value) {
    try {
      var url = new URL(value, location.href);
      if (url.origin !== location.origin || url.username || url.password || !url.pathname.startsWith(scope)) return null;
      return url.pathname.replace(/index\.html$/, "");
    } catch (_) { return null; }
  }
  var currentPath = path(location.href);
  function readSeen() {
    try {
      var raw = localStorage.getItem(storageKey);
      var value = raw && raw.length < 250000 ? JSON.parse(raw) : {};
      seen = value && typeof value === "object" && !Array.isArray(value) ? value : {};
    } catch (_) { /* Retain this session's state when storage is blocked. */ }
  }
  readSeen();
  function visible() { return document.visibilityState !== "hidden" && !document.prerendering; }
  function remember(record) {
    if (seen[record.id] === record.revision) return;
    readSeen();
    seen[record.id] = record.revision;
    var keys = Object.keys(seen);
    if (keys.length > 1000) keys.slice(0, keys.length - 1000).forEach(function (key) { delete seen[key]; });
    try { localStorage.setItem(storageKey, JSON.stringify(seen)); } catch (_) { /* Session memory still works. */ }
  }
  function recordAt(value) {
    var target = path(value);
    return target && manifest && manifest.articles.find(function (item) { return item.paths.includes(target); });
  }
  function marker(record) {
    var date = Date.parse(record.updatedAt), published = Date.parse(record.publishedAt + "T00:00:00+09:00");
    if (seen[record.id] === record.revision || date > Date.now() || Date.now() - date >= week) return "";
    return record.change === "updated" || date - published >= 86400000 ? labels.updated : labels.fresh;
  }
  function paint() {
    if (!manifest) return;
    readSeen();
    // Only a visibly loaded CURRENT document acknowledges a revision. A stale
    // tab or a card click that fails to load must not hide the new-content cue.
    if (visible() && manifest.pages[currentPath] === version) {
      var current = recordAt(location.href);
      if (current && config.articleVersion === current.revision) { refreshAssets(current); remember(current); }
    }
    document.querySelectorAll(".review-card, .latest-update, .lecture-card, .document-card").forEach(function (card) {
      var link = card.querySelector("h3 a, h2 a, a.text-link, .document-footer a, .lecture-primary");
      var record = link && recordAt(link.href);
      var meta = card.querySelector(".meta, .section-kicker, .lecture-meta, .document-meta");
      var chip = card.querySelector(".atr-content-cue"), text = record ? marker(record) : "";
      if (!meta) return;
      if (!text) { if (chip) chip.remove(); return; }
      if (!chip) { chip = document.createElement("span"); chip.className = "atr-content-cue"; meta.appendChild(chip); }
      chip.textContent = text;
      chip.title = english ? "Clears when opened, or after 7 days" : "글을 열거나 7일이 지나면 사라집니다";
    });
    // The destination may still have an older cached HTML that predates this
    // module. A revision on article/PDF links ensures a fresh first entry too.
    document.querySelectorAll("a[href]").forEach(function (link) {
      var record = recordAt(link.href);
      if (!record || path(link.href) === currentPath) return;
      var url = new URL(link.href, location.href);
      url.searchParams.set("_atr_refresh", record.revision); link.href = url.href;
    });
    clearTimeout(expiryTimer);
    var expiry = manifest.articles.reduce(function (next, record) {
      var remaining = Date.parse(record.updatedAt) + week - Date.now();
      return remaining > 0 ? Math.min(next, remaining) : next;
    }, 86400000);
    expiryTimer = setTimeout(paint, Math.max(1000, expiry + 100));
  }
  function valid(value) {
    if (!value || value.version !== 1 || !value.pages || typeof value.pages !== "object" || !Array.isArray(value.articles) || value.articles.length > 2000) return false;
    var pages = Object.entries(value.pages);
    if (pages.length > 4000 || !pages.every(function (entry) { return entry[0] === path(entry[0]) && /^[a-f0-9]{64}$/.test(entry[1]); })) return false;
    var ids = new Set(), paths = new Set();
    return value.articles.every(function (item) {
      var okay = item && typeof item.id === "string" && /^[A-Za-z0-9][A-Za-z0-9:._-]{0,199}$/.test(item.id) && !ids.has(item.id) && /^[a-f0-9]{64}$/.test(item.revision) &&
        item.path === path(item.path) && Array.isArray(item.paths) && item.paths.length > 0 && item.paths.length < 30 && item.paths.includes(item.path) &&
        item.paths.every(function (p) { return p === path(p) && !paths.has(p); }) && new Set(item.paths).size === item.paths.length &&
        ["new", "updated"].includes(item.change) && /^\d{4}-\d{2}-\d{2}$/.test(item.publishedAt) && Number.isFinite(Date.parse(item.updatedAt));
      if (okay) { ids.add(item.id); item.paths.forEach(function (p) { paths.add(p); }); }
      return okay;
    });
  }
  function refreshAssets(record) {
    var root = record.path.endsWith("/") ? record.path : record.path.slice(0, record.path.lastIndexOf("/") + 1);
    function freshURL(raw) {
      var target = path(raw);
      if (!target || !target.startsWith(root)) return raw;
      var url = new URL(raw, location.href);
      url.searchParams.set("_atr_v", record.revision); return url.href;
    }
    document.querySelectorAll("img[src], source[src], link[rel='stylesheet']").forEach(function (element) {
      var attr = element.tagName === "LINK" ? "href" : "src", raw = element.getAttribute(attr);
      var next = freshURL(raw);
      if (next !== raw) element.setAttribute(attr, next);
    });
    document.querySelectorAll("source[srcset], img[srcset]").forEach(function (element) {
      var raw = element.getAttribute("srcset");
      if (!raw || raw.includes("data:")) return;
      var next = raw.split(",").map(function (part) {
        var bits = part.trim().split(/\s+/); bits[0] = freshURL(bits[0]); return bits.join(" ");
      }).join(", ");
      if (next !== raw) element.setAttribute("srcset", next);
    });
  }
  function safeToReplace() {
    var active = document.activeElement;
    return visible() && !pull && window.scrollY < 100 && !document.querySelector("dialog[open], [aria-modal='true']") &&
      !(active && active.matches("input, textarea, select, [contenteditable='true']")) && !(window.getSelection && String(window.getSelection()));
  }
  function removeNotice() { if (notice) notice.remove(); notice = null; }
  function announce(text, targetVersion) {
    if (dismissed === targetVersion) return;
    if (notice && noticeVersion === targetVersion) return;
    removeNotice(); noticeVersion = targetVersion;
    notice = document.createElement("aside"); notice.className = "atr-update-notice"; notice.setAttribute("role", "status");
    var message = document.createElement("span"); message.textContent = text; notice.appendChild(message);
    var action = document.createElement("button"); action.type = "button"; action.textContent = labels.open;
    action.addEventListener("click", function () { void check(true); }); notice.appendChild(action);
    var close = document.createElement("button"); close.type = "button"; close.className = "atr-update-close";
    close.setAttribute("aria-label", labels.close); close.textContent = "×";
    close.addEventListener("click", function () { dismissed = targetVersion; removeNotice(); }); notice.appendChild(close);
    document.body.appendChild(notice);
  }
  function navigate(targetVersion, manual) {
    if (navigating) return;
    var url = new URL(location.href);
    var token = manual ? Date.now().toString(36) : targetVersion;
    // A stale edge response or blocked sessionStorage must not create a loop.
    if (!manual && url.searchParams.get("_atr_refresh") === token) { announce(labels.available, targetVersion); return; }
    try {
      var retryKey = "atr-refresh-attempt:" + currentPath;
      if (!manual && sessionStorage.getItem(retryKey) === token) { announce(labels.available, targetVersion); return; }
      sessionStorage.setItem(retryKey, token);
    } catch (_) { /* URL token also bounds reload attempts. */ }
    navigating = true;
    window.dispatchEvent(new Event("atr:before-refresh"));
    url.searchParams.set("_atr_refresh", token);
    location.replace(url.href);
  }
  function changed(manual) {
    var latest = manifest.pages[currentPath];
    var current = recordAt(location.href);
    var assetsChanged = current && config.articleVersion && config.articleVersion !== current.revision;
    var targetVersion = assetsChanged ? latest + "-" + current.revision : latest;
    paint();
    if (manual) { navigate(targetVersion || version, true); return; }
    if (!latest || (latest === version && !assetsChanged)) { removeNotice(); return; }
    if (safeToReplace() && dismissed !== targetVersion) navigate(targetVersion, false);
    else announce(labels.available, targetVersion);
  }
  async function check(manual) {
    if (!visible() || navigating) return false;
    if (pending) return manual ? pending.then(function (ok) {
      if (ok && manifest && !navigating) changed(true);
      else if (!ok) announce(labels.failed, "offline");
      return ok;
    }) : pending;
    if (!manual && Date.now() - lastCheck < 30000) { if (manifest) paint(); return false; }
    lastCheck = Date.now();
    pending = (async function () {
      var controller = new AbortController(), timer = setTimeout(function () { controller.abort(); }, 7000);
      try {
        var url = new URL(scope + "reader-updates.json", location.origin);
        url.searchParams.set("_atr_check", Date.now().toString(36));
        var response = await fetch(url.href, { cache: "no-store", credentials: "omit", signal: controller.signal });
        if (!response.ok) throw new Error("unavailable");
        var value = await response.json();
        if (!valid(value)) throw new Error("invalid_updates");
        manifest = value;
        changed(manual);
        return true;
      } catch (_) {
        if (manual) announce(labels.failed, "offline");
        return false;
      } finally { clearTimeout(timer); }
    })().finally(function () { pending = null; });
    return pending;
  }
  // Transient freshness tokens never leak into copy/share links or bookmarks.
  try {
    var clean = new URL(location.href);
    if (clean.searchParams.has("_atr_refresh")) {
      // Retain on a mismatched document until the check can prevent a loop.
      var oldToken = clean.searchParams.get("_atr_refresh");
      sessionStorage.setItem("atr-refresh-attempt:" + currentPath, oldToken);
      clean.searchParams.delete("_atr_refresh"); history.replaceState(history.state, "", clean.href);
    }
  } catch (_) { /* Private storage limits must not prevent reading. */ }
  function restoreForeground() { if (visible()) { paint(); void check(false); } }
  window.addEventListener("pageshow", restoreForeground);
  window.addEventListener("focus", restoreForeground);
  document.addEventListener("visibilitychange", restoreForeground);
  if (navigator.serviceWorker && navigator.serviceWorker.addEventListener) navigator.serviceWorker.addEventListener("message", function (event) {
    if (!event.data || event.data.type !== "atr-reader-notifications-changed" || !event.source) return;
    try {
      if (new URL(event.source.scriptURL).href !== new URL(scope + "sw.js", location.origin).href) return;
    } catch (_) { return; }
    lastCheck = 0; void check(false);
  });
  window.addEventListener("online", function () { lastCheck = 0; void check(false); });
  window.addEventListener("storage", function (event) { if (event.key === storageKey) { readSeen(); paint(); } });
  var scrollTimer;
  window.addEventListener("scroll", function () {
    clearTimeout(scrollTimer); scrollTimer = setTimeout(function () {
      if (manifest && notice && safeToReplace()) changed(false);
    }, 180);
  }, { passive: true });
  // Installed apps have a compact fallback for the authored pull gesture.
  // Ordinary browser tabs keep their native refresh gesture and browser tools.
  if (standalone) {
    var footer = document.querySelector("footer, .atr-reader-actions");
    if (footer) {
      var refresh = document.createElement("button"); refresh.type = "button"; refresh.className = "atr-page-refresh";
      refresh.setAttribute("aria-label", labels.refresh); refresh.title = labels.refresh;
      refresh.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7v5h-5M4 17v-5h5M6.1 7a7 7 0 0 1 11.5-1L20 9M4 15l2.4 3A7 7 0 0 0 18 17"/></svg>';
      refresh.addEventListener("click", function () {
        refresh.disabled = true; refresh.setAttribute("aria-busy", "true");
        void check(true).finally(function () { refresh.disabled = false; refresh.removeAttribute("aria-busy"); });
      }); footer.appendChild(refresh);
    }
    function clearPull() { pull = null; if (pullNode) pullNode.remove(); pullNode = null; }
    document.addEventListener("touchstart", function (event) {
      clearPull();
      if (event.touches.length !== 1 || window.scrollY > 0 || !safeToReplace() || event.target.closest("a, button, input, textarea, select, [contenteditable], dialog, .atr-reader-dialog")) return;
      pull = { x: event.touches[0].clientX, y: event.touches[0].clientY, ready: false };
    }, { passive: true });
    document.addEventListener("touchmove", function (event) {
      if (!pull) return;
      if (event.touches.length !== 1) { clearPull(); return; }
      var dx = Math.abs(event.touches[0].clientX - pull.x), dy = event.touches[0].clientY - pull.y;
      if (dx > 24 || dy < -8 || window.scrollY > 0) { clearPull(); return; }
      if (dy < 14 || dy < dx * 2) return;
      if (event.cancelable) event.preventDefault();
      pull.ready = dy >= 88;
      if (!pullNode) { pullNode = document.createElement("div"); pullNode.className = "atr-pull-status"; pullNode.setAttribute("role", "status"); document.body.appendChild(pullNode); }
      var message = pull.ready ? labels.release : labels.pull;
      if (pullNode.textContent !== message) pullNode.textContent = message;
    }, { passive: false });
    document.addEventListener("touchend", function () {
      var ready = pull && pull.ready; clearPull();
      if (ready) {
        var busy = document.createElement("div"); busy.className = "atr-pull-status"; busy.setAttribute("role", "status"); busy.textContent = labels.busy;
        document.body.appendChild(busy); void check(true).finally(function () { busy.remove(); });
      }
    }, { passive: true });
    document.addEventListener("touchcancel", clearPull, { passive: true });
  }
  void check(false);
})();
