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
    section("document.addEventListener('visibilitychange'", 'let resizeTimer;'), ctx);
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
