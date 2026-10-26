const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.resolve(__dirname, '../../../../scripts/public_assets/preferences.js'), 'utf8');
const key = 'atr.reader.preferences.v1';

function harness(options = {}) {
  const storage = options.storage || new Map(), trace = [], reads = [], writes = [], navigation = [], windowListeners = {}, documentListeners = {}, mediaListeners = [];
  if (Object.hasOwn(options, 'stored')) storage.set(key, options.stored);
  class Element {
    constructor(value = '') { this.value = value; this.textContent = ''; this.attributes = {}; this.listeners = {}; this.open = false; }
    addEventListener(name, handler) { (this.listeners[name] ||= []).push(handler); }
    dispatch(name, extra = {}) { for (const handler of this.listeners[name] || []) handler({ type: name, target: this, ...extra }); }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    getAttribute(name) { return this.attributes[name] || null; }
    focus() { document.activeElement = this; }
  }
  const themes = [new Element(), new Element()], language = new Element(), summary = new Element(), details = new Element(), status = new Element();
  details.contains = target => [details, summary, ...themes].includes(target);
  details.querySelector = selector => selector === 'summary' ? summary : null;
  const href = options.href || 'https://infant83.io/AI_Tech_Review/';
  const current = new URL(href);
  const root = { dataset: { ...(options.initialTheme ? { theme: options.initialTheme } : {}) }, style: {} };
  if (options.language !== null) root.dataset.hubLanguage = options.language || 'ko';
  const home = options.home === null ? null : new Element();
  if (home) home.attributes.href = options.home || '/AI_Tech_Review/index.html';
  const document = { documentElement: root, readyState: options.loading ? 'loading' : 'complete', activeElement: null,
    querySelector: selector => selector === '[data-hub-home]' ? home : null,
    querySelectorAll: selector => ({ '[data-hub-theme]': themes, '.hub-appearance summary': [summary], '[data-hub-preference-status]': [status], '[data-hub-language-select]': [language], '.hub-appearance': [details] })[selector] || [],
    addEventListener: (name, handler, settings) => { (documentListeners[name] ||= []).push({ handler, once: settings?.once === true }); }
  };
  const media = { matches: options.osDark === true, addListener: handler => mediaListeners.push(handler) };
  if (!options.legacyMedia) media.addEventListener = (name, handler) => { if (name === 'change') mediaListeners.push(handler); };
  const location = { href, origin: current.origin, pathname: current.pathname, search: current.search, hash: current.hash,
    assign: target => { trace.push('assign'); navigation.push({ method: 'assign', target }); },
    replace: target => { trace.push('replace'); navigation.push({ method: 'replace', target }); }
  };
  const context = { document, location, URL, JSON, Set, String, Array,
    localStorage: {
      getItem(name) { reads.push(name); if (options.blocked) throw Error('storage blocked'); return storage.get(name) || null; },
      setItem(name, value) { if (options.blocked) throw Error('storage blocked'); trace.push('persist'); writes.push({ name, value }); storage.set(name, value); }
    },
    Event: class { constructor(type) { this.type = type; } },
    addEventListener(name, handler) { (windowListeners[name] ||= []).push(handler); },
    dispatchEvent(event) { trace.push(event.type); for (const handler of windowListeners[event.type] || []) handler(event); return true; }
  };
  if (!options.noMedia) context.matchMedia = () => media;
  context.window = context;
  vm.runInNewContext(source, context);
  return { root, document, themes, language, summary, details, status, media, storage, reads, writes, trace, navigation, context,
    ready() { document.readyState = 'interactive'; const entries = documentListeners.DOMContentLoaded || []; for (const entry of entries) entry.handler(); documentListeners.DOMContentLoaded = entries.filter(entry => !entry.once); },
    mediaChange(dark) { media.matches = dark; for (const handler of mediaListeners) handler({ matches: dark }); },
    storageChange(value, name = key) { context.dispatchEvent({ type: 'storage', key: name, newValue: value }); },
    documentClick(target) { for (const entry of documentListeners.click || []) entry.handler({ target }); }
  };
}

test('stored theme is applied before DOM ready and first visits remain light regardless of device theme', () => {
  const early = harness({ loading: true, stored: JSON.stringify({ readerLanguage: 'ko', readerTheme: 'dark' }) });
  assert.equal(early.root.dataset.theme, 'dark'); assert.equal(early.root.dataset.themePreference, 'dark');
  assert.equal(early.root.style.colorScheme, 'dark'); assert.equal(early.themes[0].listeners.change, undefined);
  early.ready(); assert.equal(early.themes[0].value, 'dark'); assert.equal(early.language.value, 'ko');
  const fresh = harness({ osDark: true });
  assert.equal(fresh.root.dataset.theme, 'light'); assert.equal(fresh.root.dataset.themePreference, 'light');
});

test('theme selection persists the active language, synchronizes controls and restores on the next visit', () => {
  const h = harness(); h.themes[0].value = 'dark'; h.themes[0].dispatch('change');
  assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.themes[1].value, 'dark');
  assert.deepEqual(JSON.parse(h.storage.get(key)), { readerTheme: 'dark', readerLanguage: 'ko' });
  assert.equal(h.status.textContent, '선택을 저장했습니다.');
  assert.equal(h.summary.getAttribute('aria-label'), '화면 테마: 어둡게');
  const restored = harness({ storage: h.storage });
  assert.equal(restored.root.dataset.theme, 'dark'); assert.equal(restored.themes[0].value, 'dark');
  assert.ok(h.writes.every(write => write.name === key));
});

test('device theme follows media changes only while the device-setting preference is active', () => {
  for (const legacyMedia of [false, true]) {
    const h = harness({ legacyMedia, osDark: true, stored: JSON.stringify({ readerTheme: 'system' }) });
    assert.equal(h.root.dataset.theme, 'dark'); h.mediaChange(false); assert.equal(h.root.dataset.theme, 'light');
    h.themes[0].value = 'dark'; h.themes[0].dispatch('change'); h.mediaChange(false);
    assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.root.dataset.themePreference, 'dark');
  }
});

test('stored English redirects only the Korean hub entry and retains query and anchor', () => {
  const h = harness({ href: 'https://infant83.io/AI_Tech_Review/?period=7d#topic-filter', stored: JSON.stringify({ readerLanguage: 'en', readerTheme: 'dark' }) });
  assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.navigation.length, 1);
  assert.equal(h.navigation[0].method, 'replace');
  assert.equal(h.navigation[0].target, 'https://infant83.io/AI_Tech_Review/en/?period=7d&lang=en#topic-filter');
  assert.equal(h.language.listeners.change, undefined, 'a redirecting document does not bind stale controls');
});

test('an explicit Korean query bypasses stored English and an explicit English path is never forced to Korean', () => {
  const ko = harness({ href: 'https://infant83.io/AI_Tech_Review/?lang=ko', stored: JSON.stringify({ readerLanguage: 'en' }) });
  assert.deepEqual(ko.navigation, []); assert.equal(ko.language.value, 'ko');
  assert.equal(JSON.parse(ko.storage.get(key)).readerLanguage, 'ko');
  for (const suffix of ['en/', 'en/index.html']) {
    const en = harness({ href: 'https://infant83.io/AI_Tech_Review/' + suffix, language: 'en', home: '../index.html', stored: JSON.stringify({ readerLanguage: 'ko' }) });
    assert.deepEqual(en.navigation, []); assert.equal(en.language.value, 'en');
  }
});

test('a locale choice saves preferences and dispatches browse preservation before same-origin navigation', () => {
  const h = harness({ href: 'https://infant83.io/AI_Tech_Review/?period=30d#review-grid' });
  h.language.value = 'en'; h.language.dispatch('change');
  assert.deepEqual(h.trace, ['persist', 'hub:before-language-change', 'assign']);
  assert.equal(h.navigation[0].target, 'https://infant83.io/AI_Tech_Review/en/?period=30d&lang=en#review-grid');
  assert.deepEqual(JSON.parse(h.storage.get(key)), { readerTheme: 'light', readerLanguage: 'en' });
  const back = harness({ href: h.navigation[0].target, language: 'en', home: '../index.html', storage: h.storage });
  assert.deepEqual(back.navigation, []); back.language.value = 'ko'; back.language.dispatch('change');
  assert.equal(new URL(back.navigation[0].target).pathname, '/AI_Tech_Review/');
  assert.equal(new URL(back.navigation[0].target).searchParams.get('lang'), 'ko');
});

test('corrupt preferences are ignored and unsupported control values never navigate', () => {
  for (const stored of ['not json', 'null', '[]', '"en"', '{"readerLanguage":"fr","readerTheme":"red"}', ' '.repeat(1025)]) {
    const h = harness({ stored });
    assert.equal(h.root.dataset.theme, 'light'); assert.deepEqual(h.navigation, []);
    h.language.value = 'https://evil.example/'; h.language.dispatch('change');
    assert.equal(h.language.value, 'ko'); assert.deepEqual(h.navigation, []);
    h.themes[0].value = 'dark'; h.themes[0].dispatch('change'); assert.equal(h.root.dataset.theme, 'dark');
  }
});

test('blocked storage still applies theme and carries an explicit locale in the destination URL', () => {
  const h = harness({ blocked: true }); h.themes[0].value = 'dark'; h.themes[0].dispatch('change');
  assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.status.textContent, '이번 방문에 적용했습니다.');
  h.language.value = 'en'; h.language.dispatch('change');
  assert.deepEqual(h.trace, ['hub:before-language-change', 'assign']);
  assert.equal(h.navigation[0].target, 'https://infant83.io/AI_Tech_Review/en/?lang=en');
  const arrived = harness({ blocked: true, href: h.navigation[0].target, language: 'en', home: '../index.html' });
  assert.deepEqual(arrived.navigation, []); assert.equal(arrived.language.value, 'en');
});

test('foreign or invalid home links never apply state or create an open redirect', () => {
  for (const home of ['https://evil.example/AI_Tech_Review/', '//evil.example/', 'javascript:alert(1)', 'data:text/html,hello', 'https://[invalid']) {
    const h = harness({ home, initialTheme: 'sentinel', stored: JSON.stringify({ readerLanguage: 'en', readerTheme: 'dark' }) });
    assert.equal(h.root.dataset.theme, 'sentinel'); assert.equal(h.reads.length, 0); assert.equal(h.navigation.length, 0);
  }
  const query = harness({ href: 'https://infant83.io/AI_Tech_Review/?lang=https://evil.example/&next=https://evil.example/', stored: JSON.stringify({ readerLanguage: 'en' }) });
  assert.equal(new URL(query.navigation[0].target).origin, 'https://infant83.io');
  assert.equal(new URL(query.navigation[0].target).pathname, '/AI_Tech_Review/en/');
});

test('preferences do not affect article, methods, unrelated paths, or documents without hub markers', () => {
  for (const href of ['https://infant83.io/AI_Tech_Review/reviews/sample/', 'https://infant83.io/AI_Tech_Review/methods/', 'https://infant83.io/unrelated/']) {
    const h = harness({ href, initialTheme: 'sentinel', stored: JSON.stringify({ readerLanguage: 'en', readerTheme: 'dark' }) });
    assert.equal(h.root.dataset.theme, 'sentinel'); assert.equal(h.reads.length, 0); assert.deepEqual(h.navigation, []);
  }
  for (const options of [{ language: null }, { language: 'fr' }, { home: null }]) {
    const h = harness({ ...options, initialTheme: 'sentinel' });
    assert.equal(h.root.dataset.theme, 'sentinel'); assert.equal(h.reads.length, 0);
  }
});

test('cross-tab theme changes do not navigate the current language and the appearance disclosure closes accessibly', () => {
  const h = harness({ language: 'en', href: 'https://infant83.io/AI_Tech_Review/en/', home: '../index.html' });
  h.storageChange(JSON.stringify({ readerTheme: 'dark', readerLanguage: 'ko' }));
  assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.language.value, 'en'); assert.deepEqual(h.navigation, []);
  h.storageChange(JSON.stringify({ readerTheme: 'light' }), 'unrelated'); assert.equal(h.root.dataset.theme, 'dark');
  h.details.open = true; h.details.dispatch('keydown', { key: 'Escape' });
  assert.equal(h.details.open, false); assert.equal(h.document.activeElement, h.summary);
  h.details.open = true; h.documentClick(h.summary); assert.equal(h.details.open, true);
  h.documentClick(new Object()); assert.equal(h.details.open, false);
});
