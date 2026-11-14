// The manifest uses provider-independent SHA keys and exact legacy URL aliases.
// store.get(key, range) and store.head(key) are the storage-specific adapters.
const sha256 = /^[a-f0-9]{64}$/;
const unavailable = () => failure('PDF unavailable', 503);
function failure(message, status, extra = {}) {
  return new Response(message, { status, headers: { 'Cache-Control': 'no-store', ...extra } });
}
function edition(manifest, entry, expected) {
  let digest, key;
  if (manifest.version === 1 && typeof entry === 'string') {
    key = entry;
    digest = Object.hasOwn(manifest.objects, key) ? manifest.objects[key]?.sha256 : null;
    if (expected && expected !== digest) return { unsupported: true };
  } else if (manifest.version === 2 && entry && typeof entry === 'object' && !Array.isArray(entry)) {
    if (!sha256.test(entry.current) || !entry.editions || typeof entry.editions !== 'object'
        || Array.isArray(entry.editions) || !Object.hasOwn(entry.editions, entry.current)) return null;
    digest = expected || entry.current;
    if (!Object.hasOwn(entry.editions, digest)) return { unsupported: true };
    key = entry.editions[digest];
  } else return null;
  const meta = typeof key === 'string' && Object.hasOwn(manifest.objects, key) ? manifest.objects[key] : null;
  if (!sha256.test(digest) || key !== `pdf/sha256/${digest.slice(0, 2)}/${digest}.pdf`
      || !meta || meta.sha256 !== digest || meta.content_type !== 'application/pdf'
      || !Number.isSafeInteger(meta.size_bytes) || meta.size_bytes <= 0) return null;
  return { key, meta };
}
export async function serveMedia(request, manifest, store, fallback = () => new Response('Not found', { status: 404 })) {
  const url = new URL(request.url);
  let path;
  try { path = decodeURIComponent(url.pathname); } catch { return failure('Bad path', 400); }
  if (!manifest?.aliases || typeof manifest.aliases !== 'object' || Array.isArray(manifest.aliases)
      || !manifest.objects || typeof manifest.objects !== 'object' || Array.isArray(manifest.objects)) return unavailable();
  if (!Object.hasOwn(manifest.aliases, path)) return fallback(request);
  if (!['GET', 'HEAD'].includes(request.method)) return failure(null, 405, { Allow: 'GET, HEAD' });
  const expected = url.searchParams.getAll('sha256');
  if (expected.length > 1 || (expected.length === 1 && !sha256.test(expected[0]))
      || [...url.searchParams.keys()].some(name => name !== 'sha256')) return failure('Bad edition query', 400);
  const selected = edition(manifest, manifest.aliases[path], expected[0]);
  if (!selected) return unavailable();
  if (selected.unsupported) return failure('Unsupported PDF edition', 409);
  const { key, meta } = selected;
  // Existence/size is checked before conditional responses. This is not a SHA
  // proof: activation still requires full uploaded-byte hash verification.
  let head;
  try { head = await store.head(key); } catch { return unavailable(); }
  if (!head || head.size !== meta.size_bytes) return unavailable();
  const etag = `"sha256-${meta.sha256}"`;
  const headers = new Headers({ 'Content-Type': 'application/pdf', 'ETag': etag,
    'Accept-Ranges': 'bytes', 'X-Content-Type-Options': 'nosniff',
    // Legacy aliases can change editions. Revalidate instead of caching forever.
    'Cache-Control': 'public, max-age=0, must-revalidate' });
  if ((request.headers.get('if-none-match') || '').split(',').map(v => v.trim().replace(/^W\//, '')).some(v => v === '*' || v === etag)) return new Response(null, { status: 304, headers });
  let range = null;
  const rawRange = request.method === 'GET' && request.headers.get('range');
  const ifRange = request.headers.get('if-range');
  if (rawRange && (!ifRange || ifRange === etag)) {
    const match = /^bytes=(\d*)-(\d*)$/.exec(rawRange);
    let start, end;
    if (match && (match[1] || match[2])) {
      if (!match[1]) { start = Math.max(0, meta.size_bytes - Number(match[2])); end = meta.size_bytes - 1; }
      else { start = Number(match[1]); end = match[2] ? Math.min(Number(match[2]), meta.size_bytes - 1) : meta.size_bytes - 1; }
    }
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start < 0 || start > end || start >= meta.size_bytes || (match && !match[1] && Number(match[2]) === 0)) {
      return failure(null, 416, { 'Content-Range': `bytes */${meta.size_bytes}` });
    }
    range = { offset: start, length: end - start + 1 };
    headers.set('Content-Range', `bytes ${start}-${end}/${meta.size_bytes}`);
  }
  headers.set('Content-Length', String(range?.length ?? meta.size_bytes));
  if (request.method === 'HEAD') return new Response(null, { headers });
  let object;
  try { object = await store.get(key, range); } catch { return unavailable(); }
  if (!object || object.size !== meta.size_bytes || object.body == null) return unavailable();
  return new Response(object.body, { status: range ? 206 : 200, headers });
}
