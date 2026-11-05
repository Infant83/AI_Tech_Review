import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { webcrypto } from 'node:crypto';
import vm from 'node:vm';

// Exercise production orchestration with delayed cache, fetch and file reads.
// The PDF renderer is the terminal boundary: only the latest intent may reach it.
const reader = await readFile(new URL('./reader.mjs', import.meta.url), 'utf8');
const cloud = await readFile(new URL('./cloud.mjs', import.meta.url), 'utf8');
function section(source, start, end) {
  const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Missing production function: ${start}`);
  return source.slice(a, b);
}
function deferred() { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; }
const a = 'a'.repeat(64), b = 'b'.repeat(64);
const metadata = fingerprint => ({ id: `book-${fingerprint[0]}`, fingerprint, title: fingerprint[0], publicId: null });
const cached = fingerprint => ({ fingerprint, title: fingerprint[0], pdf: { arrayBuffer: async () => new ArrayBuffer(4) } });
function harness(overrides = {}) {
  let visible = b;
  const listeners = new Map(), events = [], opened = [], errors = [], activated = [], warnings = [];
  const nodes = new Map([
    ['import-pdf', { before(node) { nodes.set(node.id, node); }, setAttribute() {}, removeAttribute() {}, focus() {} }],
    ['original-link', { hidden: false }],
  ]);
  const context = {
    requestedId: null, selection: null, notebookOpenGeneration: 0, documentOpenGeneration: 0,
    requestedLocalPDF: null, explicitSelection: false, busy: false, retry: null, en: false,
    account: { id: 'owner' }, active: null, inviteToken: null, path: '/v1/study', idPattern: /^[A-Za-z0-9_-]+$/,
    URL, URLSearchParams, Uint8Array, crypto: webcrypto,
    location: { href: 'https://example.test/reader/?notebook=book-a', assign() { throw Error('Unexpected navigation'); } },
    history: { state: null, replaceState(_state, _title, href) { context.location.href = href; } },
    current: () => ({ fingerprint: visible, busy: false, drawing: false }),
    storage: { getDocument: async fingerprint => cached(fingerprint), listDocuments: async () => [] },
    openBytes: async (_bytes, value) => { visible = value.sha256 || `local:${value.title}`; opened.push(visible); return true; },
    activate: async value => { activated.push(value.id); }, matches: () => false,
    showError: value => errors.push(value), toast: value => warnings.push(value), status() {}, t: key => key,
    error: code => Error(code), safeMetadata: value => value, stateKey: (...values) => values.join(':'), linkKey: (...values) => values.join(':'),
    readStore: async () => null, showLibrary: async () => {}, closeDialogs() {},
    catalog: [{ id: 'published-a', href: 'a.pdf', sha256: a, title: 'A' }], rootURL: new URL('https://example.test/'),
    document: { createElement: () => ({ attributes: {}, setAttribute(key, value) { this.attributes[key] = value; }, remove() { nodes.delete(this.id); } }) },
    $: key => nodes.get(key),
    dialog: { open: true, close() { this.open = false; } },
    CustomEvent: class { constructor(type, { detail } = {}) { this.type = type; this.detail = detail; } },
    ...overrides,
  };
  context.window = {
    ATRNotebook: {},
    addEventListener(name, callback) { if (!listeners.has(name)) listeners.set(name, []); listeners.get(name).push(callback); },
    dispatchEvent(event) { events.push(event); for (const callback of listeners.get(event.type) || []) callback(event); },
  };
  context.signal = (name, detail) => context.window.dispatchEvent(new context.CustomEvent(name, { detail }));
  vm.createContext(context);
  vm.runInContext(
    section(reader, 'function beginDocumentOpen(', 'function status(') +
    section(reader, 'async function openPublished(', 'function closeDialogs(') +
    section(reader, 'function clearLocalPDFRequest(', 'async function showLibrary(') +
    section(cloud, 'async function openNotebook(', 'async function activate(') +
    section(cloud, 'async function resume()', 'async function documentOpened(') +
    section(reader, "window.addEventListener('atr:cloud-document-request'", "$('library-dialog').addEventListener("),
    context,
  );
  context.window.ATRNotebook.openStored = context.openStored;
  return { context, events, opened, errors, activated, warnings, nodes, visible: () => visible,
    choose: async fingerprint => {
      const intent = context.beginDocumentOpen({ explicit: true, fingerprint });
      context.clearLocalPDFRequest(context.requestedLocalPDF !== fingerprint);
      return context.openStored(fingerprint, { intent });
    } };
}

for (const delayAt of ['metadata', 'bytes']) test(`a newer explicit PDF wins over a delayed private cache ${delayAt} read`, async () => {
  const held = deferred(), entered = deferred();
  const qa = harness({ storage: { async getDocument(fingerprint) {
    if (fingerprint !== a) return cached(fingerprint);
    if (delayAt === 'metadata') { entered.resolve(); await held.promise; return cached(a); }
    return { ...cached(a), pdf: { async arrayBuffer() { entered.resolve(); await held.promise; return new ArrayBuffer(4); } } };
  } } });
  const first = qa.context.openNotebook(metadata(a)); await entered.promise;
  await qa.choose(b); held.resolve(); await first;
  assert.deepEqual(qa.opened, [b]); assert.equal(qa.visible(), b);
  assert.equal(qa.context.requestedId, null); assert.equal(qa.context.selection, null);
  assert.equal(new URL(qa.context.location.href).searchParams.has('notebook'), false);
  assert.equal(qa.events.some(event => event.type === 'atr:cloud-open-local'), false);
});

test('an obsolete missing-cache result does not reopen the old private-file prompt', async () => {
  const held = deferred();
  const qa = harness({ storage: { getDocument: async fingerprint => fingerprint === a ? held.promise : cached(b) } });
  const first = qa.context.openNotebook(metadata(a)); await qa.choose(b); held.resolve(null); await first;
  assert.deepEqual(qa.opened, [b]); assert.deepEqual(qa.errors, []);
  assert.equal(qa.events.some(event => event.type === 'atr:cloud-open-local'), false);
});

test('selecting the already displayed cloud notebook also invalidates a pending cache open', async () => {
  const held = deferred();
  const qa = harness({ storage: { getDocument: async fingerprint => fingerprint === a ? held.promise : cached(b) } });
  const first = qa.context.openNotebook(metadata(a));
  await qa.context.openNotebook(metadata(b)); held.resolve(cached(a)); await first;
  assert.deepEqual(qa.opened, []); assert.deepEqual(qa.activated, ['book-b']); assert.equal(qa.visible(), b);
  assert.equal(qa.context.requestedId, 'book-b');
});

test('a late requested-notebook lookup cannot restore a target cancelled by manual selection', async () => {
  const held = deferred(), qa = harness({ requestedId: 'book-a', api: async () => held.promise });
  const first = qa.context.resume(); await qa.choose(b);
  held.resolve({ notebook: metadata(a) }); await first;
  assert.deepEqual(qa.opened, [b]); assert.deepEqual(qa.activated, []); assert.equal(qa.context.requestedId, null);
});

test('an automatic cached-link resume cannot activate after a newer document selection', async () => {
  const held = deferred(), qa = harness({ readStore: async store => store === 'links' ? held.promise : { metadata: metadata(b) } });
  const first = qa.context.resume(); await qa.choose(b); held.resolve({ notebookId: 'book-b' }); await first;
  assert.deepEqual(qa.activated, []); assert.deepEqual(qa.opened, [b]);
});

for (const delayAt of ['response', 'bytes']) test(`a delayed public PDF ${delayAt} cannot replace a newer private selection`, async () => {
  const held = deferred(), entered = deferred();
  const qa = harness({ fetch: async () => {
    if (delayAt === 'response') { entered.resolve(); await held.promise; }
    return { ok: true, async arrayBuffer() { if (delayAt === 'bytes') { entered.resolve(); await held.promise; } return new ArrayBuffer(4); } };
  } });
  const first = qa.context.openPublished('published-a'); await entered.promise;
  await qa.choose(b); held.resolve(); assert.equal(await first, false);
  assert.deepEqual(qa.opened, [b]); assert.deepEqual(qa.errors, []);
});

test('a delayed public-cache fallback cannot supersede a newer selection', async () => {
  const held = deferred(), entered = deferred();
  const qa = harness({ fetch: async () => { throw Error('offline'); }, storage: {
    getDocument: async fingerprint => cached(fingerprint),
    async listDocuments() { entered.resolve(); return held.promise; },
  } });
  const first = qa.context.openPublished('published-a'); await entered.promise;
  await qa.choose(b); held.resolve([{ ...cached(a), publicId: 'published-a' }]); await first;
  assert.deepEqual(qa.opened, [b]); assert.deepEqual(qa.errors, []);
});

test('a delayed local-file read cannot replace a newer cached PDF selection', async () => {
  const held = deferred(), qa = harness();
  const first = qa.context.importPDFFile({ name: 'A.pdf', type: 'application/pdf', size: 4, arrayBuffer: () => held.promise });
  await qa.choose(b); held.resolve(new ArrayBuffer(4)); await first;
  assert.deepEqual(qa.opened, [b]);
});

test('explicitly retrying an imported PDF invalidates an older cache request', async () => {
  const held = deferred(), entered = deferred();
  const qa = harness({ storage: { getDocument: async () => { entered.resolve(); return held.promise; } } });
  await qa.context.importPDFFile({ name: 'B.pdf', type: 'application/pdf', size: 4, arrayBuffer: async () => new ArrayBuffer(4) });
  const first = qa.context.openStored(a); await entered.promise;
  await qa.context.retry(); held.resolve(cached(a)); await first;
  assert.deepEqual(qa.opened, ['local:B', 'local:B']);
});

test('a wrong requested original shows a modal error and a subsequent matching file retains the cloud target', async () => {
  const bytes = new Uint8Array([37, 80, 68, 70]), fingerprint = Buffer.from(await webcrypto.subtle.digest('SHA-256', bytes)).toString('hex');
  const qa = harness({ storage: { getDocument: async () => null } });
  await qa.context.openNotebook({ ...metadata(fingerprint), id: 'private' });
  await qa.context.requestLocalPDF({ fingerprint, title: 'Original' });
  await qa.context.importPDFFile({ name: 'wrong.pdf', type: 'application/pdf', size: 1, arrayBuffer: async () => new Uint8Array([1]).buffer });
  assert.deepEqual(qa.opened, []); assert.equal(qa.context.requestedId, 'private');
  assert.equal(qa.context.requestedLocalPDF, fingerprint);
  assert.equal(qa.nodes.get('local-pdf-request').textContent, 'requestedPDFMismatch');
  assert.equal(qa.nodes.get('local-pdf-request').attributes.role, 'alert');
  await qa.context.importPDFFile({ name: 'right.pdf', type: 'application/pdf', size: bytes.length, arrayBuffer: async () => bytes.buffer });
  assert.deepEqual(qa.opened, [fingerprint]); assert.equal(qa.context.requestedId, 'private');
  assert.equal(qa.context.selection.fingerprint, fingerprint); assert.equal(qa.context.requestedLocalPDF, null);
  assert.equal(qa.events.some(event => event.type === 'atr:cloud-local-cancel'), false);
});

test('choosing the expected cached PDF preserves its target while invalidating the older cache probe', async () => {
  const held = deferred(); let first = true;
  const qa = harness({ storage: { async getDocument(fingerprint) {
    if (first) { first = false; return held.promise; } return cached(fingerprint);
  } } });
  const pending = qa.context.openNotebook(metadata(a)); await qa.choose(a); held.resolve(cached(a)); await pending;
  assert.deepEqual(qa.opened, [a]); assert.equal(qa.context.requestedId, 'book-a');
  assert.equal(qa.context.selection.fingerprint, a);
});

test('cancelling a requested-file prompt also cancels its pending file read', async () => {
  const bytes = new Uint8Array([37, 80, 68, 70]), fingerprint = Buffer.from(await webcrypto.subtle.digest('SHA-256', bytes)).toString('hex');
  const held = deferred(), qa = harness();
  qa.context.selection = { ...metadata(fingerprint), id: 'private' }; qa.context.requestedId = 'private';
  await qa.context.requestLocalPDF({ fingerprint, title: 'Original' });
  const first = qa.context.importPDFFile({ name: 'right.pdf', type: 'application/pdf', size: bytes.length, arrayBuffer: () => held.promise });
  qa.context.clearLocalPDFRequest(true); held.resolve(bytes.buffer); await first;
  assert.deepEqual(qa.opened, []); assert.equal(qa.context.requestedId, null); assert.equal(qa.context.selection, null);
});
