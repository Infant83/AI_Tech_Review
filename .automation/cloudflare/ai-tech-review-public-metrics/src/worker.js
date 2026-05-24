const ALLOWED_PRODUCTION_ORIGIN = "https://infant83.github.io";
const MAX_PATH_LENGTH = 320;

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const headers = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers });
    }

    if (origin && !isAllowedOrigin(origin)) {
      return json({ ok: false, error: "origin_not_allowed" }, 403, headers);
    }

    const url = new URL(request.url);

    try {
      if (url.pathname === "/health") {
        return json({ ok: true, service: "ai-tech-review-public-metrics" }, 200, headers);
      }

      if (url.pathname === "/hit" && request.method === "POST") {
        const body = await readJson(request);
        const path = normalizePath(body.path);
        await recordHit(env.DB, path);
        return json({ ok: true, page: await getPageStats(env.DB, path) }, 200, headers);
      }

      if (url.pathname === "/engagement" && request.method === "POST") {
        const body = await readJson(request);
        const path = normalizePath(body.path);
        const activeSeconds = clampInteger(body.activeSeconds, 0, 300);
        const maxScrollPercent = clampInteger(body.maxScrollPercent, 0, 100);
        if (activeSeconds > 0 || maxScrollPercent > 0) {
          await recordEngagement(env.DB, path, activeSeconds, maxScrollPercent);
        }
        return json({ ok: true }, 200, headers);
      }

      if (url.pathname === "/stats" && request.method === "GET") {
        const path = normalizePath(url.searchParams.get("path") || "");
        return json({ ok: true, page: await getPageStats(env.DB, path), totals: await getTotals(env.DB) }, 200, headers);
      }

      if (url.pathname === "/summary" && request.method === "GET") {
        const paths = dedupe(url.searchParams.getAll("path").map(normalizePath)).slice(0, 30);
        return json({ ok: true, totals: await getTotals(env.DB), pages: await getPageSummary(env.DB, paths) }, 200, headers);
      }

      return json({ ok: false, error: "not_found" }, 404, headers);
    } catch (error) {
      const message = error instanceof PublicError ? error.message : "server_error";
      const status = error instanceof PublicError ? error.status : 500;
      return json({ ok: false, error: message }, status, headers);
    }
  },
};

class PublicError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}

function isAllowedOrigin(origin) {
  return (
    origin === ALLOWED_PRODUCTION_ORIGIN ||
    /^http:\/\/localhost(?::\d+)?$/.test(origin) ||
    /^http:\/\/127\.0\.0\.1(?::\d+)?$/.test(origin)
  );
}

function corsHeaders(origin) {
  const allowOrigin = origin && isAllowedOrigin(origin) ? origin : ALLOWED_PRODUCTION_ORIGIN;
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Cache-Control": "no-store",
    "Content-Type": "application/json; charset=utf-8",
    "Vary": "Origin",
  };
}

function json(payload, status, headers) {
  return new Response(JSON.stringify(payload), { status, headers });
}

async function readJson(request) {
  const text = await request.text();
  if (!text.trim()) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch {
    throw new PublicError("invalid_json", 400);
  }
}

function normalizePath(rawPath) {
  let path = String(rawPath || "").trim();
  if (!path) {
    throw new PublicError("missing_path", 400);
  }
  if (/^https?:\/\//i.test(path)) {
    path = new URL(path).pathname;
  }
  path = path.replace(/\/index\.html$/i, "/");
  if (!path.startsWith("/")) {
    path = `/${path}`;
  }
  if (path === "/AI_Tech_Review") {
    path = "/AI_Tech_Review/";
  }
  if (path !== "/" && !path.startsWith("/AI_Tech_Review/")) {
    throw new PublicError("path_not_allowed", 400);
  }
  if (path.includes("..") || path.includes("\0") || path.length > MAX_PATH_LENGTH) {
    throw new PublicError("invalid_path", 400);
  }
  return path;
}

function clampInteger(value, min, max) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return min;
  }
  return Math.min(max, Math.max(min, Math.round(number)));
}

function dedupe(values) {
  return Array.from(new Set(values));
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function nowIso() {
  return new Date().toISOString();
}

async function recordHit(db, path) {
  const now = nowIso();
  const date = todayIso();
  await db.batch([
    db.prepare(
      `INSERT INTO page_counts (path, views, active_seconds, engagement_events, max_scroll_percent, updated_at)
       VALUES (?, 1, 0, 0, 0, ?)
       ON CONFLICT(path) DO UPDATE SET
         views = views + 1,
         updated_at = excluded.updated_at`
    ).bind(path, now),
    db.prepare(
      `INSERT INTO daily_counts (date, path, views, active_seconds, engagement_events, max_scroll_percent, updated_at)
       VALUES (?, ?, 1, 0, 0, 0, ?)
       ON CONFLICT(date, path) DO UPDATE SET
         views = views + 1,
         updated_at = excluded.updated_at`
    ).bind(date, path, now),
  ]);
}

async function recordEngagement(db, path, activeSeconds, maxScrollPercent) {
  const now = nowIso();
  const date = todayIso();
  const engagementEvents = activeSeconds > 0 ? 1 : 0;
  await db.batch([
    db.prepare(
      `INSERT INTO page_counts (path, views, active_seconds, engagement_events, max_scroll_percent, updated_at)
       VALUES (?, 0, ?, ?, ?, ?)
       ON CONFLICT(path) DO UPDATE SET
         active_seconds = active_seconds + excluded.active_seconds,
         engagement_events = engagement_events + excluded.engagement_events,
         max_scroll_percent = MAX(max_scroll_percent, excluded.max_scroll_percent),
         updated_at = excluded.updated_at`
    ).bind(path, activeSeconds, engagementEvents, maxScrollPercent, now),
    db.prepare(
      `INSERT INTO daily_counts (date, path, views, active_seconds, engagement_events, max_scroll_percent, updated_at)
       VALUES (?, ?, 0, ?, ?, ?, ?)
       ON CONFLICT(date, path) DO UPDATE SET
         active_seconds = active_seconds + excluded.active_seconds,
         engagement_events = engagement_events + excluded.engagement_events,
         max_scroll_percent = MAX(max_scroll_percent, excluded.max_scroll_percent),
         updated_at = excluded.updated_at`
    ).bind(date, path, activeSeconds, engagementEvents, maxScrollPercent, now),
  ]);
}

async function getPageStats(db, path) {
  const row = await db.prepare(
    `SELECT path, views, active_seconds, engagement_events, max_scroll_percent, updated_at
     FROM page_counts
     WHERE path = ?`
  ).bind(path).first();
  return normalizeStats(row, path);
}

async function getTotals(db) {
  const row = await db.prepare(
    `SELECT
       COALESCE(SUM(views), 0) AS views,
       COALESCE(SUM(active_seconds), 0) AS active_seconds,
       COALESCE(SUM(engagement_events), 0) AS engagement_events
     FROM page_counts`
  ).first();
  return normalizeStats(row, "all");
}

async function getPageSummary(db, paths) {
  if (!paths.length) {
    return {};
  }
  const placeholders = paths.map(() => "?").join(", ");
  const { results } = await db.prepare(
    `SELECT path, views, active_seconds, engagement_events, max_scroll_percent, updated_at
     FROM page_counts
     WHERE path IN (${placeholders})`
  ).bind(...paths).all();

  const pages = {};
  for (const path of paths) {
    pages[path] = normalizeStats(null, path);
  }
  for (const row of results || []) {
    pages[row.path] = normalizeStats(row, row.path);
  }
  return pages;
}

function normalizeStats(row, path) {
  const views = Number(row?.views || 0);
  const activeSeconds = Number(row?.active_seconds || 0);
  const engagementEvents = Number(row?.engagement_events || 0);
  return {
    path,
    views,
    activeSeconds,
    engagementEvents,
    averageActiveSeconds: views > 0 ? Math.round(activeSeconds / views) : 0,
    maxScrollPercent: Number(row?.max_scroll_percent || 0),
    updatedAt: row?.updated_at || null,
  };
}
