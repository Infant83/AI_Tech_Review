/* Push only: deliberately does not intercept or cache article requests. */
"use strict";

const READER_SCOPE = new URL(self.registration.scope);
const READER_ICON = new URL("assets/apple-touch-icon.png", READER_SCOPE).href;
const READER_STATE_DB = "atr-reader-notifications:" + READER_SCOPE.pathname;
const READER_STATE_STORE = "state";
const READER_STATE_KEY = "notification-state";
const READER_MAX_SEEN = 2000;
const READER_MAX_RECENT = 20;
let readerDatabasePromise;
let readerStateQueue = Promise.resolve();
let readerDesiredBadge = 0;
let readerBadgeGeneration = 0;
let readerBadgeReconcileScheduled = false;
let readerNavigationGeneration = 0;

function readerScopedURL(value) {
  if (typeof value !== "string" || !value) return null;
  try {
    const url = new URL(value, READER_SCOPE);
    if (!url.username && !url.password && url.origin === READER_SCOPE.origin && url.pathname.startsWith(READER_SCOPE.pathname)) return url.href;
  } catch (_) { /* Untrusted links must not enter notification history. */ }
  return null;
}

function readerNotificationURL(value) {
  return readerScopedURL(value) || READER_SCOPE.href;
}

function readerArticleId(value) {
  return typeof value === "string" && /^(?:lecture:)?[A-Za-z0-9][A-Za-z0-9._-]{0,179}$/.test(value);
}

function readerArticle(payload, title, rawURL) {
  if (!readerArticleId(payload.articleId) || typeof title !== "string" || !title.trim()) return null;
  const url = readerScopedURL(rawURL);
  if (!url) return null;
  const pathname = new URL(url).pathname;
  const relative = pathname.slice(READER_SCOPE.pathname.length);
  if (payload.articleId.startsWith("lecture:")) {
    if (!/^(?:lectures\/[A-Za-z0-9][A-Za-z0-9._-]{0,179}\/(?:index\.html)?|archive\/files\/[A-Za-z0-9][A-Za-z0-9._-]{0,179}\.pdf)$/.test(relative)) return null;
  } else {
    const base = "reviews/" + payload.articleId + "/";
    if (![base, base + "index.html", base + "en/", base + "en/index.html"].includes(relative)) return null;
  }
  const text = title.replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, 160);
  return text ? { id: payload.articleId, title: text, url: url } : null;
}

function readerStoredState(value) {
  const current = value && typeof value === "object" ? value : {};
  const seen = Array.isArray(current.seenArticleIds) ? current.seenArticleIds.slice(-READER_MAX_SEEN) : [];
  const seenArticleIds = Array.from(new Set(seen.filter(readerArticleId)));
  const notifications = [];
  const recentIds = new Set();
  if (Array.isArray(current.notifications)) current.notifications.slice(0, READER_MAX_RECENT).forEach(function (item) {
    if (!item || typeof item !== "object" || !Number.isSafeInteger(item.receivedAt) || item.receivedAt <= 0) return;
    const article = readerArticle({ articleId: item.id }, item.title, item.url);
    if (!article || recentIds.has(article.id)) return;
    recentIds.add(article.id);
    notifications.push({ ...article, receivedAt: item.receivedAt });
  });
  return {
    count: Number.isSafeInteger(current.count) && current.count >= 0 ? current.count : 0,
    seenArticleIds: seenArticleIds,
    notifications: notifications
  };
}

function readerDatabase() {
  if (readerDatabasePromise) return readerDatabasePromise;
  readerDatabasePromise = new Promise(function (resolve, reject) {
    const factory = self.indexedDB || (typeof indexedDB !== "undefined" ? indexedDB : null);
    if (!factory) { reject(new Error("notification_state_unavailable")); return; }
    let request, settled = false;
    const timer = setTimeout(function () { finish(new Error("notification_state_timeout")); }, 2500);
    function finish(error, database) {
      if (settled) { if (database) database.close(); return; }
      settled = true;
      clearTimeout(timer);
      if (error) reject(error); else resolve(database);
    }
    try { request = factory.open(READER_STATE_DB, 1); }
    catch (error) { finish(error); return; }
    request.onupgradeneeded = function () {
      if (!request.result.objectStoreNames.contains(READER_STATE_STORE)) request.result.createObjectStore(READER_STATE_STORE);
    };
    request.onerror = function () { finish(request.error || new Error("notification_state_unavailable")); };
    request.onblocked = function () { finish(new Error("notification_state_blocked")); };
    request.onsuccess = function () {
      const database = request.result;
      database.onversionchange = function () { database.close(); readerDatabasePromise = null; };
      finish(null, database);
    };
  }).catch(function (error) { readerDatabasePromise = null; throw error; });
  return readerDatabasePromise;
}

async function readerChangeState(change) {
  const database = await readerDatabase();
  return new Promise(function (resolve, reject) {
    let transaction, next, settled = false;
    const timer = setTimeout(function () {
      try { transaction.abort(); } catch (_) { /* It may already have finished. */ }
      finish(new Error("notification_state_timeout"));
    }, 2500);
    function finish(error) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (error) reject(error); else resolve(next);
    }
    try {
      transaction = database.transaction(READER_STATE_STORE, change ? "readwrite" : "readonly");
      const store = transaction.objectStore(READER_STATE_STORE);
      const request = store.get(READER_STATE_KEY);
      request.onsuccess = function () {
        if (settled) return;
        try {
          // No await between read and write: one atomic IDB transaction also
          // protects against an overlapping worker instance during an update.
          next = readerStoredState(request.result);
          if (change) {
            next = readerStoredState(change(next));
            store.put(next, READER_STATE_KEY);
          }
        } catch (error) {
          try { transaction.abort(); } catch (_) { /* Report the original error. */ }
          finish(error);
        }
      };
      transaction.oncomplete = function () { finish(); };
      transaction.onabort = function () { finish(transaction.error || new Error("notification_state_aborted")); };
      transaction.onerror = function () { /* The subsequent abort rejects once. */ };
    } catch (error) { finish(error); }
  });
}

function readerSerialState(operation) {
  const next = readerStateQueue.then(operation);
  // A storage or OS failure must not poison later push/clear operations.
  readerStateQueue = next.catch(function () {});
  return next;
}

function readerInvokeNativeBadge(count, generation) {
  const badgeNavigator = self.navigator || (typeof navigator !== "undefined" ? navigator : null);
  if (!badgeNavigator) return Promise.resolve();
  let request;
  try {
    if (count === 0 && typeof badgeNavigator.clearAppBadge === "function") request = badgeNavigator.clearAppBadge();
    else if (typeof badgeNavigator.setAppBadge === "function") request = badgeNavigator.setAppBadge(count);
    else return Promise.resolve();
  } catch (_) { return Promise.resolve(); }
  const native = Promise.resolve(request);
  async function completed() {
    try {
      // An update can briefly overlap two worker globals. Their promise queues
      // are separate, so also compare against the durable count after an OS
      // call completes. A late old worker cannot leave its stale badge behind.
      const durable = await readerChangeState(null);
      if (generation === readerBadgeGeneration && durable.count !== count) {
        readerDesiredBadge = durable.count;
        readerBadgeGeneration += 1;
      }
    } catch (_) { /* Storage failure cannot block native completion. */ }
    // The OS API cannot be cancelled. If an old set finishes after a newer
    // clear, reapply the latest desired value without changing its generation.
    if (generation !== readerBadgeGeneration && !readerBadgeReconcileScheduled) {
      readerBadgeReconcileScheduled = true;
      Promise.resolve().then(function () {
        readerBadgeReconcileScheduled = false;
        readerInvokeNativeBadge(readerDesiredBadge, readerBadgeGeneration);
      });
    }
  }
  const completion = native.then(completed, completed);
  return new Promise(function (resolve) {
    const timer = setTimeout(resolve, 1200);
    completion.then(function () { clearTimeout(timer); resolve(); }, function () { clearTimeout(timer); resolve(); });
  });
}

function readerNativeBadge(count) {
  readerDesiredBadge = count;
  readerBadgeGeneration += 1;
  return readerInvokeNativeBadge(count, readerBadgeGeneration);
}

function readerScopedWindow(client) {
  return !!client && client.type === "window" && !!readerScopedURL(client.url);
}

async function readerWindowStatus() {
  try {
    const windows = (await self.clients.matchAll({ type: "window", includeUncontrolled: true })).filter(readerScopedWindow);
    return { windows: windows, focused: windows.some(function (client) {
      return client.visibilityState === "visible" && client.focused === true;
    }) };
  } catch (_) { return { windows: [], focused: false }; }
}

function readerRememberArticle(article) {
  return readerSerialState(async function () {
    const status = await readerWindowStatus();
    let added = false;
    const state = await readerChangeState(function (current) {
      if (!current.seenArticleIds.includes(article.id)) {
        added = true;
        current.seenArticleIds.push(article.id);
        current.seenArticleIds = current.seenArticleIds.slice(-READER_MAX_SEEN);
        current.notifications.unshift({ ...article, receivedAt: Date.now() });
        current.notifications = current.notifications.slice(0, READER_MAX_RECENT);
        current.count = Math.min(Number.MAX_SAFE_INTEGER, current.count + 1);
      }
      if (status.focused) current.count = 0;
      return current;
    });
    if (added) status.windows.forEach(function (client) {
      try { client.postMessage({ type: "atr-reader-notifications-changed" }); } catch (_) { /* Optional UI refresh hint only. */ }
    });
    // Serialize the desired value with the transaction, but never hold the
    // state queue while waiting for an OS API that might remain pending.
    return { state: state, badge: readerNativeBadge(state.count) };
  }).then(async function (result) { await result.badge; return result.state; });
}

self.addEventListener("message", function (event) {
  if (!event.data || event.data.type !== "atr-reader-notification-state") return;
  const port = event.ports && event.ports[0];
  if (!port || typeof port.postMessage !== "function") return;
  const operation = readerSerialState(async function () {
    let source;
    try {
      if (!readerScopedWindow(event.source) || typeof event.source.id !== "string") return { response: { ok: false, error: "source_not_allowed" } };
      source = await self.clients.get(event.source.id);
    } catch (_) { return { response: { ok: false, error: "source_not_allowed" } }; }
    if (!readerScopedWindow(source) || source.id !== event.source.id) return { response: { ok: false, error: "source_not_allowed" } };
    const foreground = source.visibilityState === "visible" && source.focused === true;
    let state;
    try {
      state = await readerChangeState(function (current) { if (foreground) current.count = 0; return current; });
    } catch (_) {
      return { response: { ok: false, error: "state_unavailable" }, badge: foreground ? readerNativeBadge(0) : null };
    }
    return { response: { ok: true, count: state.count, notifications: state.notifications }, badge: foreground ? readerNativeBadge(0) : null };
  }).then(function (result) {
    try { port.postMessage(result.response); } catch (_) { /* The page may have closed. */ }
    return result.badge;
  }).catch(function () {
    try { port.postMessage({ ok: false, error: "state_unavailable" }); } catch (_) {}
  });
  event.waitUntil(operation);
});

// There is no fetch/cache handler, so claiming an existing client does not
// change article loading and lets new reader controls contact this worker.
self.addEventListener("install", function (event) {
  if (typeof self.skipWaiting === "function") event.waitUntil(self.skipWaiting());
});
self.addEventListener("activate", function (event) {
  if (typeof self.clients.claim === "function") event.waitUntil(self.clients.claim());
});

self.addEventListener("push", function (event) {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch (_) { /* An invalid payload must still produce a visible notification. */ }
  if (!payload || typeof payload !== "object") payload = {};
  const notification = payload.notification && typeof payload.notification === "object"
    ? payload.notification : payload;
  const rawURL = notification.navigate || notification.url || payload.url;
  const url = readerNotificationURL(rawURL);
  const title = (typeof notification.title === "string" && notification.title ? notification.title : "AI Tech Review Letters").slice(0, 160);
  const body = (typeof notification.body === "string" ? notification.body : "새 글이 발행되었습니다. New article published.").slice(0, 400);
  const tag = (typeof notification.tag === "string" ? notification.tag : typeof payload.articleId === "string" ? payload.articleId : url).slice(0, 240);
  // Start the visible notification independently. IDB/Badging API failures or
  // delays must never suppress the existing user-visible Web Push alert.
  let visible;
  try { visible = Promise.resolve(self.registration.showNotification(title, {
    body: body,
    icon: READER_ICON,
    badge: READER_ICON,
    tag: tag,
    data: { url: url },
    // Updating a retried notification should not alert the reader a second time.
    renotify: false
  })); } catch (error) { visible = Promise.reject(error); }
  const article = readerArticle(payload, notification.title, rawURL);
  const recorded = article ? readerRememberArticle(article).catch(function () {}) : Promise.resolve();
  event.waitUntil(Promise.all([visible, recorded]));
});

self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  const url = readerNotificationURL(event.notification.data && event.notification.data.url);
  const fresh = new URL(url);
  // A tap asks to see the current article. A matching open window may contain
  // an older DOM, and the canonical URL may still be fresh in the HTTP cache.
  // Keep real query parameters and anchors while giving this navigation its
  // own cache key; the page removes the transient marker after it has loaded.
  fresh.searchParams.set("_atr_refresh", Date.now().toString(36) + "-" + (++readerNavigationGeneration).toString(36));
  event.waitUntil((async function () {
    const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true }).catch(function () { return []; });
    const scoped = windows.filter(readerScopedWindow);
    const comparable = function (value) {
      const current = new URL(value);
      current.searchParams.delete("_atr_refresh");
      return current.href;
    };
    const exact = scoped.find(function (client) { return comparable(client.url) === comparable(url); });
    const candidates = exact ? [exact, ...scoped.filter(function (client) { return client !== exact; })] : scoped;
    for (const app of candidates) {
      if (typeof app.navigate !== "function") continue;
      try {
        const navigated = await app.navigate(fresh.href);
        if (!navigated) continue;
        if (typeof navigated.focus === "function") return await navigated.focus();
        return navigated;
      } catch (_) { /* A closed window can race with the click. Try another. */ }
    }
    if (typeof self.clients.openWindow === "function") return self.clients.openWindow(fresh.href);
  })());
});
