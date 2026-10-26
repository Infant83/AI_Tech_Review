(function () {
  "use strict";
  const search = document.querySelector("#search"), category = document.querySelector("#category");
  const reviewGrid = document.querySelector("#review-grid"), topicFilter = document.querySelector("#topic-filter");
  const sort = document.querySelector("#review-sort"), period = document.querySelector("#review-period");
  const from = document.querySelector("#discovery-from"), to = document.querySelector("#discovery-to"), dates = document.querySelector("#discovery-dates");
  const hint = document.querySelector("#discovery-hint"), status = document.querySelector("#discovery-status"), retry = document.querySelector("#discovery-retry");
  const results = document.querySelector("#review-results"), empty = document.querySelector("#review-empty"), more = document.querySelector("#review-more");
  if (!search || !category || !reviewGrid || !sort || !period || !from || !to || !dates || !hint || !status || !retry || !results || !empty || !more) return;
  const cards = Array.from(reviewGrid.querySelectorAll(".review-card"));
  const categoryTriggers = Array.from(document.querySelectorAll("[data-category-filter]"));
  const originalOptions = Array.from(category.options);
  const originalOrder = new Map(cards.map((card, index) => [card, index]));
  const english = String(document.documentElement && document.documentElement.lang || "ko").toLowerCase().startsWith("en");
  const searchText = new Map(cards.map(card => [card, normalize(card.dataset.search || `${card.dataset.title} ${card.dataset.tags}`)]));
  const cache = new Map();
  const pageSize = 6;
  const viewButtons = [document.querySelector("#hub-view-covers"), document.querySelector("#hub-view-list")].filter(Boolean);
  const browseStateKey = "atr.hub.browse.v1";
  const expandedSummaries = new Set();
  const summaryRecords = cards.map(card => ({card, summary: card.querySelector(".review-summary"), button: card.querySelector("[data-summary-toggle]")})).filter(record => record.summary && record.button);
  const text = english ? {
    invalidPeriod: "Choose an activity period again.", invalidDates: "Choose both a start date and an end date.",
    reversedDates: "The end date must be on or after the start date.", futureDate: "Choose a date no later than today.",
    longRange: "Choose an activity period of no more than 3,660 days.",
    hint: "Periods use view and like activity dates, not publication dates. Card counts are lifetime totals.",
    topicHint: " Topics use activity totals from the same period.", loading: "Loading views and likes…",
    unavailable: "View and like statistics are unavailable. Showing newest reviews."
  } : {
    invalidPeriod: "기간을 다시 선택해 주세요.", invalidDates: "시작일과 종료일을 모두 선택해 주세요.",
    reversedDates: "종료일은 시작일 이후로 선택해 주세요.", futureDate: "오늘 이후의 날짜는 선택할 수 없어요.",
    longRange: "집계 기간은 3,660일 이내로 선택해 주세요.",
    hint: "기간은 글 발행일이 아닌 조회·좋아요 활동 기준이며, 카드 수치는 누적값입니다.",
    topicHint: " 주제 선택도 같은 기간의 활동 합계순입니다.", loading: "조회·좋아요 통계를 불러오는 중…",
    unavailable: "조회·좋아요 통계에 연결할 수 없어 최신순으로 보여드려요."
  };
  let view = "gallery";
  let visibleLimit = pageSize, matched = [], discovery = null, ready = false, generation = 0, pending = null;
  let renderedOrder = cards.map(card => card.dataset.articleId).join("|");
  let apiBase = "https://api.infant83.io";
  try {
    const config = document.querySelector("#reader-engagement-config");
    const value = config ? JSON.parse(config.textContent) : {};
    const requested = new URL(String(value.apiBase || apiBase));
    const local = /^(localhost|127\.0\.0\.1|\[::1\])$/;
    if (requested.origin === apiBase || (value.allowLocalApi === true && local.test(location.hostname) && local.test(requested.hostname) && ["http:", "https:"].includes(requested.protocol))) apiBase = requested.origin;
  } catch (_) { /* A configured host cannot redirect public requests elsewhere. */ }

  function normalize(value) { return String(value || "").toLocaleLowerCase(english ? "en-US" : "ko-KR").trim(); }
  function refreshSummaries() {
    for (const {card, summary, button} of summaryRecords) {
      if (card.hidden) continue;
      // Measure the same three-line layout in both views, even after expansion.
      summary.dataset.summaryCollapsed = "true";
      const long = summary.clientHeight > 0 && summary.scrollHeight > summary.clientHeight + 1;
      const expanded = expandedSummaries.has(card.dataset.articleId);
      summary.dataset.summaryCollapsed = long && !expanded ? "true" : "false";
      button.hidden = !long;
      button.setAttribute("aria-expanded", expanded ? "true" : "false");
      button.textContent = english ? (expanded ? "Show less" : "Read full summary") : (expanded ? "요약 접기" : "요약 더 보기");
    }
  }
  for (const {card, button} of summaryRecords) button.addEventListener("click", () => {
    const id = card.dataset.articleId;
    if (expandedSummaries.has(id)) expandedSummaries.delete(id);
    else expandedSummaries.add(id);
    refreshSummaries();
  });
  let summaryRefreshPending = false;
  function scheduleSummaryRefresh() {
    if (summaryRefreshPending) return;
    summaryRefreshPending = true;
    const schedule = typeof window.requestAnimationFrame === "function" ? window.requestAnimationFrame.bind(window) : callback => setTimeout(callback, 0);
    schedule(() => { summaryRefreshPending = false; refreshSummaries(); });
  }
  window.addEventListener("resize", scheduleSummaryRefresh);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(scheduleSummaryRefresh, () => {});
  function todayKST() { return new Date(Date.now() + 9 * 3600000).toISOString().slice(0, 10); }
  function validDay(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const date = new Date(value + "T00:00:00Z");
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
  }
  function selectedRange() {
    if (period.value !== "custom") {
      if (!["all", "7d", "30d", "90d"].includes(period.value)) throw Error(text.invalidPeriod);
      return { key: "period=" + period.value, period: period.value };
    }
    if (!validDay(from.value) || !validDay(to.value)) throw Error(text.invalidDates);
    if (from.value > to.value) throw Error(text.reversedDates);
    if (to.value > todayKST()) throw Error(text.futureDate);
    if ((Date.parse(to.value) - Date.parse(from.value)) / 86400000 + 1 > 3660) throw Error(text.longRange);
    return { key: "from=" + from.value + "&to=" + to.value, period: "custom", from: from.value, to: to.value };
  }
  function setPopularityAvailable(value, reset) {
    ready = value;
    for (const option of Array.from(sort.options)) option.disabled = option.value !== "latest" && !value;
    if (!value && reset !== false && sort.value !== "latest") sort.value = "latest";
  }
  function updateHint() {
    let value = text.hint;
    if (sort.value !== "latest" && ready) value += text.topicHint;
    if (discovery && discovery.range.period !== "all" && validDay(discovery.activitySince || "") && discovery.range.from < discovery.activitySince) value += english ? " Activity statistics for this period are available from " + discovery.activitySince + "." : " 이 기간의 활동 통계는 " + discovery.activitySince + "부터 제공됩니다.";
    hint.textContent = value;
  }
  function activity(card, kind) {
    const row = discovery && discovery.rows.get(card.dataset.articleId);
    return row ? row[kind === "views" ? "periodOpens" : "periodLikes"] : -1;
  }
  function newest(a, b) {
    const byDate = String(b.dataset.published || "").localeCompare(String(a.dataset.published || ""));
    return byDate || originalOrder.get(a) - originalOrder.get(b);
  }
  function orderTopics() {
    const selected = category.value;
    const totals = new Map();
    if (ready && sort.value !== "latest") {
      for (const card of cards) totals.set(card.dataset.category, (totals.get(card.dataset.category) || 0) + Math.max(0, activity(card, sort.value)));
    }
    const ordered = originalOptions.slice().sort((a, b) => {
      if (!a.value || !b.value) return a.value ? 1 : b.value ? -1 : 0;
      return (totals.get(b.value) || 0) - (totals.get(a.value) || 0) || originalOptions.indexOf(a) - originalOptions.indexOf(b);
    });
    const before = Array.from(category.options).map(option => option.value).join("|");
    if (before !== ordered.map(option => option.value).join("|")) for (const option of ordered) category.appendChild(option);
    category.value = selected;
  }
  function applyFilters(reset) {
    if (reset) visibleLimit = pageSize;
    const q = normalize(search.value), selected = category.value;
    matched = cards.filter(card => (!selected || card.dataset.category === selected) && (!q || searchText.get(card).includes(q)));
    matched.sort((a, b) => ready && sort.value !== "latest" ? activity(b, sort.value) - activity(a, sort.value) || newest(a, b) : newest(a, b));
    const focused = document.activeElement, focusedCard = focused && typeof focused.closest === "function" ? focused.closest(".review-card") : null;
    const focusedIndex = matched.indexOf(focusedCard);
    if (view === "gallery" && !reset && focusedIndex >= visibleLimit) visibleLimit = focusedIndex + 1;
    const shown = new Set(view === "list" ? matched : matched.slice(0, visibleLimit));
    const ordered = matched.concat(cards.filter(card => !matched.includes(card)));
    const orderKey = ordered.map(card => card.dataset.articleId).join("|");
    if (orderKey !== renderedOrder) {
      for (const card of ordered) reviewGrid.appendChild(card);
      renderedOrder = orderKey;
    }
    for (const card of cards) { card.hidden = !shown.has(card); card.classList.toggle("hidden", card.hidden); }
    for (const trigger of categoryTriggers) {
      trigger.classList.toggle("active", trigger.dataset.categoryFilter === selected);
      if (trigger.tagName === "BUTTON") trigger.setAttribute("aria-pressed", trigger.dataset.categoryFilter === selected ? "true" : "false");
    }
    orderTopics(); updateHint();
    reviewGrid.dataset.view = view;
    for (const button of viewButtons) {
      const selectedView = button.dataset.view || (button.id === "hub-view-list" ? "list" : "gallery");
      button.setAttribute("aria-pressed", selectedView === view ? "true" : "false");
    }
    const shownCount = view === "list" ? matched.length : Math.min(visibleLimit, matched.length);
    results.textContent = english ? (view === "list" ? `${matched.length} ${matched.length === 1 ? "review" : "reviews"}` : `${shownCount} of ${matched.length} reviews`) : (view === "list" ? `${matched.length}편 전체 목록` : `${matched.length}편 중 ${shownCount}편`);
    empty.hidden = matched.length !== 0;
    more.hidden = view === "list" || shownCount >= matched.length;
    more.textContent = english ? `Show ${Math.min(pageSize, matched.length - shownCount)} more` : `더 보기 (${Math.min(pageSize, matched.length - shownCount)}편)`;
    refreshSummaries();
    if (focusedCard && shown.has(focusedCard) && typeof focused.focus === "function") focused.focus({ preventScroll: true });
  }
  function validateDiscovery(value, requested) {
    if (!value || value.ok !== true || !Array.isArray(value.articles) || value.articles.length > 500 || typeof value.since !== "string" || !Number.isFinite(Date.parse(value.since)) || !value.range || value.range.period !== requested.period) throw Error("invalid_discovery");
    if (requested.period === "all" ? value.range.from !== null || value.range.to !== null : !validDay(value.range.from || "") || !validDay(value.range.to || "")) throw Error("invalid_range");
    if (requested.period === "custom" && (value.range.from !== requested.from || value.range.to !== requested.to)) throw Error("invalid_range");
    const rows = new Map();
    for (const row of value.articles) {
      if (!row || typeof row.id !== "string" || !/^(?:lecture:)?[A-Za-z0-9][A-Za-z0-9._-]{0,179}$/.test(row.id) || rows.has(row.id)) throw Error("invalid_article");
      for (const key of ["opens", "likes", "shares", "copies", "periodOpens", "periodLikes"]) if (typeof row[key] !== "number" || !Number.isSafeInteger(row[key]) || row[key] < 0) throw Error("invalid_count");
      rows.set(row.id, row);
    }
    return { rows, range: value.range, activitySince: value.activitySince || null };
  }
  function showCounts(value) {
    const formatter = new Intl.NumberFormat(english ? "en-US" : "ko-KR");
    for (const card of cards) {
      const row = value.rows.get(card.dataset.articleId);
      for (const kind of ["opens", "likes"]) {
        const field = card.querySelector('[data-discovery-field="' + kind + '"]');
        if (field) field.textContent = row ? formatter.format(row[kind]) : "—";
      }
    }
  }
  async function loadDiscovery(force) {
    let selected;
    try { selected = selectedRange(); }
    catch (error) { generation += 1; if (pending) pending.abort(); setPopularityAvailable(false); status.textContent = error.message; retry.hidden = true; applyFilters(true); return; }
    const current = ++generation;
    if (pending) pending.abort();
    pending = null;
    const previous = cache.get(selected.key);
    if (!force && previous && Date.now() - previous.time < 30000) {
      discovery = previous.value; setPopularityAvailable(true); showCounts(discovery); status.textContent = ""; retry.hidden = true; applyFilters(false); return;
    }
    setPopularityAvailable(false, false); status.textContent = text.loading; retry.hidden = true;
    const controller = typeof AbortController === "function" ? new AbortController() : null;
    let deadline;
    pending = controller;
    try {
      const response = await Promise.race([
        fetch(apiBase + "/v1/discovery?" + selected.key, { credentials: "omit", mode: "cors", cache: "no-store", headers: { Accept: "application/json" }, signal: controller ? controller.signal : undefined }).then(async response => {
          if (!response.ok) throw Error("discovery_unavailable");
          return response.json();
        }),
        new Promise((_, reject) => { deadline = setTimeout(() => { if (controller) controller.abort(); reject(Error("discovery_timeout")); }, 8000); })
      ]);
      if (current !== generation) return;
      discovery = validateDiscovery(response, selected);
      cache.set(selected.key, { time: Date.now(), value: discovery });
      if (cache.size > 8) cache.delete(cache.keys().next().value);
      setPopularityAvailable(true); showCounts(discovery); status.textContent = ""; retry.hidden = true; applyFilters(false);
    } catch (_) {
      if (current !== generation) return;
      setPopularityAvailable(false);
      status.textContent = text.unavailable;
      retry.hidden = false; applyFilters(false);
    } finally { if (deadline !== undefined) clearTimeout(deadline); if (current === generation) pending = null; }
  }
  search.addEventListener("input", () => applyFilters(true));
  category.addEventListener("change", () => applyFilters(true));
  sort.addEventListener("change", () => { if (!ready) sort.value = "latest"; applyFilters(true); });
  period.addEventListener("change", () => {
    dates.hidden = period.value !== "custom";
    if (period.value === "custom" && !from.value && !to.value) {
      to.value = todayKST(); from.value = new Date(Date.parse(to.value) - 29 * 86400000).toISOString().slice(0, 10);
    }
    visibleLimit = pageSize; void loadDiscovery(false);
  });
  for (const field of [from, to]) field.addEventListener("change", () => { visibleLimit = pageSize; void loadDiscovery(false); });
  for (const trigger of categoryTriggers) trigger.addEventListener("click", event => {
    event.preventDefault(); category.value = trigger.dataset.categoryFilter || ""; applyFilters(true);
    if (trigger.tagName === "A") reviewGrid.scrollIntoView({ behavior: window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  });
  document.querySelector('a[href="#topic-filter"]')?.addEventListener("click", event => { event.preventDefault(); if (topicFilter) topicFilter.scrollIntoView({ behavior: "smooth", block: "start" }); });
  more.addEventListener("click", () => {
    const previous = Math.min(visibleLimit, matched.length); visibleLimit += pageSize; applyFilters(false);
    const next = matched[previous]?.querySelector("h3 a"); if (next) next.focus({ preventScroll: true });
  });
  retry.addEventListener("click", () => { void loadDiscovery(true); });
  for (const button of viewButtons) button.addEventListener("click", () => {
    view = (button.dataset.view || (button.id === "hub-view-list" ? "list" : "gallery")) === "list" ? "list" : "gallery";
    applyFilters(false);
  });
  function saveBrowseState() {
    const state = { version: 1, time: Date.now(), search: String(search.value || "").slice(0, 1000), category: category.value, sort: sort.value, period: period.value, from: from.value, to: to.value, view, limit: Math.min(Math.max(pageSize, cards.length), Math.max(pageSize, visibleLimit)), expandedSummaries: Array.from(expandedSummaries) };
    try { window.sessionStorage.setItem(browseStateKey, JSON.stringify(state)); } catch (_) { /* Navigation remains usable when storage is blocked. */ }
  }
  function restoreBrowseState() {
    let state;
    try {
      const stored = window.sessionStorage.getItem(browseStateKey);
      window.sessionStorage.removeItem(browseStateKey);
      if (!stored || stored.length > 131072) return false;
      state = JSON.parse(stored);
    } catch (_) { return false; }
    if (!state || state.version !== 1 || !Number.isFinite(state.time) || state.time > Date.now() || Date.now() - state.time > 600000 || typeof state.search !== "string" || state.search.length > 1000 || !originalOptions.some(option => option.value === state.category) || !["latest", "views", "likes"].includes(state.sort) || !["all", "7d", "30d", "90d", "custom"].includes(state.period) || !["gallery", "list"].includes(state.view) || !Number.isSafeInteger(state.limit) || state.limit < pageSize || state.limit > Math.max(pageSize, cards.length)) return false;
    if (typeof state.from !== "string" || typeof state.to !== "string" || (state.from && !validDay(state.from)) || (state.to && !validDay(state.to))) return false;
    const expanded = state.expandedSummaries === undefined ? [] : state.expandedSummaries;
    const knownIds = new Set(cards.map(card => card.dataset.articleId));
    if (!Array.isArray(expanded) || expanded.length > cards.length || expanded.some(id => typeof id !== "string" || !knownIds.has(id))) return false;
    for (const id of expanded) expandedSummaries.add(id);
    search.value = state.search; category.value = state.category; sort.value = state.sort; period.value = state.period;
    from.value = state.from; to.value = state.to; view = state.view; visibleLimit = state.limit;
    dates.hidden = period.value !== "custom";
    return true;
  }
  window.addEventListener("hub:before-language-change", saveBrowseState);
  window.addEventListener("pageshow", event => { if (event.persisted) void loadDiscovery(true); });
  from.max = to.max = todayKST();
  applyFilters(!restoreBrowseState());
  void loadDiscovery(false);
})();
