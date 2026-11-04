/** Pure geometry and portable notebook validation; no browser or storage access. */
export const NOTEBOOK_FORMAT = 'ai-tech-review-notebook';
export const MAX_PAGES = 10000;
export const MAX_POINTS = 1000000;
export const STROKE_CHUNK_POINTS = 4000;
export const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
export function normalizedPoint(clientX, clientY, rect, pressure = 0.5) {
  return { x: clamp((clientX - rect.left) / rect.width, 0, 1),
    y: clamp((clientY - rect.top) / rect.height, 0, 1), p: clamp(pressure || 0.5, 0.05, 1) };
}
export function pointSegmentDistance(p, a, b) {
  const dx = b.x - a.x, dy = b.y - a.y;
  const t = dx || dy ? clamp(((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy), 0, 1) : 0;
  return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy);
}
function cross(a, b, p) { return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x); }
export function segmentDistance(a, b, c, d) {
  const abC = cross(a, b, c), abD = cross(a, b, d), cdA = cross(c, d, a), cdB = cross(c, d, b);
  if (abC * abD <= 0 && cdA * cdB <= 0 &&
      Math.max(Math.min(a.x, b.x), Math.min(c.x, d.x)) <= Math.min(Math.max(a.x, b.x), Math.max(c.x, d.x)) &&
      Math.max(Math.min(a.y, b.y), Math.min(c.y, d.y)) <= Math.min(Math.max(a.y, b.y), Math.max(c.y, d.y))) return 0;
  return Math.min(pointSegmentDistance(a, c, d), pointSegmentDistance(b, c, d),
    pointSegmentDistance(c, a, b), pointSegmentDistance(d, a, b));
}
export function eraseStrokes(strokes, from, to, radiusPx, width, height) {
  const pixel = p => ({ x: p.x * width, y: p.y * height });
  const a = pixel(from), b = pixel(to);
  return strokes.filter(stroke => {
    const radius = radiusPx + stroke.width * width * 0.85;
    const pts = stroke.points.map(pixel);
    if (pts.length === 1) return pointSegmentDistance(pts[0], a, b) > radius;
    for (let i = 1; i < pts.length; i++) if (segmentDistance(a, b, pts[i - 1], pts[i]) <= radius) return false;
    return true;
  });
}
/** Split a long gesture at real samples, repeating the join sample, without decimation. */
export function splitStroke(stroke, idFactory, maximum = STROKE_CHUNK_POINTS) {
  if (maximum < 2 || !Number.isInteger(maximum)) throw new Error('INVALID_CHUNK_SIZE');
  if (stroke.points.length <= maximum) return [stroke];
  const parts = [];
  for (let start = 0; start < stroke.points.length - 1; start += maximum - 1) {
    parts.push({ ...stroke, id: parts.length ? idFactory() : stroke.id, points: stroke.points.slice(start, start + maximum) });
  }
  return parts;
}
/** Map normalized PDF.js display coordinates to unrotated PDF page coordinates. */
export function pdfPoint(point, box, rotation = 0) {
  const angle = ((rotation % 360) + 360) % 360;
  const displayW = angle % 180 ? box.height : box.width;
  const displayH = angle % 180 ? box.width : box.height;
  const x = point.x * displayW, y = point.y * displayH;
  if (angle === 90) return { x: box.x + y, y: box.y + x };
  if (angle === 180) return { x: box.x + box.width - x, y: box.y + y };
  if (angle === 270) return { x: box.x + box.width - y, y: box.y + box.height - x };
  return { x: box.x + x, y: box.y + box.height - y };
}
export function validateNotebook(value, expectedFingerprint = null) {
  const fail = message => { throw new Error(message); };
  if (!value || value.format !== NOTEBOOK_FORMAT || value.version !== 1) fail('UNSUPPORTED_BACKUP');
  const doc = value.document;
  if (!doc || !/^[a-f0-9]{64}$/.test(doc.fingerprint) || typeof doc.title !== 'string' ||
      doc.title.length > 500 || !Number.isInteger(doc.pageCount) || doc.pageCount < 1 || doc.pageCount > MAX_PAGES) fail('INVALID_DOCUMENT');
  if (expectedFingerprint && doc.fingerprint !== expectedFingerprint) fail('FINGERPRINT_MISMATCH');
  if (!Array.isArray(value.pages) || value.pages.length > doc.pageCount) fail('INVALID_PAGES');
  let total = 0; const seen = new Set(), seenStrokeIds = new Set();
  const pages = value.pages.map(page => {
    if (!page || !Number.isInteger(page.number) || page.number < 1 || page.number > doc.pageCount || seen.has(page.number) ||
        !Array.isArray(page.strokes) || page.strokes.length > 50000) fail('INVALID_PAGE');
    seen.add(page.number);
    const strokes = page.strokes.map(stroke => {
      if (!stroke || !/^#[a-f0-9]{6}$/i.test(stroke.color) || !Number.isFinite(stroke.width) || stroke.width <= 0 || stroke.width > .1 ||
          !Array.isArray(stroke.points) || !stroke.points.length || stroke.points.length > 100000) fail('INVALID_STROKE');
      total += stroke.points.length;
      if (total > MAX_POINTS) fail('BACKUP_TOO_LARGE');
      const points = stroke.points.map(p => {
        if (!p || !Number.isFinite(p.x) || !Number.isFinite(p.y) || !Number.isFinite(p.p) ||
            p.x < 0 || p.x > 1 || p.y < 0 || p.y > 1 || p.p < 0 || p.p > 1) fail('INVALID_POINT');
        return { x: p.x, y: p.y, p: p.p };
      });
      if (stroke.id !== undefined && (typeof stroke.id !== 'string' || !/^[A-Za-z0-9_-]{1,100}$/.test(stroke.id))) fail('INVALID_STROKE_ID');
      if (stroke.id !== undefined && seenStrokeIds.has(stroke.id)) fail('DUPLICATE_STROKE_ID');
      if (stroke.id !== undefined) seenStrokeIds.add(stroke.id);
      return { ...(stroke.id === undefined ? {} : { id: stroke.id }), color: stroke.color.toLowerCase(), width: stroke.width, points };
    });
    return { number: page.number, strokes };
  });
  const bookmarks = value.bookmarks || [];
  if (!Array.isArray(bookmarks) || bookmarks.length > doc.pageCount || bookmarks.some(n => !Number.isInteger(n) || n < 1 || n > doc.pageCount)) fail('INVALID_BOOKMARKS');
  const position = Number.isInteger(value.position) && value.position >= 1 && value.position <= doc.pageCount ? value.position : 1;
  return { format: NOTEBOOK_FORMAT, version: 1,
    document: { fingerprint: doc.fingerprint, title: doc.title, pageCount: doc.pageCount },
    pages, bookmarks: [...new Set(bookmarks)], position };
}
