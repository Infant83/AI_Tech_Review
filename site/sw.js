/* Push only: deliberately does not intercept or cache article requests. */
"use strict";

const READER_SCOPE = new URL(self.registration.scope);
const READER_ICON = new URL("assets/apple-touch-icon.png", READER_SCOPE).href;

function readerNotificationURL(value) {
  try {
    const url = new URL(String(value || ""), READER_SCOPE);
    if (url.origin === READER_SCOPE.origin && url.pathname.startsWith(READER_SCOPE.pathname)) {
      return url.href;
    }
  } catch (_) { /* Fall back to the review hub. */ }
  return READER_SCOPE.href;
}

self.addEventListener("push", function (event) {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch (_) { /* An invalid payload must still produce a visible notification. */ }
  if (!payload || typeof payload !== "object") payload = {};
  const notification = payload.notification && typeof payload.notification === "object"
    ? payload.notification : payload;
  const url = readerNotificationURL(notification.navigate || notification.url || payload.url);
  const title = (typeof notification.title === "string" && notification.title ? notification.title : "AI Tech Review Letters").slice(0, 160);
  const body = (typeof notification.body === "string" ? notification.body : "새 글이 발행되었습니다. New article published.").slice(0, 400);
  const tag = (typeof notification.tag === "string" ? notification.tag : typeof payload.articleId === "string" ? payload.articleId : url).slice(0, 240);
  event.waitUntil(self.registration.showNotification(title, {
    body: body,
    icon: READER_ICON,
    badge: READER_ICON,
    tag: tag,
    data: { url: url },
    // Updating a retried notification should not alert the reader a second time.
    renotify: false
  }));
});

self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  const url = readerNotificationURL(event.notification.data && event.notification.data.url);
  event.waitUntil((async function () {
    const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true }).catch(function () { return []; });
    const exact = windows.find(function (client) { return client.url === url; });
    if (exact && typeof exact.focus === "function") {
      try { return await exact.focus(); } catch (_) { /* A closed window can race with the click. */ }
    }
    const app = windows.find(function (client) {
      try {
        const current = new URL(client.url);
        return current.origin === READER_SCOPE.origin && current.pathname.startsWith(READER_SCOPE.pathname);
      } catch (_) { return false; }
    });
    if (app && typeof app.navigate === "function") {
      try {
        const navigated = await app.navigate(url);
        if (navigated && typeof navigated.focus === "function") return navigated.focus();
      } catch (_) { /* A closed window can race with the click. Open a new one. */ }
    }
    if (typeof self.clients.openWindow === "function") return self.clients.openWindow(url);
  })());
});
