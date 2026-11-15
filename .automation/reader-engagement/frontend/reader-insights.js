/* Read-only aggregate insights. No reader session, event writes or polling. */
(function () {
  "use strict";
  const SCOPE = "/AI_Tech_Review/", API = "https://api.infant83.io";
  const PERIODS = { "7d": 7, "30d": 30, "90d": 90 };
  const ID = /^[A-Za-z0-9][A-Za-z0-9:_-]{0,179}$/;
  function validDay(value) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const parsed = new Date(value + "T00:00:00Z");
    return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
  }
  function dayOffset(day, offset) {
    return new Date(Date.parse(day + "T00:00:00Z") + offset * 86400000).toISOString().slice(0, 10);
  }
  function kstDay(iso) {
    if (typeof iso !== "string" || !/^\d{4}-\d{2}-\d{2}T/.test(iso) || !Number.isFinite(Date.parse(iso))) throw Error("invalid_time");
    return new Date(Date.parse(iso) + 9 * 3600000).toISOString().slice(0, 10);
  }
  function count(value) {
    if (!Number.isSafeInteger(value) || value < 0) throw Error("invalid_count");
    return value;
  }
  function add(left, right) { return count(left + right); }
  function safePath(value, topic) {
    if (typeof value !== "string" || !value.startsWith(SCOPE) || !/^[A-Za-z0-9_./-]+$/.test(value) || value.includes("//") || value.split("/").some(part => part === "." || part === "..")) return false;
    return topic === "review" ? value.startsWith(SCOPE + "reviews/") :
      value.startsWith(SCOPE + "lectures/") || value.startsWith(SCOPE + "archive/files/") && value.endsWith(".pdf");
  }
  function validateCatalog(value) {
    if (!value || value.version !== 1 || !["ko", "en"].includes(value.language) || value.scope !== SCOPE || value.apiBase !== API || !Array.isArray(value.articles) || !value.articles.length || value.articles.length > 500) throw Error("invalid_catalog");
    const ids = new Set();
    for (const row of value.articles) {
      if (!row || !ID.test(row.id || "") || ids.has(row.id) || !["review", "lecture"].includes(row.topic) || !safePath(row.path, row.topic) || !validDay(row.publishedAt) || typeof row.title !== "string" || !row.title.trim() || row.title.length > 240 || !["ko", "en"].includes(row.contentLanguage) || typeof row.categoryLabel !== "string" || !row.categoryLabel.trim() || row.categoryLabel.length > 100 || !(row.category === null || typeof row.category === "string" && row.category.trim() && row.category.length <= 100) || row.topic === "lecture" && row.category !== null) throw Error("invalid_catalog_article");
      ids.add(row.id);
    }
    return value;
  }
  function sameIds(rows, catalog) {
    if (rows.size !== catalog.articles.length || catalog.articles.some(row => !rows.has(row.id))) throw Error("catalog_changed");
  }
  function validateInsights(value, period, catalog) {
    if (!PERIODS[period] || !value || value.ok !== true || !Array.isArray(value.articles) || value.articles.length > 500 || !Array.isArray(value.daily) || value.daily.length > 10000) throw Error("invalid_insights");
    const range = value.range, coverage = value.coverage;
    const today = kstDay(value.generatedAt), started = kstDay(value.since);
    if (!range || range.period !== period || !validDay(range.from) || range.to !== today || range.from !== dayOffset(today, 1 - PERIODS[period])) throw Error("invalid_range");
    if (!validDay(value.activitySince) || !coverage || coverage.timezone !== "Asia/Seoul" || coverage.collectionStartedOn !== started || coverage.activityRecordedFrom !== value.activitySince || coverage.firstDayMayBePartial !== true || coverage.todayPartial !== true || coverage.outageHistoryAvailable !== false || started > today || value.activitySince > today || value.activitySince < started) throw Error("invalid_coverage");
    if (!value.limits || value.limits.maxArticles !== 500 || value.limits.maxDays !== 90 || value.limits.maxRows !== 10000 || value.limits.maxBytes !== 750000) throw Error("invalid_limits");
    const rows = new Map(), sums = new Map(), seen = new Set();
    for (const row of value.articles) {
      if (!row || !ID.test(row.id || "") || rows.has(row.id)) throw Error("invalid_article");
      rows.set(row.id, count(row.periodOpens)); sums.set(row.id, 0);
    }
    sameIds(rows, catalog);
    for (const row of value.daily) {
      if (!row || !rows.has(row.articleId) || !validDay(row.day) || row.day < range.from || row.day > range.to || row.day < started || !Number.isSafeInteger(row.opens) || row.opens < 0 || seen.has(row.day + "/" + row.articleId)) throw Error("invalid_daily");
      seen.add(row.day + "/" + row.articleId);
      sums.set(row.articleId, add(sums.get(row.articleId), row.opens));
    }
    for (const [id, total] of rows) if (sums.get(id) !== total) throw Error("inconsistent_totals");
    return { range, coverage, generatedAt: value.generatedAt, rows, daily: value.daily };
  }
  function validateDiscovery(value, insights, catalog) {
    if (!value || value.ok !== true || !Array.isArray(value.articles) || value.articles.length > 500 || !value.range || value.range.period !== insights.range.period || value.range.from !== insights.range.from || value.range.to !== insights.range.to) throw Error("invalid_discovery");
    kstDay(value.since);
    const rows = new Map();
    for (const row of value.articles) {
      if (!row || !ID.test(row.id || "") || rows.has(row.id)) throw Error("invalid_article");
      for (const key of ["opens", "likes", "shares", "copies", "periodOpens", "periodLikes"]) count(row[key]);
      rows.set(row.id, row);
    }
    sameIds(rows, catalog);
    return rows;
  }
  function summarize(catalog, insights, discovery, kind) {
    if (!["all", "review", "lecture"].includes(kind)) throw Error("invalid_kind");
    const articles = catalog.articles.filter(row => kind === "all" || row.topic === kind).map(row => ({ ...row, opens: insights.rows.get(row.id), likes: discovery.get(row.id).likes }));
    const ids = new Set(articles.map(row => row.id)), categories = new Map(), byDay = new Map();
    let total = 0;
    for (const row of articles) {
      total = add(total, row.opens);
      const key = row.category === null ? "unclassified" : "category:" + row.category;
      const group = categories.get(key) || { key, label: row.categoryLabel, articles: 0, opens: 0 };
      group.articles++; group.opens = add(group.opens, row.opens); categories.set(key, group);
    }
    for (const row of insights.daily) if (ids.has(row.articleId)) byDay.set(row.day, add(byDay.get(row.day) || 0, row.opens));
    const daily = [];
    for (let day = insights.range.from; day <= insights.range.to; day = dayOffset(day, 1)) {
      const before = day < insights.coverage.collectionStartedOn, incomplete = !before && day < insights.coverage.activityRecordedFrom;
      const retained = byDay.has(day);
      daily.push({ day, opens: before || incomplete && !retained ? null : (byDay.get(day) || 0),
        state: before ? "uncollected" : incomplete ? "incomplete" : day === insights.range.to ? "today" : day === insights.coverage.activityRecordedFrom || day === insights.coverage.collectionStartedOn ? "first" : "recorded" });
    }
    const dailyTotal = daily.reduce((sum, row) => add(sum, row.opens || 0), 0);
    if (dailyTotal !== total) throw Error("inconsistent_scope");
    return { articles, categories: [...categories.values()].sort((a, b) => b.opens - a.opens || (a.key < b.key ? -1 : 1)), daily, total };
  }
  function ranked(articles, metric) {
    return [...articles].sort((a, b) => b[metric] - a[metric] || (a.publishedAt > b.publishedAt ? -1 : a.publishedAt < b.publishedAt ? 1 : a.id < b.id ? -1 : 1));
  }
  function popularArticles(articles, metric) {
    return ranked(articles, metric).filter(row => row[metric] > 0).slice(0, 10);
  }
  async function jsonResponse(response, maximum) {
    if (!response.ok) throw Error("request_failed");
    const declared = response.headers.get("content-length");
    if (declared && (!/^\d+$/.test(declared) || Number(declared) > maximum)) throw Error("response_too_large");
    let text = "";
    if (response.body && typeof response.body.getReader === "function") {
      const reader = response.body.getReader(), decoder = new TextDecoder();
      let bytes = 0;
      try {
        while (true) {
          const part = await reader.read(); if (part.done) break;
          bytes += part.value.byteLength;
          if (bytes > maximum) throw Error("response_too_large");
          text += decoder.decode(part.value, { stream: true });
        }
        text += decoder.decode();
      } catch (error) { try { await reader.cancel(); } catch (_) {} throw error; }
    } else {
      text = await response.text();
      if (new TextEncoder().encode(text).byteLength > maximum) throw Error("response_too_large");
    }
    return JSON.parse(text);
  }
  const exported = { validDay, dayOffset, kstDay, safePath, validateCatalog, validateInsights, validateDiscovery, summarize, ranked, popularArticles, jsonResponse };
  if (typeof module !== "undefined" && module.exports) module.exports = exported;
  if (typeof document === "undefined") return;
  function start() {
    const configNode = document.getElementById("reader-insights-config");
    if (!configNode) return;
    let catalog;
    const get = id => document.getElementById("insights-" + id);
    try { catalog = validateCatalog(JSON.parse(configNode.textContent)); }
    catch (_) { get("status").textContent = "Statistics unavailable / 통계를 표시할 수 없습니다."; return; }
    const en = catalog.language === "en", word = (ko, english) => en ? english : ko;
    const format = value => new Intl.NumberFormat(en ? "en-US" : "ko-KR").format(value);
    const node = (tag, text, cls) => { const element = document.createElement(tag); if (text !== undefined) element.textContent = text; if (cls) element.className = cls; return element; };
    const status = get("status"), results = get("results"), period = get("period"), kind = get("kind"), ranking = get("ranking"), refresh = get("refresh");
    let theme = "light", generation = 0, pending, snapshot;
    try { const saved = localStorage.getItem("atr.reader.theme.v1"); if (saved === "dark") theme = saved; } catch (_) {}
    function applyTheme() { document.documentElement.dataset.theme = theme; get("theme").setAttribute("aria-checked", String(theme === "dark")); get("theme").title = theme === "dark" ? word("밝은 화면으로 전환", "Switch to light theme") : word("어두운 화면으로 전환", "Switch to dark theme"); }
    applyTheme();
    get("theme").addEventListener("click", () => { theme = theme === "dark" ? "light" : "dark"; try { localStorage.setItem("atr.reader.theme.v1", theme); } catch (_) {} applyTheme(); });
    window.addEventListener("storage", event => { if (event.key === "atr.reader.theme.v1") { theme = event.newValue === "dark" ? "dark" : "light"; applyTheme(); } });
    const initial = new URL(location.href);
    if (PERIODS[initial.searchParams.get("period")]) period.value = initial.searchParams.get("period");
    if (["all", "review", "lecture"].includes(initial.searchParams.get("kind"))) kind.value = initial.searchParams.get("kind");
    if (initial.searchParams.get("rank") === "likes") ranking.value = "likes";
    function saveFilters() {
      const current = new URL(location.href); current.searchParams.set("period", period.value); current.searchParams.set("kind", kind.value); current.searchParams.set("rank", ranking.value);
      try { history.replaceState(null, "", current.href); } catch (_) {}
      const link = new URL(get("language").getAttribute("href"), location.href); link.search = current.search; link.searchParams.set("lang", en ? "ko" : "en"); get("language").href = link.href;
    }
    get("language").addEventListener("click", () => { try { localStorage.setItem("atr.reader.language.v1", en ? "ko" : "en"); } catch (_) {} });
    function cellRow(parent, cells) { const tr = node("tr"); for (const content of cells) { const td = node("td"); if (typeof content === "string") td.textContent = content; else td.appendChild(content); tr.appendChild(td); } parent.appendChild(tr); }
    function articleLink(row) { const a = node("a", row.title); a.href = row.path; a.hreflang = row.contentLanguage; return a; }
    function bars(target, rows, maximum, emptyText) {
      target.replaceChildren();
      if (!rows.length) { target.appendChild(node("p", emptyText || word("이 범위에 글이 없습니다.", "No articles in this scope."), "empty")); return; }
      const list = node("ol", undefined, "bars");
      for (const row of rows) {
        const li = node("li", undefined, "bar-row"), label = node("span", undefined, "bar-label");
        label.appendChild(row.article ? articleLink(row.article) : node("span", row.label));
        if (row.article && en && row.article.contentLanguage === "ko") label.appendChild(node("small", "Korean"));
        li.appendChild(label); li.appendChild(node("span", format(row.value), "bar-value"));
        const track = node("span", undefined, "bar-track"), fill = node("span", undefined, "bar-fill"); track.setAttribute("aria-hidden", "true"); fill.style.width = (maximum ? row.value / maximum * 100 : 0) + "%"; track.appendChild(fill); li.appendChild(track); list.appendChild(li);
      }
      target.appendChild(list);
    }
    function dayState(row) {
      return ({ uncollected: word("미수집", "Not collected"), incomplete: word("보존 전 · 불완전", "Before retention · incomplete"), first: word("첫 보존일 · 일부", "First retained day · partial"), today: word("오늘 · 일부", "Today · partial"), recorded: row.opens === 0 ? word("기록 0", "Recorded zero") : word("기록됨", "Recorded") })[row.state];
    }
    function timeline(days) {
      const target = get("daily"); target.replaceChildren();
      const ns = "http://www.w3.org/2000/svg", svg = document.createElementNS(ns, "svg"), width = 840, height = 190, top = 22, baseline = 154, step = 804 / days.length;
      svg.setAttribute("viewBox", "0 0 " + width + " " + height); svg.setAttribute("class", "timeline"); svg.setAttribute("role", "img"); svg.setAttribute("aria-label", word("일별 읽기 그래프. 자세한 값은 아래 일별 기록 표에 있습니다.", "Daily opens chart. Exact values and coverage are in the daily records table below."));
      function item(name, attributes, text) { const element = document.createElementNS(ns, name); for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, String(value)); if (text !== undefined) element.textContent = text; svg.appendChild(element); return element; }
      const observedMax = Math.max(0, ...days.map(row => row.opens || 0)), max = Math.max(1, observedMax);
      item("line", { x1: 18, y1: baseline, x2: 822, y2: baseline, class: "axis" });
      days.forEach((row, index) => {
        const h = row.opens === null ? baseline - top : row.opens / max * (baseline - top);
        const rect = item("rect", { x: 18 + index * step + step * .13, y: baseline - Math.max(row.opens === null ? h : 1, h), width: step * .74, height: Math.max(1, h), class: row.opens === null ? "unknown" : ["first", "today", "incomplete"].includes(row.state) ? "partial" : "open-bar" });
        const title = document.createElementNS(ns, "title"); title.textContent = row.day + ": " + (row.opens === null ? "—" : format(row.opens)) + " · " + dayState(row); rect.appendChild(title);
      });
      target.appendChild(svg);
      const dates = node("div", undefined, "timeline-dates"); dates.appendChild(node("span", days[0].day)); dates.appendChild(node("span", days[days.length - 1].day)); target.appendChild(dates);
      const key = node("div", undefined, "timeline-key"); key.appendChild(node("span", word("기록된 읽기", "Recorded opens"))); key.appendChild(node("span", word("일부 기록", "Partial records"), "partial")); key.appendChild(node("span", word("미수집·불완전", "Not collected / incomplete"), "unknown")); target.appendChild(key);
    }
    function render() {
      if (!snapshot) return;
      const summary = summarize(catalog, snapshot.insights, snapshot.discovery, kind.value), metric = ranking.value === "likes" ? "likes" : "opens";
      const ordered = ranked(summary.articles, metric), top = popularArticles(summary.articles, metric);
      const emptyRanking = !summary.articles.length ? word("이 범위에 글이 없습니다.", "No articles in this scope.") : metric === "likes" ? word("선택 범위에 현재 좋아요가 없습니다.", "There are no current likes in this scope.") : word("선택 범위에 기록된 읽기가 없습니다.", "There are no recorded opens in this scope.");
      bars(get("popular"), top.map(row => ({ article: row, value: row[metric] })), Math.max(0, ...top.map(row => row[metric])), emptyRanking);
      get("ranking-note").textContent = metric === "likes" ? word("현재 유지된 좋아요 순위입니다. 선택 기간의 클릭이나 증가량이 아닙니다.", "Ranks currently retained likes, not clicks or growth within the selected period.") : word("선택 기간에 기록된 열람 횟수로 정렬합니다.", "Ranks recorded opens in the selected period.");
      const articleTable = get("article-table"); articleTable.replaceChildren();
      for (const row of ordered) cellRow(articleTable, [articleLink(row), format(row.opens), format(row.likes)]);
      bars(get("categories"), summary.categories.map(row => ({ label: row.label, value: row.opens })), Math.max(0, ...summary.categories.map(row => row.opens)));
      const categoryTable = get("category-table"); categoryTable.replaceChildren(); for (const row of summary.categories) cellRow(categoryTable, [row.label, format(row.articles), format(row.opens)]);
      timeline(summary.daily); const dailyTable = get("daily-table"); dailyTable.replaceChildren();
      for (const row of summary.daily) cellRow(dailyTable, [row.day, row.opens === null ? "—" : format(row.opens), dayState(row)]);
      const chosen = kind.options[kind.selectedIndex].textContent;
      status.textContent = chosen + " · " + word("기록된 읽기 ", "Recorded opens: ") + format(summary.total) + (en ? "" : "회"); status.dataset.state = "ready";
      get("range").textContent = snapshot.insights.range.from + " — " + snapshot.insights.range.to + " · KST · " + word("조회 ", "Queried ") + new Date(snapshot.insights.generatedAt).toLocaleString(en ? "en-GB" : "ko-KR", { timeZone: "Asia/Seoul", hour12: false }) + " KST";
      results.hidden = false; saveFilters();
    }
    async function load() {
      const sequence = ++generation; if (pending) pending.abort();
      const controller = new AbortController(); pending = controller;
      const timeout = setTimeout(() => controller.abort(), 8000), selected = period.value;
      snapshot = null; results.hidden = true; get("range").textContent = ""; status.dataset.state = "loading"; status.textContent = word("통계를 불러오는 중입니다.", "Loading statistics."); refresh.disabled = true; saveFilters();
      try {
        const request = async (path, maximum) => jsonResponse(await fetch(API + path + "?period=" + selected, { method: "GET", credentials: "omit", cache: "no-store", redirect: "error", headers: { Accept: "application/json" }, signal: controller.signal }), maximum);
        const values = await Promise.all([request("/v1/insights", 750000), request("/v1/discovery", 300000)]);
        if (sequence !== generation) return;
        const insights = validateInsights(values[0], selected, catalog), discovery = validateDiscovery(values[1], insights, catalog);
        snapshot = { insights, discovery }; render();
      } catch (error) {
        if (sequence !== generation) return;
        controller.abort(); status.dataset.state = "error";
        status.textContent = error.message === "catalog_changed" ? word("글 목록이 변경되었습니다. 페이지를 새로 연 뒤 다시 조회해 주세요.", "The article catalog has changed. Reload this page, then refresh the statistics.") : word("통계를 불러오지 못했습니다. 새로 조회해 주세요. 미확인 값은 0으로 표시하지 않습니다.", "Statistics could not be loaded. Try Refresh. Unconfirmed values are not shown as zero.");
      } finally { clearTimeout(timeout); if (sequence === generation) { refresh.disabled = false; pending = null; } }
    }
    get("filters").addEventListener("submit", event => event.preventDefault());
    period.addEventListener("change", load); kind.addEventListener("change", () => { saveFilters(); render(); }); ranking.addEventListener("change", () => { saveFilters(); render(); }); refresh.addEventListener("click", load);
    saveFilters(); load();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true }); else start();
})();
