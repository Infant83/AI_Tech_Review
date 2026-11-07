const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.resolve(__dirname, '../../../../scripts/public_assets/hub.js'), 'utf8');
const flush = () => new Promise(resolve => setImmediate(resolve));
const day = offset => new Date(Date.now() + 9 * 3600000 - offset * 86400000).toISOString().slice(0, 10);

function harness(settings = {}) {
  const calls = [], listeners = {}, byId = {}, cards = [], summaries = [], storage = settings.storage || new Map();
  let document;
  class Element {
    constructor(tag, id = '') {
      this.tagName = tag.toUpperCase(); this.id = id; this.children = []; this.parentNode = null;
      this.dataset = {}; this.listeners = {}; this.attributes = {}; this.value = ''; this.hidden = false; this._text = ''; this.className = '';
      this.classList = {
        contains: name => this.className.split(/\s+/).includes(name),
        toggle: (name, force) => {
          const classes = new Set(this.className.split(/\s+/).filter(Boolean));
          const present = force === undefined ? !classes.has(name) : Boolean(force);
          if (present) classes.add(name); else classes.delete(name);
          this.className = [...classes].join(' '); return present;
        }
      };
    }
    set textContent(value) { this.replaceChildren(); this._text = String(value); }
    get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
    get isConnected() { return document?.body === this || Boolean(this.parentNode?.isConnected); }
    get scrollHeight() { return settings.summaryLayout && this.summaryIndex !== undefined ? settings.summaryLayout(this.summaryIndex, byId['review-grid'].dataset.view || 'gallery') : this.fullHeight || 0; }
    get clientHeight() { return this.dataset.summaryCollapsed === 'true' ? Math.min(this.scrollHeight, 60) : this.scrollHeight; }
    get options() { return this.children.filter(child => child.tagName === 'OPTION'); }
    contains(other) { return this === other || this.children.some(child => child.contains(other)); }
    removeChild(child) {
      const index = this.children.indexOf(child); assert.notEqual(index, -1, 'Cannot remove a non-child');
      if (this.isConnected && child.contains(document.activeElement)) document.activeElement = document.body;
      this.children.splice(index, 1); child.parentNode = null; return child;
    }
    appendChild(child) { if (child.parentNode) child.parentNode.removeChild(child); child.parentNode = this; this.children.push(child); return child; }
    replaceChildren(...children) {
      for (const child of [...this.children]) this.removeChild(child);
      this._text = ''; children.forEach(child => this.appendChild(child));
    }
    addEventListener(name, handler) { (this.listeners[name] ||= []).push(handler); }
    async dispatch(name) {
      await Promise.all((this.listeners[name] || []).map(handler => handler({ target: this, preventDefault() {} })));
      await flush();
    }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    closest(selector) { return selector === '.review-card' && this.classList.contains('review-card') ? this : this.parentNode?.closest(selector) || null; }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
    querySelectorAll(selector) {
      const all = []; const walk = node => { for (const child of node.children) { all.push(child); walk(child); } }; walk(this);
      if (selector === '.review-card') return all.filter(node => node.classList.contains('review-card'));
      if (selector === 'h3 a') return all.filter(node => node.tagName === 'A');
      if (selector === '.review-summary') return all.filter(node => node.className === 'review-summary');
      if (selector === '[data-summary-toggle]') return all.filter(node => Object.hasOwn(node.dataset, 'summaryToggle'));
      const field = /^\[data-discovery-field="(.+)"\]$/.exec(selector);
      return field ? all.filter(node => node.dataset.discoveryField === field[1]) : [];
    }
    focus(options) { document.activeElement = this; this.focusOptions = options; }
    scrollIntoView(options) { this.scrollOptions = options; }
  }
  const body = new Element('body');
  for (const [id, tag] of Object.entries({ search: 'input', category: 'select', 'review-grid': 'section', 'topic-filter': 'section', 'review-sort': 'select', 'review-period': 'select', 'discovery-from': 'input', 'discovery-to': 'input', 'discovery-dates': 'div', 'discovery-hint': 'p', 'discovery-status': 'p', 'discovery-retry': 'button', 'review-results': 'p', 'review-empty': 'p', 'review-more': 'button', 'hub-view-covers': 'button', 'hub-view-list': 'button' })) byId[id] = new Element(tag, id);
  Object.values(byId).forEach(element => body.appendChild(element));
  byId['hub-view-covers'].dataset.view = 'gallery'; byId['hub-view-list'].dataset.view = 'list';
  const option = (value, label) => { const node = new Element('option'); node.value = value; node.textContent = label; return node; };
  for (const value of ['', 'Quantum', 'Materials']) byId.category.appendChild(option(value, value || '전체'));
  for (const value of ['latest', 'views', 'likes']) byId['review-sort'].appendChild(option(value, value));
  byId['review-sort'].value = 'latest'; byId['review-period'].value = 'all';
  const data = [];
  for (let i = 0; i < (settings.count || 31); i++) {
    const card = new Element('article'); card.className = 'review-card';
    card.dataset = { articleId: 'review-' + i, published: day(i), category: i % 2 ? 'Materials' : 'Quantum', title: '제목 ' + i, tags: 'tag-' + i, search: '제목 ' + i + ' tag-' + i + ' 과학 내용' };
    for (const kind of ['opens', 'likes']) { const field = new Element('strong'); field.dataset.discoveryField = kind; field.textContent = '—'; card.appendChild(field); }
    const heading = new Element('h3'), link = new Element('a'); link.textContent = '제목 ' + i; heading.appendChild(link); card.appendChild(heading);
    if (settings.summaries) {
      const summary = new Element('p', 'review-summary-review-' + i), button = new Element('button');
      summary.className = 'review-summary'; summary.summaryIndex = i; summary.fullHeight = settings.summaryHeights?.[i] ?? 120;
      summary.textContent = 'Existing review summary ' + i;
      button.dataset.summaryToggle = ''; button.hidden = true; button.setAttribute('aria-controls', summary.id); button.setAttribute('aria-expanded', 'false');
      card.appendChild(summary); card.appendChild(button); summaries.push({summary, button});
    }
    byId['review-grid'].appendChild(card); cards.push(card);
    data.push({ id: card.dataset.articleId, opens: i * 10, likes: i % 4, shares: 0, copies: 0, periodOpens: i % 7, periodLikes: i % 5 });
  }
  const triggers = ['', 'Quantum', 'Materials'].map(value => { const node = new Element('button'); node.dataset.categoryFilter = value; return node; });
  const config = new Element('script'); config.textContent = JSON.stringify(settings.config || {});
  document = { body, documentElement: { lang: settings.lang || 'ko' }, activeElement: body, querySelector: selector => selector === '#reader-engagement-config' ? config : byId[selector.replace(/^#/, '')] || null,
    querySelectorAll: selector => selector === '[data-category-filter]' ? triggers : [] };
  function payload(url) {
    const params = new URL(url).searchParams, period = params.get('period') || 'custom';
    const range = period === 'all' ? { period, from: null, to: null } : { period, from: params.get('from') || day(Number(period.slice(0, -1)) - 1), to: params.get('to') || day(0) };
    return { ok: true, since: day(0) + 'T00:00:00.000Z', activitySince: day(0), range, articles: data };
  }
  const context = { document, URL, Date, Map, Set, Array, String, Number, Intl, Promise, Error, JSON, AbortController,
    location: { hostname: settings.hostname || 'infant83.io' }, setTimeout, clearTimeout,
    fetch: async (url, init) => { calls.push({ url, init }); if (settings.fetch) return settings.fetch(url, init, payload(url)); return { ok: true, json: async () => payload(url) }; },
    addEventListener: (name, handler) => { (listeners[name] ||= []).push(handler); }, matchMedia: () => ({ matches: true }) };
  context.sessionStorage = {
    getItem: key => { if (settings.blockStorage) throw Error('blocked'); return storage.get(key) || null; },
    setItem: (key, value) => { if (settings.blockStorage) throw Error('blocked'); storage.set(key, value); },
    removeItem: key => { if (settings.blockStorage) throw Error('blocked'); storage.delete(key); }
  };
  context.window = context;
  vm.runInNewContext(source, context);
  return { nodes: byId, cards, summaries, data, calls, document, triggers, listeners, storage, payload, visible: () => byId['review-grid'].children.filter(card => !card.hidden) };
}

test('hub renders six cards, loads six more, focuses the first new link and reaches the final partial batch', async () => {
  const h = harness(); await flush();
  assert.equal(h.visible().length, 6); assert.match(h.nodes['review-results'].textContent, /31편 중 6편/);
  await h.nodes['review-more'].dispatch('click');
  assert.equal(h.visible().length, 12); assert.equal(h.document.activeElement, h.cards[6].querySelector('h3 a'));
  assert.equal(h.document.activeElement.focusOptions.preventScroll, true);
  for (let i = 0; i < 4; i++) await h.nodes['review-more'].dispatch('click');
  assert.equal(h.visible().length, 31); assert.equal(h.nodes['review-more'].hidden, true);
  assert.equal(h.calls.length, 1); assert.equal(h.calls[0].init.credentials, 'omit');
});
test('search and topic changes reset pagination and never search dynamically added count labels', async () => {
  const h = harness(); await flush(); await h.nodes['review-more'].dispatch('click');
  h.nodes.search.value = '좋아요'; await h.nodes.search.dispatch('input');
  assert.equal(h.visible().length, 0); assert.equal(h.nodes['review-empty'].hidden, false);
  h.nodes.search.value = ''; await h.nodes.search.dispatch('input'); h.nodes.category.value = 'Materials'; await h.nodes.category.dispatch('change');
  assert.equal(h.visible().length, 6); assert.ok(h.visible().every(card => card.dataset.category === 'Materials'));
  assert.equal(h.nodes['review-results'].textContent, '15편 중 6편');
  await h.triggers[1].dispatch('click'); assert.equal(h.nodes.category.value, 'Quantum'); assert.equal(h.nodes['review-grid'].scrollOptions, undefined);
});
test('activity sorting uses period totals, card labels keep lifetime totals and topic options aggregate the same period', async () => {
  const h = harness(); await flush();
  h.nodes['review-sort'].value = 'views'; await h.nodes['review-sort'].dispatch('change');
  assert.equal(h.visible()[0].dataset.articleId, 'review-6');
  assert.equal(h.cards[6].querySelector('[data-discovery-field="opens"]').textContent, '60');
  assert.match(h.nodes['discovery-hint'].textContent, /활동 합계순/);
  const sums = h.cards.reduce((map, card, index) => { map[card.dataset.category] = (map[card.dataset.category] || 0) + h.data[index].periodOpens; return map; }, {});
  assert.equal(h.nodes.category.options[0].value, '');
  assert.equal(h.nodes.category.options[1].value, sums.Quantum >= sums.Materials ? 'Quantum' : 'Materials');
  h.nodes['review-sort'].value = 'latest'; await h.nodes['review-sort'].dispatch('change');
  assert.equal(h.visible()[0].dataset.articleId, 'review-0'); assert.equal(h.nodes.category.options[1].value, 'Quantum');
  assert.equal(h.calls.length, 1);
});
test('relative and custom periods use one batch each and preserve the chosen popularity sort', async () => {
  const h = harness(); await flush();
  h.nodes['review-sort'].value = 'likes'; await h.nodes['review-sort'].dispatch('change');
  h.nodes['review-period'].value = '7d'; await h.nodes['review-period'].dispatch('change'); await flush();
  assert.equal(h.nodes['review-sort'].value, 'likes'); assert.match(h.calls[1].url, /period=7d$/);
  h.nodes['review-period'].value = 'custom'; await h.nodes['review-period'].dispatch('change'); await flush();
  assert.equal(h.nodes['discovery-dates'].hidden, false); assert.match(h.calls[2].url, /from=\d{4}-\d{2}-\d{2}&to=/);
  h.nodes['discovery-from'].value = day(0); h.nodes['discovery-to'].value = day(1); await h.nodes['discovery-to'].dispatch('change'); await flush();
  assert.equal(h.calls.length, 3); assert.match(h.nodes['discovery-status'].textContent, /종료일/);
  h.nodes['discovery-to'].value = day(-1); await h.nodes['discovery-to'].dispatch('change'); await flush();
  assert.equal(h.calls.length, 3); assert.match(h.nodes['discovery-status'].textContent, /오늘 이후/);
});
test('offline or malformed metrics keep search/latest usable, disable popularity and never invent zero card counts', async () => {
  for (const fetch of [async () => { throw Error('offline'); }, async (_url, _init, value) => ({ ok: true, json: async () => ({ ...value, articles: [{ ...value.articles[0], likes: '9' }] }) })]) {
    const h = harness({ fetch }); await flush();
    assert.equal(h.visible().length, 6); assert.equal(h.nodes['review-sort'].options[1].disabled, true);
    assert.equal(h.nodes['discovery-retry'].hidden, false); assert.match(h.nodes['discovery-status'].textContent, /最新順|최신순/);
    assert.equal(h.cards[0].querySelector('[data-discovery-field="opens"]').textContent, '—');
    h.nodes.search.value = '제목 30'; await h.nodes.search.dispatch('input'); assert.equal(h.visible().length, 1);
  }
});
test('stale range responses cannot overwrite a newer selected activity period', async () => {
  let release;
  const h = harness({ fetch: async (url, _init, value) => ({ ok: true, json: () => url.endsWith('period=all') ? new Promise(resolve => { release = () => resolve(value); }) : Promise.resolve({ ...value, articles: value.articles.map(row => ({ ...row, likes: 99 })) }) }) });
  await flush(); h.nodes['review-period'].value = '7d'; await h.nodes['review-period'].dispatch('change'); await flush();
  assert.equal(h.cards[0].querySelector('[data-discovery-field="likes"]').textContent, '99');
  release(); await flush();
  assert.equal(h.cards[0].querySelector('[data-discovery-field="likes"]').textContent, '99');
});
test('back-cache refresh preserves expanded card count and updates totals without extra per-card requests', async () => {
  const h = harness(); await flush(); await h.nodes['review-more'].dispatch('click');
  h.listeners.pageshow[0]({ persisted: true }); await flush();
  assert.equal(h.visible().length, 12); assert.equal(h.calls.length, 2);
});
test('configured external hosts cannot redirect discovery requests', async () => {
  const h = harness({ config: { apiBase: 'https://evil.example/collect', allowLocalApi: true } }); await flush();
  assert.match(h.calls[0].url, /^https:\/\/api\.infant83\.io\/v1\/discovery\?/);
});
test('list presentation shares bounded pagination, preserves gallery expansion and does not fetch per-card statistics', async () => {
  const h = harness(); await flush(); await h.nodes['review-more'].dispatch('click');
  await h.nodes['hub-view-list'].dispatch('click');
  assert.equal(h.visible().length, 12); assert.equal(h.nodes['review-grid'].dataset.view, 'list');
  assert.equal(h.nodes['review-grid'].children.length, 12); assert.equal(h.nodes['review-more'].hidden, false); assert.equal(h.nodes['hub-view-list'].attributes['aria-pressed'], 'true');
  await h.nodes['hub-view-covers'].dispatch('click'); assert.equal(h.visible().length, 12);
  await h.nodes['hub-view-list'].dispatch('click'); h.nodes.category.value = 'Materials'; await h.nodes.category.dispatch('change');
  assert.equal(h.visible().length, 6); assert.ok(h.visible().every(card => card.dataset.category === 'Materials'));
  await h.nodes['hub-view-covers'].dispatch('click'); assert.equal(h.visible().length, 6); assert.equal(h.calls.length, 1);
});
test('English hub localizes discovery feedback, results and period errors', async () => {
  const h = harness({ lang: 'en' }); await flush();
  assert.equal(h.nodes['review-results'].textContent, '6 of 31 reviews'); assert.equal(h.nodes['review-more'].textContent, 'Show 6 more');
  assert.match(h.nodes['discovery-hint'].textContent, /activity dates, not publication dates/);
  h.nodes['review-period'].value = 'custom'; await h.nodes['review-period'].dispatch('change'); await flush();
  h.nodes['discovery-from'].value = day(0); h.nodes['discovery-to'].value = day(1); await h.nodes['discovery-to'].dispatch('change');
  assert.match(h.nodes['discovery-status'].textContent, /end date must be on or after/);
  const offline = harness({ lang: 'en', fetch: async () => { throw Error('offline'); } }); await flush();
  assert.match(offline.nodes['discovery-status'].textContent, /Showing newest reviews/);
});
test('language navigation restores shared browse state and the chosen activity sort once', async () => {
  const h = harness(); await flush();
  h.nodes.search.value = '제목'; await h.nodes.search.dispatch('input'); h.nodes.category.value = 'Materials'; await h.nodes.category.dispatch('change');
  h.nodes['review-sort'].value = 'likes'; await h.nodes['review-sort'].dispatch('change');
  h.nodes['review-period'].value = '7d'; await h.nodes['review-period'].dispatch('change'); await flush();
  await h.nodes['review-more'].dispatch('click'); await h.nodes['hub-view-list'].dispatch('click'); h.listeners['hub:before-language-change'][0]();
  const translated = harness({ lang: 'en', storage: h.storage }); await flush();
  assert.equal(translated.nodes.search.value, '제목'); assert.equal(translated.nodes.category.value, 'Materials');
  assert.equal(translated.nodes['review-sort'].value, 'likes'); assert.equal(translated.nodes['review-period'].value, '7d');
  assert.equal(translated.nodes['review-grid'].dataset.view, 'list'); assert.equal(translated.visible().length, 12);
  assert.equal(h.storage.has('atr.hub.browse.v1'), false); assert.match(translated.calls[0].url, /period=7d$/);
  await translated.nodes['hub-view-covers'].dispatch('click'); assert.equal(translated.visible().length, 12);
});
test('a completed final batch survives language navigation without an oversized stored limit', async () => {
  const h = harness(); await flush();
  for (let i = 0; i < 5; i++) await h.nodes['review-more'].dispatch('click');
  assert.equal(h.visible().length, 31); h.listeners['hub:before-language-change'][0]();
  const translated = harness({ lang: 'en', storage: h.storage }); await flush();
  assert.equal(translated.visible().length, 31); assert.equal(translated.nodes['review-more'].hidden, true);
});
test('malformed, expired and blocked browse storage leave the default hub usable', async () => {
  for (const stored of ['not json', JSON.stringify({ version: 1, time: Date.now() - 600001 }), JSON.stringify({ version: 1, time: Date.now(), search: '', category: '', sort: 'likes', period: 'all', from: '', to: '', view: 'list', limit: 1000000 })]) {
    const h = harness({ storage: new Map([['atr.hub.browse.v1', stored]]) }); await flush();
    assert.equal(h.visible().length, 6); assert.equal(h.nodes['review-grid'].dataset.view, 'gallery');
  }
  const blocked = harness({ blockStorage: true }); await flush();
  assert.doesNotThrow(() => blocked.listeners['hub:before-language-change'][0]());
  await blocked.nodes['hub-view-list'].dispatch('click'); assert.equal(blocked.visible().length, 6);
});

test('only overflowing summaries gain a localized accessible toggle, leaving titles and short summaries intact', async () => {
  for (const lang of ['ko', 'en']) {
    const h = harness({ lang, count: 7, summaries: true, summaryHeights: [120, 40] }); await flush();
    const long = h.summaries[0], short = h.summaries[1];
    assert.equal(long.summary.dataset.summaryCollapsed, 'true'); assert.equal(long.button.hidden, false);
    assert.equal(long.button.attributes['aria-controls'], long.summary.id); assert.equal(long.button.attributes['aria-expanded'], 'false');
    assert.equal(long.button.textContent, lang === 'en' ? 'Read full summary' : '요약 더 보기');
    assert.equal(short.summary.dataset.summaryCollapsed, 'false'); assert.equal(short.button.hidden, true);
    await long.button.dispatch('click'); assert.equal(long.summary.dataset.summaryCollapsed, 'false');
    assert.equal(long.button.attributes['aria-expanded'], 'true'); assert.equal(long.button.textContent, lang === 'en' ? 'Show less' : '요약 접기');
    assert.equal(h.cards[0].querySelector('h3 a').textContent, '제목 0');
    await long.button.dispatch('click'); assert.equal(long.summary.dataset.summaryCollapsed, 'true'); assert.equal(long.button.attributes['aria-expanded'], 'false');
    await h.nodes['review-more'].dispatch('click'); assert.equal(h.summaries[6].button.hidden, false);
  }
});

test('summary overflow is measured again on list changes and resize without discarding a reader expansion', async () => {
  const h = harness({ count: 7, summaries: true, summaryLayout: (_index, view) => view === 'list' ? 40 : 120 }); await flush();
  const first = h.summaries[0]; await first.button.dispatch('click');
  await h.nodes['hub-view-list'].dispatch('click'); assert.equal(first.button.hidden, true); assert.equal(first.summary.dataset.summaryCollapsed, 'false');
  await h.nodes['hub-view-covers'].dispatch('click'); assert.equal(first.button.hidden, false); assert.equal(first.button.attributes['aria-expanded'], 'true');
  const resized = harness({ count: 7, summaries: true }); await flush();
  const summary = resized.summaries[0]; summary.summary.fullHeight = 40;
  resized.listeners.resize[0](); await new Promise(resolve => setTimeout(resolve, 10));
  assert.equal(summary.button.hidden, true); assert.equal(summary.summary.dataset.summaryCollapsed, 'false');
  summary.summary.fullHeight = 120; resized.listeners.resize[0](); await new Promise(resolve => setTimeout(resolve, 10));
  assert.equal(summary.button.hidden, false); assert.equal(summary.summary.dataset.summaryCollapsed, 'true');
});

test('summary expansions follow article identity across language navigation and remain after filtering', async () => {
  const h = harness({ count: 7, summaries: true }); await flush();
  await h.summaries[0].button.dispatch('click'); await h.summaries[2].button.dispatch('click');
  h.nodes.category.value = 'Materials'; await h.nodes.category.dispatch('change');
  h.nodes.category.value = ''; await h.nodes.category.dispatch('change');
  assert.equal(h.summaries[0].button.attributes['aria-expanded'], 'true');
  h.listeners['hub:before-language-change'][0]();
  const saved = JSON.parse(h.storage.get('atr.hub.browse.v1'));
  assert.deepEqual(saved.expandedSummaries, ['review-0', 'review-2']);
  const en = harness({ lang: 'en', count: 7, summaries: true, storage: h.storage }); await flush();
  assert.equal(en.summaries[0].summary.dataset.summaryCollapsed, 'false'); assert.equal(en.summaries[0].button.textContent, 'Show less');
  assert.equal(en.summaries[2].button.attributes['aria-expanded'], 'true'); assert.equal(en.summaries[1].button.attributes['aria-expanded'], 'false');
  saved.expandedSummaries = ['missing-article'];
  const invalid = harness({ count: 7, summaries: true, storage: new Map([['atr.hub.browse.v1', JSON.stringify(saved)]]) }); await flush();
  assert.equal(invalid.summaries[0].summary.dataset.summaryCollapsed, 'true');
});

test('bounded rendering detaches unseen cards and reconnects only the next requested batch', async () => {
  const h = harness({ count: 13, summaries: true }); await flush();
  assert.equal(h.nodes['review-grid'].children.length, 6);
  assert.equal(h.cards.filter(card => card.isConnected).length, 6);
  assert.equal(h.cards[6].parentNode, null);
  assert.equal(h.summaries[6].button.hidden, true, 'detached summaries are not measured as visible');
  await h.nodes['review-more'].dispatch('click');
  assert.equal(h.nodes['review-grid'].children.length, 12);
  assert.equal(h.cards.filter(card => card.isConnected).length, 12);
  assert.equal(h.cards[6].parentNode, h.nodes['review-grid']);
  assert.equal(h.summaries[6].button.hidden, false);
  assert.equal(h.cards[12].isConnected, false);
  await h.nodes['hub-view-list'].dispatch('click');
  assert.equal(h.nodes['review-grid'].children.length, 12, 'changing presentation must not attach the final unrequested card');
});

test('normal pagehide preserves expanded card count and summary state for a subsequent return', async () => {
  const h = harness({ count: 13, summaries: true }); await flush();
  await h.nodes['review-more'].dispatch('click'); await h.summaries[7].button.dispatch('click');
  h.listeners.pagehide[0]();
  const saved = JSON.parse(h.storage.get('atr.hub.browse.v1'));
  assert.equal(saved.limit, 12); assert.deepEqual(saved.expandedSummaries, ['review-7']);
  const returned = harness({ count: 13, summaries: true, storage: h.storage }); await flush();
  assert.equal(returned.nodes['review-grid'].children.length, 12);
  assert.equal(returned.summaries[7].button.attributes['aria-expanded'], 'true');
  assert.equal(returned.document.activeElement, returned.document.body, 'detaching nodes clears stale fake focus like the DOM');
});
