import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { webcrypto } from 'node:crypto';
import vm from 'node:vm';

// Run the actual UI functions with deterministic file/cache boundaries.
const reader = await readFile(new URL('./reader.mjs', import.meta.url), 'utf8');
const cloud = await readFile(new URL('./cloud.mjs', import.meta.url), 'utf8');
function section(source, start, end) {
  const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Missing production function: ${start}`);
  return source.slice(a, b);
}
const fingerprint = 'a'.repeat(64), otherFingerprint = 'b'.repeat(64);

for (const bound of [false, true]) test(`logout ${bound ? 'keeps account-bound ink locked' : 'restores anonymous local writing'}`, async () => {
  const view = { fingerprint, busy: false, drawing: false, role: 'local' };
  const marker = bound ? { stateKey: 'member:book', accountId: 'member', transition: false } : null;
  const ctx = { path: '/v1/study', account: { id: 'member' }, active: null, epoch: 0, authGeneration: 0, activationGeneration: 0, workingGeneration: 0,
    window: { ATRNotebook: { current: () => view, setPermissions: value => { view.role = value.role; } } },
    workingKey: value => value, readStore: async store => store === 'links' ? marker : { accountId: 'member', metadata: { role: 'owner' } },
    stopSession: async () => {}, exported: async () => ({ document: { fingerprint } }), preserveDisplayed: async () => {},
    api: async () => ({ ok: true }), status() {}, render: async () => {}, t: key => key,
  };
  vm.createContext(ctx);
  vm.runInContext(section(cloud, 'function lockReader()', 'function workingToken(') + section(cloud, 'async function logout()', 'async function enableCurrent('), ctx);
  await ctx.logout();
  assert.equal(ctx.account, null); assert.equal(view.role, bound ? 'viewer' : 'local');
});

for (const cached of [true, false]) test(`private notebook open ${cached ? 'uses the cached original and closes the modal' : 'requests an actionable local-file prompt'}`, async () => {
  const events = []; let closed = 0, lookups = 0;
  const ctx = { requestedId: null, selection: null, active: null, notebookOpenGeneration: 0, account: { id: 'member' }, current: () => ({ fingerprint: otherFingerprint }),
    window: { addEventListener() {}, ATRNotebook: { openStored: async (id, options) => { lookups++; assert.equal(id, fingerprint); assert.equal(options.quietMissing, true); return cached; } }, dispatchEvent: event => events.push(event) },
    CustomEvent: class { constructor(type, options = {}) { this.type = type; this.detail = options.detail; } },
    dialog: { open: true, close() { closed++; this.open = false; } }, status() {}, t: key => key,
  };
  vm.createContext(ctx);
  vm.runInContext(section(cloud, 'async function openNotebook(', "window.addEventListener('atr:cloud-local-cancel'"), ctx);
  await ctx.openNotebook({ id: 'private-book', fingerprint, title: 'My original PDF', publicId: null });
  assert.equal(lookups, 1); assert.equal(closed, 1);
  assert.equal(events.filter(event => event.type === 'atr:cloud-document-request').length, 1);
  const prompts = events.filter(event => event.type === 'atr:cloud-open-local');
  assert.equal(prompts.length, cached ? 0 : 1);
  if (!cached) assert.equal(prompts[0].detail.title, 'My original PDF');
});

test('missing cache probes leave the existing document free of a load-error screen', async () => {
  let errors = 0;
  const ctx = vm.createContext({ busy: false, documentOpenGeneration: 0, explicitSelection: false, signal() {}, storage: { getDocument: async () => null }, showError: () => { errors++; }, t: key => key });
  vm.runInContext(section(reader, 'function beginDocumentOpen(', 'function status(') + section(reader, 'async function openStored(', 'function closeDialogs('), ctx);
  assert.equal(await ctx.openStored(fingerprint, { quietMissing: true }), false); assert.equal(errors, 0);
  assert.equal(await ctx.openStored(fingerprint), false); assert.equal(errors, 1);
});

function pickerContext() {
  const nodes = new Map(), events = []; let libraryOpened = 0, focused = false;
  const importButton = { before: node => nodes.set(node.id, node), setAttribute() {}, removeAttribute() {}, focus: () => { focused = true; } };
  nodes.set('import-pdf', importButton); nodes.set('original-link', { hidden: false });
  const ctx = { requestedLocalPDF: null, en: false, busy: false, explicitSelection: false, documentOpenGeneration: 0, retry: null,
    $: key => nodes.get(key), document: { createElement: () => ({ setAttribute() {}, remove() { nodes.delete(this.id); } }) },
    showLibrary: async () => { libraryOpened++; }, signal: (name, detail) => events.push({ name, detail }),
    crypto: webcrypto, Uint8Array, t: key => key, toast() {}, clearLocalPDFRequest: undefined,
  };
  vm.createContext(ctx);
  vm.runInContext(section(reader, 'function beginDocumentOpen(', 'function status(') + section(reader, 'function clearLocalPDFRequest(', 'async function showLibrary('), ctx);
  return { ctx, nodes, events, opened: () => libraryOpened, focused: () => focused };
}

test('a missing private original opens visible guidance and focuses a real file-selection button', async () => {
  const qa = pickerContext();
  await qa.ctx.requestLocalPDF({ fingerprint, title: 'My original' });
  assert.equal(qa.opened(), 1); assert.equal(qa.focused(), true);
  assert.match(qa.nodes.get('local-pdf-request').textContent, /My original/);
  assert.match(qa.nodes.get('local-pdf-request').textContent, /내 PDF 가져오기/);
  qa.ctx.clearLocalPDFRequest(true);
  assert.equal(qa.events[0].name, 'atr:cloud-local-cancel'); assert.equal(qa.ctx.requestedLocalPDF, null);
});

test('a wrong PDF in the requested-file flow preserves the current document and prompt', async () => {
  const qa = pickerContext(); let opened = 0, closed = 0, warning;
  await qa.ctx.requestLocalPDF({ fingerprint, title: 'Required original' });
  qa.ctx.openBytes = async () => { opened++; }; qa.ctx.closeDialogs = () => { closed++; }; qa.ctx.toast = key => { warning = key; };
  await qa.ctx.importPDFFile({ name: 'different.pdf', type: 'application/pdf', size: 3, arrayBuffer: async () => new Uint8Array([1, 2, 3]).buffer });
  assert.equal(opened, 0); assert.equal(closed, 0); assert.equal(qa.ctx.requestedLocalPDF, fingerprint);
  assert.equal(warning, 'requestedPDFMismatch'); assert.ok(qa.nodes.has('local-pdf-request'));
});

test('a matching selected PDF preserves notebook selection before closing its picker', async () => {
  const qa = pickerContext(), bytes = new Uint8Array([37, 80, 68, 70]);
  const expected = Buffer.from(await webcrypto.subtle.digest('SHA-256', bytes)).toString('hex');
  await qa.ctx.requestLocalPDF({ fingerprint: expected, title: 'Required original' });
  let metadata;
  qa.ctx.closeDialogs = () => { qa.ctx.clearLocalPDFRequest(true); };
  qa.ctx.openBytes = async (_bytes, value) => { metadata = value; return true; };
  await qa.ctx.importPDFFile({ name: 'original.pdf', type: 'application/pdf', size: 4, arrayBuffer: async () => bytes.buffer });
  assert.equal(metadata.sha256, expected); assert.equal(qa.events.filter(event => event.name === 'atr:cloud-local-cancel').length, 0);
  assert.equal(qa.events.filter(event => event.name === 'atr:document-selection').length, 1); assert.equal(qa.ctx.requestedLocalPDF, null);
});

test('the personal-library route opens its visible library without a PDF id', async () => {
  let opened = 0;
  const ctx = vm.createContext({ controls() {}, chooseTool() {}, rootURL: new URL('https://example.test/'), URL,
    params: new URLSearchParams('library=1'), initialLocal: null, current: null, busy: false, explicitSelection: false, catalog: [],
    fetch: async () => ({ ok: true, json: async () => ({ documents: [] }) }), showLibrary: async () => { opened++; }, signal() {}, currentInfo() {},
  });
  vm.runInContext(section(reader, 'async function init()', 'init().catch('), ctx); await ctx.init();
  assert.equal(opened, 1);
});

test('original-PDF export copies the source bytes without baking in notebook ink', () => {
  const source = new Uint8Array([37, 80, 68, 70, 45, 49]); let output;
  const ctx = vm.createContext({ current: { title: 'Original' }, busy: false, pdfBytes: source,
    download: (bytes, name, type) => { output = { bytes, name, type }; }, safeName: value => value, toast() {}, t: key => key,
  });
  vm.runInContext(section(reader, 'function exportOriginalPDF()', 'function safeName('), ctx); ctx.exportOriginalPDF();
  assert.deepEqual(Array.from(output.bytes), Array.from(source)); assert.equal(output.type, 'application/pdf');
  output.bytes[0] = 0; assert.equal(source[0], 37);
});

test('cloud notebook clearing asks explicitly about deleting other members’ ink', () => {
  let handler, question;
  const ctx = vm.createContext({ current: { fingerprint }, permissions: { notebookId: 'shared-book' },
    canEditAllInk: () => true, state: () => [{}], confirm: key => { question = key; return false; }, t: key => key,
    $: () => ({ addEventListener: (_name, callback) => { handler = callback; } }),
  });
  vm.runInContext(section(reader, "$('clear-page').addEventListener('click'", "$('persistent-storage').addEventListener("), ctx);
  handler(); assert.equal(question, 'clearSharedConfirm');
});

test('cancelling the private-file prompt clears only the matching pending notebook selection', () => {
  let handler;
  const ctx = vm.createContext({ selection: { fingerprint }, requestedId: 'pending-private', active: null, notebookOpenGeneration: 0,
    window: { addEventListener: (_name, callback) => { handler = callback; } }, matches: () => false, status() {}, t: key => key,
  });
  vm.runInContext(section(cloud, "window.addEventListener('atr:cloud-local-cancel'", 'async function activate('), ctx);
  handler({ detail: { fingerprint: otherFingerprint } }); assert.equal(ctx.requestedId, 'pending-private');
  handler({ detail: { fingerprint } }); assert.equal(ctx.requestedId, null); assert.equal(ctx.selection, null);
});

function fakeElement(tag, text = '') {
  return { tag, text, children: [], dataset: {}, append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = items; }, setAttribute() {}, remove() {},
  };
}
function descendants(node) { return [node, ...node.children.flatMap(descendants)]; }

for (const failure of [{ status: 410, message: 'invite_expired' }, { status: 404, message: 'not_found' }, { status: 0, message: 'NETWORK' }]) {
  test(`invitation preview ${failure.status || 'network'} failure offers dismissal without consent and still renders personal notebooks`, async () => {
    const content = fakeElement('content');
    const ctx = vm.createContext({ content, dialog: { open: true }, renderGeneration: 0, account: { id: 'member', displayName: 'Member' },
      inviteToken: 'a'.repeat(43), invitePreview: null, path: '/v1/study', t: key => key, current: () => null,
      feedbackText() {}, el: fakeElement, action: (text, handler) => ({ ...fakeElement('button', text), handler }),
      logout() {}, dismissInvitation() {}, safeMetadata: value => value,
      api: async endpoint => { if (endpoint.endsWith('/invites/preview')) throw failure; return { ok: true, notebooks: [] }; },
    });
    vm.runInContext(section(cloud, 'function help(', 'function feedbackText(') + section(cloud, 'async function render()', 'async function authenticate('), ctx);
    await ctx.render();
    const nodes = descendants(content), text = nodes.map(node => node.text).join('\n');
    assert.ok(nodes.some(node => node.text === '초대 닫고 내 노트 보기'));
    assert.ok(nodes.some(node => node.text === '다시 확인'));
    assert.ok(nodes.some(node => node.text === '클라우드 노트'));
    assert.equal(nodes.some(node => node.text === '초대 수락'), false);
    assert.equal(ctx.inviteToken, 'a'.repeat(43));
    if (failure.status === 410) assert.match(text, /만료되었거나 이미 사용/);
    if (failure.status === 404) assert.match(text, /초대 링크를 찾을 수 없/);
    if (!failure.status) assert.match(text, /연결을 확인/);
  });
}

test('dismissing an invitation clears only its fragment and resumes personal notes even when rendering is offline', async () => {
  let resumed = 0, currentURL;
  const ctx = vm.createContext({ inviteToken: 'a'.repeat(43), invitePreview: { role: 'viewer' },
    location: { href: 'https://example.test/reader/?lang=en#invite=fixture&local=' + fingerprint }, URL, URLSearchParams,
    history: { state: null, replaceState: (_state, _title, url) => { currentURL = url; } },
    render: async () => { throw { status: 0, message: 'NETWORK' }; }, resume: async () => { resumed++; },
    feedbackText() {}, help: () => 'offline', status() {},
  });
  vm.runInContext(section(cloud, 'async function dismissInvitation()', 'async function acceptInvite('), ctx);
  await ctx.dismissInvitation();
  assert.equal(ctx.inviteToken, null); assert.equal(ctx.invitePreview, null); assert.equal(resumed, 1);
  const fragment = new URLSearchParams(new URL(currentURL).hash.slice(1));
  assert.equal(fragment.has('invite'), false); assert.equal(fragment.get('local'), fingerprint);
});

test('controls created by an async UI rerender stay disabled until the handler actually finishes', async () => {
  let release, reached;
  const waiting = new Promise(resolve => { release = resolve; }), started = new Promise(resolve => { reached = resolve; });
  const make = (tag, text) => ({ ...fakeElement(tag, text), isConnected: true, disabled: false, addEventListener() {} });
  const oldButton = make('button', 'old'); let displayed = [oldButton], nextButton, nextSelect;
  const ctx = vm.createContext({ busyUI: false, el: make, roleLabel: value => value, t: key => key, feedbackText() {}, help: value => value.message,
    dialog: { setAttribute() {}, removeAttribute() {}, querySelectorAll: () => displayed },
  });
  vm.runInContext(section(cloud, 'function roleSelect(', 'function setReaderRole(') + section(cloud, 'function action(', 'function ensureDialog('), ctx);
  const running = ctx.runUI(async () => {
    nextButton = ctx.action('new', () => {}); nextSelect = ctx.roleSelect();
    oldButton.isConnected = false; displayed = [nextButton, nextSelect]; reached(); await waiting;
  });
  await started;
  assert.equal(oldButton.disabled, true); assert.equal(nextButton.disabled, true); assert.equal(nextSelect.disabled, true);
  release(); await running;
  assert.equal(ctx.busyUI, false); assert.equal(nextButton.disabled, false); assert.equal(nextSelect.disabled, false);
});
