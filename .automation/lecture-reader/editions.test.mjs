import test from 'node:test';
import assert from 'node:assert/strict';
import { editionsFor, selectEdition } from './editions.mjs';
const id = '2026-11-07-example';
const doc = { id, href: `archive/files/${id}.pdf`, sha256: 'a'.repeat(64), editions: [
  { sha256: 'b'.repeat(64), href: `archive/editions/${id}/${'b'.repeat(64)}.pdf` },
] };
test('exact edition selection preserves the PDF fingerprint, never silently picks latest', () => {
  assert.equal(selectEdition(doc).sha256, doc.sha256);
  assert.equal(selectEdition(doc, 'b'.repeat(64)).current, false);
  assert.equal(selectEdition(doc, 'c'.repeat(64)), null);
});
test('foreign, traversing, duplicate and malformed edition URLs cannot be fetched', () => {
  const invalid = { ...doc, editions: [...doc.editions, ...doc.editions,
    { sha256: 'c'.repeat(64), href: 'https://other.invalid/private.pdf' },
    { sha256: 'd'.repeat(64), href: `archive/editions/${id}/../other.pdf` },
    { sha256: doc.sha256, href: doc.href }, null] };
  assert.equal(editionsFor(invalid).length, 2);
  assert.deepEqual(editionsFor({ ...doc, href: 'archive/files/other.pdf' }), []);
});
