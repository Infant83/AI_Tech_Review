import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

// Execute the real startup orchestration at its HTTP-cache and PDF-open
// boundaries. An old, still-fresh cache must not hide a newly published ID.
const source = await readFile(new URL('./reader.mjs', import.meta.url), 'utf8');
const start = source.indexOf('async function init()');
const end = source.indexOf('init().catch(', start);
assert.ok(start >= 0 && end > start);
const initialization = source.slice(start, end);
const oldHash = 'a'.repeat(64), newHash = 'b'.repeat(64);
const entry = (id, sha256 = oldHash) => ({ id, series: 'lecture-notes', href: `archive/files/${id}.pdf`, sha256 });
const oldCatalog = [entry('lecture-old')];
const response = documents => ({ ok: true, json: async () => ({ documents }) });
function deferred() { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; }
function harness(fetcher, query = 'id=lecture-new', initialLocal = null) {
  const requests = [], opened = [], localOpened = [], signals = [];
  const ink = new Map([[oldHash, [{ id: 'saved-stroke', page: 2 }]]]);
  const ctx = vm.createContext({
    URL, URLSearchParams, rootURL: new URL('https://example.test/AI_Tech_Review/'),
    params: new URLSearchParams(query), location: { hash: '' }, initialLocal,
    explicitSelection: false, current: null, busy: false, catalog: [],
    controls() {}, chooseTool() {},
    fetch: async (url, options) => { requests.push({ url: url.href, ...options }); return fetcher(options); },
    openPublished: async id => {
      const selected = ctx.catalog.find(doc => doc.id === id);
      assert.ok(selected, `The requested public ID ${id} must be present before opening its PDF`);
      opened.push({ ...selected });
    },
    openStored: async fingerprint => localOpened.push(fingerprint),
    signal: name => signals.push(name), currentInfo: () => ctx.current,
    storage: new Proxy({}, { get() { throw Error('Catalog refresh must not touch personal storage'); } }),
    ink,
  });
  vm.runInContext(initialization, ctx);
  return { ctx, requests, opened, localOpened, signals, ink };
}

test('a newly published lecture opens while the ordinary HTTP cache still has the previous catalog', async () => {
  const qa = harness(async options => response(options.cache === 'no-cache'
    ? [...oldCatalog, entry('lecture-new', newHash)] : oldCatalog));
  await qa.ctx.init();
  assert.deepEqual(qa.opened.map(doc => doc.id), ['lecture-new']);
  assert.equal(qa.opened[0].sha256, newHash);
  assert.deepEqual(qa.requests.map(item => item.cache), ['only-if-cached', 'no-cache']);
  assert.ok(qa.requests.every(item => item.url === 'https://example.test/AI_Tech_Review/archive-manifest.json'
    && item.credentials === 'omit' && item.mode === 'same-origin'));
  assert.deepEqual(qa.signals, ['atr:reader-ready']);
});

test('a revalidated edition retains its public ID without rewriting the previous edition or its ink', async () => {
  const qa = harness(async () => response([entry('lecture-old', newHash)]), 'id=lecture-old');
  await qa.ctx.init();
  assert.equal(qa.opened[0].id, 'lecture-old');
  assert.equal(qa.opened[0].sha256, newHash);
  assert.deepEqual(qa.ink.get(oldHash), [{ id: 'saved-stroke', page: 2 }]);
  assert.equal(qa.ink.has(newHash), false);
});

for (const failure of ['offline', 'HTTP failure', 'invalid JSON', 'invalid catalog shape']) {
  test(`${failure} during revalidation uses the previously validated public catalog snapshot`, async () => {
    const qa = harness(async options => {
      if (options.cache === 'only-if-cached') return response([...oldCatalog,
        { ...entry('unsafe-path'), href: 'https://other.test/private.pdf' },
        entry('bad-hash', 'bad'), { ...entry('review'), series: 'review' }]);
      assert.equal(options.cache, 'no-cache', 'A captured snapshot does not require another cache/network fetch');
      if (failure === 'offline') throw Error('OFFLINE');
      if (failure === 'HTTP failure') return { ok: false };
      if (failure === 'invalid JSON') return { ok: true, json: async () => { throw Error('JSON'); } };
      return { ok: true, json: async () => ({ documents: null }) };
    }, 'id=lecture-old');
    await qa.ctx.init();
    assert.deepEqual(qa.requests.map(item => item.cache), ['only-if-cached', 'no-cache']);
    assert.ok(qa.requests.every(item => item.credentials === 'omit' && item.mode === 'same-origin'));
    assert.deepEqual(Array.from(qa.ctx.catalog, doc => doc.id), ['lecture-old']);
    assert.equal(qa.opened[0].sha256, oldHash);
    assert.deepEqual(qa.ink.get(oldHash), [{ id: 'saved-stroke', page: 2 }]);
  });
}

test('an unavailable network and public cache still allow a private stored PDF to reopen', async () => {
  const qa = harness(async () => { throw Error('OFFLINE'); }, '', oldHash);
  await qa.ctx.init();
  assert.deepEqual(qa.requests.map(item => item.cache), ['only-if-cached', 'no-cache', 'force-cache']);
  assert.deepEqual(qa.localOpened, [oldHash]);
  assert.deepEqual(qa.ink.get(oldHash), [{ id: 'saved-stroke', page: 2 }]);
  assert.deepEqual(qa.signals, ['atr:reader-ready']);
});

for (const stage of ['cache snapshot', 'revalidation', 'cached fallback']) {
  test(`an explicit PDF selection during ${stage} takes precedence over the startup link`, async () => {
    const reached = deferred(), release = deferred();
    const qa = harness(async options => {
      if (stage === 'cached fallback' && options.cache !== 'force-cache') throw Error('OFFLINE');
      if (stage === 'revalidation' && options.cache === 'only-if-cached') return response(oldCatalog);
      reached.resolve(); await release.promise;
      return response([...oldCatalog, entry('lecture-new', newHash)]);
    });
    const starting = qa.ctx.init(); await reached.promise;
    const chosen = { fingerprint: oldHash, title: 'Private study PDF' };
    qa.ctx.explicitSelection = true; qa.ctx.current = chosen;
    release.resolve(); await starting;
    assert.deepEqual(qa.opened, []);
    assert.equal(qa.ctx.current, chosen);
    assert.deepEqual(qa.ink.get(oldHash), [{ id: 'saved-stroke', page: 2 }]);
  });
}

test('a failed revalidation cannot erase the captured catalog before a known PDF opens', async () => {
  let httpCache = [entry('lecture-new', newHash)];
  const qa = harness(async options => {
    if (options.cache === 'only-if-cached') return response(httpCache);
    if (options.cache === 'no-cache') {
      httpCache = null; // The real Firefox 503/no-store case invalidates this HTTP entry.
      return { ok: false, status: 503 };
    }
    return httpCache ? response(httpCache) : { ok: false, status: 503 };
  });
  await qa.ctx.init();
  assert.equal(httpCache, null);
  assert.deepEqual(qa.opened.map(doc => doc.id), ['lecture-new']);
  assert.equal(qa.opened[0].sha256, newHash);
  assert.deepEqual(qa.requests.map(item => item.cache), ['only-if-cached', 'no-cache']);
  assert.deepEqual(qa.ink.get(oldHash), [{ id: 'saved-stroke', page: 2 }]);
});

for (const failure of ['cache miss', 'unsupported cache-only mode']) {
  test(`${failure} still revalidates and opens the current public catalog`, async () => {
    const qa = harness(async options => {
      if (options.cache === 'only-if-cached') {
        if (failure === 'cache miss') return { ok: false, status: 504 };
        throw new TypeError('Unsupported request cache mode');
      }
      assert.equal(options.cache, 'no-cache');
      return response([entry('lecture-new', newHash)]);
    });
    await qa.ctx.init();
    assert.deepEqual(qa.requests.map(item => item.cache), ['only-if-cached', 'no-cache']);
    assert.equal(qa.opened[0].sha256, newHash);
  });
}

test('a browser without cache-only support can still use its validated force-cache fallback', async () => {
  const qa = harness(async options => {
    if (options.cache === 'only-if-cached') throw new TypeError('Unsupported request cache mode');
    if (options.cache === 'no-cache') throw Error('OFFLINE');
    assert.equal(options.cache, 'force-cache');
    return response(oldCatalog);
  }, 'id=lecture-old');
  await qa.ctx.init();
  assert.deepEqual(qa.requests.map(item => item.cache), ['only-if-cached', 'no-cache', 'force-cache']);
  assert.equal(qa.opened[0].sha256, oldHash);
});
