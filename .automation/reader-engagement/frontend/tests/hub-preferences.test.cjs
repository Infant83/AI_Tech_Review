const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.resolve(__dirname, '../../../../scripts/public_assets/preferences.js'), 'utf8');
const languageKey = 'atr.reader.language.v1';
const themeKey = 'atr.reader.theme.v1';
const legacyKey = 'atr.reader.preferences.v1';

function harness(options = {}) {
  const storage = options.storage || new Map(), trace = [], reads = [], writes = [], navigation = [], windowListeners = {}, documentListeners = {}, mediaListeners = [];
  for (const [option, key] of [['stored', legacyKey], ['savedLanguage', languageKey], ['savedTheme', themeKey]]) {
    if (Object.hasOwn(options, option)) storage.set(key, options[option]);
  }
  class Element {
    constructor() { this.textContent = ''; this.attributes = {}; this.listeners = {}; }
    addEventListener(name, handler) { (this.listeners[name] ||= []).push(handler); }
    click() { for (const handler of this.listeners.click || []) handler({ type: 'click', target: this }); }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    getAttribute(name) { return this.attributes[name] || null; }
  }
  const themes = [new Element(), new Element()], languages = [new Element(), new Element()], status = new Element();
  const href = options.href || 'https://infant83.io/AI_Tech_Review/';
  const current = new URL(href);
  const root = { dataset: { ...(options.initialTheme ? { theme: options.initialTheme } : {}) }, style: {} };
  if (options.language !== null) root.dataset.hubLanguage = options.language || 'ko';
  const home = options.home === null ? null : new Element();
  if (home) home.attributes.href = options.home || '/AI_Tech_Review/index.html';
  const document = { documentElement: root, readyState: options.loading ? 'loading' : 'complete',
    querySelector: selector => selector === '[data-hub-home]' ? home : null,
    querySelectorAll: selector => ({ '[data-hub-theme-toggle]': themes, '[data-hub-preference-status]': [status], '[data-hub-language-toggle]': languages })[selector] || [],
    addEventListener: (name, handler, settings) => { (documentListeners[name] ||= []).push({ handler, once: settings?.once === true }); }
  };
  const media = { matches: options.osDark === true, addEventListener: (name, handler) => mediaListeners.push(handler) };
  const location = { href, origin: current.origin, pathname: current.pathname, search: current.search, hash: current.hash,
    assign: target => { trace.push('assign'); navigation.push({ method: 'assign', target }); },
    replace: target => { trace.push('replace'); navigation.push({ method: 'replace', target }); }
  };
  const storageAPI = {
    getItem(name) { reads.push(name); if (options.blocked) throw Error('storage blocked'); return storage.has(name) ? storage.get(name) : null; },
    setItem(name, value) { if (options.blocked || options.writeBlocked) throw Error('storage blocked'); trace.push('persist:' + name); writes.push({ name, value }); storage.set(name, value); }
  };
  const context = { document, location, URL, JSON, Set, String, Array,
    Event: class { constructor(type) { this.type = type; } },
    addEventListener(name, handler) { (windowListeners[name] ||= []).push(handler); },
    dispatchEvent(event) { trace.push(event.type); for (const handler of windowListeners[event.type] || []) handler(event); return true; }
  };
  Object.defineProperty(context, 'localStorage', { get() { if (options.accessBlocked) throw Error('blocked storage accessor'); return storageAPI; } });
  if (!options.noMedia) context.matchMedia = () => media;
  context.window = context;
  vm.runInNewContext(source, context);
  return { root, document, themes, languages, status, media, storage, reads, writes, trace, navigation, context,
    ready() { document.readyState = 'interactive'; const entries = documentListeners.DOMContentLoaded || []; for (const entry of entries) entry.handler(); documentListeners.DOMContentLoaded = entries.filter(entry => !entry.once); },
    mediaChange(dark) { media.matches = dark; for (const handler of mediaListeners) handler({ matches: dark }); },
    storageChange(value, name = themeKey, area = storageAPI) {
      if (area === storageAPI) { if (name === null) storage.clear(); else if (value === null) storage.delete(name); else storage.set(name, value); }
      context.dispatchEvent({ type: 'storage', key: name, newValue: value, storageArea: area });
    }
  };
}

test('saved theme is applied before DOM ready and first visits stay light regardless of device appearance', () => {
  const early = harness({ loading: true, savedTheme: 'dark' });
  assert.equal(early.root.dataset.theme, 'dark'); assert.equal(early.root.dataset.themePreference, 'dark');
  assert.equal(early.root.style.colorScheme, 'dark'); assert.equal(early.themes[0].listeners.click, undefined);
  early.ready(); assert.equal(early.themes[0].getAttribute('aria-checked'), 'true');
  const fresh = harness({ osDark: true });
  assert.equal(fresh.root.dataset.theme, 'light'); assert.equal(fresh.writes.length, 0);
});

test('theme toggles save only theme, synchronize switches and restore after reload', () => {
  const h = harness({ savedLanguage: 'ko' });
  h.themes[0].click();
  assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.themes[1].getAttribute('aria-checked'), 'true');
  assert.deepEqual(h.writes, [{ name: themeKey, value: 'dark' }]);
  assert.equal(h.storage.get(languageKey), 'ko'); assert.equal(h.status.textContent, '선택을 저장했습니다.');
  assert.equal(h.themes[0].getAttribute('aria-label'), '어두운 화면');
  assert.equal(h.themes[0].getAttribute('title'), '밝은 화면으로 전환');
  const restored = harness({ storage: h.storage });
  assert.equal(restored.root.dataset.theme, 'dark'); assert.equal(restored.themes[0].getAttribute('aria-checked'), 'true');
  restored.themes[1].click(); assert.equal(restored.root.dataset.theme, 'light');
  assert.equal(restored.themes[0].getAttribute('aria-label'), '어두운 화면', 'switch name is stable as its checked state changes');
  assert.deepEqual(restored.writes, [{ name: themeKey, value: 'light' }]);
});

test('language toggles save only language and preserve browse state before same-origin navigation', () => {
  const h = harness({ href: 'https://infant83.io/AI_Tech_Review/?period=30d#review-grid', savedTheme: 'dark' });
  assert.equal(h.languages[0].getAttribute('aria-checked'), 'false');
  assert.equal(h.languages[0].getAttribute('aria-label'), '영어'); h.languages[0].click();
  assert.deepEqual(h.trace, ['persist:' + languageKey, 'hub:before-language-change', 'assign']);
  assert.deepEqual(h.writes, [{ name: languageKey, value: 'en' }]);
  assert.equal(h.storage.get(themeKey), 'dark');
  assert.equal(h.navigation[0].target, 'https://infant83.io/AI_Tech_Review/en/?period=30d&lang=en#review-grid');
  const back = harness({ href: h.navigation[0].target, language: 'en', home: '../index.html', storage: h.storage });
  assert.deepEqual(back.navigation, []); assert.equal(back.languages[0].getAttribute('aria-checked'), 'true');
  assert.equal(back.languages[0].getAttribute('aria-label'), 'English'); back.languages[1].click();
  assert.equal(new URL(back.navigation[0].target).pathname, '/AI_Tech_Review/');
  assert.equal(new URL(back.navigation[0].target).searchParams.get('lang'), 'ko');
  assert.ok(back.writes.every(write => write.name === languageKey));
});

test('existing combined preferences migrate independently without replacing a newer individual choice', () => {
  const legacy = JSON.stringify({ readerLanguage: 'en', readerTheme: 'dark' });
  const both = harness({ stored: legacy });
  assert.equal(both.storage.get(languageKey), 'en'); assert.equal(both.storage.get(themeKey), 'dark');
  assert.equal(both.root.dataset.theme, 'dark'); assert.equal(both.navigation[0].method, 'replace');
  const keepLanguage = harness({ stored: legacy, savedLanguage: 'ko' });
  assert.deepEqual(keepLanguage.writes, [{ name: themeKey, value: 'dark' }]); assert.deepEqual(keepLanguage.navigation, []);
  const keepTheme = harness({ stored: legacy, savedTheme: 'light' });
  assert.deepEqual(keepTheme.writes, [{ name: languageKey, value: 'en' }]); assert.equal(keepTheme.root.dataset.theme, 'light');
  const keepBoth = harness({ stored: legacy, savedLanguage: 'ko', savedTheme: 'light' });
  assert.deepEqual(keepBoth.writes, []); assert.ok(!keepBoth.reads.includes(legacyKey));
});

test('legacy device appearance becomes a one-time binary theme, then uses its independent saved value', () => {
  for (const osDark of [false, true]) {
    const h = harness({ osDark, stored: JSON.stringify({ readerTheme: 'system' }) });
    const expected = osDark ? 'dark' : 'light';
    assert.equal(h.root.dataset.theme, expected); assert.equal(h.storage.get(themeKey), expected);
    h.mediaChange(!osDark); assert.equal(h.root.dataset.theme, expected);
    const next = harness({ osDark: !osDark, storage: h.storage });
    assert.equal(next.root.dataset.theme, expected); assert.deepEqual(next.writes, []);
  }
  const unavailable = harness({ noMedia: true, stored: JSON.stringify({ readerTheme: 'system' }) });
  assert.equal(unavailable.root.dataset.theme, 'light');
});

test('saved English redirects only Korean hub entries while retaining query and anchor', () => {
  const h = harness({ href: 'https://infant83.io/AI_Tech_Review/?period=7d#topic-filter', savedLanguage: 'en', savedTheme: 'dark' });
  assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.navigation.length, 1);
  assert.equal(h.navigation[0].target, 'https://infant83.io/AI_Tech_Review/en/?period=7d&lang=en#topic-filter');
  assert.equal(h.languages[0].listeners.click, undefined, 'redirecting documents do not bind stale controls');
  for (const suffix of ['', 'index.html', '../AI_Tech_Review']) {
    const url = new URL(suffix, 'https://infant83.io/AI_Tech_Review/').href;
    const alias = harness({ href: url, savedLanguage: 'en' });
    assert.equal(new URL(alias.navigation[0].target).pathname, '/AI_Tech_Review/en/');
  }
});

test('explicit language URLs override saved language without changing the stored theme', () => {
  const ko = harness({ href: 'https://infant83.io/AI_Tech_Review/?lang=ko', savedLanguage: 'en', savedTheme: 'dark' });
  assert.deepEqual(ko.navigation, []); assert.equal(ko.languages[0].getAttribute('aria-checked'), 'false');
  assert.deepEqual(ko.writes, [{ name: languageKey, value: 'ko' }]); assert.equal(ko.storage.get(themeKey), 'dark');
  const en = harness({ href: 'https://infant83.io/AI_Tech_Review/?lang=en', savedTheme: 'dark' });
  assert.equal(new URL(en.navigation[0].target).pathname, '/AI_Tech_Review/en/');
  for (const suffix of ['en/', 'en/index.html']) {
    const direct = harness({ href: 'https://infant83.io/AI_Tech_Review/' + suffix, language: 'en', home: '../index.html', savedLanguage: 'ko' });
    assert.deepEqual(direct.navigation, []); assert.equal(direct.languages[0].getAttribute('aria-checked'), 'true');
  }
});

test('invalid stored fields are ignored independently and never replaced by legacy migration when present', () => {
  for (const stored of ['not json', 'null', '[]', '"en"', '{"readerLanguage":"fr","readerTheme":"red"}', ' '.repeat(1025)]) {
    const h = harness({ stored });
    assert.equal(h.root.dataset.theme, 'light'); assert.deepEqual(h.navigation, []); assert.equal(h.writes.length, 0);
    h.themes[0].click(); assert.equal(h.root.dataset.theme, 'dark');
  }
  const h = harness({ savedLanguage: 'https://evil.example/', savedTheme: 'red', stored: JSON.stringify({ readerLanguage: 'en', readerTheme: 'dark' }) });
  assert.equal(h.root.dataset.theme, 'light'); assert.deepEqual(h.navigation, []); assert.equal(h.writes.length, 0);
  h.languages[0].click(); assert.equal(new URL(h.navigation[0].target).origin, 'https://infant83.io');
});

test('blocked storage still changes theme and carries the language choice in the destination URL', () => {
  for (const access of [{ blocked: true }, { accessBlocked: true }, { writeBlocked: true }]) {
    const h = harness(access); h.themes[0].click();
    assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.status.textContent, '이번 방문에 적용했습니다.');
    h.languages[0].click(); assert.deepEqual(h.trace, ['hub:before-language-change', 'assign']);
    assert.equal(h.navigation[0].target, 'https://infant83.io/AI_Tech_Review/en/?lang=en');
    const arrived = harness({ ...access, href: h.navigation[0].target, language: 'en', home: '../index.html' });
    assert.deepEqual(arrived.navigation, []); assert.equal(arrived.languages[0].getAttribute('aria-checked'), 'true');
  }
});

test('foreign or invalid home links never apply state or create an open redirect', () => {
  for (const home of ['https://evil.example/AI_Tech_Review/', '//evil.example/', 'javascript:alert(1)', 'data:text/html,hello', 'https://[invalid']) {
    const h = harness({ home, initialTheme: 'sentinel', savedLanguage: 'en', savedTheme: 'dark' });
    assert.equal(h.root.dataset.theme, 'sentinel'); assert.equal(h.reads.length, 0); assert.equal(h.navigation.length, 0);
  }
  const query = harness({ href: 'https://infant83.io/AI_Tech_Review/?lang=https://evil.example/&next=https://evil.example/', savedLanguage: 'en' });
  assert.equal(new URL(query.navigation[0].target).origin, 'https://infant83.io');
  assert.equal(new URL(query.navigation[0].target).pathname, '/AI_Tech_Review/en/');
});

test('preferences never affect article, methods, unrelated paths, or documents without hub markers', () => {
  for (const href of ['https://infant83.io/AI_Tech_Review/reviews/sample/', 'https://infant83.io/AI_Tech_Review/methods/', 'https://infant83.io/unrelated/']) {
    const h = harness({ href, initialTheme: 'sentinel', savedLanguage: 'en', savedTheme: 'dark' });
    assert.equal(h.root.dataset.theme, 'sentinel'); assert.equal(h.reads.length, 0); assert.deepEqual(h.navigation, []);
  }
  for (const options of [{ language: null }, { language: 'fr' }, { home: null }]) {
    const h = harness({ ...options, initialTheme: 'sentinel' });
    assert.equal(h.root.dataset.theme, 'sentinel'); assert.equal(h.reads.length, 0);
  }
});

test('cross-tab theme updates refresh switches without navigating or rewriting the language preference', () => {
  const h = harness({ language: 'en', href: 'https://infant83.io/AI_Tech_Review/en/', home: '../index.html', savedLanguage: 'en' });
  h.storageChange('dark');
  assert.equal(h.root.dataset.theme, 'dark'); assert.equal(h.themes[0].getAttribute('aria-checked'), 'true');
  assert.equal(h.languages[0].getAttribute('aria-checked'), 'true'); assert.deepEqual(h.navigation, []); assert.deepEqual(h.writes, []);
  h.storageChange('ko', languageKey); h.themes[0].click();
  assert.equal(h.storage.get(languageKey), 'ko', 'a stale English page cannot overwrite a newer independent language choice');
  assert.deepEqual(h.writes, [{ name: themeKey, value: 'light' }]);
  h.storageChange('dark', themeKey, {}); assert.equal(h.root.dataset.theme, 'light', 'unrelated storage areas are ignored');
  h.storageChange('dark'); h.storageChange(null); assert.equal(h.root.dataset.theme, 'light');
  h.storageChange('dark'); h.storageChange(null, null); assert.equal(h.root.dataset.theme, 'light');
});

test('language changes after a theme change in another tab never restore an older theme', () => {
  const h = harness({ savedTheme: 'light' }); h.storageChange('dark'); h.languages[0].click();
  assert.equal(h.storage.get(themeKey), 'dark');
  assert.deepEqual(h.writes, [{ name: languageKey, value: 'en' }]);
});
