/* Exact row-local references; no search normalization or index changes. */
(function (root) {
  "use strict";
  const fields = ["id", "scope", "title", "title_en", "url", "url_en", "date", "titles", "topics", "summary", "summary_en", "text", "headings"];
  const maxUnits = 2 * 1024 * 1024;
  const fail = () => { throw Error("Invalid search wire"); };
  const yieldToBrowser = () => new Promise(resolve => setTimeout(resolve, 0));
  async function decodeAsync(wire, options = {}) {
    const yieldTask = options.yieldTask || yieldToBrowser;
    const now = options.now || (() => typeof performance !== "undefined" ? performance.now() : Date.now());
    const batchSize = Math.max(1, Math.min(100, options.batchSize || 12));
    const sliceMs = Math.max(1, Math.min(8, options.sliceMs || 8));
    // Restore and index in separate bounded stages; neither runs before yield.
    await yieldTask();
    if (!wire || typeof wire !== "object" || Array.isArray(wire) ||
        Object.keys(wire).length !== 4 || !["version", "coverage", "fields", "records"].every(key => Object.hasOwn(wire, key)) ||
        wire.version !== 2 || typeof wire.coverage !== "string" || wire.coverage.length > maxUnits || !Array.isArray(wire.fields) ||
        wire.fields.length !== fields.length || fields.some((key, i) => key !== wire.fields[i]) ||
        !Array.isArray(wire.records) || wire.records.length > 10000) fail();
    const coverage = wire.coverage;
    const encoder = new TextEncoder();
    const jsonBytes = value => encoder.encode(JSON.stringify(value)).length;
    const rowOverhead = 2 + fields.length - 1 + fields.reduce((sum, key) => sum + jsonBytes(key) + 1, 0);
    let bytes = jsonBytes({version: 1, coverage, records: []});
    if (bytes > maxUnits) fail();
    let units = coverage.length, batch = 0, started = now();
    const records = [];
    for (const cells of wire.records) {
      if (!Array.isArray(cells) || cells.length !== fields.length) fail();
      let rowBytes = rowOverhead;
      const values = [];
      for (let field = 0; field < fields.length; field++) {
        const cell = cells[field]; let value;
        if (typeof cell === "string") value = cell;
        else {
          const permitted = field === 7 ? [2, 3] : field === 11 ? [9, 10] : null;
          if (!permitted || !Array.isArray(cell) || cell.length < 2 || cell.length > 5) fail();
          let nextRef = 0, previousLiteral = false, length = 0;
          const pieces = [];
          for (const fragment of cell) {
            if (typeof fragment === "string") {
              if (!fragment || previousLiteral) fail();
              pieces.push(fragment); length += fragment.length; previousLiteral = true;
            } else {
              if (!Number.isSafeInteger(fragment) || fragment !== permitted[nextRef++] || !values[fragment]) fail();
              pieces.push(values[fragment]); length += values[fragment].length; previousLiteral = false;
            }
            if (length > maxUnits - units) fail();
          }
          if (nextRef !== 2) fail();
          value = pieces.join("");
        }
        units += value.length;
        if (units > maxUnits) fail();
        rowBytes += jsonBytes(value);
        if (bytes + rowBytes > maxUnits) fail();
        values.push(value);
      }
      bytes += rowBytes + (records.length ? 1 : 0);
      if (bytes > maxUnits) fail();
      records.push(Object.fromEntries(fields.map((key, i) => [key, values[i]])));
      if (++batch >= batchSize || now() - started >= sliceMs) {
        await yieldTask(); batch = 0; started = now();
      }
    }
    return {version: 1, coverage, records};
  }
  const api = {version: 2, decodeAsync};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SiteSearchWire = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
