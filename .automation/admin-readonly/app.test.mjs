import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const source = await readFile(new URL('./app.js', import.meta.url), 'utf8');
const { LIMITS, validateInventory, safePublicURL, linkDisplayPath, filterItems, pageItems, readInventoryResponse } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const item = (sourceId = 'example', extra = {}) => ({
  id: `archive:${sourceId}`, sourceId, kind: 'archive', title: '긴 제목과 <script>문자 그대로', languages: ['ko'], tags: ['tag'], category: 'daily-quantum', series: null,
  originalPublishedDate: '2026-11-17', registrationState: 'registered', notificationCatalogMember: null,
  releaseMembership: 'unknown', contentComparison: { state: 'unknown', basis: 'no_reviewed_output', coveredPaths: [] },
  checkedInputState: { article: 'not_recorded', registration: 'unknown', basis: 'no_request' },
  candidateState: 'not_provided', previewUrl: null, publicLinks: [], relatedDocumentIds: [], versionEvidence: {}, warnings: [], ...extra,
});
const inventory = (items = [item()]) => ({ schemaVersion: 1, baseline: { status: 'not_provided', releaseRevision: null }, totals: { registered: items.length, reconciled: 0, displayed: items.length }, items });
const link = (url, evidenceState = 'sealed_artifact_metadata') => ({ role: 'pdf', language: 'ko', url, sha256: null, sizeBytes: null, evidenceState, httpsVerifiedAt: null });

test('schema preserves separate unknown evidence, empty snapshot and native IDs', () => {
  assert.equal(validateInventory(inventory()).items[0].contentComparison.state, 'unknown');
  assert.equal(validateInventory(inventory([])).items.length, 0);
  assert.throws(() => validateInventory(inventory([item(), item()])), /DUPLICATE_OR_INVALID_ID/);
  assert.throws(() => validateInventory(inventory([item('example', { id: 'archive:different' })])), /DUPLICATE_OR_INVALID_ID/);
  assert.throws(() => validateInventory(inventory([item('example', { previewUrl: 'https://invalid.example/' })])), /INVALID_ITEM_STATE/);
  assert.throws(() => validateInventory(inventory([item('example', { releaseMembership: 'present' })])), /INVALID_BASELINE_EVIDENCE/);
  assert.throws(() => validateInventory(inventory([item('example', { notificationCatalogMember: false })])), /INVALID_ITEM_STATE/);
  const altered = inventory(); altered.totals.registered = 0;
  assert.throws(() => validateInventory(altered), /TOTALS_MISMATCH/);
});

test('client revalidates exact public origin/scope, declared evidence, canonical paths and anchors', () => {
  assert.equal(safePublicURL(link('https://infant83.io/AI_Tech_Review/lectures/reader/#chapter-1'), 'archive'), 'https://infant83.io/AI_Tech_Review/lectures/reader/#chapter-1');
  for (const value of [
    'javascript:alert(1)', 'file:///private/a.pdf', 'http://infant83.io/AI_Tech_Review/a.pdf',
    'https://infant83.io.evil.example/AI_Tech_Review/a.pdf', 'https://user:pass@infant83.io/AI_Tech_Review/a.pdf',
    'https://infant83.io/other/a.pdf', 'https://infant83.io/AI_Tech_Review/a/../a.pdf',
    'https://infant83.io/AI_Tech_Review/%2e%2e/a.pdf', 'https://infant83.io/AI_Tech_Review/a.pdf?token=private',
    'https://infant83.io/AI_Tech_Review/a.pdf?', 'https://infant83.io/AI_Tech_Review\\a.pdf',
    'https://infant83.io:444/AI_Tech_Review/a.pdf', ' https://infant83.io/AI_Tech_Review/a.pdf',
  ]) assert.equal(safePublicURL(link(value), 'archive'), null, value);
  assert.equal(safePublicURL(link('https://infant83.io/AI_Tech_Review/a.pdf', 'unrecognized'), 'archive'), null);
});

test('only external rows can open declared HTTPS landing pages without private query or credentials', () => {
  assert.equal(safePublicURL(link('https://example.org/paper', 'external_link_only'), 'external'), 'https://example.org/paper');
  for (const value of ['https://localhost/paper', 'https://127.0.0.1/paper', 'https://10.0.0.1/paper', 'https://[::1]/paper', 'https://service.internal/paper', 'https://example.org/paper?token=private']) {
    assert.equal(safePublicURL(link(value, 'external_link_only'), 'external'), null, value);
  }
  assert.equal(safePublicURL(link('https://example.org/paper', 'external_link_only'), 'review'), null);
});

test('study views and repeated roles have distinct exact public paths in their link labels', () => {
  const views = ['glossary.html', 'lectures-01-kernels.html', 'lectures-02-optimization.html'].map(name => ({ ...link(`https://infant83.io/AI_Tech_Review/lectures/example/${name}`), role: 'study_view' }));
  const paths = views.map(value => linkDisplayPath(value, 'archive', views));
  assert.equal(new Set(paths).size, views.length);
  assert.deepEqual(paths, ['/AI_Tech_Review/lectures/example/glossary.html', '/AI_Tech_Review/lectures/example/lectures-01-kernels.html', '/AI_Tech_Review/lectures/example/lectures-02-optimization.html']);
  const pdfs = ['old.pdf', 'current.pdf'].map(name => link(`https://infant83.io/AI_Tech_Review/archive/${name}`));
  assert.equal(linkDisplayPath(pdfs[0], 'archive', pdfs), '/AI_Tech_Review/archive/old.pdf');
  assert.equal(linkDisplayPath(pdfs[0], 'archive', [pdfs[0]]), null);
  const chapters = ['chapter-1', 'chapter-2'].map(anchor => ({ ...views[0], url: `https://infant83.io/AI_Tech_Review/lectures/example/index.html#${anchor}` }));
  assert.equal(new Set(chapters.map(value => linkDisplayPath(value, 'archive', chapters))).size, 2);
  assert.equal(linkDisplayPath({ ...views[0], url: 'file:///private/glossary.html' }, 'archive', views), null);
});

test('filters compose without sorting, merging documents or treating notification absence as unpublished', () => {
  const rows = [item('one'), item('two', { series: { id: 'course', title: '강의' }, languages: ['en'], category: null, releaseMembership: 'present', tags: ['SECOND'] }), item('three', { category: null })];
  assert.deepEqual(filterItems(rows, { category: null }).map(x => x.sourceId), ['two', 'three']);
  assert.deepEqual(filterItems(rows, { series: 'course', language: 'en', evidence: 'present', query: 'second' }).map(x => x.sourceId), ['two']);
  assert.deepEqual(filterItems(rows, { evidence: 'unknown' }).map(x => x.sourceId), ['one', 'three']);
  assert.deepEqual(filterItems(rows, { query: 'archive:two' }).map(x => x.sourceId), ['two']);
  assert.deepEqual(filterItems(rows, { query: '<script>' }).map(x => x.sourceId), ['one', 'two', 'three']);
  assert.deepEqual(rows.map(x => x.sourceId), ['one', 'two', 'three']);
});

test('200-character search and 50/100 local pages have explicit boundaries', () => {
  assert.doesNotThrow(() => filterItems([], { query: '🧪'.repeat(200) }));
  assert.throws(() => filterItems([], { query: 'a'.repeat(201) }), /SEARCH_TOO_LONG/);
  const rows = Array.from({ length: 151 }, (_, index) => item(String(index)));
  assert.equal(pageItems(rows).items.length, 50);
  assert.equal(pageItems(rows, 2, 100).items.length, 51);
  assert.deepEqual([pageItems(rows, 99, 100).page, pageItems(rows, 99, 100).pages], [2, 2]);
  assert.deepEqual([pageItems([], 1).from, pageItems([], 1).to], [0, 0]);
  for (const size of [0, 49, 101, 2000]) assert.throws(() => pageItems(rows, 1, size), /INVALID_PAGE/);
  assert.throws(() => pageItems(rows, 0), /INVALID_PAGE/);
});

test('row and UTF-8 response byte limits fail instead of rendering partial or normal-empty data', async () => {
  const rows = Array.from({ length: LIMITS.maxRows + 1 }, (_, index) => item(String(index)));
  assert.equal(validateInventory(inventory(rows.slice(0, LIMITS.maxRows))).items.length, LIMITS.maxRows);
  assert.throws(() => validateInventory(inventory(rows)), /ROW_LIMIT/);
  const response = body => new Response(body, { headers: { 'content-type': 'application/json' } });
  const encoded = JSON.stringify(inventory());
  assert.equal((await readInventoryResponse(response(encoded))).items.length, 1);
  const exactLimit = encoded + ' '.repeat(LIMITS.maxBytes - Buffer.byteLength(encoded));
  assert.equal((await readInventoryResponse(response(exactLimit))).items.length, 1);
  await assert.rejects(readInventoryResponse(response('x'.repeat(LIMITS.maxBytes + 1))), /BYTE_LIMIT/);
  await assert.rejects(readInventoryResponse(response('{"items":')), /INVALID_JSON/);
  await assert.rejects(readInventoryResponse(new Response('{}', { status: 503 })), /INVENTORY_UNAVAILABLE/);
  await assert.rejects(readInventoryResponse(new Response('{}', { headers: { 'content-type': 'text/html' } })), /INVALID_CONTENT_TYPE/);
  await assert.rejects(readInventoryResponse(new Response('{}', { headers: { 'content-type': 'application/json', 'content-length': String(LIMITS.maxBytes + 1) } })), /BYTE_LIMIT/);
});

test('assets use text DOM, one local inventory fetch and no reader/session/telemetry hooks', async () => {
  assert.doesNotMatch(source, /innerHTML|outerHTML|insertAdjacentHTML|document\.write|localStorage|sessionStorage|serviceWorker|sendBeacon|new Worker|eval\(/u);
  assert.equal((source.match(/\bfetch\(/gu) || []).length, 1);
  assert.match(source, /credentials: 'omit'/u);
  assert.match(source, /redirect: 'error'/u);
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');
  assert.doesNotMatch(html, /\son[a-z]+\s*=|https?:\/\/|reader-engagement/iu);
  assert.match(html, /connect-src 'self'/u);
});
