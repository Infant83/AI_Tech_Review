/* Run: NODE_PATH=<Playwright package directory> node --test this-file.cjs */
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const http = require('node:http');
const unitOnly = process.env.READER_UNIT_ONLY === '1';
const browserTest = unitOnly ? test.skip : test;
const chromium = unitOnly ? null : require('playwright').chromium;

const frontend = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(frontend, 'reader-engagement.js'), 'utf8');
const workerSource = fs.readFileSync(path.join(frontend, 'sw.js'), 'utf8');
const metricsSummary = (articleId = null) => ({ ok: true, since: '2026-10-25T00:00:00.000Z',
  site: { visitors: 42, todayVisitors: 7, opens: 98, shares: 8, copies: 4, activeSubscribers: 3, subscriptionRegistrations: 2, articleNotificationsSent: 6 },
  article: articleId ? { id: articleId, opens: 11, shares: 3, copies: 2 } : null });
let server, origin, browser;

before(async () => {
  if (unitOnly) return;
  server = http.createServer((request, response) => {
    if (request.url.endsWith('reader-engagement.js')) {
      response.writeHead(200, { 'content-type': 'text/javascript' }); return response.end(source);
    }
    if (request.url.endsWith('reader-engagement.css')) {
      response.writeHead(200, { 'content-type': 'text/css' }); return response.end(fs.readFileSync(path.join(frontend, 'reader-engagement.css')));
    }
    const english = request.url.includes('/en/');
    const config = { scope: '/AI_Tech_Review/', apiBase: 'https://api.infant83.io', article: {
      id: '2026-10-23_test', title: 'Test article', path: '/AI_Tech_Review/reviews/2026-10-23_test/'
    }};
    response.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    response.end(`<!doctype html><html lang="${english ? 'en' : 'ko'}"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Test review</title><link rel="stylesheet" href="/reader-engagement.css"><style>body{margin:18px;font:16px system-ui}main{max-width:980px;margin:auto}header{display:flex;gap:12px;flex-wrap:wrap}article{min-height:160px}</style></head><body><header><a href="/AI_Tech_Review/">AI Tech Review Letters</a><span class="topbar-links">Existing links</span></header><main><article><h1>기존 기사 제목</h1><p>기존 본문을 유지합니다.</p></article><footer>Existing footer</footer></main><script id="reader-engagement-config" type="application/json">${JSON.stringify(config)}</script><script src="/reader-engagement.js" defer></script></body></html>`);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  origin = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHROMIUM_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHROMIUM_CHANNEL } : {}) });
});
after(async () => {
  if (browser) await browser.close();
  if (server) await new Promise(resolve => server.close(resolve));
});

async function setup(options = {}) {
  const context = await browser.newContext({ viewport: { width: options.width || 390, height: options.height || 844 },
    userAgent: options.ios ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 Version/18.4 Mobile/15E148 Safari/604.1' : undefined });
  await context.addInitScript(({ standalone, permissionResult, shareMode }) => {
    window.__calls = [];
    window.__events = [];
    window.__permission = 'default';
    window.__localSubscription = null;
    const json = { endpoint: 'https://fcm.googleapis.com/fcm/send/test-endpoint', expirationTime: null, keys: { p256dh: 'test', auth: 'test' } };
    function subscription() { return { ...json, toJSON: () => json, unsubscribe: async () => { window.__events.push('unsubscribe'); window.__localSubscription = null; return true; } }; }
    window.PushManager = function () {};
    window.Notification = { get permission() { return window.__permission; }, requestPermission() {
      window.__events.push({ name: 'permission', active: navigator.userActivation.isActive });
      window.__permission = permissionResult; return Promise.resolve(permissionResult);
    }};
    Object.defineProperty(navigator, 'standalone', { value: standalone });
    Object.defineProperty(navigator, 'serviceWorker', { value: { register: async (url, settings) => {
      window.__events.push({ name: 'register', url, scope: settings.scope });
      return { active: {}, pushManager: { getSubscription: async () => window.__localSubscription,
        subscribe: async () => { window.__events.push('subscribe'); window.__localSubscription = subscription(); return window.__localSubscription; } } };
    }}});
    const realFetch = window.fetch;
    window.fetch = (url, init) => { window.__calls.push({ url, credentials: init.credentials, method: init.method, body: init.body, headers: init.headers }); window.__events.push('fetch:' + new URL(url).pathname); return realFetch(url, init); };
    Object.defineProperty(navigator, 'clipboard', { value: { writeText: async value => { window.__copied = value; } } });
    Object.defineProperty(navigator, 'share', { value: shareMode === 'cancel' ? async () => { throw new DOMException('Canceled', 'AbortError'); } : undefined });
  }, { standalone: options.standalone !== false, permissionResult: options.permissionResult || 'granted', shareMode: options.shareMode });
  const data = { subscription: null, topics: ['review', 'lecture'], liked: false, count: 0, testCount: 0 };
  await context.route('https://api.infant83.io/**', async route => {
    const request = route.request(), url = new URL(request.url()), method = request.method();
    const headers = { 'access-control-allow-origin': origin, 'access-control-allow-credentials': 'true', 'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS', 'access-control-allow-headers': 'content-type,accept', 'content-type': 'application/json' };
    if (method === 'OPTIONS') return route.fulfill({ status: 204, headers });
    let result = { ok: true }, status = 200;
    if (url.pathname === '/v1/metrics' || url.pathname === '/v1/metrics/events') result = metricsSummary(url.pathname.endsWith('/events') ? request.postDataJSON().articleId : url.searchParams.get('articleId'));
    else if (url.pathname === '/v1/config') result.vapidPublicKey = 'B' + 'A'.repeat(86);
    else if (url.pathname === '/v1/devices') result.deviceId = 'device-for-test';
    else if (url.pathname.endsWith('/like')) {
      if (method === 'PUT') { data.liked = request.postDataJSON().liked; data.count = data.liked ? 1 : 0; }
      result = { ok: true, count: data.count, liked: data.liked };
    } else if (url.pathname === '/v1/subscription/test') { data.testCount += 1; result.queued = true; }
    else if (url.pathname === '/v1/subscription') {
      if (method === 'PUT') { const body = request.postDataJSON(); data.subscription = body.subscription; data.topics = body.topics; }
      if (method === 'DELETE') data.subscription = null;
      result = { ok: true, subscribed: Boolean(data.subscription), subscription: data.subscription, topics: data.topics };
    } else { status = 404; result = { ok: false, error: 'missing' }; }
    await route.fulfill({ status, headers, body: JSON.stringify(result) });
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(origin + '/AI_Tech_Review/reviews/2026-10-23_test/' + (options.english ? 'en/' : ''));
  await page.waitForFunction(() => window.__calls.some(call => call.url.endsWith('/v1/subscription')));
  return { page, context, data, errors };
}

browserTest('iPhone browser gives real installation instructions and never requests permission automatically', async () => {
  const { page, context, errors } = await setup({ ios: true, standalone: false });
  await page.getByRole('button', { name: '새 글 알림', exact: true }).first().click();
  await page.getByRole('heading', { name: '테크리뷰를 홈 화면에 추가해 주세요' }).waitFor();
  assert.equal(await page.getByRole('button', { name: '새 글 알림 받기', exact: true }).count(), 0);
  assert.deepEqual(await page.evaluate(() => window.__events.filter(event => event.name === 'permission')), []);
  assert.deepEqual(errors, []);
  await context.close();
});

browserTest('subscribe follows a direct gesture; settings, test and unsubscribe work; resubscribe preserves granted permission', async () => {
  const { page, context, data, errors } = await setup({ ios: true });
  const opener = page.getByRole('button', { name: '새 글 알림', exact: true }).first();
  await opener.click();
  const subscribe = page.getByRole('button', { name: '새 글 알림 받기', exact: true });
  await subscribe.waitFor();
  await page.waitForFunction(() => !document.querySelector('[data-reader-action="subscribe"]').disabled);
  await subscribe.click();
  await page.getByRole('button', { name: '이 기기로 테스트 알림 보내기' }).waitFor();
  const events = await page.evaluate(() => window.__events);
  assert.equal(events.find(event => event.name === 'permission').active, true);
  assert.ok(events.findIndex(event => event.name === 'permission') < events.indexOf('fetch:/v1/devices'));
  await page.getByRole('checkbox', { name: '렉처 노트' }).uncheck();
  await page.getByRole('button', { name: '설정 저장' }).click();
  await page.getByText('알림 설정을 저장했어요.', { exact: true }).waitFor();
  assert.deepEqual(data.topics, ['review']);
  await page.getByRole('button', { name: '이 기기로 테스트 알림 보내기' }).click();
  await page.getByText(/테스트 알림 발송을 접수했어요/).waitFor();
  assert.equal(data.testCount, 1);
  await page.getByRole('button', { name: '이 기기에서 구독 해제' }).click();
  await page.getByText('이 기기의 새 글 알림을 해제했어요.', { exact: true }).waitFor();
  assert.equal(data.subscription, null);
  await page.getByRole('button', { name: '새 글 알림 받기', exact: true }).click();
  await page.getByRole('button', { name: '이 기기로 테스트 알림 보내기' }).waitFor();
  assert.equal(await page.evaluate(() => window.__events.filter(event => event.name === 'permission').length), 1);
  const calls = await page.evaluate(() => window.__calls);
  assert.ok(calls.every(call => call.credentials === (new URL(call.url).pathname.startsWith('/v1/metrics') ? 'omit' : 'include')));
  assert.ok(calls.every(call => !Object.keys(call.headers).some(key => key.toLowerCase() === 'authorization')));
  await page.getByRole('button', { name: '닫기', exact: true }).click();
  assert.equal(await page.evaluate(() => document.activeElement.dataset.readerAction), 'open');
  assert.deepEqual(errors, []);
  await context.close();
});

browserTest('denied permission shows settings and never creates a subscription', async () => {
  const { page, context, data } = await setup({ ios: true, permissionResult: 'denied' });
  await page.getByRole('button', { name: '새 글 알림', exact: true }).first().click();
  await page.waitForFunction(() => !document.querySelector('[data-reader-action="subscribe"]').disabled);
  await page.getByRole('button', { name: '새 글 알림 받기', exact: true }).click();
  await page.getByText(/iPhone 설정 → 알림/).waitFor();
  assert.equal(data.subscription, null);
  assert.equal(await page.evaluate(() => window.__calls.filter(call => call.url.endsWith('/v1/devices')).length), 0);
  await page.getByRole('button', { name: '다시 확인' }).click();
  assert.equal(await page.evaluate(() => window.__events.filter(event => event.name === 'permission').length), 1);
  await context.close();
});

browserTest('likes toggle from server response; share fallback keeps the English article path; cancel is silent', async () => {
  const { page, context, data } = await setup({ english: true });
  await page.getByRole('button', { name: 'Like', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('[data-reader-action="like"]').getAttribute('aria-pressed') === 'true');
  assert.equal(data.count, 1);
  await page.getByRole('button', { name: 'Unlike', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('[data-reader-action="like"]').getAttribute('aria-pressed') === 'false');
  assert.equal(data.count, 0);
  await page.getByRole('button', { name: 'Share', exact: true }).click();
  await page.getByText('Article link copied.', { exact: true }).waitFor();
  assert.equal(await page.evaluate(() => window.__copied), 'https://infant83.io/AI_Tech_Review/reviews/2026-10-23_test/en/');
  await context.close();
  const canceled = await setup({ english: true, shareMode: 'cancel' });
  await canceled.page.getByRole('button', { name: 'Share', exact: true }).click();
  assert.equal(await canceled.page.locator('.atr-reader-status').textContent(), '');
  await canceled.context.close();
});

for (const width of [320, 390, 736, 1280]) browserTest(`dialog stays inside viewport, focus and controls work at ${width}px`, async () => {
  const { page, context } = await setup({ width, height: 736 });
  await page.getByRole('button', { name: '새 글 알림', exact: true }).first().click();
  const bounds = await page.locator('dialog').boundingBox();
  assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= width + 1);
  assert.ok(bounds.y >= 0 && bounds.y + bounds.height <= 737);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  for (const button of await page.locator('dialog button').all()) {
    const box = await button.boundingBox();
    assert.ok(box.height >= 44, 'touch target must be at least 44px high');
  }
  await page.keyboard.press('Shift+Tab');
  assert.equal(await page.evaluate(() => document.querySelector('dialog').contains(document.activeElement)), true);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('dialog').evaluate(element => element.open), false);
  await context.close();
});

function workerHarness() {
  const handlers = {}, shown = [], opened = [];
  const self = { registration: { scope: 'https://infant83.io/AI_Tech_Review/', showNotification: async (title, options) => shown.push({ title, options }) },
    addEventListener: (name, handler) => { handlers[name] = handler; },
    clients: { matchAll: async () => [], openWindow: async url => opened.push(url) } };
  vm.runInNewContext(workerSource, { self, URL });
  return { self, handlers, shown, opened };
}
function frontendHarness(options = {}) {
  const calls = [], events = [], channels = [], storage = options.storage || new Map();
  let permission = 'default', subscribeCount = 0, unsubscribeCount = 0, resolvePermission;
  const subscriptionJSON = { endpoint: 'https://push.example/device', keys: { p256dh: 'public', auth: 'auth' } };
  const subscription = { endpoint: subscriptionJSON.endpoint, toJSON: () => subscriptionJSON, unsubscribe: async () => {
    unsubscribeCount++; if (options.browserRemovalFails) throw Error('browser removal failed'); return true;
  }};
  const config = { apiBase: options.apiBase || 'https://api.infant83.io', scope: '/AI_Tech_Review/', article: options.article || null };
  let document;
  class MiniNode {
    constructor(tag) { this.tagName = tag.toUpperCase(); this.dataset = {}; this.style = {}; this.children = []; this.attributes = {}; this.listeners = {}; this._text = ''; this.classList = { add: (...names) => { this.className = [this.className || '', ...names].join(' '); } }; }
    set textContent(value) { this._text = String(value); this.children = []; }
    get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
    set innerHTML(_) { throw Error('HTML injection is forbidden in reader controls'); }
    appendChild(child) { child.parentNode = this; this.children.push(child); return child; }
    replaceChildren(...children) { this._text = ''; this.children = []; children.forEach(child => this.appendChild(child)); }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    removeAttribute(name) { delete this.attributes[name]; }
    getAttribute(name) { return this.attributes[name] || null; }
    addEventListener(name, listener) { (this.listeners[name] ||= []).push(listener); }
    insertAdjacentElement(position, element) { (this.adjacent ||= []).push({ position, element }); }
    focus() { document.activeElement = this; }
    closest() { return this.tagName === 'BUTTON' && this.dataset.readerAction ? this : this.parentNode && this.parentNode.closest ? this.parentNode.closest() : null; }
    querySelectorAll(selector) {
      const all = [];
      function walk(element) { for (const child of element.children || []) { all.push(child); walk(child); } }
      walk(this);
      return all.filter(element => {
        if (!element.tagName) return false;
        if (selector === '[data-reader-action]') return Boolean(element.dataset.readerAction);
        if (selector === '[data-reader-topic]') return Boolean(element.dataset.readerTopic);
        if (selector === '[data-reader-guide]') return Boolean(element.dataset.readerGuide);
        if (selector === 'input[data-reader-topic]:checked') return element.tagName === 'INPUT' && element.dataset.readerTopic && element.checked;
        return selector.split(',').some(part => {
          const tag = part.match(/^([a-z]+)/);
          return tag && element.tagName === tag[1].toUpperCase() && (!part.includes(':disabled') || !element.disabled);
        });
      });
    }
    getClientRects() {
      let ancestor = this.parentNode;
      while (ancestor) {
        if (ancestor.tagName === 'DETAILS' && !ancestor.open && !(this.tagName === 'SUMMARY' && this.parentNode === ancestor)) return [];
        ancestor = ancestor.parentNode;
      }
      return [{}];
    }
    showModal() { this.open = true; }
    close() { this.open = false; (this.listeners.close || []).forEach(listener => listener()); }
  }
  const main = new MiniNode('main'), articleElement = new MiniNode('article'), header = new MiniNode('header'), topbar = new MiniNode('span');
  document = { querySelector: selector => {
    if (selector.includes(',')) return options.article ? main : header; // CSS lists use document order, not selector order.
    return ({ 'main article': articleElement, 'article:not(.review-card)': articleElement, main,
      '.topbar-links': options.noHeader || options.headerOnly ? null : topbar,
      'body > header': options.noHeader ? null : header, header: options.noHeader ? null : header })[selector] || null;
  }, getElementById: () => ({ tagName: 'SCRIPT', type: 'application/json', textContent: JSON.stringify(config) }),
  documentElement: { lang: options.english ? 'en' : 'ko', style: {} }, currentScript: null, body: new MiniNode('body'), title: 'Article',
  visibilityState: options.visibility || 'visible', hasFocus() { return this.focused !== false; }, focused: options.focused !== false,
  createElement: tag => new MiniNode(tag), createTextNode: value => ({ textContent: value }), contains: () => true };
  const context = { URL, Intl, Uint8Array, Array, Promise, JSON, String, Number, Boolean, Error,
    location: { protocol: 'https:', origin: 'https://infant83.io', pathname: options.pathname || '/AI_Tech_Review/', hostname: 'infant83.io' }, document,
    navigator: { userAgent: options.userAgent || '', standalone: options.standalone !== false, serviceWorker: {} },
    Notification: { get permission() { return permission; }, requestPermission: () => {
      events.push('permission');
      if (options.permissionPending) return new Promise(resolve => { resolvePermission = resolve; });
      permission = 'granted'; return Promise.resolve('granted');
    } },
    PushManager: function () {}, isSecureContext: true,
    atob: value => Buffer.from(value, 'base64').toString('binary'),
    setTimeout: options.clock ? options.clock.setTimeout : setTimeout,
    clearTimeout: options.clock ? options.clock.clearTimeout : clearTimeout,
    fetch: async (url, init) => {
      calls.push({ url, init }); events.push(new URL(url).pathname);
      const status = options.responseStatus ? options.responseStatus(url, init, calls) : 200;
      return { ok: status >= 200 && status < 300, status, json: async () => options.responseJSON ? options.responseJSON(url, init) : ({ ok: true, subscription: subscriptionJSON }) };
    }
  };
  context.navigator.clipboard = { writeText: async value => { context.copied = value; } };
  if (options.metricsStorage) {
    context.localStorage = { getItem: key => { if (options.storageBlocked) throw Error('blocked'); return storage.get(key) || null; },
      setItem: (key, value) => { if (options.storageBlocked) throw Error('blocked'); storage.set(key, value); } };
    let uuid = 0;
    context.crypto = { randomUUID: () => '00000000-0000-4000-8000-' + String(++uuid).padStart(12, '0') };
  }
  context.navigator.globalPrivacyControl = options.gpc === true;
  context.navigator.doNotTrack = options.dnt || null;
  context.scrollY = 1780;
  context.scrollX = 0;
  context.scrollTo = (x, y) => { context.restoredScroll = [x, y]; };
  context.self = context;
  context.top = options.iframe ? {} : context;
  if (options.messageChannel) context.MessageChannel = class {
    constructor() {
      this.port1 = { onmessage: null, onmessageerror: null, close() {}, start() {} };
      this.port2 = { postMessage: data => queueMicrotask(() => { if (this.port1.onmessage) this.port1.onmessage({ data }); }), close() {} };
      channels.push(this);
    }
  };
  if (options.unsupported) { delete context.PushManager; delete context.Notification; delete context.navigator.serviceWorker; }
  context.window = context;
  const initializer = source.lastIndexOf('\n  mount();');
  assert.ok(initializer > 0, 'test harness must suppress automatic DOM mounting');
  const testSource = source.slice(0, initializer) + '\n  window.__readerTest = { state: state, subscribe: subscribeFromGesture, unsubscribe: unsubscribe, ensureDevice: ensureDevice, mount: mount, open: openDialog, close: closeDialog, like: like, share: share, copy: copyLink, loadLikes: loadLikes, updateButtons: updateButtons, prepare: prepare, render: renderDialog, deviceGuide: deviceGuide, offerInstall: offerInstall, installedApp: installedApp, install: installFromGesture, refreshHistory: refreshNotificationState, sanitizeHistory: notificationList, notificationHint: notificationHint, action: handleAction, startMetrics: startMetrics, refreshMetrics: refreshMetrics, recordMetrics: recordMetrics, applyMetrics: applyMetrics, metricsRoot: function () { return metricsRoot; }, metricsVisitor: metricsVisitorId };\n})();';
  vm.runInNewContext(testSource, context);
  const api = context.__readerTest;
  api.state.preparing = false;
  api.state.key = 'B' + 'A'.repeat(86);
  let current = options.existingSubscription ? subscription : null;
  api.state.registration = { active: options.notificationWorker, pushManager: { getSubscription: async () => current,
    subscribe: async () => { subscribeCount++; current = subscription; return subscription; } } };
  return { api, calls, events, channels, storage, subscription, subscriptionJSON, context, document, main, articleElement, topbar, header,
    releasePermission: value => { permission = value; if (resolvePermission) resolvePermission(value); },
    counts: () => ({ subscribeCount, unsubscribeCount }) };
}
function fakeClock() {
  let now = 0, next = 0;
  const timers = new Map();
  return {
    setTimeout: (callback, delay) => { const id = ++next; timers.set(id, { callback, at: now + delay }); return id; },
    clearTimeout: id => timers.delete(id),
    advance: milliseconds => {
      now += milliseconds;
      for (const [id, timer] of Array.from(timers.entries())) {
        if (timer.at <= now) { timers.delete(id); timer.callback(); }
      }
    }
  };
}
const flushPromises = () => new Promise(resolve => setImmediate(resolve));
const iphoneAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 Version/18.4 Mobile/15E148 Safari/604.1';
const macChromeAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/152.0.0.0 Safari/537.36';
const macSafariAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Version/26.0 Safari/605.1.15';
function modal(harness) { return harness.document.body.children.find(element => element.tagName === 'DIALOG'); }
function openModal(harness) { harness.api.mount(); harness.api.open(harness.topbar.children[0]); return modal(harness); }
function currentGuide(harness) { return modal(harness).querySelectorAll('details')[0]; }

test('iPhone browser shows three required installation steps and the real subscribe/test sequence without prompting', () => {
  const harness = frontendHarness({ userAgent: iphoneAgent, standalone: false });
  const dialog = openModal(harness);
  const guide = currentGuide(harness);
  assert.equal(harness.api.deviceGuide(), 'iphone');
  assert.equal(guide.open, true);
  assert.equal(guide.querySelectorAll('li').length, 3);
  assert.match(guide.textContent, /공유 메뉴/);
  assert.match(guide.textContent, /‘홈 화면에 추가’/);
  assert.match(guide.textContent, /이미 같은 주소의 웹앱 아이콘이 있으면/);
  assert.match(guide.textContent, /iOS ‘허용’/);
  assert.match(guide.textContent, /테스트 알림 보내기/);
  assert.equal(dialog.querySelectorAll('[data-reader-action]').some(element => element.dataset.readerAction === 'subscribe'), false);
  assert.equal(harness.events.filter(event => event === 'permission').length, 0);
});
test('installed iPhone web apps show subscription help without repeating installation instructions', async () => {
  const harness = frontendHarness({ userAgent: iphoneAgent });
  openModal(harness);
  assert.match(modal(harness).textContent, /홈 화면 앱으로 열었어요/);
  assert.doesNotMatch(currentGuide(harness).textContent, /‘홈 화면에 추가’/);
  await harness.context.Notification.requestPermission();
  harness.api.state.localSubscription = harness.subscription;
  harness.api.state.serverSubscription = harness.subscriptionJSON;
  harness.api.render();
  assert.match(currentGuide(harness).textContent, /이미 이 기기에서 새 글 알림/);
  assert.ok(currentGuide(harness).querySelectorAll('summary').length, 'subscribed readers can still discover the guide');
});
test('Mac Chrome and Safari default to matching optional-install and OS notification instructions', () => {
  for (const [agent, expected, menu, application] of [[macChromeAgent, 'mac-chrome', /전송, 저장 및 공유/, /Google Chrome/], [macSafariAgent, 'mac-safari', /파일 → Dock에 추가/, /Safari/]]) {
    const harness = frontendHarness({ userAgent: agent, standalone: false });
    const dialog = openModal(harness);
    assert.equal(harness.api.deviceGuide(), expected);
    assert.match(dialog.textContent, /일반 브라우저 탭에서도 알림/);
    assert.match(currentGuide(harness).textContent, menu);
    assert.match(currentGuide(harness).textContent, application);
    assert.match(currentGuide(harness).textContent, /이미 이 주소의 앱을 설치했다면 기존 Dock/);
    assert.match(currentGuide(harness).textContent, /날짜·시간/);
    assert.match(currentGuide(harness).textContent, /집중 모드/);
    assert.equal(dialog.querySelectorAll('[data-reader-action]').some(element => element.dataset.readerAction === 'install-app'), false);
    assert.equal(harness.events.length, 0);
  }
});
test('installed Mac apps do not ask the reader to install again', () => {
  const harness = frontendHarness({ userAgent: macChromeAgent });
  openModal(harness);
  assert.match(modal(harness).textContent, /설치한 웹앱으로 열었어요/);
  assert.doesNotMatch(currentGuide(harness).textContent, /전송, 저장 및 공유|이전 설치 여부/);
  assert.match(currentGuide(harness).textContent, /추가 macOS 권한/);
});
test('guide choice, disclosure state and select focus survive a full modal render', () => {
  const harness = frontendHarness({ userAgent: macChromeAgent, standalone: false });
  const dialog = openModal(harness);
  const previous = currentGuide(harness);
  previous.open = true;
  previous.listeners.toggle[0]();
  const select = previous.querySelectorAll('select')[0];
  select.value = 'iphone'; select.focus();
  dialog.listeners.change[0]({ target: select });
  assert.equal(harness.api.state.guideDevice, 'iphone');
  assert.equal(currentGuide(harness).open, true);
  assert.equal(harness.document.activeElement.dataset.readerGuide, 'device');
  assert.equal(harness.document.activeElement.value, 'iphone');
  previous.open = false; previous.listeners.toggle[0]();
  assert.equal(harness.api.state.guideOpen, true, 'removed disclosure events must not overwrite the current state');
  harness.api.render();
  assert.equal(currentGuide(harness).querySelectorAll('select')[0].value, 'iphone');
  assert.equal(currentGuide(harness).open, true);
  currentGuide(harness).open = false; currentGuide(harness).listeners.toggle[0]();
  harness.api.render();
  assert.equal(currentGuide(harness).open, false);
});
test('focus trap includes the guide summary/select and skips hidden closed-details controls', () => {
  const harness = frontendHarness({ userAgent: macChromeAgent, standalone: false });
  const dialog = openModal(harness);
  const summary = currentGuide(harness).querySelectorAll('summary')[0];
  summary.focus();
  let prevented = false;
  dialog.listeners.keydown[0]({ key: 'Tab', shiftKey: false, preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(harness.document.activeElement.dataset.readerAction, 'close');
  currentGuide(harness).open = true;
  dialog.listeners.keydown[0]({ key: 'Tab', shiftKey: true, preventDefault() {} });
  assert.equal(harness.document.activeElement.dataset.readerGuide, 'device');
});
test('a disclosure opened just before an asynchronous render keeps its native open state', () => {
  const harness = frontendHarness({ userAgent: macChromeAgent, standalone: false });
  openModal(harness);
  currentGuide(harness).open = true; // The browser's queued toggle event has not fired yet.
  harness.api.render();
  assert.equal(currentGuide(harness).open, true);
});
test('a real install offer is optional and prompts only after the explicit install action', async () => {
  const harness = frontendHarness({ userAgent: macChromeAgent, standalone: false });
  openModal(harness);
  let prompts = 0, prevented = 0;
  const offer = { preventDefault() { prevented++; }, prompt() { prompts++; return Promise.resolve(); }, userChoice: Promise.resolve({ outcome: 'accepted' }) };
  harness.api.offerInstall(offer);
  assert.equal(prevented, 1);
  assert.equal(prompts, 0);
  assert.ok(currentGuide(harness).querySelectorAll('[data-reader-action]').some(element => element.dataset.readerAction === 'install-app'));
  await harness.api.install();
  await harness.api.install();
  assert.equal(prompts, 1);
  assert.equal(harness.events.filter(event => event === 'permission').length, 0);
  assert.match(harness.api.state.feedback, /알림 허용은 별도 단계/);
  harness.api.installedApp();
  harness.api.offerInstall(offer);
  await harness.api.install();
  assert.equal(prompts, 1, 'installed apps must not offer installation again');
});
test('English guide text uses the matching browser and preserves optional installation wording', () => {
  const harness = frontendHarness({ userAgent: macSafariAgent, standalone: false, english: true });
  openModal(harness);
  assert.match(modal(harness).textContent, /Installing an app is optional/);
  assert.match(currentGuide(harness).textContent, /File → Add to Dock/);
  assert.match(currentGuide(harness).textContent, /Notification Center/);
});
function historyRecord(id, extra = {}) {
  return { id, title: 'New article ' + id, url: 'https://infant83.io/AI_Tech_Review/reviews/' + id + '/', receivedAt: 1792893600000, ...extra };
}
function replyingWorker(records, count = 0) {
  const worker = { requests: 0, postMessage(message, ports) {
    worker.requests++;
    assert.equal(message.type, 'atr-reader-notification-state');
    ports[0].postMessage({ ok: true, count, notifications: records });
  }};
  return worker;
}
test('recent alert records are bounded, deduplicated and validate current-origin scoped URLs and received timestamps', () => {
  const harness = frontendHarness();
  const records = harness.api.sanitizeHistory({ ok: true, count: 3, notifications: [
    historyRecord('valid', { title: '<img src=x onerror=alert(1)>', url: '/AI_Tech_Review/reviews/valid/en/?x=1#part' }),
    historyRecord('valid', { title: 'Duplicate must not replace first' }),
    historyRecord('foreign', { url: 'https://evil.example/article' }),
    historyRecord('outside', { url: 'https://infant83.io/other/' }),
    historyRecord('prefix', { url: 'https://infant83.io/AI_Tech_Review-other/' }),
    historyRecord('script', { url: 'javascript:alert(1)' }),
    historyRecord('userinfo', { url: 'https://user:secret@infant83.io/AI_Tech_Review/' }),
    historyRecord('bad-time', { receivedAt: '2026-10-25' }),
    historyRecord('negative-time', { receivedAt: -1 }),
    historyRecord('object-title', { title: { toString: null } })
  ] });
  assert.equal(records.length, 1);
  assert.equal(records[0].title, '<img src=x onerror=alert(1)>');
  assert.equal(records[0].url, 'https://infant83.io/AI_Tech_Review/reviews/valid/en/?x=1#part');
  assert.equal(harness.api.sanitizeHistory({ ok: true, count: -1, notifications: [] }), null);
  assert.equal(harness.api.sanitizeHistory({ ok: true, count: 0, notifications: {} }), null);
  assert.equal(harness.api.sanitizeHistory({ ok: false, count: 0, notifications: [] }), null);
  assert.equal(harness.api.sanitizeHistory({ ok: true, count: 0, notifications: Array.from({ length: 30 }, (_, i) => historyRecord('a' + i)) }).length, 20);
});
test('recent alerts appear before help with received times, safe title text and at most twenty expandable records', async () => {
  const worker = replyingWorker(Array.from({ length: 25 }, (_, i) => historyRecord('r' + i, i === 0 ? { title: '<script>literal title</script>' } : {})));
  const harness = frontendHarness({ messageChannel: true, notificationWorker: worker });
  const dialog = openModal(harness);
  await harness.api.refreshHistory(false);
  const recent = dialog.querySelectorAll('section').find(element => element.className === 'atr-reader-recent');
  assert.ok(recent);
  assert.equal(recent.querySelectorAll('li').length, 5);
  assert.equal(recent.querySelectorAll('a')[0].textContent, '<script>literal title</script>');
  assert.match(recent.querySelectorAll('time')[0].textContent, /^받은 시각/);
  assert.equal(recent.querySelectorAll('time')[0].dateTime, new Date(1792893600000).toISOString());
  assert.ok(recent.parentNode.children.indexOf(recent) < recent.parentNode.children.indexOf(currentGuide(harness)));
  for (let i = 0; i < 3; i++) {
    const more = dialog.querySelectorAll('[data-reader-action]').find(element => element.dataset.readerAction === 'recent-more');
    more.focus(); harness.api.action({ target: more });
  }
  const expanded = dialog.querySelectorAll('section').find(element => element.className === 'atr-reader-recent');
  assert.equal(expanded.querySelectorAll('li').length, 20);
  assert.equal(harness.document.activeElement.id, 'atr-reader-recent-title');
  assert.equal(harness.api.state.notificationHistory.length, 20);
  assert.equal(harness.api.state.historyCount, 0);
});
test('new subscribers receive an empty recent-alert list without fetching or inventing old publications', async () => {
  const worker = replyingWorker([]);
  const harness = frontendHarness({ messageChannel: true, notificationWorker: worker });
  openModal(harness);
  await harness.api.refreshHistory(false);
  assert.match(modal(harness).textContent, /저장된 새 글 알림이 아직 없어요/);
  assert.match(modal(harness).textContent, /앞으로 도착하는 새 글 알림을 여기에/);
  assert.equal(harness.calls.length, 0);
  assert.equal(harness.api.state.notificationHistory.length, 0);
});
test('an old worker timeout preserves alert controls and a late response cannot overwrite a newer result', async () => {
  const clock = fakeClock();
  const oldWorker = { postMessage() {} };
  const harness = frontendHarness({ clock, messageChannel: true, notificationWorker: oldWorker });
  const waiting = harness.api.refreshHistory(true);
  const late = harness.channels[0].port1.onmessage;
  clock.advance(4000);
  await waiting;
  assert.equal(harness.api.state.historyReady, false);
  assert.equal(harness.api.state.configError, false);
  assert.equal(harness.api.state.registrationError, false);
  assert.equal(harness.api.state.busy, false);
  harness.api.state.registration.active = replyingWorker([historyRecord('new')]);
  await harness.api.refreshHistory(true);
  late({ data: { ok: true, count: 0, notifications: [historyRecord('old')] } });
  await flushPromises();
  assert.equal(harness.api.state.notificationHistory[0].id, 'new');
});
test('history requests are serialized across a controller change and stale worker data is ignored', async () => {
  let oldPort;
  const oldWorker = { requests: 0, postMessage(message, ports) { oldWorker.requests++; oldPort = ports[0]; } };
  const nextWorker = replyingWorker([historyRecord('current')]);
  const harness = frontendHarness({ messageChannel: true, notificationWorker: oldWorker });
  const initial = harness.api.refreshHistory(true);
  harness.context.navigator.serviceWorker.controller = nextWorker;
  harness.api.refreshHistory(true);
  assert.equal(nextWorker.requests, 0, 'the replacement request must wait for the earlier request to finish');
  oldPort.postMessage({ ok: true, count: 0, notifications: [historyRecord('stale')] });
  await initial;
  await flushPromises();
  assert.equal(oldWorker.requests, 1);
  assert.equal(nextWorker.requests, 1);
  assert.equal(harness.api.state.notificationHistory[0].id, 'current');
});
test('hidden, unfocused and framed documents do not send automatic notification confirmation requests', async () => {
  const worker = replyingWorker([historyRecord('visible')], 2);
  const harness = frontendHarness({ messageChannel: true, notificationWorker: worker, visibility: 'hidden' });
  await harness.api.refreshHistory(true);
  harness.document.visibilityState = 'visible'; harness.document.focused = false;
  await harness.api.refreshHistory(true);
  harness.document.focused = true; harness.context.top = {};
  await harness.api.refreshHistory(true);
  assert.equal(worker.requests, 0);
  harness.context.top = harness.context.self;
  await harness.api.refreshHistory(true);
  assert.equal(worker.requests, 1);
  assert.equal(harness.api.state.historyCount, 2, 'a worker may return a nonzero count while OS focus metadata catches up');
  assert.equal(harness.api.state.notificationHistory[0].id, 'visible');
});
test('only the current scoped worker hint refreshes history, and hidden hints wait until foreground', async () => {
  const worker = replyingWorker([historyRecord('hint')]);
  const harness = frontendHarness({ messageChannel: true, notificationWorker: worker, visibility: 'hidden' });
  harness.api.notificationHint({ data: { type: 'atr-reader-notifications-changed' }, source: { scriptURL: 'https://evil.example/sw.js' } });
  harness.api.notificationHint({ data: { type: 'atr-reader-notifications-changed' }, source: { scriptURL: 'https://infant83.io/AI_Tech_Review/sw.js' } });
  assert.equal(worker.requests, 0);
  harness.document.visibilityState = 'visible';
  await harness.api.refreshHistory(false);
  assert.equal(worker.requests, 1);
  harness.api.notificationHint({ data: { type: 'atr-reader-notifications-changed' }, source: { scriptURL: 'https://infant83.io/AI_Tech_Review/sw.js' } });
  await flushPromises();
  assert.equal(worker.requests, 2, 'a valid new-alert hint bypasses the debounce window');
  harness.api.notificationHint({ data: { type: 'atr-reader-notifications-changed' }, source: { scriptURL: 'https://infant83.io/elsewhere/sw.js' } });
  assert.equal(worker.requests, 2);
});
test('ordinary dialog re-renders never clear notification state or bypass request debounce', async () => {
  const worker = replyingWorker([historyRecord('kept')]);
  const harness = frontendHarness({ messageChannel: true, notificationWorker: worker });
  openModal(harness);
  await harness.api.refreshHistory(false);
  harness.api.render(); harness.api.render();
  await harness.api.refreshHistory(false);
  assert.equal(worker.requests, 1);
  assert.equal(harness.api.state.notificationHistory[0].id, 'kept');
});

test('a pending permission request times out in 30 seconds and retries never duplicate the OS request', async () => {
  const clock = fakeClock();
  const harness = frontendHarness({ clock, permissionPending: true });
  const first = harness.api.subscribe();
  clock.advance(29999);
  await flushPromises();
  assert.equal(harness.api.state.busy, true);
  clock.advance(1);
  await first;
  assert.equal(harness.api.state.busy, false);
  assert.equal(harness.api.state.feedbackError, true);
  assert.match(harness.api.state.feedback, /권한 창이 응답하지 않았어요/);
  const retry = harness.api.subscribe();
  clock.advance(30000);
  await retry;
  assert.equal(harness.events.filter(event => event === 'permission').length, 1);
  harness.releasePermission('granted');
  await flushPromises();
  assert.equal(harness.calls.length, 0, 'a late permission result must not create a device or save a subscription');
  assert.equal(harness.api.state.serverSubscription, null);
  await harness.api.subscribe();
  assert.equal(harness.events.filter(event => event === 'permission').length, 1);
  assert.equal(harness.api.state.serverSubscription.endpoint, harness.subscription.endpoint);
});
test('a pending PushManager lookup times out in 25 seconds and retains one in-flight lookup', async () => {
  const clock = fakeClock();
  const harness = frontendHarness({ clock });
  let release, lookups = 0;
  const pending = new Promise(resolve => { release = resolve; });
  harness.api.state.registration.pushManager.getSubscription = () => { lookups++; return pending; };
  const first = harness.api.subscribe();
  await flushPromises();
  clock.advance(25000);
  await first;
  assert.equal(harness.api.state.busy, false);
  assert.match(harness.api.state.feedback, /알림 연결이 응답하지 않았어요/);
  const retry = harness.api.subscribe();
  await flushPromises();
  clock.advance(25000);
  await retry;
  assert.equal(lookups, 1);
  release(harness.subscription);
  await flushPromises();
  assert.equal(harness.api.state.localSubscription, null, 'a late lookup cannot report subscription success');
  assert.equal(harness.calls.filter(call => call.init.method === 'PUT').length, 0);
});
test('a pending PushManager subscribe times out without duplicates or a late server write', async () => {
  const clock = fakeClock();
  const harness = frontendHarness({ clock });
  let release, subscriptions = 0;
  const pending = new Promise(resolve => { release = resolve; });
  harness.api.state.registration.pushManager.subscribe = () => { subscriptions++; return pending; };
  const first = harness.api.subscribe();
  await flushPromises();
  clock.advance(25000);
  await first;
  assert.equal(harness.api.state.busy, false);
  const retry = harness.api.subscribe();
  await flushPromises();
  clock.advance(25000);
  await retry;
  assert.equal(subscriptions, 1);
  release(harness.subscription);
  await flushPromises();
  assert.equal(harness.api.state.serverSubscription, null);
  assert.equal(harness.calls.filter(call => call.init.method === 'PUT').length, 0);
  harness.api.state.registration.pushManager.getSubscription = async () => harness.subscription;
  await harness.api.subscribe();
  assert.equal(subscriptions, 1);
  assert.equal(harness.api.state.serverSubscription.endpoint, harness.subscription.endpoint);
});
test('a pending service worker registration restores preparation controls after 25 seconds', async () => {
  const clock = fakeClock();
  const harness = frontendHarness({ clock, responseJSON: url => url.endsWith('/v1/config')
    ? { ok: true, vapidPublicKey: 'B' + 'A'.repeat(86) } : { ok: true, subscription: null } });
  harness.context.navigator.serviceWorker.register = () => new Promise(() => {});
  const preparing = harness.api.prepare();
  await flushPromises();
  clock.advance(25000);
  await preparing;
  assert.equal(harness.api.state.preparing, false);
  assert.equal(harness.api.state.registrationError, true);
});
test('mount uses explicit header priority and inserts article controls immediately after the article', () => {
  const hub = frontendHarness();
  hub.api.mount();
  assert.equal(hub.topbar.children.length, 1);
  assert.equal(hub.topbar.children[0].dataset.readerAction, 'open');
  assert.equal(hub.header.children.length, 0);
  const article = frontendHarness({ article: { id: 'test-review', title: 'Review' } });
  article.api.mount();
  assert.equal(article.articleElement.adjacent[0].position, 'afterend');
  assert.equal(article.articleElement.adjacent[0].element.className, 'atr-reader-actions');
  assert.equal(article.main.children.length, 0);
  assert.equal(article.topbar.children.length, 1, 'long articles must also have a header alert button');
});
test('article header and footer alert buttons stay synchronized; layouts without a header keep footer only', async () => {
  const harness = frontendHarness({ article: { id: 'test-review', title: 'Review' } });
  harness.api.mount();
  const footerButton = harness.articleElement.adjacent[0].element.children.find(element => element.dataset && element.dataset.readerAction === 'open');
  const headerButton = harness.topbar.children[0];
  await harness.context.Notification.requestPermission();
  harness.api.state.localSubscription = harness.subscription;
  harness.api.state.serverSubscription = harness.subscriptionJSON;
  harness.api.updateButtons();
  assert.equal(headerButton.textContent, '알림 설정');
  assert.equal(footerButton.textContent, '알림 설정');
  for (const control of [headerButton, footerButton]) {
    assert.equal(control.getAttribute('aria-controls'), 'atr-reader-dialog');
    assert.equal(control.getAttribute('aria-haspopup'), 'dialog');
  }
  const noHeader = frontendHarness({ article: { id: 'test-review' }, noHeader: true });
  noHeader.api.mount();
  assert.equal(noHeader.topbar.children.length, 0);
  assert.equal(noHeader.header.children.length, 0);
  assert.ok(noHeader.articleElement.adjacent[0]);
  const plainHeader = frontendHarness({ article: { id: 'test-review' }, headerOnly: true });
  plainHeader.api.mount();
  assert.equal(plainHeader.header.children.length, 1);
});
test('article controls always include a direct copy button beside share and preserve the English URL', async () => {
  const harness = frontendHarness({ article: { id: 'test-review', title: 'Review' }, pathname: '/AI_Tech_Review/reviews/test-review/en/' });
  harness.api.mount();
  const controls = harness.articleElement.adjacent[0].element.children.filter(element => element.tagName === 'BUTTON');
  assert.deepEqual(controls.map(element => element.dataset.readerAction), ['like', 'share', 'copy', 'open']);
  await harness.api.copy();
  assert.equal(harness.context.copied, 'https://infant83.io/AI_Tech_Review/reviews/test-review/en/');
});
test('closing the modal restores original overflow, scroll position and opener focus', () => {
  const harness = frontendHarness();
  harness.api.mount();
  harness.document.body.style.overflow = 'auto';
  const opener = harness.topbar.children[0];
  harness.api.open(opener);
  assert.equal(harness.document.body.style.overflow, 'hidden');
  harness.api.close();
  assert.equal(harness.document.body.style.overflow, 'auto');
  assert.deepEqual(harness.context.restoredScroll, [0, 1780]);
  assert.equal(harness.document.activeElement, opener);
  assert.equal(opener.getAttribute('aria-expanded'), 'false');
});
test('likes and English sharing remain usable when web notifications are unsupported', async () => {
  const harness = frontendHarness({ article: { id: 'test-review', title: 'Review' }, unsupported: true,
    pathname: '/AI_Tech_Review/reviews/test-review/en/index.html',
    responseJSON: (url, init) => url.endsWith('/like') ? { ok: true, liked: JSON.parse(init.body).liked, count: 1 } : { ok: true } });
  await harness.api.like();
  assert.equal(harness.api.state.liked, true);
  assert.equal(harness.api.state.count, 1);
  await harness.api.share();
  assert.equal(harness.context.copied, 'https://infant83.io/AI_Tech_Review/reviews/test-review/en/');
});
test('rapid likes send only one mutation; retry remains idempotent after a failed response', async () => {
  let puts = 0;
  const harness = frontendHarness({ article: { id: 'test-review' }, responseStatus: (url, init) => {
    if (url.endsWith('/like') && init.method === 'PUT' && ++puts === 1) return 503;
    return 200;
  }, responseJSON: (url, init) => url.endsWith('/like') ? { ok: true, liked: JSON.parse(init.body).liked, count: 1 } : { ok: true } });
  await Promise.all([harness.api.like(), harness.api.like(), harness.api.like()]);
  assert.equal(puts, 1);
  assert.equal(harness.api.state.liked, false);
  await harness.api.like();
  const writes = harness.calls.filter(call => call.url.endsWith('/like'));
  assert.equal(writes.length, 2);
  assert.deepEqual(writes.map(call => JSON.parse(call.init.body).liked), [true, true]);
  assert.equal(harness.api.state.liked, true);
});
test('successful like loading clears its earlier retry error and rejects nonnumeric API counts', async () => {
  let gets = 0;
  const harness = frontendHarness({ article: { id: 'test-review' }, responseStatus: (url, init) => {
    if (url.endsWith('/like') && init.method === 'GET' && ++gets === 1) return 503;
    return 200;
  }, responseJSON: () => ({ ok: true, liked: false, count: '<img src=x onerror=alert(1)>', error: '<script>bad</script>' }) });
  harness.api.mount();
  const status = harness.articleElement.adjacent[0].element.children.find(element => element.className === 'atr-reader-status');
  await harness.api.loadLikes();
  assert.match(status.textContent, /불러올 수 없어요/);
  await harness.api.loadLikes();
  assert.equal(status.textContent, '');
  assert.equal(harness.api.state.count, 0);
});
test('a slow initial like response cannot overwrite a newer confirmed mutation', async () => {
  let releaseRead;
  const harness = frontendHarness({ article: { id: 'test-review' }, responseJSON: (url, init) => {
    if (url.endsWith('/like') && init.method === 'GET') return new Promise(resolve => { releaseRead = resolve; });
    return url.endsWith('/like') ? { ok: true, liked: true, count: 1 } : { ok: true };
  }});
  harness.api.mount();
  const read = harness.api.loadLikes();
  await new Promise(resolve => setImmediate(resolve));
  await harness.api.like();
  releaseRead({ ok: true, liked: false, count: 0 });
  await read;
  assert.equal(harness.api.state.liked, true);
  assert.equal(harness.api.state.count, 1);
});
test('API storage failure keeps the existing push subscription for a safe retry', async () => {
  let puts = 0;
  const harness = frontendHarness({ responseStatus: (url, init) => {
    if (url.endsWith('/v1/subscription') && init.method === 'PUT' && ++puts === 1) return 503;
    return 200;
  }});
  await harness.api.subscribe();
  assert.equal(harness.api.state.localSubscription, harness.subscription);
  assert.equal(harness.api.state.serverSubscription, null);
  assert.equal(harness.api.state.feedbackError, true);
  await harness.api.subscribe();
  assert.equal(harness.counts().subscribeCount, 1);
  assert.equal(harness.events.filter(event => event === 'permission').length, 1);
  assert.equal(harness.api.state.feedbackError, false);
  assert.ok(harness.events.indexOf('permission') < harness.events.indexOf('/v1/devices'));
});
test('a missing device cookie never pretends to save a subscription', async () => {
  const harness = frontendHarness({ responseStatus: (url, init) => url.endsWith('/v1/subscription') && init.method === 'PUT' ? 401 : 200 });
  await harness.api.subscribe();
  assert.equal(harness.api.state.serverSubscription, null);
  assert.equal(harness.api.state.feedbackError, true);
  assert.match(harness.api.state.feedback, /쿠키/);
});
test('unsubscribe server failures retain retry state and do not claim complete success', async () => {
  for (const status of [401, 503]) {
    const harness = frontendHarness({ responseStatus: () => status });
    harness.api.state.localSubscription = harness.subscription;
    harness.api.state.serverSubscription = harness.subscriptionJSON;
    await harness.api.unsubscribe();
    assert.equal(harness.api.state.localSubscription, null);
    assert.equal(harness.api.state.pendingServerDelete, true);
    assert.equal(harness.api.state.feedbackError, true);
    assert.match(harness.api.state.feedback, /서버 연결을 지우지 못했어요/);
  }
});
test('unsubscribe browser failure does not claim complete success after server removal', async () => {
  const harness = frontendHarness({ browserRemovalFails: true });
  harness.api.state.localSubscription = harness.subscription;
  harness.api.state.serverSubscription = harness.subscriptionJSON;
  await harness.api.unsubscribe();
  assert.equal(harness.api.state.serverSubscription, null);
  assert.equal(harness.api.state.localSubscription, harness.subscription);
  assert.equal(harness.api.state.feedbackError, true);
});
test('embedded configuration cannot redirect credentialed requests to a foreign host', async () => {
  const harness = frontendHarness({ apiBase: 'https://evil.example/collect' });
  await harness.api.ensureDevice();
  assert.equal(harness.calls[0].url, 'https://api.infant83.io/v1/devices');
  assert.equal(harness.calls[0].init.credentials, 'include');
  assert.equal(Object.keys(harness.calls[0].init.headers).some(key => key.toLowerCase() === 'authorization'), false);
});
test('service worker allows only same-origin in-scope notification links and always displays invalid payloads', async () => {
  const { handlers, shown } = workerHarness();
  for (const url of ['https://evil.example/phish', 'https://infant83.io/other/', 'javascript:alert(1)', '/AI_Tech_Review/../outside/']) {
    let promise;
    handlers.push({ data: { json: () => ({ title: '<script>no execution</script>', url, icon: 'https://evil.example/x.png' }) }, waitUntil: p => { promise = p; } });
    await promise;
    assert.equal(shown.at(-1).options.data.url, 'https://infant83.io/AI_Tech_Review/');
    assert.equal(shown.at(-1).options.icon, 'https://infant83.io/AI_Tech_Review/assets/apple-touch-icon.png');
  }
  let promise;
  handlers.push({ data: { json: () => { throw Error('invalid JSON'); } }, waitUntil: p => { promise = p; } });
  await promise;
  assert.equal(shown.at(-1).title, 'AI Tech Review Letters');
  handlers.push({ data: { json: () => ({ title: { toString: null }, body: { toString: null }, articleId: { toString: null } }) }, waitUntil: p => { promise = p; } });
  await promise;
  assert.equal(shown.at(-1).title, 'AI Tech Review Letters');
  assert.match(shown.at(-1).options.body, /New article published/);
  assert.equal(Object.hasOwn(handlers, 'fetch'), false, 'must not rewrite or cache article requests');
});
test('notification click opens the article and focuses an existing exact match', async () => {
  const harness = workerHarness();
  const url = 'https://infant83.io/AI_Tech_Review/reviews/example/';
  let promise, closed = 0;
  harness.handlers.notificationclick({ notification: { data: { url }, close: () => closed++ }, waitUntil: p => { promise = p; } });
  await promise;
  assert.equal(closed, 1);
  assert.deepEqual(harness.opened, [url]);
  let focused = 0;
  harness.self.clients.matchAll = async () => [{ url, focus: async () => focused++ }];
  harness.handlers.notificationclick({ notification: { data: { url }, close() {} }, waitUntil: p => { promise = p; } });
  await promise;
  assert.equal(focused, 1);
  assert.equal(harness.opened.length, 1);
  harness.self.clients.matchAll = async () => { throw Error('clients unavailable'); };
  harness.handlers.notificationclick({ notification: { data: { url }, close() {} }, waitUntil: p => { promise = p; } });
  await promise;
  assert.equal(harness.opened.length, 2);
});

test('public metrics use browser storage separately from auth and do not create a reader session', async () => {
  const harness = frontendHarness({ metricsStorage: true, article: { id: 'test-review' }, responseJSON: () => metricsSummary('test-review') });
  harness.api.mount();
  harness.api.startMetrics();
  await flushPromises();
  assert.equal(harness.calls.length, 1);
  const call = harness.calls[0], body = JSON.parse(call.init.body);
  assert.equal(call.url, 'https://api.infant83.io/v1/metrics/events');
  assert.equal(call.init.credentials, 'omit');
  assert.deepEqual(Object.keys(body).sort(), ['articleId', 'eventId', 'type', 'visitorId']);
  assert.equal(body.type, 'open');
  assert.equal(body.articleId, 'test-review');
  assert.match(body.visitorId, /^[a-f0-9-]{36}$/);
  assert.notEqual(body.eventId, body.visitorId);
  assert.equal(harness.storage.size, 1);
  assert.equal(harness.calls.some(value => value.url.includes('/v1/devices')), false);
  assert.equal(harness.api.metricsRoot().dataset.state, 'ready');
  assert.match(harness.api.metricsRoot().textContent, /이 브라우저는 브라우저 기준 방문·열람·공유 집계에 참여/);
  assert.match(harness.api.metricsRoot().textContent, /이 글 열람11/);
  assert.match(harness.api.metricsRoot().textContent, /공유·복사5/);
  assert.match(harness.api.metricsRoot().textContent, /방문 브라우저42/);
  harness.api.startMetrics();
  await flushPromises();
  assert.equal(harness.calls.length, 1, 'focus/pageshow must not count the same page again');
});
test('hidden and framed documents do not count or create an anonymous browser identifier', async () => {
  for (const options of [{ visibility: 'hidden' }, { iframe: true }]) {
    const harness = frontendHarness({ ...options, metricsStorage: true });
    harness.api.mount(); harness.api.startMetrics();
    await flushPromises();
    assert.equal(harness.calls.length, 0);
    assert.equal(harness.storage.size, 0);
    assert.doesNotMatch(harness.api.metricsRoot().textContent, /이 브라우저에서는 집계용 식별자를/);
    if (!options.iframe) {
      harness.document.visibilityState = 'visible';
      harness.api.startMetrics(); await flushPromises();
      assert.equal(JSON.parse(harness.calls[0].init.body).type, 'open');
    }
  }
});
test('privacy preferences and blocked storage use public totals without tracking or authentication cookies', async () => {
  for (const options of [{ gpc: true }, { dnt: '1' }, { dnt: 'yes' }, { storageBlocked: true }]) {
    const harness = frontendHarness({ ...options, metricsStorage: true, responseJSON: () => metricsSummary() });
    harness.api.mount(); harness.api.startMetrics();
    await flushPromises();
    assert.equal(harness.calls.length, 1);
    assert.equal(harness.calls[0].init.method, 'GET');
    assert.equal(harness.calls[0].init.credentials, 'omit');
    assert.equal(harness.calls[0].init.body, undefined);
    assert.equal(harness.storage.size, 0);
    assert.equal(harness.api.metricsRoot().dataset.state, 'ready');
    assert.match(harness.api.metricsRoot().textContent, options.storageBlocked ? /이 브라우저에서는 집계용 식별자를 저장해 사용할 수 없어/ : /이 브라우저는 개인정보 보호 설정\(GPC·Do Not Track\)에 따라/);
  }
});
test('a persisted anonymous browser identifier is reused across English and Korean pages', async () => {
  const storage = new Map([['atr-reader-metrics-visitor:/AI_Tech_Review/', '11111111-1111-4111-8111-111111111111']]);
  for (const english of [true, false]) {
    const harness = frontendHarness({ metricsStorage: true, storage, english, article: { id: 'same-review' } });
    harness.api.mount(); harness.api.startMetrics(); await flushPromises();
    const body = JSON.parse(harness.calls[0].init.body);
    assert.equal(body.visitorId, '11111111-1111-4111-8111-111111111111');
    assert.equal(body.articleId, 'same-review');
  }
});
test('successful native sharing and link copying count separately after completion; cancel and failure do not count', async () => {
  const harness = frontendHarness({ metricsStorage: true, article: { id: 'test-review' }, responseJSON: () => metricsSummary('test-review') });
  harness.api.mount();
  let releaseShare;
  harness.context.navigator.share = () => new Promise(resolve => { releaseShare = resolve; });
  const sharing = harness.api.share();
  await flushPromises();
  assert.equal(harness.calls.length, 0, 'opening the share sheet does not count');
  harness.document.visibilityState = 'hidden';
  releaseShare(); await sharing; await flushPromises();
  assert.equal(JSON.parse(harness.calls[0].init.body).type, 'share', 'a completed user share can resolve while the page is backgrounded');
  await harness.api.copy(); await flushPromises();
  assert.equal(JSON.parse(harness.calls[1].init.body).type, 'copy');
  assert.notEqual(JSON.parse(harness.calls[0].init.body).eventId, JSON.parse(harness.calls[1].init.body).eventId);
  harness.context.navigator.share = async () => { const error = new Error('canceled'); error.name = 'AbortError'; throw error; };
  await harness.api.share(); await flushPromises();
  assert.equal(harness.calls.length, 2);
  harness.context.navigator.share = async () => { throw Error('unavailable'); };
  await harness.api.share();
  harness.context.navigator.clipboard.writeText = async () => { throw Error('permission denied'); };
  await harness.api.copy(); await flushPromises();
  assert.equal(harness.calls.length, 2);
});
test('native sharing fallback records only a successful link copy', async () => {
  const harness = frontendHarness({ metricsStorage: true, article: { id: 'test-review' }, responseJSON: () => metricsSummary('test-review') });
  harness.api.mount(); await harness.api.share(); await flushPromises();
  assert.equal(harness.calls.length, 1);
  assert.equal(JSON.parse(harness.calls[0].init.body).type, 'copy');
});
test('analytics failures remain separate from successful sharing and never render fake zero counters', async () => {
  const harness = frontendHarness({ metricsStorage: true, article: { id: 'test-review' }, responseStatus: () => 503 });
  harness.api.mount(); await harness.api.copy(); await flushPromises();
  assert.match(harness.api.metricsRoot().textContent, /이 글 열람—/);
  assert.match(harness.articleElement.adjacent[0].element.textContent, /글 주소를 복사했어요/);
  assert.equal(harness.api.metricsRoot().dataset.state, 'error');
  assert.equal(harness.api.state.feedbackError, false);
});
test('public metrics validate every count, matching article and start date before displaying a result', () => {
  const harness = frontendHarness({ article: { id: 'test-review' } });
  harness.api.mount();
  const invalid = [
    { ...metricsSummary('test-review'), since: '<img src=x>' },
    { ...metricsSummary('test-review'), site: { ...metricsSummary().site, visitors: '99' } },
    { ...metricsSummary('test-review'), article: { id: 'other', opens: 3, shares: 1, copies: 1 } },
    { ...metricsSummary('test-review'), article: { id: 'test-review', opens: -1, shares: 1, copies: 1 } }
  ];
  for (const data of invalid) assert.throws(() => harness.api.applyMetrics(data), /invalid_metrics/);
  assert.match(harness.api.metricsRoot().textContent, /이 글 열람—/);
  harness.api.applyMetrics(metricsSummary('test-review'));
  assert.match(harness.api.metricsRoot().textContent, /한국 시간 하루에 한 번/);
  assert.match(harness.api.metricsRoot().textContent, /Global Privacy Control/);
  assert.match(harness.api.metricsRoot().textContent, /도착·읽음 확인이 아닙니다/);
});
test('a late metrics read cannot overwrite counts from a newer completed share', async () => {
  let releaseRead;
  const harness = frontendHarness({ metricsStorage: true, article: { id: 'test-review' }, responseJSON: (url, init) => {
    if (init.method === 'GET') return new Promise(resolve => { releaseRead = resolve; });
    return { ...metricsSummary('test-review'), article: { id: 'test-review', opens: 11, shares: 4, copies: 2 } };
  }});
  harness.api.mount();
  const read = harness.api.refreshMetrics(); await flushPromises();
  harness.context.navigator.share = async () => {};
  await harness.api.share(); await flushPromises();
  releaseRead(metricsSummary('test-review')); await read;
  assert.match(harness.api.metricsRoot().textContent, /공유·복사6/);
});
test('English public metrics retain clear browser/device and sharing definitions', () => {
  const harness = frontendHarness({ english: true });
  harness.api.mount(); harness.api.applyMetrics(metricsSummary());
  assert.match(harness.api.metricsRoot().textContent, /Visiting browsers42/);
  assert.match(harness.api.metricsRoot().textContent, /Shares · copies12/);
  assert.match(harness.api.metricsRoot().textContent, /Alert subscriptions3 devices/);
  assert.match(harness.api.metricsRoot().textContent, /not people/);
  assert.match(harness.api.metricsRoot().textContent, /push provider accepted/);
});

test('a storage-blocked copy cannot invalidate an in-flight public counter read', async () => {
  let releaseRead;
  const harness = frontendHarness({ metricsStorage: true, storageBlocked: true, article: { id: 'test-review' },
    responseJSON: () => new Promise(resolve => { releaseRead = resolve; }) });
  harness.api.mount(); const read = harness.api.refreshMetrics(); await flushPromises();
  await harness.api.copy();
  releaseRead(metricsSummary('test-review')); await read;
  assert.equal(harness.calls.length, 1);
  assert.equal(harness.api.metricsRoot().dataset.state, 'ready');
});
test('a subscription-change refresh queues one fresh read behind an older in-flight counter request', async () => {
  let releaseRead;
  const harness = frontendHarness({ responseJSON: () => new Promise(resolve => { releaseRead = resolve; }) });
  harness.api.mount();
  const initial = harness.api.refreshMetrics(); await flushPromises();
  harness.api.refreshMetrics(true); harness.api.refreshMetrics(true);
  assert.equal(harness.calls.length, 1);
  releaseRead(metricsSummary()); await initial; await flushPromises();
  assert.equal(harness.calls.length, 2);
  releaseRead(metricsSummary()); await flushPromises();
  assert.equal(harness.calls.length, 2);
});
