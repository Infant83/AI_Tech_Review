import test from 'node:test';
import assert from 'node:assert/strict';
import { safeExternalURL, linkRectangle, resolveDestination, createNavigationHistory } from './pdf-navigation.mjs';

test('external links use only independently validated HTTP(S) URLs', () => {
  assert.equal(safeExternalURL({ url: 'https://example.org/paper?q=1#results' }), 'https://example.org/paper?q=1#results');
  assert.equal(safeExternalURL({ url: 'HTTP://EXAMPLE.ORG/a' }), 'http://example.org/a');
  assert.equal(safeExternalURL({ url: 'https://example.org/', unsafeUrl: 'javascript:alert(1)' }), 'https://example.org/');
  for (const url of ['javascript:alert(1)', 'data:text/html,hi', 'file:///private/paper.pdf', 'mailto:a@example.org',
    'https://user:password@example.org/', 'https:example.org', 'https://example.org/\nprivate', 'https://example.org/\\other']) {
    assert.equal(safeExternalURL({ url }, { baseURL: 'https://infant83.io/AI_Tech_Review/' }), null, url);
  }
  assert.equal(safeExternalURL({ unsafeUrl: 'https://example.org/' }), null);
  for (const key of ['action', 'actions', 'js', 'jsAction', 'jsActions', 'javascript', 'launch', 'file', 'attachment', 'resetForm']) {
    assert.equal(safeExternalURL({ url: 'https://example.org/', [key]: 'untrusted action' }), null, key);
  }
  assert.equal(safeExternalURL({ url: 'https://example.org/', isJSAction: true }), null);
});

test('relative links need an explicit public HTTP(S) base and never use a local filename', () => {
  for (const url of ['next.pdf', '../paper.pdf#page=2', '//example.org/paper', '#section']) assert.equal(safeExternalURL({ url }), null, url);
  const baseURL = 'https://infant83.io/AI_Tech_Review/archive/files/original.pdf';
  assert.equal(safeExternalURL({ url: '../paper.pdf#page=2' }, { baseURL }), 'https://infant83.io/AI_Tech_Review/archive/paper.pdf#page=2');
  assert.equal(safeExternalURL({ url: '//example.org/paper' }, { baseURL }), 'https://example.org/paper');
  for (const baseURL of ['file:///private/name.pdf', 'javascript:alert(1)', 'https://user:password@example.org/', 'relative.pdf']) {
    assert.equal(safeExternalURL({ url: 'other.pdf' }, { baseURL }), null);
  }
  for (const value of [null, [], {}, { url: 7 }, { url: '' }, { url: 'a'.repeat(8193) }]) assert.equal(safeExternalURL(value), null);
});

const viewport = (rotation = 0) => ({ width: 100, height: 200, rotation,
  convertToViewportPoint(x, y) { return rotation === 90 ? [y, x] : [x, 200 - y]; } });

test('link rectangles convert PDF coordinates in CSS units, normalize rotation and clip to the page', () => {
  assert.deepEqual(linkRectangle([10, 20, 30, 50], viewport()), { left: 10, top: 150, width: 20, height: 30 });
  assert.deepEqual(linkRectangle([30, 50, 10, 20], viewport()), { left: 10, top: 150, width: 20, height: 30 });
  assert.deepEqual(linkRectangle([10, 20, 30, 50], viewport(90)), { left: 20, top: 10, width: 30, height: 20 });
  assert.deepEqual(linkRectangle([-20, -20, 40, 230], viewport()), { left: 0, top: 0, width: 40, height: 200 });
  const scaled = { width: 200, height: 400, convertToViewportPoint(x, y) { return [x * 2, 400 - y * 2]; } };
  assert.deepEqual(linkRectangle([10, 20, 30, 50], scaled), { left: 20, top: 300, width: 40, height: 60 });
});

test('bad, empty and off-page link geometry cannot create a hit target', () => {
  for (const rect of [null, [], [1, 2, 3], [1, 2, 3, NaN], [1, 2, Infinity, 4], ['1', 2, 3, 4], new Array(4),
    [0, 0, 0, 10], [101, 0, 110, 10]]) assert.equal(linkRectangle(rect, viewport()), null);
  for (const patch of [{ width: 0 }, { height: Infinity }, { rotation: NaN }, { rotation: 45 },
    { convertToViewportPoint: null }, { convertToViewportPoint() { return [0, Infinity]; } },
    { convertToViewportPoint() { return new Array(2); } },
    { convertToViewportPoint() { throw Error('invalid viewport'); } }]) {
    assert.equal(linkRectangle([1, 2, 3, 4], { ...viewport(), ...patch }), null);
  }
});

test('named destinations resolve asynchronously through exact PDF references and preserve zero/null', async () => {
  const calls = [];
  const pdf = { numPages: 8,
    async getDestination(name) { calls.push(['name', name]); return [{ num: 17, gen: 0 }, { name: 'XYZ' }, 0, null, 0]; },
    async getPageIndex(ref) { calls.push(['ref', ref]); return 0; },
  };
  assert.deepEqual(await resolveDestination(pdf, 'Section 1'), { page: 1, kind: 'XYZ', point: { x: 0, y: null }, zoom: null });
  assert.deepEqual(calls, [['name', 'Section 1'], ['ref', { num: 17, gen: 0 }]]);
  assert.deepEqual(await resolveDestination(pdf, [7, { name: 'XYZ' }, null, 0, 2]), { page: 8, kind: 'XYZ', point: { x: null, y: 0 }, zoom: 2 });
});

test('fit destinations retain their exact kind and PDF-space placement', async () => {
  const pdf = { numPages: 3 };
  for (const kind of ['Fit', 'FitB']) assert.deepEqual(await resolveDestination(pdf, [0, { name: kind }]), { page: 1, kind });
  for (const kind of ['FitH', 'FitBH']) assert.deepEqual(await resolveDestination(pdf, [1, { name: kind }, 0]), { page: 2, kind, point: { x: null, y: 0 } });
  for (const kind of ['FitV', 'FitBV']) assert.deepEqual(await resolveDestination(pdf, [1, { name: kind }, null]), { page: 2, kind, point: { x: null, y: null } });
  assert.deepEqual(await resolveDestination(pdf, [2, { name: 'FitR' }, 0, -10, 100, 200]),
    { page: 3, kind: 'FitR', point: { x: 0, y: 200 }, rect: { left: 0, bottom: -10, right: 100, top: 200 } });
});

test('malformed and out-of-range destinations fail without requesting a page or moving anything', async () => {
  let calls = 0;
  const pdf = { numPages: 3, async getPageIndex() { calls++; return 0; } };
  const invalid = [null, [], {}, '', 'unknown', [-1, { name: 'Fit' }], [3, { name: 'Fit' }], [0.5, { name: 'Fit' }],
    [false, { name: 'Fit' }], [{ num: 0, gen: 0 }, { name: 'Fit' }], [{ num: 2, gen: -1 }, { name: 'Fit' }],
    [0, { name: 'Launch' }], [0, { name: '__proto__' }], [0, { name: 'XYZ' }, 0, 0, -1],
    [0, { name: 'XYZ' }, 0, 0, Infinity], [0, { name: 'XYZ' }, undefined, 0, 1], [0, { name: 'XYZ' }, true, 0, 1],
    [0, { name: 'FitH' }, NaN], [0, { name: 'Fit' }, 0], [0, { name: 'FitR' }, 0, 0, 0, 100], [0, { name: 'FitR' }, 0, null, 100, 100],
    [0, { name: 'XYZ' }, ...new Array(3)], [0, { name: 'FitR' }, -1e308, 0, 1e308, 100]];
  for (const dest of invalid) assert.equal(await resolveDestination(pdf, dest), null, JSON.stringify(dest));
  assert.equal(calls, 0);
  for (const index of [-1, 3, 0.5, NaN, false]) assert.equal(await resolveDestination({ ...pdf, getPageIndex: async () => index }, [{ num: 2, gen: 0 }, { name: 'Fit' }]), null);
  for (const numPages of [0, -1, 1.5, NaN, Infinity]) assert.equal(await resolveDestination({ numPages }, [0, { name: 'Fit' }]), null);
});

test('missing, rejected and invalid named/reference results return null without unhandled rejection', async () => {
  for (const getDestination of [async () => null, async () => 'recursive name', async () => { throw Error('document closed'); }]) {
    assert.equal(await resolveDestination({ numPages: 2, getDestination }, 'named'), null);
  }
  assert.equal(await resolveDestination({ numPages: 2, getPageIndex: async () => { throw Error('reference missing'); } }, [{ num: 1, gen: 0 }, { name: 'Fit' }]), null);
});

const anchor = overrides => ({ page: 1, nx: 0, ny: 1, zoom: 1, fingerprint: 'a'.repeat(64), ...overrides });
test('history is bounded, cloned and does not retain filenames or unrelated metadata', () => {
  const history = createNavigationHistory(2), first = anchor({ page: 1, filename: 'private.pdf' });
  assert.equal(history.push(first), true); first.page = 99;
  history.push(anchor({ page: 2 })); history.push(anchor({ page: 3 }));
  assert.equal(history.size, 2);
  assert.deepEqual(history.pop(), anchor({ page: 3 }));
  assert.deepEqual(history.pop(), anchor({ page: 2 }));
  assert.equal(history.pop(), null);
  history.push(anchor({ filename: 'private.pdf', networkURL: 'file:///private.pdf' }));
  assert.deepEqual(history.pop(), anchor());
  history.push(anchor()); history.clear(); assert.equal(history.size, 0);
  history.push(anchor({ fingerprint: 'b'.repeat(64) })); assert.equal(history.pop().fingerprint, 'b'.repeat(64));
});

test('history preserves an optional viewport placement without changing legacy anchors', () => {
  const history = createNavigationHistory();
  const placed = anchor({ viewportY: .6 });
  assert.equal(history.push(placed), true); placed.viewportY = .2;
  assert.deepEqual(history.pop(), anchor({ viewportY: .6 }));
  for (const viewportY of [0, 1]) {
    assert.equal(history.push(anchor({ viewportY })), true);
    assert.equal(history.pop().viewportY, viewportY);
  }
  assert.equal(history.push(anchor()), true);
  assert.deepEqual(history.pop(), anchor());
  for (const viewportY of [-.01, 1.01, NaN, Infinity, null, undefined, '0.5', false, {}, []]) {
    assert.equal(history.push(anchor({ viewportY })), false);
    assert.equal(history.size, 0);
  }
});

test('invalid anchors cannot change history and invalid bounds are rejected', () => {
  for (const limit of [0, -1, 1.5, NaN, Infinity, '30', Number.MAX_SAFE_INTEGER + 1]) assert.throws(() => createNavigationHistory(limit), RangeError);
  const history = createNavigationHistory();
  for (const bad of [null, [], {}, anchor({ page: 0 }), anchor({ page: 1.5 }), anchor({ nx: -0.1 }), anchor({ ny: 1.1 }),
    anchor({ nx: NaN }), anchor({ ny: Infinity }), anchor({ zoom: 0 }), anchor({ zoom: .09 }), anchor({ zoom: 10.1 }),
    anchor({ zoom: '1' }), anchor({ fingerprint: 'A'.repeat(64) })]) {
    assert.equal(history.push(bad), false); assert.equal(history.size, 0);
  }
  for (let page = 1; page <= 35; page++) history.push(anchor({ page }));
  assert.equal(history.size, 30);
  for (let page = 35; page >= 6; page--) assert.equal(history.pop().page, page);
  assert.equal(history.size, 0);
  history.push(anchor({ zoom: .1 })); assert.equal(history.pop().zoom, .1);
  history.push(anchor({ zoom: 10 })); assert.equal(history.pop().zoom, 10);
});
