/* Observable refresh/read-state flows in a small DOM; no private test exports. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../reader-updates.js'), 'utf8');
const scope = '/AI_Tech_Review/', origin = 'https://infant83.io';
const pageA = 'a'.repeat(64), pageB = 'b'.repeat(64), articleA = 'c'.repeat(64), articleB = 'd'.repeat(64);
const now = Date.parse('2026-10-27T12:00:00Z'), storageKey = 'atr-seen-content:' + scope;
const ko = scope + 'reviews/example/', en = ko + 'en/';
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };

function eventTarget(value = {}) {
  const listeners = new Map();
  value.addEventListener = (type, listener, options) => {
    if (!listeners.has(type)) listeners.set(type, []);
    listeners.get(type).push({ listener, options });
  };
  value.dispatchEvent = event => {
    event.target ||= value;
    for (const { listener } of listeners.get(event.type) || []) listener(event);
    return true;
  };
  value.listeners = listeners;
  return value;
}
class Element {
  constructor(tag = 'div', className = '') {
    eventTarget(this); this.tagName = tag.toUpperCase(); this.className = className;
    this.children = []; this.attributes = {}; this.textContent = ''; this.parentNode = null;
  }
  appendChild(child) { this.children.push(child); child.parentNode = this; return child; }
  setAttribute(key, value) { this.attributes[key] = String(value); }
  removeAttribute(key) { delete this.attributes[key]; }
  getAttribute(key) { return this.attributes[key] ?? null; }
  remove() { if (this.parentNode) this.parentNode.children = this.parentNode.children.filter(child => child !== this); this.parentNode = null; }
  matches(selector) {
    return selector.split(',').some(item => {
      const s = item.trim();
      if (s === "[contenteditable='true']" || s === '[contenteditable]') return this.attributes.contenteditable !== undefined;
      if (s === "[aria-modal='true']") return this.attributes['aria-modal'] === 'true';
      if (s === 'dialog[open]') return this.tagName === 'DIALOG' && this.open;
      if (s.startsWith('.')) return this.className.split(/\s+/).includes(s.slice(1));
      const attr = /^(\w+)\[([\w-]+)(?:=['"]?([^'"\]]+)['"]?)?\]$/.exec(s);
      if (attr) return this.tagName === attr[1].toUpperCase() && (attr[3] === undefined ? this.attributes[attr[2]] !== undefined : this.attributes[attr[2]] === attr[3]);
      return this.tagName === s.toUpperCase();
    });
  }
  closest(selector) { return this.matches(selector) ? this : this.parentNode?.closest(selector) || null; }
  querySelectorAll(selector) {
    const result = [];
    for (const child of this.children) {
      if (child.matches(selector)) result.push(child);
      result.push(...child.querySelectorAll(selector));
    }
    return result;
  }
  querySelector(selector) {
    if (selector === 'h3 a, h2 a, a.text-link, .document-footer a, .lecture-primary') return this.link || null;
    return this.querySelectorAll(selector)[0] || null;
  }
}
function record(overrides = {}) {
  return { id: 'example', path: ko, paths: [ko, en], revision: articleA, change: 'new',
    publishedAt: '2026-10-27', updatedAt: '2026-10-27T03:00:00Z', ...overrides };
}
function manifest(overrides = {}) {
  return { version: 1, pages: { [scope]: pageA, [ko]: pageA, [en]: pageA }, articles: [record()], ...overrides };
}
const flush = () => new Promise(resolve => setImmediate(resolve));

function harness(options = {}) {
  let time = now, nextTimer = 0;
  const timers = new Map(), replacements = [], requests = [], events = [], storage = options.storage || new Map();
  const session = options.session || new Map();
  const body = new Element('body'), footer = body.appendChild(new Element('footer'));
  const assets = (options.assets || []).map(item => {
    const node = body.appendChild(new Element(item.tag));
    for (const [key, value] of Object.entries(item.attributes)) node.setAttribute(key, value);
    return node;
  });
  const cards = (options.cards || []).map(href => {
    const card = body.appendChild(new Element('article', 'review-card'));
    card.link = card.appendChild(new Element('a')); card.link.href = new URL(href, origin).href;
    card.appendChild(new Element('div', 'meta')); return card;
  });
  const article = options.article === false ? null : { id: 'example' };
  const config = { scope, pageVersion: pageA, articleVersion: articleA, article, ...options.config };
  const configNode = { textContent: options.configJSON || JSON.stringify(config) };
  const location = { href: origin + (options.pathname || ko) + (options.search || '') + (options.hash || ''),
    origin, pathname: options.pathname || ko, replace(url) { replacements.push(url); } };
  const document = eventTarget({ body, documentElement: { lang: options.english ? 'en' : 'ko' },
    visibilityState: options.hidden ? 'hidden' : 'visible', prerendering: !!options.prerendering,
    activeElement: options.active || body,
    createElement: tag => new Element(tag), getElementById: id => id === 'reader-engagement-config' ? configNode : null,
    querySelector: selector => body.querySelector(selector), querySelectorAll: selector => body.querySelectorAll(selector) });
  const window = eventTarget({ scrollY: options.scrollY || 0, matchMedia: () => ({ matches: !!options.standalone }),
    getSelection: () => options.selection || '' });
  const storageAPI = map => ({
    getItem(key) { if (options.storageBlocked) throw Error('blocked'); return map.get(key) ?? null; },
    setItem(key, value) { if (options.storageBlocked) throw Error('blocked'); map.set(key, String(value)); },
    removeItem(key) { if (options.storageBlocked) throw Error('blocked'); map.delete(key); }
  });
  const fetch = async (url, init) => {
    requests.push({ url, init });
    if (options.fetch) return options.fetch(url, init, requests.length);
    return { ok: true, json: async () => options.manifest || manifest() };
  };
  class ClockDate extends Date { static now() { return time; } }
  class TestEvent { constructor(type) { this.type = type; } }
  const history = { state: {}, replaceState(_state, _unused, url) { location.href = url; } };
  const context = { document, window, navigator: { standalone: !!options.standalone }, location, history,
    localStorage: storageAPI(storage), sessionStorage: storageAPI(session), fetch,
    URL, Date: ClockDate, AbortController, Event: TestEvent, Promise, Number,
    setTimeout(fn, delay) { const id = ++nextTimer; timers.set(id, { fn, due: time + delay }); return id; },
    clearTimeout(id) { timers.delete(id); } };
  window.addEventListener('atr:before-refresh', () => events.push('before-refresh'));
  vm.runInNewContext(source, context);
  const emit = (target, type, extra = {}) => target.dispatchEvent({ type, ...extra });
  const advance = async milliseconds => {
    time += milliseconds;
    for (const [id, timer] of [...timers]) if (timer.due <= time) { timers.delete(id); timer.fn(); }
    await flush();
  };
  const click = node => { assert.ok(node, 'expected visible control'); emit(node, 'click'); };
  const touch = (type, touches, target = body) => {
    const event = { type, target, touches, cancelable: true, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } };
    document.dispatchEvent(event); return event;
  };
  const find = selector => body.querySelector(selector);
  return { body, cards, assets, footer, document, window, location, replacements, requests, events, storage, session,
    emit, advance, click, touch, find, cue: card => card.querySelector('.atr-content-cue'),
    notice: () => find('.atr-update-notice'), read: () => JSON.parse(storage.get(storageKey) || '{}') };
}

test('an up-to-date visible article acknowledges its revision without reloading', async () => {
  const h = harness({ cards: [en] }); await flush();
  assert.equal(h.requests.length, 1);
  assert.equal(h.requests[0].init.cache, 'no-store');
  assert.equal(h.requests[0].init.credentials, 'omit');
  assert.equal(h.read().example, articleA);
  assert.equal(h.cue(h.cards[0]), null, 'same Korean/English article shares one read receipt');
  assert.equal(h.replacements.length, 0);
});
test('a stale article remains unread and offers a quiet notice while reading deep in the page', async () => {
  const latest = manifest({ pages: { [ko]: pageB }, articles: [record({ revision: articleB, change: 'updated' })] });
  const h = harness({ manifest: latest, scrollY: 600, search: '?mode=full', hash: '#section-4' }); await flush();
  assert.equal(h.replacements.length, 0); assert.equal(h.read().example, undefined);
  assert.equal(h.notice()?.attributes.role, 'status');
  h.click(h.notice().children[1]); await flush();
  assert.equal(h.requests.length, 2); assert.equal(h.replacements.length, 1);
  const target = new URL(h.replacements[0]);
  assert.equal(target.pathname, ko); assert.equal(target.searchParams.get('mode'), 'full');
  assert.equal(target.hash, '#section-4'); assert.ok(target.searchParams.get('_atr_refresh'));
  assert.deepEqual(h.events, ['before-refresh']);
});
test('stale content at the top refreshes once, and a repeated stale edge response cannot loop', async () => {
  const latest = manifest({ pages: { [ko]: pageB }, articles: [record({ revision: articleB })] });
  const session = new Map();
  const h = harness({ manifest: latest, session }); await flush();
  assert.equal(h.replacements.length, 1); assert.equal(h.read().example, undefined);
  const again = harness({ manifest: latest, session }); await flush();
  assert.equal(again.replacements.length, 0); assert.ok(again.notice());
});
test('focused editing, text selection and open dialogs postpone automatic replacement', async () => {
  const latest = manifest({ pages: { [ko]: pageB } });
  for (const options of [{ active: new Element('input') }, { selection: 'selected sentence' }, { dialog: true }]) {
    const h = harness({ ...options, manifest: latest, hidden: !!options.dialog });
    if (options.dialog) { const dialog = h.body.appendChild(new Element('dialog')); dialog.open = true; h.document.visibilityState = 'visible'; h.emit(h.document, 'visibilitychange'); }
    await flush(); assert.equal(h.replacements.length, 0); assert.ok(h.notice());
  }
});
test('hidden and prerendered pages cannot acknowledge articles before becoming visible', async () => {
  for (const options of [{ hidden: true }, { prerendering: true }]) {
    const h = harness(options); await flush();
    assert.equal(h.requests.length, 0); assert.equal(h.read().example, undefined);
    h.document.visibilityState = 'visible'; h.document.prerendering = false;
    h.emit(h.document, 'visibilitychange'); await flush();
    assert.equal(h.requests.length, 1); assert.equal(h.read().example, articleA);
  }
});
test('loading an old article bundle never acknowledges a newer article revision just because the page digest matches', async () => {
  const h = harness({ manifest: manifest({ articles: [record({ revision: articleB, change: 'updated' })] }) });
  await flush(); assert.equal(h.read().example, undefined);
});
test('new and revised cards have quiet labels, and opening either language elsewhere clears both', async () => {
  const changed = record({ id: 'changed', path: scope + 'reviews/changed/', paths: [scope + 'reviews/changed/'], revision: articleB, change: 'updated', publishedAt: '2026-10-27' });
  const h = harness({ pathname: scope, article: false, cards: [ko, en, changed.path], manifest: manifest({ articles: [record(), changed] }) });
  await flush();
  assert.equal(h.cue(h.cards[0])?.textContent, '새 글'); assert.equal(h.cue(h.cards[1])?.textContent, '새 글');
  assert.equal(h.cue(h.cards[2])?.textContent, '업데이트', 'a same-day correction remains an update');
  h.storage.set(storageKey, JSON.stringify({ example: articleA })); h.emit(h.window, 'storage', { key: storageKey });
  assert.equal(h.cue(h.cards[0]), null); assert.equal(h.cue(h.cards[1]), null);
  assert.equal(h.cue(h.cards[2])?.textContent, '업데이트');
  assert.equal(h.replacements.length, 0);
});
test('unopened recency cues expire seven days after the change without a reload or click', async () => {
  const h = harness({ pathname: scope, article: false, cards: [ko], manifest: manifest({ articles: [record({ updatedAt: new Date(now - 7 * 86400000 + 2000).toISOString() })] }) });
  await flush(); assert.ok(h.cue(h.cards[0]));
  await h.advance(2500); assert.equal(h.cue(h.cards[0]), null); assert.equal(h.replacements.length, 0);
});
test('future and expired changes do not create attention cues', async () => {
  for (const updatedAt of [new Date(now + 1000).toISOString(), new Date(now - 7 * 86400000).toISOString()]) {
    const h = harness({ pathname: scope, article: false, cards: [ko], manifest: manifest({ articles: [record({ updatedAt })] }) });
    await flush(); assert.equal(h.cue(h.cards[0]), null);
  }
});
test('foreign paths, malformed data and oversized manifests leave the original page usable', async () => {
  const bad = [null, manifest({ pages: { 'https://evil.example/': pageB } }),
    manifest({ articles: [record({ paths: ['https://evil.example/'], path: 'https://evil.example/' })] }),
    manifest({ articles: Array.from({ length: 2001 }, () => record()) }),
    manifest({ pages: { [ko]: '<script>' } }), manifest({ articles: [record(), record()] }),
    manifest({ articles: [record(), record({ id: 'other' })] })];
  for (const value of bad) {
    const h = harness({ manifest: value, fetch: async () => ({ ok: true, json: async () => value }) }); await flush();
    assert.equal(h.replacements.length, 0); assert.equal(h.read().example, undefined); assert.equal(h.notice(), null);
  }
});
test('offline background checks stay quiet; an explicit refresh gives a bounded accessible failure', async () => {
  const h = harness({ standalone: true, fetch: async () => { throw Error('offline'); } }); await flush();
  assert.equal(h.notice(), null); assert.equal(h.replacements.length, 0);
  h.click(h.find('.atr-page-refresh')); await flush();
  assert.ok(h.notice()); assert.equal(h.notice().attributes.role, 'status');
  assert.equal(h.replacements.length, 0);
});
test('a network timeout restores a manual refresh action without navigating to unconfirmed content', async () => {
  const h = harness({ standalone: true, fetch: async (_url, init, call) => call === 1
    ? { ok: true, json: async () => manifest() }
    : new Promise((_, reject) => init.signal.addEventListener('abort', () => reject(Error('timeout')))) });
  await flush(); h.click(h.find('.atr-page-refresh')); await flush(); await h.advance(7001);
  assert.ok(h.notice()); assert.equal(h.replacements.length, 0);
});
test('native browser tabs keep browser refresh gestures and have no authored refresh control', async () => {
  const h = harness(); await flush();
  assert.equal(h.find('.atr-page-refresh'), null);
  for (const name of ['touchstart', 'touchmove', 'touchend', 'touchcancel']) assert.equal(h.document.listeners.has(name), false);
});
test('installed apps provide an accessible footer refresh independent of touch gestures', async () => {
  const h = harness({ standalone: true }); await flush();
  const button = h.find('.atr-page-refresh'); assert.equal(button?.tagName, 'BUTTON');
  assert.equal(button.attributes['aria-label'], '새로고침'); assert.equal(button.type, 'button');
  h.click(button); await flush(); assert.equal(h.replacements.length, 1);
});
test('installed pull refresh happens only after a deliberate downward drag is released', async () => {
  const h = harness({ standalone: true }); await flush();
  h.touch('touchstart', [{ clientX: 100, clientY: 10 }]);
  const move = h.touch('touchmove', [{ clientX: 102, clientY: 110 }]); await flush();
  assert.equal(move.defaultPrevented, true); assert.equal(h.requests.length, 1);
  assert.equal(h.find('.atr-pull-status')?.textContent, '놓으면 새로고침');
  h.touch('touchend', []); await flush();
  assert.equal(h.requests.length, 2); assert.equal(h.replacements.length, 1); assert.equal(h.find('.atr-pull-status'), null);
});
test('short, horizontal, multi-touch, cancelled and interactive drags never refresh', async () => {
  for (const kind of ['short', 'horizontal', 'multi', 'cancel', 'input', 'scrolled']) {
    const h = harness({ standalone: true, scrollY: kind === 'scrolled' ? 300 : 0 }); await flush();
    const target = kind === 'input' ? new Element('input') : h.body;
    h.touch('touchstart', [{ clientX: 100, clientY: 10 }], target);
    const touches = kind === 'multi' ? [{ clientX: 100, clientY: 130 }, { clientX: 110, clientY: 130 }]
      : [{ clientX: kind === 'horizontal' ? 160 : 100, clientY: kind === 'short' ? 40 : 130 }];
    const move = h.touch('touchmove', touches, target);
    if (kind === 'cancel') h.touch('touchcancel', []);
    h.touch('touchend', []); await flush();
    assert.equal(h.requests.length, 1, kind); assert.equal(h.replacements.length, 0, kind);
    if (['horizontal', 'multi', 'input', 'scrolled'].includes(kind)) assert.equal(move.defaultPrevented, false, kind);
  }
});
test('foreground event bursts share one request and later resume checks the latest document', async () => {
  const waiting = deferred();
  const h = harness({ fetch: async () => waiting.promise });
  h.emit(h.window, 'pageshow'); h.emit(h.window, 'focus'); h.emit(h.document, 'visibilitychange');
  assert.equal(h.requests.length, 1);
  waiting.resolve({ ok: true, json: async () => manifest() }); await flush();
  h.emit(h.window, 'focus'); await flush(); assert.equal(h.requests.length, 1);
  await h.advance(30001); h.emit(h.window, 'focus'); await flush(); assert.equal(h.requests.length, 2);
});
test('manual refresh requested during an automatic check is honored when that check completes', async () => {
  const waiting = deferred(); const h = harness({ standalone: true, fetch: async () => waiting.promise });
  h.click(h.find('.atr-page-refresh')); waiting.resolve({ ok: true, json: async () => manifest() }); await flush();
  assert.equal(h.replacements.length, 1, 'an explicit refresh must not disappear behind a foreground check');
});
test('current article assets are versioned inside its own folder and unrelated assets stay untouched', async () => {
  const h = harness({ assets: [
    { tag: 'img', attributes: { src: 'figure.svg?size=large#detail' } },
    { tag: 'link', attributes: { rel: 'stylesheet', href: './review.css' } },
    { tag: 'source', attributes: { src: 'comparison.mp4' } },
    { tag: 'img', attributes: { src: 'https://elsewhere.example/photo.png' } },
    { tag: 'link', attributes: { rel: 'stylesheet', href: scope + 'assets/site.css?v=global' } }
  ] }); await flush();
  for (const [index, attr] of [[0, 'src'], [1, 'href'], [2, 'src']]) {
    const url = new URL(h.assets[index].getAttribute(attr)); assert.equal(url.searchParams.get('_atr_v'), articleA);
    assert.ok(url.pathname.startsWith(ko));
  }
  const figure = new URL(h.assets[0].getAttribute('src'));
  assert.equal(figure.searchParams.get('size'), 'large'); assert.equal(figure.hash, '#detail');
  assert.equal(h.assets[3].getAttribute('src'), 'https://elsewhere.example/photo.png');
  assert.equal(h.assets[4].getAttribute('href'), scope + 'assets/site.css?v=global');
});
test('dismissing an update notice suppresses the same revision without concealing a later change', async () => {
  const data = manifest({ pages: { [ko]: pageB }, articles: [record({ revision: articleB, change: 'updated' })] });
  const h = harness({ manifest: data, scrollY: 600 }); await flush();
  h.click(h.notice().children[2]); assert.equal(h.notice(), null);
  await h.advance(30001); h.emit(h.window, 'focus'); await flush(); assert.equal(h.notice(), null);
  data.pages[ko] = 'e'.repeat(64);
  await h.advance(30001); h.emit(h.window, 'focus'); await flush(); assert.ok(h.notice());
  assert.equal(h.replacements.length, 0);
});
test('unsafe scopes and corrupt embedded configuration do not start the refresh controller', async () => {
  for (const invalid of ['/AI_Tech_Review/../', '//AI_Tech_Review/', '/AI_Tech_Review//']) {
    const h = harness({ config: { scope: invalid }, pathname: invalid, standalone: true }); await flush();
    assert.equal(h.requests.length, 0); assert.equal(h.find('.atr-page-refresh'), null);
  }
  for (const configJSON of ['null', '[]', '{broken']) {
    const h = harness({ configJSON }); await flush(); assert.equal(h.requests.length, 0);
  }
});
test('a manual refresh joining a failed automatic check still reports the failure', async () => {
  const waiting = deferred(), h = harness({ standalone: true, fetch: async () => waiting.promise });
  h.click(h.find('.atr-page-refresh')); waiting.reject(Error('offline')); await flush();
  assert.ok(h.notice()); assert.equal(h.replacements.length, 0);
});
