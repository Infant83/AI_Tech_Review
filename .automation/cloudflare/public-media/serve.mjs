// The manifest uses provider-independent SHA keys and exact legacy URL aliases.
// store.get(key, range) and store.head(key) are the storage-specific adapters.
export async function serveMedia(request, manifest, store, fallback = () => new Response('Not found', { status: 404 })) {
  const url = new URL(request.url);
  let path;
  try { path = decodeURIComponent(url.pathname); } catch { return new Response('Bad path', { status: 400 }); }
  const key = Object.hasOwn(manifest.aliases, path) ? manifest.aliases[path] : null;
  if (!key) return fallback(request);
  if (!['GET', 'HEAD'].includes(request.method)) return new Response(null, { status: 405, headers: { Allow: 'GET, HEAD' } });
  const meta = manifest.objects[key];
  if (!meta) return new Response('Unavailable', { status: 503 });
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
      headers.set('Content-Range', `bytes */${meta.size_bytes}`);
      return new Response(null, { status: 416, headers });
    }
    range = { offset: start, length: end - start + 1 };
    headers.set('Content-Range', `bytes ${start}-${end}/${meta.size_bytes}`);
  }
  headers.set('Content-Length', String(range?.length ?? meta.size_bytes));
  const object = request.method === 'HEAD' ? await store.head(key) : await store.get(key, range);
  if (!object || object.size !== meta.size_bytes) return new Response('PDF unavailable', { status: 503, headers: { 'Cache-Control': 'no-store' } });
  if (request.method === 'HEAD') return new Response(null, { headers });
  return new Response(object.body, { status: range ? 206 : 200, headers });
}
