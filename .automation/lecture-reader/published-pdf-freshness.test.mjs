import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { webcrypto, createHash } from 'node:crypto';
import vm from 'node:vm';
import { selectEdition } from './editions.mjs';

// Run the real public-document orchestration at the browser HTTP cache and
// renderer boundaries. PDF parsing is outside this cache regression's scope.
const source = await readFile(new URL('./reader.mjs', import.meta.url), 'utf8');
const start = source.indexOf('async function openPublished(');
const end = source.indexOf('async function openStored(', start);
assert.ok(start >= 0 && end > start);
const bytes = value => new TextEncoder().encode(value).buffer;
const oldBytes = bytes('old PDF edition'), newBytes = bytes('new PDF edition');
async function digest(value) {
  return Buffer.from(await webcrypto.subtle.digest('SHA-256', value)).toString('hex');
}
const oldHash = await digest(oldBytes), newHash = await digest(newBytes);
const id = 'lecture-note';
const currentHref = `archive/files/${id}.pdf`;
const previousHref = `archive/editions/${id}/${oldHash}.pdf`;
const oldNotebook = { page: 2, bookmarks: [2], strokes: [{ id: 'saved-line', points: [[.1, .2], [.3, .4]] }] };
const response = value => ({ ok: true, arrayBuffer: async () => value });

function harness(fetcher) {
  const notes = new Map([[oldHash, structuredClone(oldNotebook)]]);
  const rendered = [], errors = [], restored = [];
  const context = {
    URL, rootURL: new URL('https://example.test/AI_Tech_Review/'), busy: false,
    en: false, retry: null, selectEdition,
    catalog: [{ id, title: 'Lecture', href: currentHref, sha256: newHash,
      editions: [{ href: previousHref, sha256: oldHash }] }],
    beginDocumentOpen: () => ({}), isCurrentDocumentOpen: () => true,
    $: () => ({}), t: key => key, showError: error => errors.push(error),
    fetch: fetcher,
    storage: { listDocuments: async () => [{ publicId: id, fingerprint: oldHash, hasPDF: true }] },
    openBytes: async (value, metadata) => {
      if (await digest(value) !== metadata.sha256) { errors.push('HASH_MISMATCH'); return false; }
      if (!notes.has(metadata.sha256)) notes.set(metadata.sha256, { page: 1, bookmarks: [], strokes: [] });
      rendered.push(metadata.sha256); return true;
    },
    openStored: async fingerprint => { restored.push(fingerprint); return notes.has(fingerprint); },
  };
  vm.createContext(context);
  vm.runInContext(source.slice(start, end), context);
  return { context, notes, rendered, errors, restored };
}

test('a revised current PDF opens despite a still-fresh old HTTP cache and keeps the old notebook', async () => {
  const qa = harness(async (_url, options) => response(
    options.cache === 'no-cache' ? newBytes : oldBytes,
  ));
  assert.equal(await qa.context.openPublished(id), true);
  assert.deepEqual(qa.rendered, [newHash]);
  assert.deepEqual(qa.notes.get(newHash), { page: 1, bookmarks: [], strokes: [] });
  assert.deepEqual(qa.notes.get(oldHash), oldNotebook);
  assert.deepEqual(qa.errors, []);
});

test('an incorrect revalidated response still fails fingerprint verification without changing notebooks', async () => {
  const qa = harness(async () => response(oldBytes));
  assert.equal(await qa.context.openPublished(id), false);
  assert.deepEqual(qa.rendered, []);
  assert.deepEqual(qa.errors, ['HASH_MISMATCH']);
  assert.deepEqual(qa.notes.get(oldHash), oldNotebook);
  assert.equal(qa.notes.has(newHash), false);
});

test('offline current-edition loading never substitutes an old-edition notebook', async () => {
  const qa = harness(async () => { throw Error('OFFLINE'); });
  assert.equal(await qa.context.openPublished(id), false);
  assert.deepEqual(qa.restored, []);
  assert.deepEqual(qa.errors, ['loadError']);
  assert.deepEqual(qa.notes.get(oldHash), oldNotebook);
});

test('an explicitly selected previous edition can still restore its exact saved notebook offline', async () => {
  const qa = harness(async () => { throw Error('OFFLINE'); });
  assert.equal(await qa.context.openPublished(id, { edition: oldHash }), true);
  assert.deepEqual(qa.restored, [oldHash]);
  assert.deepEqual(qa.notes.get(oldHash), oldNotebook);
  assert.equal(qa.notes.has(newHash), false);
});

test('a fresh immutable historical PDF stays usable from HTTP cache when the origin is unavailable', async () => {
  const qa = harness(async (url, options) => {
    assert.ok(url.href.endsWith(previousHref));
    if (options.cache === 'no-cache') throw Error('ORIGIN_UNAVAILABLE');
    return response(oldBytes);
  });
  qa.context.storage.listDocuments = async () => [];
  assert.equal(await qa.context.openPublished(id, { edition: oldHash }), true);
  assert.deepEqual(qa.rendered, [oldHash]);
  assert.deepEqual(qa.restored, []);
  assert.deepEqual(qa.notes.get(oldHash), oldNotebook);
});

test('the HTML entry point requests the reviewed reader module instead of the previous cached URL', async () => {
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');
  const href = html.match(/src="([^"\s]*reader\.mjs\?[^"\s]+)"/)?.[1];
  assert.ok(href, 'The reader entry must carry its module revision');
  const version = new URL(href, 'https://example.test/reader/').searchParams.get('v');
  assert.equal(version, createHash('sha256').update(source).digest('hex').slice(0, 12));
});
