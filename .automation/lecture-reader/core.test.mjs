import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizedPoint, pointSegmentDistance, segmentDistance, eraseStrokes, splitStroke, pdfPoint, validateNotebook } from './ink-core.mjs';
test('normalized ink keeps its position across responsive widths and clamps at page edges', () => {
  const a = normalizedPoint(150, 300, { left: 50, top: 100, width: 200, height: 400 }, .75);
  const b = normalizedPoint(250, 500, { left: 50, top: 100, width: 400, height: 800 }, .75);
  assert.deepEqual(a, b); assert.deepEqual(normalizedPoint(-5, 1200, { left: 0, top: 0, width: 100, height: 200 }), { x: 0, y: 1, p: .5 });
});
test('eraser intersects a line even when neither ink endpoint is near its path', () => {
  const line = { color: '#172b3b', width: .002, points: [{ x: .1, y: .5, p: .5 }, { x: .9, y: .5, p: .5 }] };
  assert.equal(eraseStrokes([line], { x: .5, y: .2 }, { x: .5, y: .8 }, 8, 600, 800).length, 0);
  assert.equal(eraseStrokes([line], { x: .5, y: .1 }, { x: .8, y: .1 }, 8, 600, 800).length, 1);
});
test('segment distance handles degenerate and parallel segments without false intersections', () => {
  assert.equal(pointSegmentDistance({ x: 3, y: 4 }, { x: 0, y: 0 }, { x: 0, y: 0 }), 5);
  assert.equal(segmentDistance({ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }), 1);
  assert.equal(segmentDistance({ x: 0, y: 0 }, { x: 2, y: 2 }, { x: 0, y: 2 }, { x: 2, y: 0 }), 0);
});
test('long pen gestures split below sync limits with every sample and join preserved', () => {
  const points = Array.from({ length: 9000 }, (_, i) => ({ x: i / 8999, y: .5, p: .6 }));
  let nextId = 0;
  const pieces = splitStroke({ id: 'original', color: '#243746', width: .002, points }, () => 'part-' + ++nextId);
  assert.equal(pieces.length, 3); assert.ok(pieces.every(p => p.points.length <= 4000));
  assert.equal(pieces[0].id, 'original'); assert.equal(new Set(pieces.map(p => p.id)).size, 3);
  assert.deepEqual(pieces[0].points.at(-1), pieces[1].points[0]);
  assert.deepEqual(pieces[1].points.at(-1), pieces[2].points[0]);
  assert.deepEqual([...pieces[0].points, ...pieces[1].points.slice(1), ...pieces[2].points.slice(1)], points);
});
test('ink export respects crop-box origin and all right-angle PDF rotations', () => {
  const box = { x: 30, y: 50, width: 200, height: 400 };
  assert.deepEqual(pdfPoint({ x: 0, y: 0 }, box, 0), { x: 30, y: 450 });
  assert.deepEqual(pdfPoint({ x: 1, y: 1 }, box, 0), { x: 230, y: 50 });
  assert.deepEqual(pdfPoint({ x: 0, y: 0 }, box, 90), { x: 30, y: 50 });
  assert.deepEqual(pdfPoint({ x: 1, y: 1 }, box, 90), { x: 230, y: 450 });
  assert.deepEqual(pdfPoint({ x: 0, y: 0 }, box, 180), { x: 230, y: 50 });
  assert.deepEqual(pdfPoint({ x: 0, y: 0 }, box, 270), { x: 230, y: 450 });
  assert.deepEqual(pdfPoint({ x: .5, y: .5 }, box, -90), { x: 130, y: 250 });
});
const fingerprint = 'a'.repeat(64);
const notebook = () => ({ format: 'ai-tech-review-notebook', version: 1, document: { fingerprint, title: 'Private <title>', pageCount: 2 }, pages: [{ number: 1, strokes: [{ color: '#ff0000', width: .003, points: [{ x: .2, y: .7, p: .6 }] }] }], bookmarks: [2], position: 2 });
test('portable backup validates identity and preserves editable normalized strokes', () => {
  const output = validateNotebook(notebook(), fingerprint); assert.deepEqual(output, notebook());
  assert.throws(() => validateNotebook(notebook(), 'b'.repeat(64)), /FINGERPRINT_MISMATCH/);
});
test('stable stroke IDs survive portable backups, malformed or duplicate IDs are rejected', () => {
  let b = notebook(); b.pages[0].strokes[0].id = 'stable-ink-7';
  assert.equal(validateNotebook(b).pages[0].strokes[0].id, 'stable-ink-7');
  b.pages[0].strokes.push({ ...b.pages[0].strokes[0] }); assert.throws(() => validateNotebook(b), /DUPLICATE_STROKE_ID/);
  b = notebook(); b.pages[0].strokes[0].id = '../invalid'; assert.throws(() => validateNotebook(b), /INVALID_STROKE_ID/);
});
test('backup rejects malformed points, duplicate pages, prototype payloads and bad page counts', () => {
  let b = notebook(); b.pages[0].strokes[0].points[0].x = Infinity; assert.throws(() => validateNotebook(b), /INVALID_POINT/);
  b = notebook(); b.pages.push(b.pages[0]); assert.throws(() => validateNotebook(b), /INVALID_PAGE/);
  b = notebook(); b.document.pageCount = 0; assert.throws(() => validateNotebook(b), /INVALID_DOCUMENT/);
  b = notebook(); b.pages[0].strokes[0].color = 'url(https://invalid/)'; assert.throws(() => validateNotebook(b), /INVALID_STROKE/);
  b = notebook(); b.document.__proto__ = { unexpected: 'never copied' }; assert.equal(Object.hasOwn(validateNotebook(b).document, '__proto__'), false);
});
