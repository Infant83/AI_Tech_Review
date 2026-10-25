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
    if (url.pathname === '/v1/config') result.vapidPublicKey = 'B' + 'A'.repeat(86);
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
  assert.ok(calls.every(call => call.credentials === 'include'));
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
  const calls = [], events = [];
  let permission = 'default', subscribeCount = 0, unsubscribeCount = 0;
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
    appendChild(child) { this.children.push(child); return child; }
    replaceChildren(...children) { this._text = ''; this.children = children; }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    removeAttribute(name) { delete this.attributes[name]; }
    getAttribute(name) { return this.attributes[name] || null; }
    addEventListener(name, listener) { (this.listeners[name] ||= []).push(listener); }
    insertAdjacentElement(position, element) { (this.adjacent ||= []).push({ position, element }); }
    focus() { document.activeElement = this; }
    querySelectorAll() { return []; }
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
  documentElement: { lang: 'ko', style: {} }, currentScript: null, body: new MiniNode('body'), title: 'Article',
  createElement: tag => new MiniNode(tag), createTextNode: value => ({ textContent: value }), contains: () => true };
  const context = { URL, Intl, Uint8Array, Array, Promise, JSON, String, Number, Boolean, Error,
    location: { protocol: 'https:', pathname: options.pathname || '/AI_Tech_Review/', hostname: 'infant83.io' }, document,
    navigator: { userAgent: '', standalone: true, serviceWorker: {} },
    Notification: { get permission() { return permission; }, requestPermission: () => { events.push('permission'); permission = 'granted'; return Promise.resolve('granted'); } },
    PushManager: function () {}, isSecureContext: true,
    atob: value => Buffer.from(value, 'base64').toString('binary'),
    setTimeout, clearTimeout,
    fetch: async (url, init) => {
      calls.push({ url, init }); events.push(new URL(url).pathname);
      const status = options.responseStatus ? options.responseStatus(url, init, calls) : 200;
      return { ok: status >= 200 && status < 300, status, json: async () => options.responseJSON ? options.responseJSON(url, init) : ({ ok: true, subscription: subscriptionJSON }) };
    }
  };
  context.navigator.clipboard = { writeText: async value => { context.copied = value; } };
  context.scrollY = 1780;
  context.scrollX = 0;
  context.scrollTo = (x, y) => { context.restoredScroll = [x, y]; };
  if (options.unsupported) { delete context.PushManager; delete context.Notification; delete context.navigator.serviceWorker; }
  context.window = context;
  const testSource = source.replace('  mount();\n  void prepare();\n  void loadLikes();', '  window.__readerTest = { state: state, subscribe: subscribeFromGesture, unsubscribe: unsubscribe, ensureDevice: ensureDevice, mount: mount, open: openDialog, close: closeDialog, like: like, share: share, loadLikes: loadLikes, updateButtons: updateButtons };');
  assert.notEqual(testSource, source, 'test harness must suppress automatic DOM mounting');
  vm.runInNewContext(testSource, context);
  const api = context.__readerTest;
  api.state.preparing = false;
  api.state.key = 'B' + 'A'.repeat(86);
  let current = options.existingSubscription ? subscription : null;
  api.state.registration = { pushManager: { getSubscription: async () => current,
    subscribe: async () => { subscribeCount++; current = subscription; return subscription; } } };
  return { api, calls, events, subscription, subscriptionJSON, context, document, main, articleElement, topbar, header, counts: () => ({ subscribeCount, unsubscribeCount }) };
}
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
  const footerButton = harness.articleElement.adjacent[0].element.children[2];
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
  const status = harness.articleElement.adjacent[0].element.children[3];
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
