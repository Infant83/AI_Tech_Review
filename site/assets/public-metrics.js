(function () {
  const config = window.AI_TECH_REVIEW_METRICS || {};
  const endpoint = String(config.endpoint || "").replace(/\/+$/, "");
  const basePath = String(config.basePath || "/AI_Tech_Review/");
  const siteId = String(config.siteId || "ai-tech-review");
  const isHttp = location.protocol === "https:" || location.protocol === "http:";

  if (!endpoint || !isHttp) {
    return;
  }

  const pagePath = canonicalPath(location.pathname);
  if (!pagePath.startsWith(basePath)) {
    return;
  }

  const pageWidget = insertPageWidget();
  const inlineMetricEls = Array.from(document.querySelectorAll("[data-inline-metrics][data-metric-path]"));
  const paths = Array.from(new Set([pagePath, ...inlineMetricEls.map((el) => canonicalPath(el.dataset.metricPath || ""))]));

  for (const el of inlineMetricEls) {
    el.dataset.state = "loading";
  }
  if (pageWidget) {
    pageWidget.dataset.state = "loading";
  }

  sendHitOnce()
    .catch(() => null)
    .then(() => loadSummary(paths))
    .then((summary) => {
      renderMetrics(summary);
      startEngagementTracking();
    })
    .catch(() => {
      if (pageWidget) {
        pageWidget.dataset.state = "error";
      }
      for (const el of inlineMetricEls) {
        el.dataset.state = "error";
      }
    });

  function canonicalPath(rawPath) {
    let path = String(rawPath || "").trim();
    if (!path) {
      return "";
    }
    if (/^https?:\/\//i.test(path)) {
      try {
        path = new URL(path).pathname;
      } catch {
        return "";
      }
    }
    if (!path.startsWith("/")) {
      path = "/" + path;
    }
    path = path.replace(/\/index\.html$/i, "/");
    if (path === basePath.replace(/\/$/, "")) {
      path = basePath;
    }
    return path;
  }

  async function sendHitOnce() {
    const key = "ai-tech-review-hit:" + pagePath;
    try {
      if (sessionStorage.getItem(key)) {
        return;
      }
      sessionStorage.setItem(key, "1");
    } catch {
      // Some privacy modes block sessionStorage. Counting the page load is still acceptable.
    }
    await postJson("/hit", { path: pagePath });
  }

  async function loadSummary(metricPaths) {
    const url = new URL(endpoint + "/summary");
    url.searchParams.append("site", siteId);
    for (const path of metricPaths.filter(Boolean)) {
      url.searchParams.append("path", path);
    }
    const response = await fetch(url.toString(), { method: "GET", mode: "cors", cache: "no-store" });
    if (!response.ok) {
      throw new Error("metrics_summary_failed");
    }
    return response.json();
  }

  async function postJson(route, payload, keepalive) {
    const response = await fetch(endpoint + route, {
      method: "POST",
      mode: "cors",
      cache: "no-store",
      keepalive: Boolean(keepalive),
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error("metrics_post_failed");
    }
    return response.json();
  }

  function renderMetrics(summary) {
    const pages = summary.pages || {};
    const page = pages[pagePath] || {};
    const site = (summary.sites || {})[siteId] || {};

    if (pageWidget) {
      pageWidget.dataset.state = "ready";
      setText(pageWidget, "total", formatNumber(site.views || 0));
      setText(pageWidget, "page", formatNumber(page.views || 0));
      setText(pageWidget, "average", formatDuration(page.averageActiveSeconds || 0));
    }

    for (const el of inlineMetricEls) {
      const path = canonicalPath(el.dataset.metricPath || "");
      const item = pages[path] || {};
      el.dataset.state = "ready";
      setText(el, "views", formatNumber(item.views || 0));
      setText(el, "average", formatDuration(item.averageActiveSeconds || 0));
    }
  }

  function setText(root, field, value) {
    const target = root.querySelector(`[data-metric-field="${field}"]`);
    if (target) {
      target.textContent = value;
    }
  }

  function insertPageWidget() {
    if (document.querySelector("[data-public-metrics-widget]")) {
      return document.querySelector("[data-public-metrics-widget]");
    }
    const isReview = document.body.classList.contains("public-review");
    const widget = document.createElement("aside");
    widget.className = "public-metrics";
    widget.dataset.publicMetricsWidget = "true";
    widget.dataset.state = "loading";
    widget.setAttribute("aria-live", "polite");
    widget.innerHTML = isReview
      ? `<span class="public-metrics-pill"><strong data-metric-field="page">-</strong> 이 리뷰 조회</span>
         <span class="public-metrics-pill">평균 읽은 시간 <strong data-metric-field="average">-</strong></span>
         <span class="public-metrics-pill"><strong data-metric-field="total">-</strong> 리뷰 허브 전체 조회</span>`
      : `<span class="public-metrics-pill"><strong data-metric-field="page">-</strong> 허브 조회</span>
         <span class="public-metrics-pill">평균 읽은 시간 <strong data-metric-field="average">-</strong></span>`;

    if (isReview) {
      const topline = document.querySelector(".topline");
      if (topline) {
        topline.insertAdjacentElement("afterend", widget);
      } else {
        document.body.insertBefore(widget, document.body.firstChild);
      }
      return widget;
    }

    const search = document.querySelector(".top-search");
    if (search) {
      search.insertAdjacentElement("afterend", widget);
      return widget;
    }
    const stats = document.querySelector(".hero .stats");
    if (stats) {
      stats.insertAdjacentElement("afterend", widget);
      return widget;
    }
    return null;
  }

  function startEngagementTracking() {
    const IDLE_TIMEOUT_MS = 2 * 60 * 1000;
    const MAX_SESSION_ACTIVE_MS = 45 * 60 * 1000;
    let lastTick = performance.now();
    let lastInteractionAt = lastTick;
    let windowFocused = document.hasFocus ? document.hasFocus() : true;
    let activeMs = 0;
    let sessionActiveMs = 0;
    let maxScrollPercent = getScrollPercent();
    let lastReportedScrollPercent = 0;

    const markInteraction = () => {
      const now = performance.now();
      if (now - lastInteractionAt > 1000) {
        lastInteractionAt = now;
      }
    };

    const tick = () => {
      const now = performance.now();
      const visible = document.visibilityState === "visible";
      const focused = document.hasFocus ? document.hasFocus() : windowFocused;
      const recentlyActive = now - lastInteractionAt <= IDLE_TIMEOUT_MS;
      if (visible && windowFocused && focused && recentlyActive && sessionActiveMs < MAX_SESSION_ACTIVE_MS) {
        const delta = Math.max(0, now - lastTick);
        const allowed = Math.min(delta, MAX_SESSION_ACTIVE_MS - sessionActiveMs);
        activeMs += allowed;
        sessionActiveMs += allowed;
      }
      lastTick = now;
      maxScrollPercent = Math.max(maxScrollPercent, getScrollPercent());
    };

    const flush = (keepalive) => {
      tick();
      const activeSeconds = Math.floor(activeMs / 1000);
      const scroll = Math.round(maxScrollPercent);
      const hasActiveTime = activeSeconds >= 5;
      const hasNewScrollDepth = scroll >= 25 && scroll > lastReportedScrollPercent;
      if (!hasActiveTime && !hasNewScrollDepth) {
        return;
      }
      activeMs = 0;
      lastReportedScrollPercent = Math.max(lastReportedScrollPercent, scroll);
      maxScrollPercent = getScrollPercent();

      const payload = { path: pagePath, activeSeconds, maxScrollPercent: scroll };
      if (keepalive && navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
        navigator.sendBeacon(endpoint + "/engagement", blob);
        return;
      }
      postJson("/engagement", payload, keepalive).catch(() => {});
    };

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") {
        flush(true);
      } else {
        markInteraction();
        lastTick = performance.now();
      }
    });
    window.addEventListener("blur", () => {
      flush(true);
      windowFocused = false;
      lastTick = performance.now();
    });
    window.addEventListener("focus", () => {
      windowFocused = true;
      markInteraction();
      lastTick = performance.now();
    });
    window.addEventListener("pagehide", () => flush(true));
    window.addEventListener("scroll", () => {
      markInteraction();
      maxScrollPercent = Math.max(maxScrollPercent, getScrollPercent());
    }, { passive: true });
    window.addEventListener("pointerdown", markInteraction, { passive: true });
    window.addEventListener("pointermove", markInteraction, { passive: true });
    window.addEventListener("wheel", markInteraction, { passive: true });
    window.addEventListener("touchstart", markInteraction, { passive: true });
    window.addEventListener("keydown", markInteraction);
    window.setInterval(() => flush(false), 15000);
  }

  function getScrollPercent() {
    const doc = document.documentElement;
    const body = document.body;
    const scrollTop = window.scrollY || doc.scrollTop || body.scrollTop || 0;
    const scrollHeight = Math.max(body.scrollHeight, doc.scrollHeight);
    const viewport = window.innerHeight || doc.clientHeight || 0;
    if (scrollHeight <= viewport) {
      return 100;
    }
    return Math.min(100, Math.max(0, ((scrollTop + viewport) / scrollHeight) * 100));
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("ko-KR").format(Number(value || 0));
  }

  function formatDuration(seconds) {
    const value = Number(seconds || 0);
    if (value <= 0) {
      return "-";
    }
    if (value < 60) {
      return `${value}초`;
    }
    return `${Math.round(value / 60)}분`;
  }
})();
