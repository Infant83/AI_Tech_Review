const SERVICE_NAME = "infant83-public-metrics";
const ALLOWED_PRODUCTION_ORIGIN = "https://infant83.github.io";
const MAX_PATH_LENGTH = 320;
const SITE_CATALOG = [
  {
    id: "profile",
    label: "Hyun-Jung Kim Profile",
    exactPaths: ["/", "/ko.html"],
    prefixes: [],
  },
  {
    id: "ai-tech-review",
    label: "AI Tech Review Letters",
    exactPaths: [],
    prefixes: ["/AI_Tech_Review/"],
  },
  {
    id: "ax-camp",
    label: "AX Camp",
    exactPaths: [],
    prefixes: ["/Lets_AX_EXE/"],
  },
  {
    id: "gitlab-lectures",
    label: "GitLab Lectures",
    exactPaths: [],
    prefixes: ["/GitLab-Onboarding-Lectures/"],
  },
  {
    id: "ml-math",
    label: "ML Math",
    exactPaths: [],
    prefixes: ["/ML_math/"],
  },
];

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
        return json({ ok: true, service: SERVICE_NAME, catalog: publicCatalog() }, 200, headers);
      }

      if (url.pathname === "/catalog" && request.method === "GET") {
        return json({ ok: true, sites: publicCatalog() }, 200, headers);
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
        const site = siteForPath(path);
        return json({
          ok: true,
          page: await getPageStats(env.DB, path),
          site: site ? await getSiteStats(env.DB, site.id) : null,
          totals: await getTotals(env.DB),
        }, 200, headers);
      }

      if (url.pathname === "/summary" && request.method === "GET") {
        const paths = dedupe(url.searchParams.getAll("path").map(normalizePath)).slice(0, 30);
        const requestedSites = dedupe([
          ...url.searchParams.getAll("site").map(normalizeSiteId),
          ...paths.map((path) => siteForPath(path)?.id).filter(Boolean),
        ]).slice(0, 30);
        return json({
          ok: true,
          totals: await getTotals(env.DB),
          sites: await getSiteSummary(env.DB, requestedSites),
          pages: await getPageSummary(env.DB, paths),
        }, 200, headers);
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
    try {
      path = new URL(path).pathname;
    } catch {
      throw new PublicError("invalid_url", 400);
    }
  }
  if (!path.startsWith("/")) {
    path = `/${path}`;
  }
  path = path.replace(/\/index\.html$/i, "/");
  path = normalizeCatalogRoot(path);
  if (path.includes("..") || path.includes("\0") || path.length > MAX_PATH_LENGTH) {
    throw new PublicError("invalid_path", 400);
  }
  if (!siteForPath(path)) {
    throw new PublicError("path_not_allowed", 400);
  }
  return path;
}

function normalizeCatalogRoot(path) {
  for (const site of SITE_CATALOG) {
    for (const prefix of site.prefixes) {
      const rootWithoutSlash = prefix.replace(/\/$/, "");
      if (path === rootWithoutSlash) {
        return prefix;
      }
    }
  }
  return path;
}

function normalizeSiteId(rawSiteId) {
  const siteId = String(rawSiteId || "").trim().toLowerCase();
  if (!siteId) {
    throw new PublicError("missing_site", 400);
  }
  if (!SITE_CATALOG.some((site) => site.id === siteId)) {
    throw new PublicError("site_not_allowed", 400);
  }
  return siteId;
}

function siteForPath(path) {
  return SITE_CATALOG.find((site) => {
    return site.exactPaths.includes(path) || site.prefixes.some((prefix) => path.startsWith(prefix));
  }) || null;
}

function publicCatalog() {
  return SITE_CATALOG.map((site) => ({
    id: site.id,
    label: site.label,
    exactPaths: site.exactPaths,
    prefixes: site.prefixes,
  }));
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

async function getSiteStats(db, siteId) {
  const site = SITE_CATALOG.find((item) => item.id === siteId);
  if (!site) {
    throw new PublicError("site_not_allowed", 400);
  }
  const rows = await getAllPageRows(db);
  return aggregateSiteRows(rows.filter((row) => siteForPath(row.path)?.id === siteId), siteId);
}

async function getSiteSummary(db, siteIds) {
  if (!siteIds.length) {
    return {};
  }
  const rows = await getAllPageRows(db);
  const sites = {};
  for (const siteId of siteIds) {
    sites[siteId] = aggregateSiteRows(rows.filter((row) => siteForPath(row.path)?.id === siteId), siteId);
  }
  return sites;
}

async function getAllPageRows(db) {
  const { results } = await db.prepare(
    `SELECT path, views, active_seconds, engagement_events, max_scroll_percent, updated_at
     FROM page_counts`
  ).all();
  return results || [];
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
    site: siteForPath(path)?.id || null,
    views,
    activeSeconds,
    engagementEvents,
    averageActiveSeconds: views > 0 ? Math.round(activeSeconds / views) : 0,
    maxScrollPercent: Number(row?.max_scroll_percent || 0),
    updatedAt: row?.updated_at || null,
  };
}

function aggregateSiteRows(rows, siteId) {
  let views = 0;
  let activeSeconds = 0;
  let engagementEvents = 0;
  let maxScrollPercent = 0;
  let updatedAt = null;

  for (const row of rows) {
    views += Number(row?.views || 0);
    activeSeconds += Number(row?.active_seconds || 0);
    engagementEvents += Number(row?.engagement_events || 0);
    maxScrollPercent = Math.max(maxScrollPercent, Number(row?.max_scroll_percent || 0));
    if (row?.updated_at && (!updatedAt || row.updated_at > updatedAt)) {
      updatedAt = row.updated_at;
    }
  }

  return {
    site: siteId,
    views,
    activeSeconds,
    engagementEvents,
    averageActiveSeconds: views > 0 ? Math.round(activeSeconds / views) : 0,
    maxScrollPercent,
    updatedAt,
  };
}
