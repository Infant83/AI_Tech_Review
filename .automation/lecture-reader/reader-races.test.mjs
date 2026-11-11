import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { webcrypto } from 'node:crypto';
import { roleCapabilities, strokeAuthorMap, strokeKey } from './cloud-core.mjs';
import { eraseStrokes } from './ink-core.mjs';

// Exercise the actual browser functions with delayed storage, without publishing
// test hooks or replacing the production implementation with a test copy.
const source = fs.readFileSync(new URL('./reader.mjs', import.meta.url), 'utf8');
const section = (start, end) => {
  const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Reader function boundaries missing: ${start}`);
  return source.slice(a, b);
};
const functions = {
  notebook: section('async function notebook(', 'async function applyNotebook('),
  applyNotebook: section('async function applyNotebook(', 'async function exportPDF('),
  ensurePage: section('async function ensurePage(', 'async function goPage('),
  goPage: section('async function goPage(', 'function renderBookmarks('),
  permissions: section('function canAddInk(', 'function state('),
  eraseAt: section('function eraseAt(', "inkCanvas.addEventListener('pointerover'"),
  undo: section('function undo(', "document.querySelectorAll('button[data-tool]')"),
  historyEntry: section('function historyEntry(', 'function finishStroke('),
};
const pointerDown = section("inkCanvas.addEventListener('pointerdown'", "inkCanvas.addEventListener('pointermove'");
const document = { fingerprint: 'a'.repeat(64), title: 'Lecture', pageCount: 2 };
const stroke = id => ({ id, color: '#123456', width: .003, points: [{ x: .1, y: .2, p: .5 }] });
const deferred = () => {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
};
function context(names) {
  const listeners = {};
  const ctx = {
    current: { ...document, bookmarks: [] }, active: null, busy: false, tool: 'pen', pageNumber: 1,
    permissions: { role: 'local', accountId: null, notebookId: null }, strokeAuthors: new Map(), suspendedTool: null,
    roleCapabilities, strokeAuthorMap, strokeKey, eraseStrokes, cssWidth: 600, cssHeight: 800,
    pages: new Map([[1, [stroke('existing')]]]), histories: new Map(), dirty: new Map(),
    metaSaved: 0, metaVersion: 0, mutationRevision: 0,
    NOTEBOOK_FORMAT: 'ai-tech-review-notebook', clone: structuredClone,
    validateNotebook: value => value, uid: () => 'new-stroke', confirm: () => true, t: value => value,
    clamp: (value, min, max) => Math.min(max, Math.max(min, value)),
    controls: () => {}, finishStroke: () => {}, renderBookmarks: () => {},
    chooseTool: next => { ctx.tool = next; }, sheet: { dataset: {} }, markDirty() {}, requestInk() {}, drawInk() {},
    retiredIds: new Set(), state: () => ctx.pages.get(ctx.pageNumber) || [],
    history: () => { if (!ctx.histories.has(ctx.pageNumber)) ctx.histories.set(ctx.pageNumber, { undo: [], redo: [] }); return ctx.histories.get(ctx.pageNumber); },
    canAddInk: () => true, canEditAllInk: () => true, ownStroke() {},
    ensurePage: async () => {}, renderPage: async () => { ctx.busy = false; },
    flush: async () => true, status: () => {}, signal: () => {}, currentInfo: () => ({ ...document }), storageFailure: () => {},
    showError: () => { ctx.busy = false; }, markMeta: () => { ctx.mutationRevision++; },
    storage: { loadPages: async () => [], loadPage: async () => [], importPages: async () => {} },
    inkCanvas: { addEventListener: (name, handler) => { listeners[name] = handler; } },
  };
  vm.createContext(ctx);
  vm.runInContext(names.map(name => functions[name]).join('\n') + '\n' + pointerDown, ctx);
  ctx.pointerDown = () => listeners.pointerdown({ pointerType: 'mouse', button: 0 });
  return ctx;
}

test('a failed full-notebook read cannot become an incomplete cloud snapshot', async () => {
  const ctx = context(['notebook']);
  ctx.storage.loadPages = async () => { throw new Error('IDB_READ_FAILED'); };
  await assert.rejects(ctx.notebook(), /IDB_READ_FAILED/);
  assert.deepEqual(ctx.pages.get(1).map(item => item.id), ['existing']);
});

test('unsaved ink prevents export when its durable flush fails', async () => {
  const ctx = context(['notebook']);
  ctx.dirty.set(1, 1); ctx.flush = async () => false;
  let read = false; ctx.storage.loadPages = async () => { read = true; return []; };
  await assert.rejects(ctx.notebook(), /SAVE_FAILED/);
  assert.equal(read, false);
});

for (const stage of ['flush', 'loadPages']) {
  test(`export refuses a stroke begun during awaited ${stage}`, async () => {
    const ctx = context(['notebook']), entered = deferred(), release = deferred();
    const delayed = async () => { entered.resolve(); await release.promise; return stage === 'flush' ? true : []; };
    if (stage === 'flush') ctx.flush = delayed; else ctx.storage.loadPages = delayed;
    const exporting = ctx.notebook(); await entered.promise;
    ctx.active = { id: 'pencil-started' }; release.resolve();
    await assert.rejects(exporting, /READER_BUSY/);
  });
}

test('incoming ink holds the edit lock through both flush and import awaits', async () => {
  const ctx = context(['applyNotebook']);
  const flushing = deferred(), flushRelease = deferred(), importing = deferred(), importRelease = deferred();
  ctx.flush = async () => { flushing.resolve(); await flushRelease.promise; return true; };
  ctx.storage.importPages = async () => { importing.resolve(); await importRelease.promise; };
  const value = { document, pages: [{ number: 1, strokes: [stroke('remote')] }], bookmarks: [], position: 1 };
  const applying = ctx.applyNotebook(value, { silent: true });
  await flushing.promise;
  assert.equal(ctx.busy, true); ctx.pointerDown(); assert.equal(ctx.active, null);
  flushRelease.resolve(); await importing.promise;
  assert.equal(ctx.busy, true); ctx.pointerDown(); assert.equal(ctx.active, null);
  assert.deepEqual(ctx.pages.get(1).map(item => item.id), ['existing']);
  importRelease.resolve(); await applying;
  assert.equal(ctx.busy, false);
  assert.deepEqual(ctx.pages.get(1).map(item => item.id), ['remote']);
});

test('explicit backup restoration creates fresh ink IDs while preserving editable geometry', async () => {
  const ctx = context(['applyNotebook']);
  const original = stroke('erased-cloud-id');
  const value = { document, pages: [{ number: 1, strokes: [original] }], bookmarks: [], position: 1 };
  await ctx.applyNotebook(value, { confirmReplace: true });
  const restored = ctx.pages.get(1)[0];
  assert.equal(restored.id, 'new-stroke');
  assert.deepEqual({ ...restored, id: original.id }, original);
});

test('page navigation locks ink and commits the page number only after storage loads', async () => {
  const ctx = context(['goPage']), entered = deferred(), release = deferred();
  ctx.ensurePage = async number => { assert.equal(number, 2); entered.resolve(); await release.promise; };
  const navigating = ctx.goPage(2); await entered.promise;
  assert.equal(ctx.busy, true); assert.equal(ctx.pageNumber, 1);
  ctx.pointerDown(); assert.equal(ctx.active, null);
  release.resolve(); await navigating;
  assert.equal(ctx.pageNumber, 2); assert.equal(ctx.busy, false);
});

test('a failed page read is propagated without caching an empty replacement page', async () => {
  const ctx = context(['ensurePage']);
  ctx.storage.loadPage = async () => { throw new Error('IDB_PAGE_READ_FAILED'); };
  await assert.rejects(ctx.ensurePage(2), /IDB_PAGE_READ_FAILED/);
  assert.equal(ctx.pages.has(2), false);
  assert.deepEqual(ctx.pages.get(1).map(item => item.id), ['existing']);
});

for (const selection of ['importing', 'opened']) {
  test(`delayed startup catalog cannot replace an explicitly ${selection} PDF`, async () => {
    const reached = deferred(), release = deferred(); let restores = 0;
    const ctx = vm.createContext({
      controls() {}, chooseTool() {}, rootURL: new URL('https://example.test/'), URL,
      params: new URLSearchParams('id=old-lecture'), initialLocal: 'a'.repeat(64),
      explicitSelection: false, current: null, busy: false, catalog: [],
      fetch: async () => { reached.resolve(); await release.promise; return { ok: true, json: async () => ({ documents: [] }) }; },
      openPublished: async () => { restores++; }, openStored: async () => { restores++; }, signal() {}, currentInfo() {},
    });
    vm.runInContext(section('async function init()', 'init().catch('), ctx);
    const startup = ctx.init(); await reached.promise;
    ctx.explicitSelection = true;
    if (selection === 'opened') ctx.current = { ...document }; else ctx.busy = true;
    release.resolve(); await startup;
    assert.equal(restores, 0);
  });
}

test('viewer guards reject drawing, undo and destructive backup replacement',async()=>{
  const ctx=context(['permissions','undo','applyNotebook']);
  ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'shared',role:'viewer',accountId:'member-a',strokeAuthors:[]});
  assert.equal(ctx.canAddInk(),false);ctx.tool='pen';ctx.pointerDown();assert.equal(ctx.active,null);
  ctx.undo();assert.deepEqual(ctx.pages.get(1).map(s=>s.id),['existing']);
  await assert.rejects(ctx.applyNotebook({document,pages:[],position:1,bookmarks:[]},{confirmReplace:true}),/NOTEBOOK_READ_ONLY/);
});

test('contributor swept erasure and undo preserve owner and legacy ink',()=>{
  const ctx=context(['permissions','eraseAt','undo']);
  const owned=stroke('mine'),owner=stroke('owner'),legacy=stroke('legacy');
  ctx.pages.set(1,[owner,legacy,owned]);
  ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'shared',role:'contributor',accountId:'member-a',
    strokeAuthors:[{page:1,id:'owner',accountId:'member-b'},{page:1,id:'legacy',accountId:null},{page:1,id:'mine',accountId:'member-a'}]});
  ctx.eraseAt({x:.1,y:.1},{x:.1,y:.3});
  assert.deepEqual(ctx.pages.get(1).map(s=>s.id),['owner','legacy']);
  const h={undo:[{added:[],removed:[owned]}],redo:[]};ctx.history=()=>h;
  ctx.undo();
  assert.deepEqual(Array.from(ctx.pages.get(1),s=>s.id),['owner','legacy','new-stroke']);
  assert.equal(ctx.strokeAuthors.get('1:new-stroke'),'member-a');
});

test('same PDF notebook changes cannot carry an ownership grant into another notebook',()=>{
  const ctx=context(['permissions']);
  ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'A',role:'contributor',accountId:'member-a',strokeAuthors:[{page:1,id:'existing',accountId:'member-a'}]});
  assert.equal(ctx.canEraseStroke(stroke('existing')),true);
  ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'B',role:'contributor',accountId:'member-a',strokeAuthors:[{page:1,id:'existing',accountId:null}]});
  assert.equal(ctx.canEraseStroke(stroke('existing')),false);
  assert.equal(ctx.canEditAllInk(),false);
});

test('an own erasure remains undoable after authoritative same-notebook sync',async()=>{
  const ctx=context(['permissions','historyEntry','eraseAt','undo','applyNotebook']);
  const own=stroke('mine'),owner=stroke('owner'),remote=stroke('remote-new');let serial=0;ctx.uid=()=>`restored-${++serial}`;
  ctx.pages.set(1,[owner,own]);
  ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'shared',role:'contributor',accountId:'member-a',
    strokeAuthors:[{page:1,id:'owner',accountId:'member-b'},{page:1,id:'mine',accountId:'member-a'}]});
  const before=structuredClone(ctx.state());ctx.eraseAt({x:.1,y:.1},{x:.1,y:.3});ctx.historyEntry(before,ctx.state());
  assert.equal(ctx.history().undo.length,1);
  await ctx.applyNotebook({document,pages:[{number:1,strokes:[owner,remote]}],bookmarks:[],position:1},{silent:true,preserveHistory:true});
  ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'shared',role:'contributor',accountId:'member-a',
    strokeAuthors:[{page:1,id:'owner',accountId:'member-b'},{page:1,id:'mine',accountId:'member-a'},{page:1,id:'remote-new',accountId:'member-b'}]});
  assert.equal(ctx.history().undo.length,1);ctx.undo();
  assert.deepEqual(Array.from(ctx.state(),s=>s.id),['owner','remote-new','restored-1']);
  assert.deepEqual(ctx.pages.get(1).find(s=>s.id==='restored-1').points,own.points);
  ctx.undo(true);assert.deepEqual(Array.from(ctx.state(),s=>s.id),['owner','remote-new']);
  ctx.undo();assert.deepEqual(Array.from(ctx.state(),s=>s.id),['owner','remote-new','restored-2']);
});

test('delta undo and redo preserve unseen remote ink and never resurrect its later erasure',async()=>{
  const ctx=context(['permissions','historyEntry','undo','applyNotebook']);
  const old=stroke('old-remote'),mine=stroke('local-addition'),remote=stroke('unseen-remote');let serial=0;ctx.uid=()=>`redo-${++serial}`;
  ctx.pages.set(1,[old,mine]);ctx.historyEntry([old],[old,mine]);
  await ctx.applyNotebook({document,pages:[{number:1,strokes:[old,mine,remote]}],bookmarks:[],position:1},{silent:true,preserveHistory:true});
  ctx.undo();assert.deepEqual(Array.from(ctx.state(),s=>s.id),['old-remote','unseen-remote']);
  ctx.undo(true);assert.deepEqual(Array.from(ctx.state(),s=>s.id),['old-remote','unseen-remote','redo-1']);
  await ctx.applyNotebook({document,pages:[{number:1,strokes:[remote,ctx.state().find(s=>s.id==='redo-1')]}],bookmarks:[],position:1},{silent:true,preserveHistory:true});
  ctx.undo();assert.deepEqual(Array.from(ctx.state(),s=>s.id),['unseen-remote']);
});

test('contributor inverse history cannot remove or restore a nonowned stroke',()=>{
  const ctx=context(['permissions','undo']);
  const present=stroke('other-present'),absent=stroke('other-erased');ctx.pages.set(1,[present]);
  ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'shared',role:'contributor',accountId:'member-a',
    strokeAuthors:[{page:1,id:'other-present',accountId:'member-b'},{page:1,id:'other-erased',accountId:null}]});
  ctx.history().undo.push({added:[present],removed:[absent]});ctx.undo();
  assert.deepEqual(Array.from(ctx.state(),s=>s.id),['other-present']);assert.equal(ctx.history().redo.length,0);
});

test('explicit replacement and role changes clear local inverse history',async()=>{
  const ctx=context(['permissions','historyEntry','applyNotebook']);
  const own=stroke('local');ctx.historyEntry([],[own]);
  await ctx.applyNotebook({document,pages:[],bookmarks:[],position:1},{confirmReplace:true,preserveHistory:true});
  assert.equal(ctx.histories.size,0);
  ctx.historyEntry([],[own]);ctx.setPermissions({fingerprint:document.fingerprint,notebookId:'shared',role:'viewer',accountId:'member-a',strokeAuthors:[]});
  assert.equal(ctx.histories.size,0);
});

function publicReadHarness(options = {}) {
  const rootURL = new URL('https://example.test/AI_Tech_Review/'), messages = [], nodes = new Map(), listeners = new Map();
  let focused = options.focused !== false;
  const subscribe = target => (name, handler) => {
    const key = target + ':' + name;
    if (!listeners.has(key)) listeners.set(key, []);
    listeners.get(key).push(handler);
  };
  const worker = { postMessage(value) { if (options.postFails) throw Error('unavailable'); messages.push(structuredClone(value)); } };
  const ctx = {
    URL, URLSearchParams, Uint8Array, Blob, crypto: webcrypto, rootURL, MAX_PAGES: 100,
    current: null, pdf: null, pdfLoadingTask: null, pdfBytes: null, busy: false, active: null,
    mutationRevision: 0, documentOpenGeneration: 0, metaVersion: 0, metaSaved: 0, pageNumber: 1,
    pages: new Map(), histories: new Map(), dirty: new Map(), versions: new Map(), retiredIds: new Set(), strokeAuthors: new Map(),
    catalog: [{ id: 'published-a', href: 'archive/files/published-a.pdf', sha256: 'a'.repeat(64) }],
    location: { href: new URL('lectures/reader/?id=published-a', rootURL).href },
    document: { visibilityState: options.hidden ? 'hidden' : 'visible', hasFocus: () => focused, addEventListener: subscribe('document') },
    navigator: { serviceWorker: options.noServiceWorker ? undefined : {
      controller: options.lookup ? null : worker,
      getRegistration: async url => { assert.equal(url, rootURL.href); return options.lookup(worker); },
      register() { assert.fail('reading must never register a service worker'); },
    } },
    $: id => { if (!nodes.has(id)) nodes.set(id, { hidden: false, textContent: '' }); return nodes.get(id); },
    sheet: { dataset: {} }, permissions: {},
    pdfjs: { getDocument: () => ({ promise: Promise.resolve({ numPages: 2 }) }) },
    storage: { getDocument: async () => null, putDocument: async () => {} },
    controls() {}, finishStroke() {}, flush: async () => true, ensurePage: async () => {},
    renderPage: options.render || (async () => {}), renderBookmarks() {}, renderEditions() {},
    clamp: (value, low, high) => Math.min(high, Math.max(low, value)), status() {}, storageFailure() {}, showError() {}, t: value => value,
    currentInfo: () => ctx.current, setTimeout, clearTimeout,
  };
  ctx.window = { addEventListener: subscribe('window'), history: { replaceState(_state, _title, url) { ctx.location.href = String(url); } } };
  ctx.window.self = ctx.window; ctx.window.top = options.framed ? {} : ctx.window;
  const emit = (target, name) => { for (const handler of listeners.get(target + ':' + name) || []) handler({}); };
  ctx.signal = name => emit('window', name);
  vm.createContext(ctx);
  vm.runInContext(section('async function openBytes(', 'function showError(').replaceAll('import.meta.url', JSON.stringify(rootURL.href)) +
    section("document.addEventListener('visibilitychange'", 'initializeReaderFullscreen();'), ctx);
  return { ctx, messages, emit, focus: value => { focused = value; },
    open: (publicId = 'published-a') => ctx.openBytes(new Uint8Array([37, 80, 68, 70]).buffer,
      { publicId, title: 'Private title must never enter an alert message' }) };
}

test('only a successfully rendered visible public PDF acknowledges its public alert through the existing worker', async () => {
  const rendered = deferred(), entered = deferred();
  const qa = publicReadHarness({ render: async () => { entered.resolve(); await rendered.promise; } });
  const opening = qa.open(); await entered.promise;
  qa.emit('window', 'focus'); assert.deepEqual(qa.messages, [], 'pending rendering is not a read');
  rendered.resolve(); assert.equal(await opening, true);
  assert.deepEqual(qa.messages, [{ type: 'atr-reader-article-read', articleId: 'lecture:published-a',
    url: 'https://example.test/AI_Tech_Review/archive/files/published-a.pdf' }]);
});

test('a public PDF first rendered while hidden waits for visibility and real focus', async () => {
  const qa = publicReadHarness({ hidden: true, focused: false });
  await qa.open(); assert.deepEqual(qa.messages, []);
  qa.ctx.document.visibilityState = 'visible'; qa.emit('document', 'visibilitychange');
  assert.deepEqual(qa.messages, []);
  qa.focus(true); qa.emit('window', 'focus');
  assert.equal(qa.messages.length, 1);
});

test('private, unknown, framed, mismatched and failed-render documents never acknowledge public alerts', async () => {
  for (const options of [{ id: null }, { id: 'unknown' }, { framed: true },
    { render: async () => { throw Error('render failed'); } }, { mismatch: true }]) {
    const qa = publicReadHarness({ ...options, hidden: true });
    await qa.open(Object.hasOwn(options, 'id') ? options.id : 'published-a');
    if (options.mismatch) qa.ctx.location.href = qa.ctx.location.href.replace('id=published-a', 'id=other');
    qa.ctx.document.visibilityState = 'visible'; qa.emit('document', 'visibilitychange'); qa.emit('window', 'focus');
    assert.deepEqual(qa.messages, []);
  }
});

test('existing registration lookup cannot send a late public read after document selection changes', async () => {
  for (const change of ['selection', 'document', 'focus', 'visibility', 'query', 'catalog']) {
    const lookup = deferred(); let lookups = 0;
    const qa = publicReadHarness({ lookup: async worker => { lookups++; await lookup.promise; return { active: worker }; } });
    await qa.open(); await new Promise(resolve => setImmediate(resolve));
    assert.equal(lookups, 1);
    if (change === 'selection') qa.ctx.documentOpenGeneration++;
    if (change === 'document') qa.ctx.current = { ...qa.ctx.current };
    if (change === 'focus') qa.focus(false);
    if (change === 'visibility') qa.ctx.document.visibilityState = 'hidden';
    if (change === 'query') qa.ctx.location.href = qa.ctx.location.href.replace('id=published-a', 'id=other');
    if (change === 'catalog') qa.ctx.catalog = [];
    lookup.resolve(); await new Promise(resolve => setImmediate(resolve));
    assert.deepEqual(qa.messages, [], change + ' changed during the lookup');
  }
});

test('a public read can reuse an already active registration without creating a new worker', async () => {
  const qa = publicReadHarness({ lookup: async worker => ({ active: worker }) });
  assert.equal(await qa.open(), true); await new Promise(resolve => setImmediate(resolve));
  assert.equal(qa.messages.length, 1);
});

test('missing or failing existing workers cannot prevent a public PDF from opening', async () => {
  for (const options of [{ noServiceWorker: true }, { lookup: async () => undefined },
    { lookup: async () => { throw Error('unavailable'); } }, { postFails: true }]) {
    const qa = publicReadHarness(options); assert.equal(await qa.open(), true);
    await new Promise(resolve => setImmediate(resolve)); assert.deepEqual(qa.messages, []);
  }
});

function saveFeedbackHarness(options = {}) {
  let now = 20_000, nextTimer = 0, text = 'saved', painted = 'saved';
  const timers = new Map(), callbacks = new Map(), writes = [], stored = [], events = [];
  const clock = {
    setTimeout(callback, delay) { const id = ++nextTimer; timers.set(id, { callback, due: now + delay }); callbacks.set(id, callback); return id; },
    clearTimeout(id) { timers.delete(id); },
    advance(delay) {
      const target = now + delay;
      for (;;) {
        const due = [...timers.entries()].filter(([, value]) => value.due <= target).sort((a, b) => a[1].due - b[1].due)[0];
        if (!due) break;
        now = due[1].due; timers.delete(due[0]); due[1].callback();
      }
      now = target;
    },
    queued(id) { assert.ok(callbacks.has(id), 'the timer callback must have been scheduled'); callbacks.get(id)(); },
  };
  const node = { dataset: {} };
  Object.defineProperty(node.dataset, 'state', { get: () => painted, set: value => { painted = value; writes.push(['state', value]); } });
  Object.defineProperty(node, 'textContent', { get: () => text, set: value => { text = value; writes.push(['text', value]); } });
  class ClockDate extends Date { static now() { return now; } }
  const ctx = {
    current: { ...document, bookmarks: [] }, documentOpenGeneration: 0, pageNumber: 1, active: null, tool: 'pen',
    readerResizePending: false, scheduleReaderResize() {},
    saveFeedbackTimer: null, saveFeedbackEpoch: 0, saveFeedbackOwner: null, saveFeedbackGeneration: -1,
    saveFeedbackShownAt: 0, saveFeedbackWanted: 'ready',
    saveTimer: null, writeQueue: Promise.resolve(true), metaVersion: 0, metaSaved: 0, mutationRevision: 0, lastStorageError: 0,
    versions: new Map(), dirty: new Map(), pages: new Map([[1, [stroke('saved-ink')]]]),
    $: id => id === 'save-state' ? node : { checked: false }, t: key => key, toast() {},
    clone: structuredClone, Date: ClockDate, setTimeout: clock.setTimeout, clearTimeout: clock.clearTimeout,
    currentInfo: () => ({ fingerprint: ctx.current?.fingerprint }), signal: (type, detail) => events.push({ type, detail }),
    historyEntry() {}, state: () => ctx.pages.get(ctx.pageNumber), requestInk() {}, inkCanvas: { releasePointerCapture() {}, style: {} },
    storage: {
      async savePage(fingerprint, number, strokes, meta) { stored.push(structuredClone({ type: 'page', fingerprint, number, strokes, meta })); await options.savePage?.(); },
      async saveMetadata(fingerprint, meta) { stored.push(structuredClone({ type: 'meta', fingerprint, meta })); await options.saveMetadata?.(); },
    },
  };
  vm.createContext(ctx);
  const feedbackStart = source.includes('function paintSaveStatus(') ? 'function paintSaveStatus(' : 'function status(';
  vm.runInContext(section(feedbackStart, 'function toast(') + section('function storageFailure(', 'function currentInfo(') +
    section('function markDirty(', 'function drawStroke(') + section('function finishStroke(', 'function chooseTool('), ctx);
  ctx.status('saved'); writes.length = 0;
  return { ctx, clock, node, writes, stored, events };
}

test('fast ink saves retain the saved display without changing the 350ms write debounce or stored strokes', async () => {
  const qa = saveFeedbackHarness();
  qa.ctx.markDirty();
  assert.equal(qa.node.dataset.state, 'saved', 'pending feedback waits 600ms');
  assert.deepEqual(qa.writes, []);
  qa.clock.advance(349); assert.equal(qa.stored.length, 0);
  qa.clock.advance(1); await qa.ctx.writeQueue;
  assert.deepEqual(qa.stored, [{ type: 'page', fingerprint: document.fingerprint, number: 1,
    strokes: [stroke('saved-ink')], meta: { position: 1, bookmarks: [] } }]);
  qa.clock.advance(600); assert.deepEqual(qa.writes, [], 'a fast completion must not rewrite an unchanged saved display');
  assert.equal(qa.events.length, 1); assert.equal(qa.events[0].type, 'atr:notes-saved');
  assert.equal(qa.events[0].detail.metadataOnly, false);
});

test('metadata keeps its 250ms debounce and pen-up still flushes immediately without visible feedback flicker', async () => {
  const meta = saveFeedbackHarness(); meta.ctx.markMeta(); meta.clock.advance(249); assert.equal(meta.stored.length, 0);
  meta.clock.advance(1); await meta.ctx.writeQueue;
  assert.deepEqual(meta.stored, [{ type: 'meta', fingerprint: document.fingerprint, meta: { position: 1, bookmarks: [] } }]);
  assert.equal(meta.events[0].detail.metadataOnly, true); assert.deepEqual(meta.writes, []);
  const pen = saveFeedbackHarness(); pen.ctx.active = { before: [], page: 1, id: 'pen-1' };
  pen.ctx.finishStroke(); await pen.ctx.writeQueue;
  assert.equal(pen.stored.length, 1, 'finishing the stroke must not wait for any UI or save timer');
  assert.deepEqual(pen.writes, []);
});

test('long saves show pending at the first 600ms deadline and keep it visible for at least 300ms', async () => {
  const gate = deferred(), qa = saveFeedbackHarness({ savePage: () => gate.promise });
  qa.ctx.markDirty(); qa.clock.advance(200); qa.ctx.markDirty();
  qa.clock.advance(350); await new Promise(resolve => setImmediate(resolve)); assert.equal(qa.stored.length, 1);
  qa.clock.advance(49); assert.equal(qa.node.dataset.state, 'saved');
  qa.clock.advance(1); assert.equal(qa.node.dataset.state, 'pending', 'repeated pointer changes must not postpone feedback');
  qa.clock.advance(50); gate.resolve(); await qa.ctx.writeQueue;
  assert.equal(qa.node.dataset.state, 'pending');
  qa.clock.advance(249); assert.equal(qa.node.dataset.state, 'pending');
  qa.clock.advance(1); assert.equal(qa.node.dataset.state, 'saved');
});

test('save errors display immediately, survive pending retries, and clear only after a successful save', async () => {
  let failing = true; const retry = deferred();
  const qa = saveFeedbackHarness({ savePage: async () => { if (failing) throw Error('STORAGE_FAILED'); await retry.promise; } });
  qa.ctx.markDirty(); assert.equal(await qa.ctx.flush(), false);
  assert.equal(qa.node.dataset.state, 'error');
  failing = false; qa.ctx.markDirty(); qa.clock.advance(1000); await new Promise(resolve => setImmediate(resolve));
  assert.equal(qa.node.dataset.state, 'error', 'pending retry must not hide a known save failure');
  retry.resolve(); await qa.ctx.writeQueue;
  assert.equal(qa.node.dataset.state, 'saved'); assert.equal(qa.events.length, 1);
});

test('queued callbacks from a cancelled feedback cycle cannot clear a newer timer or overwrite its state', () => {
  const qa = saveFeedbackHarness();
  qa.ctx.status('pending'); const oldTimer = qa.ctx.saveFeedbackTimer;
  qa.ctx.status('saved'); qa.ctx.status('pending'); const newTimer = qa.ctx.saveFeedbackTimer;
  qa.clock.queued(oldTimer);
  assert.equal(qa.ctx.saveFeedbackTimer, newTimer);
  assert.equal(qa.node.dataset.state, 'saved');
  qa.clock.advance(600); assert.equal(qa.node.dataset.state, 'pending');
  qa.ctx.status('saved'); const savedTimer = qa.ctx.saveFeedbackTimer;
  qa.ctx.status('error'); qa.clock.queued(savedTimer);
  assert.equal(qa.node.dataset.state, 'error', 'a queued delayed completion must not hide an error');
});

test('feedback timers and late owners cannot paint across document identity or selection generations', () => {
  for (const changed of ['document', 'generation']) {
    const qa = saveFeedbackHarness(), owner = qa.ctx.current;
    qa.ctx.status('pending'); const timer = qa.ctx.saveFeedbackTimer;
    if (changed === 'document') qa.ctx.current = { ...owner };
    else qa.ctx.documentOpenGeneration++;
    qa.clock.queued(timer);
    assert.equal(qa.node.dataset.state, 'saved', changed + ' invalidates an old pending timer');
  }
  const qa = saveFeedbackHarness(), old = qa.ctx.current;
  qa.ctx.current = { ...old, fingerprint: 'b'.repeat(64) }; qa.ctx.documentOpenGeneration++;
  qa.ctx.status('saved'); qa.writes.length = 0;
  qa.ctx.status('pending', old); qa.ctx.storageFailure(old); qa.ctx.status('saved', old);
  qa.clock.advance(1000);
  assert.deepEqual(qa.writes, [], 'late status/error calls from the previous document are ignored');
});
