import test from 'node:test';
import assert from 'node:assert/strict';
import { serveMedia } from './serve.mjs';
const bytes = new TextEncoder().encode('%PDF-example');
const key = 'pdf/sha256/aa/' + 'a'.repeat(64) + '.pdf';
const manifest = { aliases: { '/AI_Tech_Review/old.pdf': key, '/AI_Tech_Review/archive/copy.pdf': key }, objects: { [key]: { sha256: 'a'.repeat(64), size_bytes: bytes.length } } };
const calls = [];
const store = { async head() { return { size: bytes.length }; }, async get(key, range) { calls.push(key); return { size: bytes.length, body: range ? bytes.slice(range.offset, range.offset + range.length) : bytes }; } };
const get = (path = 'old.pdf', headers = {}, method = 'GET') => serveMedia(new Request('https://infant83.io/AI_Tech_Review/' + path, { headers, method }), manifest, store);
test('legacy aliases stream the exact same object; HEAD and ETag remain cheap', async () => {
  calls.length = 0;
  const a = await get(), b = await get('archive/copy.pdf');
  assert.deepEqual(new Uint8Array(await a.arrayBuffer()), bytes);
  assert.deepEqual(new Uint8Array(await b.arrayBuffer()), bytes);
  assert.equal(calls.length, 2); assert.equal(calls[0], calls[1]);
  assert.equal((await get('old.pdf', {}, 'HEAD')).headers.get('Content-Length'), String(bytes.length));
  assert.equal(calls.length, 2);
  assert.equal((await get('old.pdf', { 'If-None-Match': a.headers.get('ETag') })).status, 304);
  assert.equal(calls.length, 2);
});
test('byte ranges, suffix ranges, unsatisfiable ranges and If-Range follow PDF loading needs', async () => {
  let res = await get('old.pdf', { Range: 'bytes=0-4' });
  assert.equal(res.status, 206); assert.equal(await res.text(), '%PDF-');
  assert.equal(res.headers.get('Content-Range'), `bytes 0-4/${bytes.length}`);
  assert.equal(await (await get('old.pdf', { Range: 'bytes=-3' })).text(), 'ple');
  for (const range of ['bytes=900-', 'bytes=4-2', 'bytes=-0', 'bytes=1-2,4-5', 'bytes=wat']) assert.equal((await get('old.pdf', { Range: range })).status, 416);
  assert.equal((await get('old.pdf', { Range: 'bytes=0-4', 'If-Range': '"different"' })).status, 200);
});
test('missing objects fail closed, foreign paths fall back, writes are rejected', async () => {
  assert.equal((await get('unknown.pdf')).status, 404);
  assert.equal((await get('old.pdf', {}, 'POST')).status, 405);
  const res = await serveMedia(new Request('https://infant83.io/AI_Tech_Review/old.pdf'), manifest, { get: async () => null });
  assert.equal(res.status, 503); assert.equal(res.headers.get('Cache-Control'), 'no-store');
  const missingHead = await serveMedia(new Request('https://infant83.io/AI_Tech_Review/old.pdf', { method: 'HEAD' }), manifest, { head: async () => null });
  assert.equal(missingHead.status, 503);
});
