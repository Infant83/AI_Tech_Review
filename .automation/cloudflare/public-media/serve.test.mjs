import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { serveMedia } from './serve.mjs';

const encode = value => new TextEncoder().encode(value);
const old = encode('%PDF-first-edition');
const current = encode('%PDF-other-edition'); // Same size deliberately; size is not a hash proof.
const foreign = encode('%PDF-foreign-edition');
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const oldSha = digest(old), currentSha = digest(current), foreignSha = digest(foreign);
const keyOf = sha => `pdf/sha256/${sha.slice(0, 2)}/${sha}.pdf`;
const path = '/AI_Tech_Review/old.pdf';
const etagOf = sha => `"sha256-${sha}"`;
function fixture({ legacy = false, previousCurrent = false } = {}) {
  const objects = Object.fromEntries([old, current, foreign].map(bytes => [keyOf(digest(bytes)), {
    sha256: digest(bytes), size_bytes: bytes.length, content_type: 'application/pdf',
  }]));
  const aliases = {
    [path]: { current: previousCurrent ? oldSha : currentSha, editions: { [oldSha]: keyOf(oldSha), [currentSha]: keyOf(currentSha) } },
    '/AI_Tech_Review/archive/copy.pdf': { current: currentSha, editions: { [currentSha]: keyOf(currentSha) } },
    '/AI_Tech_Review/foreign.pdf': { current: foreignSha, editions: { [foreignSha]: keyOf(foreignSha) } },
  };
  const manifest = { version: legacy ? 1 : 2, scope: '/AI_Tech_Review/', objects,
    aliases: legacy ? Object.fromEntries(Object.entries(aliases).map(([name, row]) => [name, row.editions[row.current]])) : aliases };
  const calls = [], payloads = new Map([old, current, foreign].map(bytes => [keyOf(digest(bytes)), bytes]));
  const store = {
    async head(key) { calls.push({ method: 'head', key }); const bytes = payloads.get(key); return bytes ? { size: bytes.length } : null; },
    async get(key, range) {
      calls.push({ method: 'get', key, range }); const bytes = payloads.get(key);
      return bytes ? { size: bytes.length, body: range ? bytes.slice(range.offset, range.offset + range.length) : bytes } : null;
    },
  };
  const request = (query = '', headers = {}, method = 'GET', urlPath = path) =>
    new Request('https://infant83.io' + urlPath + query, { headers, method });
  const get = (query = '', headers = {}, method = 'GET', urlPath = path) => serveMedia(request(query, headers, method, urlPath), manifest, store);
  return { manifest, calls, payloads, store, request, get };
}

test('current and pinned previous editions return exact bytes, scoped ETags and lengths', async () => {
  const f = fixture();
  const a = await f.get(), b = await f.get(`?sha256=${oldSha}`);
  assert.deepEqual(new Uint8Array(await a.arrayBuffer()), current);
  assert.deepEqual(new Uint8Array(await b.arrayBuffer()), old);
  assert.equal(a.headers.get('ETag'), etagOf(currentSha));
  assert.equal(b.headers.get('ETag'), etagOf(oldSha));
  assert.equal(b.headers.get('Content-Length'), String(old.length));
  assert.deepEqual(f.calls.map(call => call.method), ['head', 'get', 'head', 'get']);
  assert.deepEqual(f.calls.map(call => call.key), [keyOf(currentSha), keyOf(currentSha), keyOf(oldSha), keyOf(oldSha)]);
  const copy = await f.get('', {}, 'GET', '/AI_Tech_Review/archive/copy.pdf');
  assert.deepEqual(new Uint8Array(await copy.arrayBuffer()), current);
  assert.equal(f.calls.at(-1).key, keyOf(currentSha));
});

test('HEAD and 304 check the selected object once, without fetching its body', async () => {
  for (const sha of [oldSha, currentSha]) {
    for (const method of ['GET', 'HEAD']) {
      const f = fixture();
      const response = await f.get(`?sha256=${sha}`, { 'If-None-Match': `"unrelated", W/${etagOf(sha)}` }, method);
      assert.equal(response.status, 304); assert.equal(await response.text(), '');
      assert.equal(response.headers.get('ETag'), etagOf(sha));
      assert.deepEqual(f.calls, [{ method: 'head', key: keyOf(sha) }]);
    }
    const f = fixture(), response = await f.get(`?sha256=${sha}`, {}, 'HEAD');
    assert.equal(response.status, 200); assert.equal(await response.text(), '');
    assert.equal(response.headers.get('Content-Length'), String(old.length));
    assert.deepEqual(f.calls, [{ method: 'head', key: keyOf(sha) }]);
  }
});

test('other-edition If-None-Match does not produce a false 304', async () => {
  const f = fixture();
  const response = await f.get(`?sha256=${oldSha}`, { 'If-None-Match': etagOf(currentSha) });
  assert.equal(response.status, 200); assert.deepEqual(new Uint8Array(await response.arrayBuffer()), old);
  assert.deepEqual(f.calls.map(call => call.method), ['head', 'get']);
});

test('actual partial/suffix/open ranges and If-Range are evaluated after selecting either edition', async () => {
  for (const [sha, bytes] of [[oldSha, old], [currentSha, current]]) {
    const f = fixture(), query = `?sha256=${sha}`;
    const part = await f.get(query, { Range: 'bytes=5-9', 'If-Range': etagOf(sha) });
    assert.equal(part.status, 206); assert.equal(part.headers.get('Content-Range'), `bytes 5-9/${bytes.length}`);
    assert.equal(part.headers.get('Content-Length'), '5');
    assert.deepEqual(new Uint8Array(await part.arrayBuffer()), bytes.slice(5, 10));
    assert.deepEqual(f.calls[1], { method: 'get', key: keyOf(sha), range: { offset: 5, length: 5 } });
    const suffix = await f.get(query, { Range: 'bytes=-3' });
    assert.equal(suffix.status, 206); assert.deepEqual(new Uint8Array(await suffix.arrayBuffer()), bytes.slice(-3));
    const open = await f.get(query, { Range: 'bytes=7-' });
    assert.equal(open.status, 206); assert.deepEqual(new Uint8Array(await open.arrayBuffer()), bytes.slice(7));
    for (const validator of [etagOf(foreignSha), `W/${etagOf(sha)}`, 'Sat, 01 Nov 2026 00:00:00 GMT']) {
      const full = await f.get(query, { Range: 'bytes=5-9', 'If-Range': validator });
      assert.equal(full.status, 200); assert.deepEqual(new Uint8Array(await full.arrayBuffer()), bytes);
    }
    const head = await f.get(query, { Range: 'bytes=5-9' }, 'HEAD');
    assert.equal(head.status, 200); assert.equal(head.headers.get('Content-Range'), null);
  }
});

test('invalid and multiple ranges fail with selected edition size and no object body read', async () => {
  for (const range of ['bytes=900-', 'bytes=4-2', 'bytes=-0', 'bytes=1-2,4-5', 'bytes=wat', 'bytes=9007199254740992-']) {
    const f = fixture();
    const response = await f.get(`?sha256=${oldSha}`, { Range: range });
    assert.equal(response.status, 416); assert.equal(response.headers.get('Content-Range'), `bytes */${old.length}`);
    assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.deepEqual(f.calls, [{ method: 'head', key: keyOf(oldSha) }]);
  }
});

test('malformed/duplicate/unknown edition queries fail closed without storage or fallback', async () => {
  for (const query of ['?sha256=', '?sha256=short', `?sha256=${oldSha.toUpperCase()}`, `?sha256=${oldSha}&sha256=${oldSha}`,
    `?%73ha256=${oldSha}&sha256=${currentSha}`, `?sha256=${oldSha}&unknown=x`, '?sha256=%GG', '?edition=old']) {
    const f = fixture();
    const response = await f.get(query);
    assert.equal(response.status, 400, query); assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.deepEqual(f.calls, []);
  }
});

test('valid but unsupported or cross-document SHA is 409, never another edition or fallback', async () => {
  for (const sha of [foreignSha, '0'.repeat(64)]) {
    const f = fixture();
    const response = await serveMedia(f.request(`?sha256=${sha}`), f.manifest, f.store, () => { assert.fail('managed path must not fall back'); });
    assert.equal(response.status, 409); assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.deepEqual(f.calls, []);
  }
  const f = fixture();
  assert.equal((await f.get(`?sha256=${oldSha}`, {}, 'GET', '/AI_Tech_Review/archive/copy.pdf')).status, 409);
});

test('missing/size-mismatched selected objects cannot hide behind exact or wildcard 304', async () => {
  for (const method of ['GET', 'HEAD']) for (const condition of [etagOf(oldSha), '*']) for (const defect of ['missing', 'size']) {
    const f = fixture();
    if (defect === 'missing') f.payloads.delete(keyOf(oldSha));
    else f.payloads.set(keyOf(oldSha), encode('%PDF-bad'));
    const response = await f.get(`?sha256=${oldSha}`, { 'If-None-Match': condition }, method);
    assert.equal(response.status, 503); assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.deepEqual(f.calls, [{ method: 'head', key: keyOf(oldSha) }]);
  }
});

test('a body disappearing/changing size after head is a noncacheable 503', async () => {
  for (const defect of [null, { size: 1, body: old }, { size: old.length, body: null }]) {
    const f = fixture(); f.store.get = async () => defect;
    const response = await f.get(`?sha256=${oldSha}`);
    assert.equal(response.status, 503); assert.equal(response.headers.get('Cache-Control'), 'no-store');
  }
  for (const which of ['head', 'get']) {
    const f = fixture(); f.store[which] = async () => { throw new Error('synthetic storage failure'); };
    assert.equal((await f.get()).status, 503);
  }
});

test('size/head/ETag are deliberately not treated as uploaded byte SHA verification', async () => {
  assert.equal(old.length, current.length);
  const f = fixture(); f.payloads.set(keyOf(oldSha), current);
  const response = await f.get(`?sha256=${oldSha}`);
  assert.equal(response.status, 200);
  assert.notEqual(digest(new Uint8Array(await response.arrayBuffer())), oldSha);
  // Full-byte export/upload verification is mandatory separately. Do not hash
  // every Range or falsely claim that an immutable name/head proves its body.
  assert.deepEqual(f.calls.map(call => call.method), ['head', 'get']);
});

test('unmanaged URLs preserve the actual fallback request, result and method', async () => {
  const f = fixture(), req = f.request('?sha256=bad&tracking=yes', {}, 'POST', '/AI_Tech_Review/unmanaged.pdf');
  const expected = new Response('fallback marker', { status: 202 }); let fallbackCalls = 0;
  const response = await serveMedia(req, f.manifest, f.store, received => { fallbackCalls++; assert.equal(received, req); return expected; });
  assert.equal(response, expected); assert.equal(await response.text(), 'fallback marker');
  assert.equal(fallbackCalls, 1); assert.deepEqual(f.calls, []);
  const malformed = await serveMedia(new Request('https://infant83.io/AI_Tech_Review/%GG.pdf'), f.manifest, f.store);
  assert.equal(malformed.status, 400); assert.equal(malformed.headers.get('Cache-Control'), 'no-store');
});

test('writes and inconsistent manifest entries do not reach storage', async () => {
  const f = fixture();
  const post = await f.get('', {}, 'POST');
  assert.equal(post.status, 405); assert.equal(post.headers.get('Allow'), 'GET, HEAD');
  assert.deepEqual(f.calls, []);
  for (const defect of ['key', 'sha', 'size', 'current', 'version']) {
    const row = fixture();
    if (defect === 'key') row.manifest.aliases[path].editions[currentSha] = keyOf(foreignSha);
    if (defect === 'sha') row.manifest.objects[keyOf(currentSha)].sha256 = oldSha;
    if (defect === 'size') row.manifest.objects[keyOf(currentSha)].size_bytes = -1;
    if (defect === 'current') row.manifest.aliases[path].current = foreignSha;
    if (defect === 'version') row.manifest.version = 900;
    const response = await row.get();
    assert.equal(response.status, 503); assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.deepEqual(row.calls, []);
  }
});

test('v1 local manifests keep current URL semantics but never ignore an explicit different SHA', async () => {
  const f = fixture({ legacy: true });
  assert.deepEqual(new Uint8Array(await (await f.get()).arrayBuffer()), current);
  assert.equal((await f.get(`?sha256=${currentSha}`)).status, 200);
  assert.equal((await f.get(`?sha256=${oldSha}`)).status, 409);
});

test('old/new catalogs and either supporting mapping remain compatible through current-pointer rollback', async () => {
  for (const previousCurrent of [false, true]) {
    const f = fixture({ previousCurrent });
    for (const [sha, bytes] of [[oldSha, old], [currentSha, current]]) {
      const response = await f.get(`?sha256=${sha}`);
      assert.equal(response.status, 200); assert.deepEqual(new Uint8Array(await response.arrayBuffer()), bytes);
    }
    assert.deepEqual(new Uint8Array(await (await f.get()).arrayBuffer()), previousCurrent ? old : current);
  }
});
