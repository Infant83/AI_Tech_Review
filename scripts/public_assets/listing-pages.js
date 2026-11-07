/* Static list pages remain usable without this optional enhancement. */
(function (root) {
  "use strict";
  function create(grid, selector) {
    const nav = document.querySelector("[data-list-pagination]");
    if (!nav) return null;
    const first = Number(nav.dataset.page), count = Number(nav.dataset.pages), total = Number(nav.dataset.total);
    if (![first, count, total].every(Number.isSafeInteger) || first < 1 || count < first || count > 2000) return null;
    const base = new URL(nav.dataset.root || "./", location.href), en = nav.dataset.language === "en", area = nav.dataset.area;
    if (!["reviews", "archive", "briefings"].includes(area) || base.origin !== location.origin) return null;
    const start = (area === "reviews" ? "" : area + "/") + (en ? "en/" : "");
    const pages = new Map([[first, [...grid.querySelectorAll(selector)]]]), pending = new Map();
    const status = document.querySelector("[data-list-load-status]");
    function absoluteLinks(card, url) {
      for (const element of card.querySelectorAll("[href],[src],[srcset]")) {
        for (const attribute of ["href", "src"]) if (element.hasAttribute(attribute)) element.setAttribute(attribute, new URL(element.getAttribute(attribute), url).href);
        if (element.hasAttribute("srcset")) element.setAttribute("srcset", element.getAttribute("srcset").split(",").map(part => { const [href, width] = part.trim().split(/\s+/); return new URL(href, url).href + (width ? " " + width : ""); }).join(", "));
      }
    }
    async function read(number) {
      if (pages.has(number)) return pages.get(number);
      if (!pending.has(number)) pending.set(number, (async () => {
        const url = new URL(start + (number > 1 ? `page/${number}/` : "") + "index.html", base);
        const response = await fetch(url, {credentials: "omit"});
        if (!response.ok || new URL(response.url).origin !== base.origin) throw Error("list_page_unavailable");
        const text = await response.text();
        if (text.length > 2_000_000) throw Error("list_page_too_large");
        const parsed = new DOMParser().parseFromString(text, "text/html"), other = parsed.querySelector("[data-list-pagination]");
        if (!other || other.dataset.area !== area || Number(other.dataset.page) !== number || Number(other.dataset.total) !== total) throw Error("list_revision_changed");
        const cards = [...parsed.querySelectorAll(selector)].map(card => { absoluteLinks(card, response.url); return document.importNode(card, true); });
        pages.set(number, cards); return cards;
      })().finally(() => pending.delete(number)));
      return pending.get(number);
    }
    const cards = () => [...pages].sort(([a], [b]) => a - b).flatMap(([, nodes]) => nodes);
    const nextNumber = () => { for (let page = first + 1; page <= count; page++) if (!pages.has(page)) return page; return null; };
    async function run(operation) {
      if (status) status.textContent = en ? "Loading list…" : "목록을 불러오는 중…";
      try { const value = await operation(); if (status) status.textContent = ""; return value; }
      catch (error) { if (status) status.textContent = en ? "The list could not load. Try again or use the page links." : "목록을 불러오지 못했습니다. 다시 시도하거나 페이지 링크를 이용해 주세요."; throw error; }
    }
    return {nav, total, first, pageSize: Number(nav.dataset.size),
      cards, complete: () => pages.size === count, hasNext: () => nextNumber() !== null,
      next: () => run(async () => { const number = nextNumber(); if (number !== null) await read(number); return cards(); }),
      all: () => run(async () => { for (let start = 1; start <= count; start += 3) { await Promise.all(Array.from({length: Math.min(3, count - start + 1)}, (_, offset) => read(start + offset))); await new Promise(resolve => setTimeout(resolve, 0)); } return cards(); }),
      filtered: active => { nav.hidden = Boolean(active); }
    };
  }
  root.ListingPages = {create};
})(typeof globalThis !== "undefined" ? globalThis : this);
