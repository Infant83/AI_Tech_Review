/* MiniSearch BM25+ ranking with explicit multilingual concept aliases. */
(function (root) {
  "use strict";
  const groups = [
    {key: "qmlconcept", pattern: /\bqml\b|quantum\s+machine\s+learning|양자\s*머신\s*러닝/gu},
    {key: "qecconcept", pattern: /\bqec\b|quantum\s+error\s+correction|양자\s*오류\s*정정/gu},
    {key: "mlffconcept", pattern: /\bmlff\b|machine[\s-]+learning\s+force\s+fields?|머신\s*러닝\s*포스\s*필드/gu}
  ];
  const normalize = value => String(value || "").normalize("NFKC").toLocaleLowerCase("en-US").replace(/\s+/gu, " ").trim();
  const tokenize = value => normalize(value).split(/[^\p{L}\p{N}_]+/u).filter(Boolean);
  const concepts = value => {
    let output = normalize(value);
    for (const group of groups) output = output.replace(group.pattern, group.key);
    return output;
  };
  const searchable = value => {
    const text = normalize(value);
    return text + " " + groups.filter(group => { group.pattern.lastIndex = 0; return group.pattern.test(text); }).map(group => group.key).join(" ");
  };
  function validatedRows(records) {
    if (!Array.isArray(records) || records.length > 10000) throw Error("Invalid search records");
  }
  const fields = ["titles", "topics", "headings", "text"];
  const miniSearch = MiniSearch => new MiniSearch({fields, tokenize, processTerm: term => term});
  const preparedRecord = record => Object.fromEntries([["id", record.id], ...fields.map(key => [key, searchable(record[key])])]);
  function searchApi(mini, rows, records) {
    return {
      search(query, scope = "all") {
        const date = normalize(query);
        if (/^\d{4}-\d{2}(?:-\d{2})?$/.test(date)) return records.filter(row => (scope === "all" || row.scope === scope) && row.date.startsWith(date)).slice().sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id));
        const words = tokenize(concepts(query));
        if (!words.length) return records.filter(row => scope === "all" || row.scope === scope).slice().sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id));
        const hits = mini.search(words.join(" "), {combineWith: "AND", boost: {titles: 8, topics: 5, headings: 3, text: 1}, prefix: term => term.length >= 3 || /^[\p{Script=Hangul}]{2,}$/u.test(term), fuzzy: false});
        return hits.map(hit => ({...rows.get(hit.id), score: hit.score})).filter(row => scope === "all" || row.scope === scope).sort((a, b) => b.score - a.score || b.date.localeCompare(a.date) || a.id.localeCompare(b.id));
      }
    };
  }
  function create(MiniSearch, records) {
    validatedRows(records);
    const rows = new Map(), mini = miniSearch(MiniSearch);
    for (const record of records) {
      if (rows.has(record.id)) throw Error("Duplicate search ID");
      rows.set(record.id, record); mini.add(preparedRecord(record));
    }
    return searchApi(mini, rows, records);
  }
  const yieldToBrowser = () => new Promise(resolve => setTimeout(resolve, 0));
  async function createAsync(MiniSearch, records, options = {}) {
    validatedRows(records);
    const yieldTask = options.yieldTask || yieldToBrowser, now = options.now || (() => typeof performance !== "undefined" ? performance.now() : Date.now());
    const maxBatch = Math.max(1, Math.min(100, options.batchSize || 12)), sliceMs = Math.max(1, options.sliceMs || 8);
    const rows = new Map(), mini = miniSearch(MiniSearch);
    let batch = 0, started = now();
    // Yield before preprocessing, then normalize and index bounded batches.
    // Building a full preparedRecords array first would keep its long task.
    await yieldTask();
    for (const record of records) {
      if (rows.has(record.id)) throw Error("Duplicate search ID");
      rows.set(record.id, record); mini.add(preparedRecord(record));
      batch += 1;
      if (batch >= maxBatch || now() - started >= sliceMs) { await yieldTask(); batch = 0; started = now(); }
    }
    return searchApi(mini, rows, records);
  }
  const api = {normalize, tokenize, concepts, create, createAsync};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SiteSearchCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
