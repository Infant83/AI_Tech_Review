export const SITE_ORIGIN = 'https://infant83.io';
export const SITE_ROOT = '/AI_Tech_Review/';
export const TOPICS = ['review', 'lecture'];
const encoder = new TextEncoder();

export class ApiError extends Error {
  constructor(code, status = 400) { super(code); this.code = code; this.status = status; }
}

export function base64url(bytes) {
  let value = '';
  for (const byte of new Uint8Array(bytes)) value += String.fromCharCode(byte);
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

export function decode64(value, length) {
  if (typeof value !== 'string' || !/^[A-Za-z0-9_-]+$/.test(value) || value.length > 256) {
    throw new ApiError('invalid_key');
  }
  let result;
  try { result = Uint8Array.from(atob(value.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)); }
  catch { throw new ApiError('invalid_key'); }
  if (result.length !== length || base64url(result) !== value) throw new ApiError('invalid_key');
  return result;
}

export async function sha256(value) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(value)))].map(v => v.toString(16).padStart(2, '0')).join('');
}

export function randomToken() { return base64url(crypto.getRandomValues(new Uint8Array(32))); }

export async function equalSecret(received, expected) {
  if (typeof expected !== 'string' || expected.length < 32) throw new ApiError('server_not_configured', 503);
  const [a, b] = await Promise.all([sha256(received || ''), sha256(expected)]);
  let difference = 0;
  for (let i = 0; i < a.length; i++) difference |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return difference === 0;
}

export function allowedOrigins(env) {
  const origins = new Set([SITE_ORIGIN]);
  for (const candidate of String(env.DEV_ALLOWED_ORIGINS || '').split(',').map(v => v.trim()).filter(Boolean)) {
    let url;
    try { url = new URL(candidate); } catch { throw new ApiError('invalid_development_config', 503); }
    if (!['localhost', '127.0.0.1', '[::1]'].includes(url.hostname) || !['http:', 'https:'].includes(url.protocol) || candidate !== url.origin) {
      throw new ApiError('invalid_development_config', 503);
    }
    origins.add(candidate);
  }
  return origins;
}

export function assertOrigin(request, env, required = false) {
  const origin = request.headers.get('Origin');
  if ((!origin && required) || (origin && !allowedOrigins(env).has(origin))) throw new ApiError('origin_not_allowed', 403);
  return origin;
}

export function responseHeaders(request, env) {
  const headers = new Headers({
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'private, no-store',
    'Vary': 'Origin',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
  });
  const origin = request.headers.get('Origin');
  // Configuration errors must still produce a closed, readable JSON error.
  let allowed = false;
  try { allowed = !!origin && allowedOrigins(env).has(origin); } catch {}
  if (allowed) {
    headers.set('Access-Control-Allow-Origin', origin);
    headers.set('Access-Control-Allow-Credentials', 'true');
    headers.set('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
    headers.set('Access-Control-Allow-Headers', 'Content-Type');
    headers.set('Access-Control-Max-Age', '600');
  }
  return headers;
}

export function cookieConfig(request, env) {
  const host = new URL(request.url).hostname;
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(host);
  const insecure = env.DEV_ALLOW_INSECURE_COOKIE === 'true' && local;
  return { name: insecure ? 'reader_session' : '__Host-reader_session', secure: !insecure };
}

export function sessionCookie(request, env, token) {
  const {name, secure} = cookieConfig(request, env);
  return `${name}=${token}; Path=/; Max-Age=31536000; HttpOnly; SameSite=Strict${secure ? '; Secure' : ''}`;
}

export function readToken(request, env) {
  const {name} = cookieConfig(request, env);
  const matches = (request.headers.get('Cookie') || '').split(';').map(v => v.trim()).filter(v => v.startsWith(`${name}=`));
  if (matches.length !== 1) return null;
  const token = matches[0].slice(name.length + 1);
  return /^[A-Za-z0-9_-]{43}$/.test(token) ? token : null;
}

export function object(value, keys, required = keys) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new ApiError('invalid_json_object');
  if (Object.keys(value).some(key => !keys.includes(key)) || required.some(key => !Object.hasOwn(value, key))) throw new ApiError('invalid_fields');
  return value;
}

export async function readJson(request, limit = 8192) {
  if (!/^application\/json(?:\s*;.*)?$/i.test(request.headers.get('Content-Type') || '')) throw new ApiError('json_required', 415);
  if (Number(request.headers.get('Content-Length') || 0) > limit) throw new ApiError('body_too_large', 413);
  let total = 0;
  const chunks = [];
  if (request.body) {
    const reader = request.body.getReader();
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > limit) { await reader.cancel(); throw new ApiError('body_too_large', 413); }
      chunks.push(value);
    }
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  try { return JSON.parse(new TextDecoder('utf-8', {fatal:true}).decode(bytes)); }
  catch { throw new ApiError('invalid_json'); }
}

export function validArticleId(id) {
  if (typeof id !== 'string' || !/^(?:lecture:)?[A-Za-z0-9][A-Za-z0-9._-]{0,179}$/.test(id)) throw new ApiError('invalid_article_id');
  return id;
}

export function article(value) {
  object(value, ['id','path','title','publishedAt','topic']);
  validArticleId(value.id);
  if (!TOPICS.includes(value.topic) || (value.topic === 'lecture') !== value.id.startsWith('lecture:')) throw new ApiError('invalid_article_topic');
  if (typeof value.title !== 'string' || !value.title.trim() || value.title.length > 240 || /[\u0000-\u001f]/.test(value.title)) throw new ApiError('invalid_article_title');
  if (typeof value.publishedAt !== 'string' || !/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z)?$/.test(value.publishedAt) || !Number.isFinite(Date.parse(value.publishedAt)) || new Date(value.publishedAt).toISOString().slice(0,10) !== value.publishedAt.slice(0,10)) throw new ApiError('invalid_publication_date');
  const folder = value.id.replace(/^lecture:/, '');
  const safeLecture = /^\/AI_Tech_Review\/(?:lectures\/[A-Za-z0-9][A-Za-z0-9._-]{0,179}\/|archive\/files\/[A-Za-z0-9][A-Za-z0-9._-]{0,179}\.pdf)$/;
  // Existing lecture document IDs predate their web-view slugs. PDF-only
  // lectures retain their public archive URL and the same document identity.
  if (value.topic === 'review' ? value.path !== `${SITE_ROOT}reviews/${folder}/` : typeof value.path !== 'string' || !safeLecture.test(value.path)) throw new ApiError('invalid_article_path');
  return {...value, title:value.title.trim()};
}

export function pushSubscription(value) {
  object(value, ['endpoint','expirationTime','keys'], ['endpoint','keys']);
  if (typeof value.endpoint !== 'string' || value.endpoint.length > 2048) throw new ApiError('invalid_push_endpoint');
  let url;
  try { url = new URL(value.endpoint); } catch { throw new ApiError('invalid_push_endpoint'); }
  if (url.protocol !== 'https:' || url.username || url.password || url.port || url.hash) throw new ApiError('invalid_push_endpoint');
  const supported =
    (url.hostname === 'web.push.apple.com' && /^\/[^/].{4,}$/.test(url.pathname)) ||
    (url.hostname === 'fcm.googleapis.com' && /^\/(?:fcm\/send|wp)\/.+/.test(url.pathname)) ||
    (url.hostname === 'updates.push.services.mozilla.com' && /^\/wpush\/v2\/.+/.test(url.pathname)) ||
    (/^[a-z0-9-]+\.notify\.windows\.com$/.test(url.hostname) && /^\/w\//.test(url.pathname));
  if (!supported || url.href !== value.endpoint) throw new ApiError('unsupported_push_endpoint');
  object(value.keys, ['p256dh','auth']);
  const publicKey = decode64(value.keys.p256dh, 65);
  if (publicKey[0] !== 4) throw new ApiError('invalid_key');
  decode64(value.keys.auth, 16);
  const expirationTime = value.expirationTime ?? null;
  if (expirationTime !== null && (!Number.isSafeInteger(expirationTime) || expirationTime <= Date.now())) throw new ApiError('invalid_expiration');
  return {endpoint:url.href, expirationTime, keys:{p256dh:value.keys.p256dh, auth:value.keys.auth}};
}

export function topics(value) {
  if (!Array.isArray(value) || value.length < 1 || value.length > 2 || value.some(v => !TOPICS.includes(v)) || new Set(value).size !== value.length) throw new ApiError('invalid_topics');
  return TOPICS.filter(topic => value.includes(topic));
}
