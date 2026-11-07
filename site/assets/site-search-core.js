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
  function create(MiniSearch, records) {
    if (!Array.isArray(records) || records.length > 10000) throw Error("Invalid search records");
    const rows = new Map(records.map(record => [record.id, record]));
    if (rows.size !== records.length) throw Error("Duplicate search ID");
    const mini = new MiniSearch({fields: ["titles", "topics", "headings", "text"], tokenize, processTerm: normalize});
    mini.addAll(records.map(record => Object.fromEntries([ ["id", record.id], ...["titles", "topics", "headings", "text"].map(key => [key, searchable(record[key])]) ])));
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
  const api = {normalize, tokenize, concepts, create};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SiteSearchCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
