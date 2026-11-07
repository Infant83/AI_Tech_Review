(function () {
  "use strict";
  const form = document.querySelector("[data-site-search]"), panel = document.querySelector("[data-site-search-results]");
  if (!form || !panel) return;
  const input = form.querySelector("input[name=q]"), scope = form.querySelector("select[name=scope]");
  const status = panel.querySelector("[data-search-status]"), list = panel.querySelector("[data-search-list]"), more = panel.querySelector("[data-search-more]");
  const en = document.documentElement.lang === "en", root = new URL(form.dataset.root || "./", location.href);
  const labels = en ? {reviews:"Review",lectures:"Lecture",briefings:"Briefing",books:"External book"} : {reviews:"리뷰",lectures:"렉처",briefings:"브리핑",books:"외부 서적"};
  let engine, loading, results = [], limit = 10, generation = 0, timer, composing = false;
  function script(name, version) {
    return new Promise((resolve, reject) => {
      const el = document.createElement("script"), url = new URL("assets/" + name, root); if (version) url.searchParams.set("v", version); el.src = url.href;
      el.onload = resolve; el.onerror = () => { el.remove(); reject(Error("search_asset")); }; document.head.append(el);
    });
  }
  async function load() {
    if (engine) return engine;
    if (!loading) loading = (async () => {
      const url = new URL("assets/search-records.json", root); if (form.dataset.searchVersion) url.searchParams.set("v", form.dataset.searchVersion);
      const catalog = fetch(url, {credentials: "omit"}).then(response => { if (!response.ok) throw Error("search_catalog"); return response.json(); });
      const [, , data] = await Promise.all([window.MiniSearch ? null : script("minisearch.js", form.dataset.engineVersion), window.SiteSearchCore ? null : script("site-search-core.js", form.dataset.coreVersion), catalog]);
      if (data.version !== 1) throw Error("search_version");
      engine = await window.SiteSearchCore.createAsync(window.MiniSearch, data.records); return engine;
    })().catch(error => { loading = null; throw error; });
    return loading;
  }
  function writeUrl() {
    const url = new URL(location.href), query = input.value.trim();
    if (query) url.searchParams.set("q", query); else url.searchParams.delete("q");
    if (scope.value !== form.dataset.defaultScope) url.searchParams.set("scope", scope.value); else url.searchParams.delete("scope");
    history.replaceState(null, "", url.pathname + url.search + url.hash);
    for (const link of document.querySelectorAll('.site-header a[hreflang]')) {
      const target = new URL(link.href, location.href);
      if (target.origin !== root.origin) continue;
      if (query) target.searchParams.set("q", query); else target.searchParams.delete("q");
      target.searchParams.set("scope", scope.value); link.href = target.href;
    }
  }
  function markText(element, text) {
    const value = String(text || ""), terms = input.value.normalize("NFKC").trim().split(/\s+/).filter(term => term.length > 1).slice(0, 12);
    if (!terms.length) { element.textContent = value; return; }
    const expression = new RegExp("(" + terms.map(term => term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")", "giu");
    for (const piece of value.split(expression)) {
      const node = terms.some(term => piece.toLocaleLowerCase() === term.toLocaleLowerCase()) ? document.createElement("mark") : document.createTextNode(piece);
      if (node.nodeType === 1) node.textContent = piece;
      element.append(node);
    }
  }
  function render() {
    list.replaceChildren();
    for (const row of results.slice(0, limit)) {
      const article = document.createElement("article"); article.className = "site-search-result"; article.dataset.searchId = row.id;
      const meta = document.createElement("p"); meta.className = "site-search-meta";
      meta.textContent = labels[row.scope] + " · " + row.date + (en && !row.title_en ? " · Korean" : "");
      const heading = document.createElement("h3"), link = document.createElement("a");
      const target = new URL(en && row.url_en ? row.url_en : row.url, root);
      if (row.scope === "books" ? target.protocol !== "https:" : target.origin !== root.origin || !target.pathname.startsWith(root.pathname)) continue;
      link.href = target.href; markText(link, en && row.title_en ? row.title_en : row.title); heading.append(link);
      if (row.scope === "books") { link.target = "_blank"; link.rel = "noopener"; }
      const summary = document.createElement("p"); const description = en && row.summary_en ? row.summary_en : row.summary;
      markText(summary, description.length > 230 ? description.slice(0, 230).trimEnd() + "…" : description);
      article.append(meta, heading, summary); list.append(article);
    }
    status.textContent = en ? `${results.length} ${results.length === 1 ? "result" : "results"} · ${Math.min(limit, results.length)} shown` : `${results.length}건 · ${Math.min(limit, results.length)}건 표시`;
    if (!results.length) status.textContent = en ? "No results. Try fewer words or choose All." : "검색 결과가 없습니다. 검색어를 줄이거나 전체 범위를 선택해 보세요.";
    more.hidden = limit >= results.length;
  }
  async function run() {
    const current = ++generation, query = input.value.trim();
    const active = Boolean(query) || scope.value !== form.dataset.defaultScope;
    writeUrl(); document.body.classList.toggle("site-search-active", active); panel.hidden = !active;
    if (!active) { list.replaceChildren(); return; }
    status.textContent = en ? "Searching…" : "검색 중…"; more.hidden = true;
    try { const search = await load(); if (current !== generation) return; results = search.search(query, scope.value); limit = 10; render(); }
    catch (_) { if (current !== generation) return; list.replaceChildren(); status.textContent = en ? "Search could not load. Press Search to retry, or clear search to browse." : "검색을 불러오지 못했습니다. 검색 버튼으로 다시 시도하거나 검색을 지우고 목록을 이용해 주세요."; }
  }
  const initial = new URL(location.href);
  input.value = (initial.searchParams.get("q") || "").slice(0, 180);
  if ([...scope.options].some(option => option.value === initial.searchParams.get("scope"))) scope.value = initial.searchParams.get("scope");
  input.addEventListener("focus", () => { load().catch(() => {}); }, {once:true});
  form.addEventListener("submit", event => { event.preventDefault(); clearTimeout(timer); if (!composing) run(); });
  input.addEventListener("compositionstart", () => { composing = true; clearTimeout(timer); });
  input.addEventListener("compositionend", () => { composing = false; clearTimeout(timer); timer = setTimeout(run, 100); });
  input.addEventListener("input", () => { if (!composing) { clearTimeout(timer); timer = setTimeout(run, 120); } });
  scope.addEventListener("change", () => { clearTimeout(timer); run(); });
  panel.querySelector("[data-search-clear]").addEventListener("click", () => { clearTimeout(timer); input.value = ""; scope.value = form.dataset.defaultScope; run(); input.focus(); });
  input.addEventListener("keydown", event => { if (event.key === "Escape") { input.value = ""; clearTimeout(timer); run(); } });
  more.addEventListener("click", () => { limit += 10; render(); list.children[limit - 10]?.querySelector("a")?.focus(); });
  window.addEventListener("popstate", () => { const url = new URL(location.href); input.value = url.searchParams.get("q") || ""; scope.value = [...scope.options].some(option => option.value === url.searchParams.get("scope")) ? url.searchParams.get("scope") : form.dataset.defaultScope; run(); });
  window.addEventListener("hub:before-language-change", writeUrl);
  document.querySelector(".site-header")?.addEventListener("click", event => { if (event.target.closest("a[hreflang]")) writeUrl(); }, true);
  if (input.value || scope.value !== form.dataset.defaultScope) run();
  else writeUrl();
})();
