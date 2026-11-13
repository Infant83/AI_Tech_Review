/** Pure PDF navigation validation. No fetch, DOM, storage or PDF mutation. */
const finite = value => typeof value === 'number' && Number.isFinite(value);
const nullableNumber = value => value === null || finite(value);
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const unsafeURLCharacters = /[\u0000-\u001f\u007f\\]/;

function httpURL(value, base) {
  if (typeof value !== 'string' || !value || value.length > 8192 || unsafeURLCharacters.test(value)) return null;
  const text = value.trim();
  if (!text || (/^[a-z][a-z0-9+.-]*:/i.test(text) && !/^https?:\/\//i.test(text))) return null;
  try {
    const url = base ? new URL(text, base) : new URL(text);
    return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password ? url : null;
  } catch { return null; }
}

export function safeExternalURL(annotation, { baseURL = null } = {}) {
  if (!record(annotation) || annotation.isJSAction === true ||
      ['action', 'actions', 'js', 'jsAction', 'jsActions', 'javascript', 'launch', 'file', 'attachment', 'resetForm']
        .some(key => annotation[key] !== undefined && annotation[key] !== null)) return null;
  // Never fall back to unsafeUrl. A normal PDF.js URI annotation may include
  // both url and unsafeUrl; only the separately validated url is considered.
  const absolute = httpURL(annotation.url);
  if (absolute) return absolute.href;
  const base = httpURL(baseURL);
  return base ? httpURL(annotation.url, base)?.href ?? null : null;
}

/** Return the clipped rectangle in viewport CSS pixels, never bitmap pixels. */
export function linkRectangle(rect, viewport) {
  if (!Array.isArray(rect) || rect.length !== 4 || !Array.from(rect).every(finite) || !record(viewport) ||
      !finite(viewport.width) || viewport.width <= 0 || !finite(viewport.height) || viewport.height <= 0 ||
      typeof viewport.convertToViewportPoint !== 'function' ||
      (viewport.rotation !== undefined && (!finite(viewport.rotation) || viewport.rotation % 90 !== 0))) return null;
  try {
    // PDFPageViewport rotations are multiples of 90 degrees. Its existing
    // transform handles origin, crop offsets, rotation and scale together.
    const a = viewport.convertToViewportPoint(rect[0], rect[1]);
    const b = viewport.convertToViewportPoint(rect[2], rect[3]);
    if (!Array.isArray(a) || a.length !== 2 || !Array.from(a).every(finite) ||
        !Array.isArray(b) || b.length !== 2 || !Array.from(b).every(finite)) return null;
    const left = clamp(Math.min(a[0], b[0]), 0, viewport.width);
    const top = clamp(Math.min(a[1], b[1]), 0, viewport.height);
    const right = clamp(Math.max(a[0], b[0]), 0, viewport.width);
    const bottom = clamp(Math.max(a[1], b[1]), 0, viewport.height);
    if (right <= left || bottom <= top) return null;
    return { left, top, width: right - left, height: bottom - top };
  } catch { return null; }
}

const destinationSizes = { XYZ: 5, Fit: 2, FitB: 2, FitH: 3, FitBH: 3, FitV: 3, FitBV: 3, FitR: 6 };

/** Resolve a PDF destination without moving the reader. Coordinates stay in PDF units. */
export async function resolveDestination(pdf, destination) {
  try {
    if (!record(pdf) || !Number.isSafeInteger(pdf.numPages) || pdf.numPages < 1) return null;
    let dest = destination;
    if (typeof dest === 'string') {
      if (!dest || dest.length > 4096 || typeof pdf.getDestination !== 'function') return null;
      dest = await pdf.getDestination(dest);
    }
    if (!Array.isArray(dest) || !record(dest[1]) || typeof dest[1].name !== 'string') return null;
    const kind = dest[1].name;
    if (!Object.hasOwn(destinationSizes, kind) || dest.length !== destinationSizes[kind]) return null;
    if (kind === 'XYZ' && (!Array.from(dest.slice(2)).every(nullableNumber) || (dest[4] !== null && dest[4] < 0))) return null;
    if (['FitH', 'FitBH', 'FitV', 'FitBV'].includes(kind) && !nullableNumber(dest[2])) return null;
    if (kind === 'FitR' && (!Array.from(dest.slice(2)).every(finite) || dest[4] <= dest[2] || dest[5] <= dest[3] ||
        !finite(dest[4] - dest[2]) || !finite(dest[5] - dest[3]))) return null;
    let index = dest[0];
    if (record(index)) {
      if (!Number.isSafeInteger(index.num) || index.num < 1 || !Number.isSafeInteger(index.gen) || index.gen < 0 ||
          typeof pdf.getPageIndex !== 'function') return null;
      index = await pdf.getPageIndex({ num: index.num, gen: index.gen });
    }
    if (!Number.isSafeInteger(index) || index < 0 || index >= pdf.numPages) return null;
    const result = { page: index + 1, kind };
    if (kind === 'XYZ') {
      result.point = { x: dest[2], y: dest[3] };
      result.zoom = dest[4] === 0 ? null : dest[4];
    } else if (kind === 'FitH' || kind === 'FitBH') result.point = { x: null, y: dest[2] };
    else if (kind === 'FitV' || kind === 'FitBV') result.point = { x: dest[2], y: null };
    else if (kind === 'FitR') {
      result.point = { x: dest[2], y: dest[5] };
      result.rect = { left: dest[2], bottom: dest[3], right: dest[4], top: dest[5] };
    }
    return result;
  } catch { return null; }
}

function copyAnchor(anchor) {
  if (!record(anchor) || !Number.isSafeInteger(anchor.page) || anchor.page < 1 ||
      !finite(anchor.nx) || anchor.nx < 0 || anchor.nx > 1 || !finite(anchor.ny) || anchor.ny < 0 || anchor.ny > 1 ||
      !finite(anchor.zoom) || anchor.zoom < .1 || anchor.zoom > 10 || typeof anchor.fingerprint !== 'string' ||
      !/^[a-f0-9]{64}$/.test(anchor.fingerprint)) return null;
  const hasViewportY = Object.hasOwn(anchor, 'viewportY');
  if (hasViewportY && (!finite(anchor.viewportY) || anchor.viewportY < 0 || anchor.viewportY > 1)) return null;
  const { page, nx, ny, zoom, fingerprint } = anchor;
  return { page, nx, ny, zoom, fingerprint, ...(hasViewportY ? { viewportY: anchor.viewportY } : {}) };
}

/** Session-local, bounded history. It does not change notebook/cloud position schemas. */
export function createNavigationHistory(limit = 30) {
  if (!Number.isSafeInteger(limit) || limit < 1) throw new RangeError('Navigation history limit must be a positive integer');
  const entries = [];
  return {
    push(anchor) {
      const value = copyAnchor(anchor);
      if (!value) return false;
      entries.push(value);
      if (entries.length > limit) entries.shift();
      return true;
    },
    pop() { return entries.length ? copyAnchor(entries.pop()) : null; },
    clear() { entries.length = 0; },
    get size() { return entries.length; },
  };
}
