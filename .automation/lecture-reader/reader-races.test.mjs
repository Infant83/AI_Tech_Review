import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

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
    pages: new Map([[1, [stroke('existing')]]]), histories: new Map(), dirty: new Map(),
    metaSaved: 0, metaVersion: 0, mutationRevision: 0,
    NOTEBOOK_FORMAT: 'ai-tech-review-notebook', clone: structuredClone,
    validateNotebook: value => value, uid: () => 'new-stroke', confirm: () => true, t: value => value,
    clamp: (value, min, max) => Math.min(max, Math.max(min, value)),
    controls: () => {}, finishStroke: () => {}, renderBookmarks: () => {},
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
