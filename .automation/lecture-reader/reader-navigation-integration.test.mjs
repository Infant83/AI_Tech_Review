import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { safeExternalURL, linkRectangle, resolveDestination, createNavigationHistory } from './pdf-navigation.mjs';
import { editionsFor } from './editions.mjs';

// Execute production orchestration. PDF rasterization, IndexedDB and window
// opening are terminal boundaries; the navigation and its intent guards are not.
const source = await readFile(new URL('./reader.mjs', import.meta.url), 'utf8');
const storageSource = await readFile(new URL('./storage.mjs', import.meta.url), 'utf8');
const cloudSource = await readFile(new URL('./cloud.mjs', import.meta.url), 'utf8');
function section(text, start, end) {
  const a = text.indexOf(start), b = text.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Missing production section: ${start}`);
  return text.slice(a, b);
}
const read = (start, end) => section(source, start, end);
const navigation = read('const readerJumpHistory', '// Continuous reader views');
const a = 'a'.repeat(64), b = 'b'.repeat(64);
const tick = () => new Promise(resolve => setImmediate(resolve));
function deferred() { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; }

class Node {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase(); this.children = []; this.parentNode = null;
    this.style = {}; this.dataset = {}; this.attributes = {}; this.listeners = new Map();
    this.hidden = false; this.inert = false; this.disabled = false; this.open = false;
    this.value = ''; this.checked = false; this.scrollLeft = 0; this.scrollTop = 0;
    this.classList = { toggle() {} };
  }
  append(...nodes) { for (const node of nodes) { node.remove(); node.parentNode = this; this.children.push(node); } }
  remove() { if (this.parentNode) this.parentNode.children = this.parentNode.children.filter(n => n !== this); this.parentNode = null; }
  replaceChildren(...nodes) { for (const node of this.children) node.parentNode = null; this.children = []; this.append(...nodes); }
  contains(node) { return this === node || this.children.some(child => child.contains(node)); }
  get isConnected() { return this.connected === true || Boolean(this.parentNode?.isConnected); }
  get options() { return this.children; }
  querySelectorAll(selector) { return this.children.filter(n => selector === 'option[data-destination-zoom]' && n.dataset.destinationZoom); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(name, callback) { if (!this.listeners.has(name)) this.listeners.set(name, []); this.listeners.get(name).push(callback); }
  emit(name, extra = {}) {
    const event = { type: name, target: this, currentTarget: this, pointerType: 'mouse', pointerId: 1, button: 0, isPrimary: true,
      clientX: 100, clientY: 150, detail: 1, prevented: false, stopped: false,
      preventDefault() { this.prevented = true; }, stopPropagation() { this.stopped = true; }, ...extra };
    for (const listener of this.listeners.get(name) || []) listener(event);
    return event;
  }
  closest(selector) { if (selector.split(',').includes(this.tagName.toLowerCase())) return this; return this.parentNode?.closest(selector) || null; }
  showModal() { this.open = true; }
  close() { this.open = false; }
}

function harness() {
  let now = 1000, timer = 0;
  const timers = new Map(), saved = [], restored = [], rendered = [], alerts = [], focused = [], scroll = [0, 0, 0, 0, 0, 0];
  const sheet = new Node(); sheet.connected = true;
  sheet.getBoundingClientRect = () => ({ left: -scroll[2], right: 600 - scroll[2], top: 40 - scroll[3], bottom: 840 - scroll[3], width: 600, height: 800 });
  const area = new Node(); area.clientWidth = 608;
  const zoom = new Node('select'); zoom.append(new Node('option')); zoom.children[0].value = '1'; zoom.value = '1';
  const nodes = new Map([['page-area', area], ['zoom', zoom], ['finger-draw', new Node('input')],
    ['navigation-back', new Node('button')], ['pdf-outline', new Node('button')], ['outline-dialog', new Node('dialog')], ['outline-items', new Node()]]);
  const document = { activeElement: null, createElement: tag => new Node(tag), querySelectorAll: () => [] };
  const page = { view: [0, 0, 600, 800], cleanup() {}, getViewport: ({ scale }) => ({ width: 600 * scale, height: 800 * scale,
    convertToViewportPoint: (x, y) => [x * scale, (800 - y) * scale], convertToPdfPoint: (x, y) => [x / scale, 800 - y / scale] }) };
  const ctx = { URL, console, Math, Number, Object, Array, Date: { now: () => now }, document, window: {},
    rootURL: new URL('https://example.test/'), en: false, $: id => nodes.get(id),
    current: { fingerprint: a, pageCount: 5, bookmarks: [], localPosition: null }, pdf: { numPages: 5, getPage: async () => page },
    pageNumber: 1, tool: 'read', active: null, busy: false, documentOpenGeneration: 1,
    readerViewEpoch: 1, readerViews: new Map(), readerMountedViews: new Set(), readerCanvasViews: new WeakMap(),
    readerFocusAnchor: null, readerFocusGeneration: 0, readerFocusInputEpoch: 0,
    readerResizePending: false, readerTouchPointers: new Set(), readerGestureCandidate: null, readerLastGestureTap: null, readerNonMouseAt: 0,
    sheet, inkCanvas: new Node('canvas'), permissions: { role: 'local' }, catalog: [],
    safeExternalURL, linkRectangle, resolveDestination, createNavigationHistory, editionsFor,
    clamp: (n, min, max) => Math.min(max, Math.max(min, n)), t: x => x, toast: x => alerts.push(x),
    readerVisibleViewport: () => ({ left: 0, right: 600, top: 40, bottom: 700 }), readerScrollOffsets: () => [...scroll],
    readerFocusMode: () => false, restoreReaderFocusAnchor: anchor => { restored.push(structuredClone({ x: anchor.x, y: anchor.y, page: anchor.page })); },
    getComputedStyle: () => ({ paddingLeft: '4px', paddingRight: '4px' }),
    setTimeout: fn => { const id = ++timer; timers.set(id, fn); return id; }, clearTimeout: id => timers.delete(id),
    writeQueue: Promise.resolve(true), storage: { saveMetadata: async (...args) => saved.push(structuredClone(args)), loadPages: async () => [] },
    storageFailure: () => alerts.push('storage'), finishStroke() {}, canAddInk: () => true,
    ensurePage: async () => true, renderPage: async () => { rendered.push(ctx.pageNumber); ctx.busy = false; }, markMeta: () => { ctx.mutationRevision++; }, scheduleReaderVisible() {},
    mutationRevision: 0, controls: () => ctx.readerNavigationControls(), resetReaderTap() { ctx.readerGestureCandidate = null; ctx.readerLastGestureTap = null; },
    pages: new Map(), histories: new Map(), dirty: new Map(), metaSaved: 0, metaVersion: 0,
    flush: async () => true, NOTEBOOK_FORMAT: 'ai-tech-review-notebook', clone: structuredClone,
  };
  ctx.readerViewsOwner = ctx.current; ctx.readerViewPDF = ctx.pdf;
  ctx.inkCanvas.focus = () => { document.activeElement = ctx.inkCanvas; focused.push('ink'); };
  vm.createContext(ctx);
  vm.runInContext(navigation + read('function resetReaderTap(', 'function prepareReaderCanvases(') +
    read('function readerTapEligible(', 'function readerPointAnchor(') +
    read('function chooseTool(', 'function pointerPoint(') +
    read('async function goPage(', 'function renderBookmarks(') +
    read('async function notebook(', 'async function applyNotebook('), ctx);
  // Expose only the actual bounded session history, not a replacement algorithm.
  vm.runInContext('globalThis.jumpHistory=readerJumpHistory;globalThis.navRequest=()=>readerNavigationRequest;', ctx);
  const addView = (number = 1) => {
    const node = number === 1 ? sheet : new Node(); node.connected = true;
    const view = { number, sheet: node, ready: true, renderToken: 1, inkCanvas: ctx.inkCanvas, pdfCanvas: { width: 600, height: 800 }, pdfPage: page };
    ctx.readerViews.set(number, view); ctx.readerMountedViews.add(view); return view;
  };
  return { ctx, nodes, sheet, page, saved, restored, rendered, alerts, timers, focused, scroll, addView,
    advance(ms) { now += ms; }, runTimers() { const all = [...timers.values()]; timers.clear(); all.forEach(fn => fn()); },
    async links(annotations, view = addView()) { await ctx.renderReaderLinks(view, { getAnnotations: async () => annotations }, page.getViewport({ scale: 1 })); return view; },
    async idle() { await tick(); await ctx.writeQueue; },
  };
}
const annotation = extra => ({ subtype: 'Link', rect: [20, 700, 180, 730], dest: [1, { name: 'XYZ' }, 120, 640, null], ...extra });

test('read links support pointer and keyboard activation while pen/eraser remove focus and disable interaction', async () => {
  const h = harness(), view = await h.links([annotation()]);
  const link = view.linkLayer.children[0]; let moved = 0; h.ctx.followReaderDestination = () => moved++;
  assert.equal(view.linkLayer.inert, false); assert.equal(view.linkLayer.hidden, false);
  link.emit('pointerdown'); assert.equal(link.emit('click').prevented, true); assert.equal(moved, 1);
  link.emit('click', { detail: 0 }); assert.equal(moved, 2, 'keyboard activation does not need a pointer candidate');
  link.emit('pointerdown', { pointerType: 'pen' }); link.emit('click', { pointerType: 'pen' }); assert.equal(moved, 3, 'a Pencil tap follows links when the selected tool is Read');
  for (const mode of ['pen', 'eraser']) {
    h.ctx.document.activeElement = link; h.ctx.chooseTool(mode);
    assert.equal(view.linkLayer.inert, true); assert.equal(view.linkLayer.hidden, true); assert.equal(h.ctx.document.activeElement, h.ctx.inkCanvas);
    assert.equal(link.emit('click', { detail: 0 }).prevented, true); assert.equal(moved, 3);
  }
  h.ctx.chooseTool('read'); assert.equal(view.linkLayer.inert, false); assert.equal(h.focused.length, 2);
});

test('link gestures reject drag, scroll, multitouch, cancel and expired taps without triggering a destination', async () => {
  for (const variant of ['drag', 'scroll', 'multitouch', 'cancel', 'expired']) {
    const h = harness(), view = await h.links([annotation()]), link = view.linkLayer.children[0]; let moved = 0;
    h.ctx.followReaderDestination = () => moved++;
    h.ctx.captureReaderTap({ pointerType: 'touch', target: link });
    link.emit('pointerdown', { pointerType: 'touch' });
    if (variant === 'drag') link.emit('pointermove', { clientX: 125 });
    if (variant === 'scroll') h.scroll[3] = 25;
    if (variant === 'multitouch') h.ctx.captureReaderTap({ pointerType: 'touch', target: link });
    if (variant === 'cancel') link.emit('pointercancel');
    if (variant === 'expired') h.advance(701);
    assert.equal(link.emit('click').prevented, true, variant); assert.equal(moved, 0, variant);
    assert.equal(h.ctx.readerGestureCandidate, null, 'interactive links never become zoom candidates');
  }
});

test('a pending pointer click cannot reactivate after switching Read to Pen and back to Read', async () => {
  const h = harness(), view = await h.links([annotation()]), link = view.linkLayer.children[0]; let moved = 0;
  h.ctx.followReaderDestination = () => moved++;
  link.emit('pointerdown'); h.ctx.chooseTool('pen'); h.ctx.chooseTool('read');
  assert.equal(link.emit('click').prevented, true); assert.equal(moved, 0);
  link.emit('pointerdown'); link.emit('click'); assert.equal(moved, 1, 'a new deliberate pointer tap still works');
});

test('external links retain normal safe new-tab anchors but unsafe PDF actions have no clickable layer entry', async () => {
  const h = harness(), view = await h.links([
    annotation({ dest: null, url: 'https://example.org/paper' }), annotation({ dest: null, url: 'javascript:alert(1)' }),
    annotation({ dest: null, url: 'https://example.org/launch', action: 'Launch' }),
  ]);
  assert.equal(view.linkLayer.children.length, 1); const link = view.linkLayer.children[0];
  assert.equal(link.href, 'https://example.org/paper'); assert.equal(link.target, '_blank'); assert.equal(link.rel, 'noopener noreferrer');
  link.emit('pointerdown'); assert.equal(link.emit('click').prevented, false);
  assert.equal(link.emit('click', { detail: 0 }).prevented, false);
});

test('relative links receive only a registered public PDF edition base and never a private or mismatched base', async () => {
  const h = harness();
  h.ctx.catalog = [{ id: 'published-a', sha256: a, href: 'archive/files/published-a.pdf', editions: [{ sha256: b, href: `archive/editions/published-a/${b}.pdf` }] }];
  assert.equal(h.ctx.readerPublicBaseURL(a, 'published-a'), 'https://example.test/archive/files/published-a.pdf');
  assert.equal(h.ctx.readerPublicBaseURL(b, 'published-a'), `https://example.test/archive/editions/published-a/${b}.pdf`);
  assert.equal(h.ctx.readerPublicBaseURL(a, null), null); assert.equal(h.ctx.readerPublicBaseURL('c'.repeat(64), 'published-a'), null);
  h.ctx.current.publicId = 'published-a';
  let view = await h.links([annotation({ dest: null, url: '../source.html' })]);
  assert.equal(view.linkLayer.children[0].href, 'https://example.test/archive/source.html');
  h.ctx.current.publicId = null;
  view = await h.links([annotation({ dest: null, url: '../source.html' })], view);
  assert.equal(view.linkLayer.children.length, 0, 'a private PDF has no guessed site-relative URL');
});

test('annotation completion rejects replaced owners, PDF, epoch, token, eviction and not-ready views', async () => {
  for (const variant of ['owner', 'pdf', 'epoch', 'token', 'evicted', 'not-ready']) {
    const h = harness(), view = h.addView(), held = deferred();
    const rendering = h.ctx.renderReaderLinks(view, { getAnnotations: () => held.promise }, h.page.getViewport({ scale: 1 }));
    if (variant === 'owner') h.ctx.current = { ...h.ctx.current, fingerprint: b };
    if (variant === 'pdf') h.ctx.pdf = { ...h.ctx.pdf };
    if (variant === 'epoch') h.ctx.readerViewEpoch++;
    if (variant === 'token') view.renderToken++;
    if (variant === 'evicted') h.ctx.readerViews.delete(view.number);
    if (variant === 'not-ready') view.ready = false;
    held.resolve([annotation()]); await rendering;
    assert.equal(view.linkLayer, null, variant); assert.equal(view.sheet.children.length, 0, variant);
  }
});

test('eviction removes existing link DOM and malformed or rejected annotations leave PDF and ink usable', async () => {
  const h = harness(), view = await h.links([annotation()]); const layer = view.linkLayer;
  h.ctx.releaseReaderView(view); assert.equal(layer.parentNode, null); assert.equal(view.linkLayer, null); assert.equal(view.ready, false);
  const other = h.addView(2); await h.ctx.renderReaderLinks(other, { getAnnotations: async () => { throw Error('annotations unavailable'); } }, h.page.getViewport({ scale: 1 }));
  assert.equal(other.ready, true); assert.equal(other.inkCanvas, h.ctx.inkCanvas); assert.deepEqual(h.alerts, []);
});

test('same-page coordinate navigation restores the exact point and the prior position stays in bounded return history', async () => {
  const h = harness(); h.addView();
  const destination = { fingerprint: a, page: 1, nx: .2, ny: .75, zoom: 2 };
  assert.equal(await h.ctx.navigateReaderPosition(destination), true);
  assert.deepEqual(h.rendered, [1]); assert.equal(h.nodes.get('zoom').value, '2');
  assert.deepEqual(h.restored, [{ x: .2, y: .75, page: 1 }]); assert.equal(h.ctx.jumpHistory.size, 1);
  const before = h.ctx.jumpHistory.pop(); assert.equal(before.page, 1); assert.equal(before.zoom, 1); assert.equal(before.ny, .01);
  assert.equal(await h.ctx.navigateReaderPosition(before, { remember: false }), true); assert.equal(h.ctx.jumpHistory.size, 0);
  assert.deepEqual(h.restored[1], { x: .5, y: .01, page: 1 });
});

test('saving and returning to a page below the viewport top preserves its visible offset instead of snapping it upward', async () => {
  const h = harness(), area = h.nodes.get('page-area'); h.addView(3); h.ctx.pageNumber = 3;
  h.nodes.get('zoom').value = '2';
  area.scrollLeft = 0; area.scrollTop = 500; area.scrollWidth = 1200; area.clientWidth = 600; area.scrollHeight = 20_000; area.clientHeight = 600;
  const top = () => 758 - area.scrollTop;
  h.sheet.getBoundingClientRect = () => ({ left: -area.scrollLeft, right: 1200 - area.scrollLeft, top: top(), bottom: top() + 1600, width: 1200, height: 1600 });
  h.ctx.readerVisibleViewport = () => ({ left: 0, right: 600, top: 58, bottom: 658 });
  h.ctx.readerScrollOffsets = () => [0, 0, area.scrollLeft, area.scrollTop, 0, 0];
  let outsideScroll = 0; h.ctx.window.scrollTo = () => outsideScroll++;
  // Use the actual final focus-restoration algorithm, including its delta
  // consumption. Merely observing an anchor would miss the 192px regression.
  vm.runInContext(read('function readerAnchorCurrent(', 'function cancelReaderFocusPosition('), h.ctx);
  const position = h.ctx.readerSavedPosition();
  assert.equal(position.ny, 0); assert.equal(position.viewportY, 1 / 3); assert.equal(top(), 258);
  assert.equal(h.ctx.validReaderPosition(position), true);
  await h.ctx.persistReaderPosition(); assert.equal(h.saved[0][1].localPosition.viewportY, 1 / 3);
  // Restoring the saved local anchor after the initial canvas has displaced it
  // restores the same page top, as reopening a locally stored PDF does.
  area.scrollTop += 100; h.ctx.readerRestorePosition(position);
  assert.equal(top(), 258); assert.equal(area.scrollTop, 500); assert.equal(outsideScroll, 0);
  // A deliberate link jump then Back must preserve that same viewport offset.
  await h.ctx.navigateReaderPosition({ fingerprint: a, page: 3, nx: .25, ny: .4, zoom: 2 });
  assert.notEqual(top(), 258); const back = h.ctx.jumpHistory.pop(); assert.equal(back.viewportY, 1 / 3);
  await h.ctx.navigateReaderPosition(back, { remember: false });
  assert.equal(top(), 258); assert.equal(area.scrollTop, 500); assert.equal(outsideScroll, 0);
  for (const viewportY of [-.1, 1.1, NaN, Infinity, '0.2']) assert.equal(h.ctx.validReaderPosition({ ...position, viewportY }), false);
  const legacy = { ...position }; delete legacy.viewportY;
  assert.equal(h.ctx.validReaderPosition(legacy), true, 'older saved anchors remain compatible');
});

test('reopening across the document scroll boundary remeasures the visible viewport and stays stable on repeated saves', async () => {
  const h = harness(), area = h.nodes.get('page-area'); h.addView(2); h.ctx.pageNumber = 2;
  const box = (left, top, width, height) => ({ left, right: left + width, top, bottom: top + height, width, height });
  const headerBottom = 151.84375, paperTop = 1237.40625, paperHeight = 1046.5625;
  const main = new Node(); h.nodes.set('reader-main', main);
  Object.assign(area, { scrollLeft: 320, scrollTop: 0, scrollWidth: 760, clientWidth: 390, scrollHeight: 18_192, clientHeight: 18_192 });
  Object.assign(main, { scrollLeft: 0, scrollTop: 0, scrollWidth: 390, clientWidth: 390, scrollHeight: 18_292, clientHeight: 18_292 });
  h.nodes.set('page-controls', { hidden: false, getBoundingClientRect: () => box(0, 783, 390, 61) });
  h.ctx.document.querySelector = selector => selector === '.reader-header' ? { getBoundingClientRect: () => box(0, 0, 390, headerBottom) } : null;
  Object.assign(h.ctx.window, { scrollX: 0, scrollY: 1363, innerWidth: 390, innerHeight: 844 });
  h.ctx.window.scrollTo = ({ left = 0, top = 0 }) => { h.ctx.window.scrollX = Math.max(0, left); h.ctx.window.scrollY = Math.max(0, Math.min(17_500, top)); };
  // A normal-flow reader region can initially sit below the sticky header;
  // after document scrolling, the visible top clips to the header instead.
  area.getBoundingClientRect = () => box(0, headerBottom + 8 - h.ctx.window.scrollY, 390, 18_192);
  h.sheet.getBoundingClientRect = () => box(10 - area.scrollLeft, paperTop - h.ctx.window.scrollY - area.scrollTop, 740, paperHeight);
  vm.runInContext(read('function readerScrollOffsets(', 'function cancelReaderFocusPosition('), h.ctx);
  const expected = h.sheet.getBoundingClientRect(), original = h.ctx.readerSavedPosition();
  assert.equal(expected.top, -125.59375); assert.equal(original.viewportY, 8 / (783 - headerBottom));
  for (let reopen = 0; reopen < 4; reopen++) {
    const saved = h.ctx.readerSavedPosition();
    h.ctx.window.scrollY = 0; area.scrollLeft = 0;
    h.ctx.readerRestorePosition(saved);
    const restored = h.sheet.getBoundingClientRect();
    assert.ok(Math.abs(restored.top - expected.top) <= .5, `reopen ${reopen}: visible paper top drifted from ${expected.top} to ${restored.top}`);
    assert.ok(Math.abs(restored.left - expected.left) <= .5, 'horizontal position stays in the existing PDF scroll region');
    await h.ctx.persistReaderPosition();
    assert.ok(Math.abs(h.saved.at(-1)[1].localPosition.ny - original.ny) * paperHeight <= .5, 'saving the reopened position must not accumulate a viewport inset');
  }
});

test('named destinations stop after new document, tool, scroll or navigation intent during resolution', async () => {
  for (const variant of ['document', 'tool', 'scroll', 'input', 'new-jump', 'cloud-page']) {
    const h = harness(), held = deferred(); h.addView(); h.addView(2);
    h.ctx.pdf.getDestination = () => held.promise;
    const pending = h.ctx.followReaderDestination('section-two');
    if (variant === 'document') { h.ctx.current = { ...h.ctx.current, fingerprint: b }; h.ctx.documentOpenGeneration++; }
    if (variant === 'tool') h.ctx.chooseTool('pen');
    if (variant === 'scroll') h.scroll[3] = 50;
    if (variant === 'input') h.ctx.readerFocusInputEpoch++;
    if (variant === 'new-jump') await h.ctx.navigateReaderPosition({ fingerprint: a, page: 1, nx: .1, ny: .1, zoom: 1 });
    if (variant === 'cloud-page') await h.ctx.goPage(1);
    const count = h.rendered.length;
    held.resolve([1, { name: 'XYZ' }, 120, 640, null]); await pending;
    assert.equal(h.rendered.length, count, variant); assert.equal(h.ctx.pageNumber, 1, variant);
  }
});

test('missing, rejected and out-of-range destinations report one failure without changing the PDF or ink', async () => {
  for (const variant of ['missing', 'rejected', 'out-of-range']) {
    const h = harness(); h.addView();
    const strokes = [{ id: 'existing-ink', points: [{ x: .2, y: .3 }] }]; h.ctx.pages.set(1, strokes);
    h.ctx.pdf.getDestination = async () => { if (variant === 'rejected') throw Error('unavailable'); return null; };
    await h.ctx.followReaderDestination(variant === 'out-of-range' ? [5, { name: 'Fit' }] : 'missing-section');
    assert.deepEqual(h.alerts, ['navigationFailed'], variant);
    assert.equal(h.ctx.pageNumber, 1); assert.equal(h.nodes.get('zoom').value, '1');
    assert.equal(h.ctx.pages.get(1), strokes); assert.equal(h.ctx.mutationRevision, 0); assert.equal(h.ctx.jumpHistory.size, 0);
    assert.deepEqual(h.saved, []); assert.deepEqual(h.rendered, []); assert.deepEqual(h.restored, []);
  }
});

test('a missing destination completed after cancellation never reports an obsolete failure', async () => {
  for (const variant of ['owner', 'pdf', 'generation', 'request', 'tool', 'input', 'scroll', 'busy', 'ink']) {
    const h = harness(), held = deferred(); h.addView();
    h.ctx.pdf.getDestination = () => held.promise;
    const pending = h.ctx.followReaderDestination('missing-section');
    if (variant === 'owner') h.ctx.current = { ...h.ctx.current };
    if (variant === 'pdf') h.ctx.pdf = { ...h.ctx.pdf };
    if (variant === 'generation') h.ctx.documentOpenGeneration++;
    if (variant === 'request') h.ctx.resetReaderNavigation();
    if (variant === 'tool') h.ctx.chooseTool('pen');
    if (variant === 'input') h.ctx.readerFocusInputEpoch++;
    if (variant === 'scroll') h.scroll[3] = 50;
    if (variant === 'busy') h.ctx.busy = true;
    if (variant === 'ink') h.ctx.active = { page: 1 };
    held.resolve(null); await pending;
    assert.deepEqual(h.alerts, [], variant); assert.deepEqual(h.rendered, []); assert.equal(h.ctx.pageNumber, 1);
  }
});

test('an awaited page failure respects the same current-intent guard as destination resolution', async () => {
  for (const variant of ['current', 'input', 'scroll', 'tool']) {
    const h = harness(), entered = deferred(), held = deferred(); h.addView();
    h.ctx.pdf.getPage = () => { entered.resolve(); return held.promise; };
    const pending = h.ctx.followReaderDestination([1, { name: 'Fit' }]); await entered.promise;
    if (variant === 'input') h.ctx.readerFocusInputEpoch++;
    if (variant === 'scroll') h.scroll[3] = 50;
    if (variant === 'tool') h.ctx.chooseTool('pen');
    held.reject(Error('page unavailable')); await pending;
    assert.deepEqual(h.alerts, variant === 'current' ? ['navigationFailed'] : [], variant);
    assert.equal(h.ctx.pageNumber, 1); assert.equal(h.ctx.jumpHistory.size, 0); assert.equal(h.ctx.mutationRevision, 0);
  }
});

test('user input during an awaited page load cancels a jump before page, history or metadata changes', async () => {
  const h = harness(), held = deferred(); h.addView(); h.addView(2);
  h.ctx.ensurePage = () => held.promise;
  const pending = h.ctx.navigateReaderPosition({ fingerprint: a, page: 2, nx: .2, ny: .3, zoom: 2 });
  h.ctx.readerFocusInputEpoch++; held.resolve(true);
  assert.equal(await pending, false); assert.equal(h.ctx.pageNumber, 1); assert.equal(h.ctx.jumpHistory.size, 0);
  assert.equal(h.ctx.mutationRevision, 0); assert.deepEqual(h.rendered, []); assert.deepEqual(h.restored, []); assert.equal(h.ctx.busy, false);
});

test('input during canvas replacement cannot force-scroll, restore an obsolete point or publish jump metadata/history', async () => {
  const h = harness(), entered = deferred(), held = deferred(); h.addView(); h.addView(2); let visible = 0;
  h.ctx.renderPage = async scroll => { assert.equal(scroll, false, 'jump does not scroll before intent approval'); entered.resolve(); await held.promise; };
  h.ctx.scheduleReaderVisible = () => visible++;
  const pending = h.ctx.navigateReaderPosition({ fingerprint: a, page: 2, nx: .2, ny: .3, zoom: 2 });
  await entered.promise; h.ctx.readerFocusInputEpoch++; held.resolve();
  assert.equal(await pending, false); assert.equal(visible, 1); assert.equal(h.ctx.jumpHistory.size, 0);
  assert.equal(h.ctx.mutationRevision, 0); assert.deepEqual(h.restored, []); assert.equal(h.ctx.busy, false);
});

test('FitR and Fit destinations can fit a viewport below width-fit without losing normalized coordinates', async () => {
  const h = harness(); h.addView(); h.addView(2);
  await h.ctx.followReaderDestination([1, { name: 'FitR' }, 100, 0, 500, 800]);
  assert.equal(h.ctx.pageNumber, 2); assert.ok(Number(h.nodes.get('zoom').value) < 1); assert.ok(Number(h.nodes.get('zoom').value) >= .1);
  assert.ok(h.restored[0].x >= 0 && h.restored[0].x <= 1); assert.ok(h.restored[0].y >= 0 && h.restored[0].y <= 1);
  assert.equal(h.ctx.validReaderPosition({ fingerprint: a, page: 2, nx: .2, ny: .3, zoom: .2 }), true);
  await h.ctx.followReaderDestination([0, { name: 'Fit' }]);
  assert.equal(h.ctx.pageNumber, 1); assert.ok(Number(h.nodes.get('zoom').value) < 1);
});

test('rotated partial XYZ, FitH and FitV destinations preserve missing coordinates in PDF space', async () => {
  const previous = { fingerprint: a, page: 1, nx: .23, ny: .61, zoom: 1 };
  for (const rotation of [90, 270]) {
    const expectedX = rotation === 90 ? .8 : .2, expectedY = rotation === 90 ? .2 : .8;
    const cases = [
      { name: 'XYZ missing x', destination: [1, { name: 'XYZ' }, null, 640, null], point: [expectedX, .61] },
      { name: 'XYZ missing y', destination: [1, { name: 'XYZ' }, 120, null, null], point: [.23, expectedY] },
      { name: 'XYZ missing both', destination: [1, { name: 'XYZ' }, null, null, null], point: [.23, .61] },
      { name: 'FitH', destination: [1, { name: 'FitH' }, 640], point: [expectedX, .61] },
      { name: 'FitV', destination: [1, { name: 'FitV' }, 120], point: [.23, expectedY] },
      { name: 'FitH missing top', destination: [1, { name: 'FitH' }, null], point: [.23, .61] },
      { name: 'FitV missing left', destination: [1, { name: 'FitV' }, null], point: [.23, .61] },
    ];
    for (const entry of cases) {
      const h = harness(); h.addView(); h.addView(2); h.ctx.readerSavedPosition = () => ({ ...previous });
      h.page.getViewport = ({ scale }) => ({ width: 800 * scale, height: 600 * scale, rotation,
        convertToViewportPoint: (x, y) => rotation === 90 ? [y * scale, x * scale] : [(800 - y) * scale, (600 - x) * scale],
        convertToPdfPoint: (x, y) => rotation === 90 ? [y / scale, x / scale] : [600 - y / scale, 800 - x / scale],
      });
      await h.ctx.followReaderDestination(entry.destination);
      assert.equal(h.restored.length, 1, `${rotation} ${entry.name}`);
      assert.ok(Math.abs(h.restored[0].x - entry.point[0]) < 1e-12, `${rotation} ${entry.name}: horizontal PDF-space preservation`);
      assert.ok(Math.abs(h.restored[0].y - entry.point[1]) < 1e-12, `${rotation} ${entry.name}: vertical PDF-space preservation`);
    }
  }
});

test('outline resolution ignores an obsolete document and closing its dialog before late completion', async () => {
  for (const variant of ['document', 'closed']) {
    const h = harness(), held = deferred(); h.ctx.pdf.getOutline = () => held.promise;
    const opening = h.ctx.openReaderOutline(); const items = h.nodes.get('outline-items');
    if (variant === 'document') { h.ctx.current = { ...h.ctx.current, fingerprint: b }; h.ctx.documentOpenGeneration++; }
    else h.nodes.get('outline-dialog').close();
    held.resolve([{ title: 'Old private title', dest: [1, { name: 'Fit' }] }]); await opening;
    assert.equal(items.children.length, 1); assert.equal(items.children[0].textContent, 'loading', variant);
  }
});

test('precision writes stay local metadata without ink revision or cloud backup fields and reject obsolete queued owners', async () => {
  const h = harness(); h.addView();
  await h.ctx.persistReaderPosition(); assert.equal(h.ctx.mutationRevision, 0); assert.equal(h.saved.length, 1);
  assert.equal(h.saved[0][0], a); assert.equal(h.saved[0][1].position, 1); assert.equal(h.saved[0][1].localPosition.fingerprint, a);
  const backup = await h.ctx.notebook(); assert.equal(backup.position, 1); assert.equal(typeof backup.position, 'number');
  assert.equal('localPosition' in backup, false); assert.equal('localPosition' in backup.document, false);
  const held = deferred(); h.ctx.writeQueue = held.promise;
  const pending = h.ctx.persistReaderPosition(); h.ctx.current = { ...h.ctx.current, fingerprint: b }; h.ctx.documentOpenGeneration++;
  held.resolve(true); await pending; assert.equal(h.saved.length, 1);
  assert.equal(h.ctx.validReaderPosition({ fingerprint: b, page: 1, nx: .2, ny: .3, zoom: 1 }), true);
  assert.equal(h.ctx.validReaderPosition({ fingerprint: b, page: 2, nx: .2, ny: .3, zoom: 1 }), false);
});

test('notebook import invalidates stored precision while preserving numeric page, PDF identity and strokes', async () => {
  const record = { fingerprint: a, position: 1, localPosition: { fingerprint: a, page: 1, nx: .2, ny: .3, zoom: 2 }, hasPDF: true, title: 'Original' };
  const puts = [], pagePuts = []; const db = { transaction() { return { abort() { assert.fail('unexpected abort'); }, objectStore(name) {
    if (name === 'pages') return { delete() {}, put(value) { pagePuts.push(value); } };
    return { get() { const req = {}; queueMicrotask(() => req.onsuccess({ target: { result: record } })); return req; }, put(value) { puts.push(value); } };
  } }; } };
  const c = vm.createContext({ META: 'document_metadata', openDatabase: async () => db, complete: async () => { await tick(); },
    IDBKeyRange: { bound: (...values) => values }, pageKey: (f, p) => `${f}:${p}`, Date,
  });
  vm.runInContext(section(storageSource, 'function metadata(', 'function pageKey(') + section(storageSource, 'export async function importPages(', 'export async function trashDocument(').replace('export async', 'async'), c);
  const strokes = [{ id: 'preserved', points: [{ x: .1, y: .2, p: .5 }] }];
  await c.importPages(a, [{ number: 2, strokes }], [2], 2);
  assert.equal(puts.length, 1); assert.equal(puts[0].localPosition, null); assert.equal(puts[0].position, 2);
  assert.equal(puts[0].fingerprint, a); assert.equal(puts[0].hasPDF, true); assert.deepEqual(pagePuts[0].strokes, strokes);
  let applied;
  const cloud = vm.createContext({ window: { ATRNotebook: { applyNotebook: async value => { applied = value; } } } });
  vm.runInContext(section(cloudSource, 'async function applyWorking(', 'function downloadBlocked('), cloud);
  await cloud.applyWorking({ position: { page: 2 }, pages: [], document: { fingerprint: a } });
  assert.equal(applied.position, 2); assert.equal('localPosition' in applied, false);
});
