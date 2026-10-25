# Reader engagement frontend

These source files are copied by the publication integration into the existing static site. They add controls without replacing the current page layout or app artwork.

| Source | Public destination |
| --- | --- |
| `reader-engagement.js` | `site/assets/reader-engagement.js` |
| `reader-engagement.css` | `site/assets/reader-engagement.css` |
| `app.webmanifest` | `site/app.webmanifest` |
| `sw.js` | `site/sw.js` |

The publisher emits an escaped JSON script with `id="reader-engagement-config"` and `type="application/json"` before the deferred JavaScript. Expected fields are `apiBase`, `scope`, and `article` (an object containing `id` and optional `title`, or `null` on hubs). Article IDs are shared between Korean and English pages. The share URL deliberately uses the current page path, preserving `/en/`, under `https://infant83.io`.

The only production API origin accepted by the frontend is `https://api.infant83.io`. Local API use requires both a localhost page and explicit `allowLocalApi: true`. All API calls use `credentials: "include"`; device sessions belong in the API's HttpOnly cookie. The frontend stores no authentication tokens and creates an anonymous device only after a reader asks to like or subscribe.

The service worker only handles push and notification clicks. It has no fetch handler, offline article cache, or page-rewriting behavior. Notification links must remain inside the worker's own origin and `/AI_Tech_Review/` scope. Existing `assets/apple-touch-icon.png` and `assets/ai-tech-review-icon.svg` artwork is reused.

## Device-specific help

The same alert dialog contains a native `details`/`summary` guide with a labeled device selector. It defaults to iPhone/iPad, Mac Chrome, Mac Safari, or other devices using the current environment as a hint. Readers can inspect another device's instructions. Their selection and the disclosure state survive asynchronous dialog updates, including a native toggle event that has not yet been delivered. Keyboard navigation includes the summary and selector but excludes controls hidden inside a closed disclosure.

On an ordinary iPhone browser tab, the installation guide opens by default: Share → Add to Home Screen → open the icon for the current address, followed by explicit alert permission and a test alert. The installed Home Screen app shows shorter subscription/settings help and does not ask to install again. Old icons for a different address are not treated as equivalent.

Mac installation is optional because supported regular browser tabs can receive web alerts. Chrome instructions describe the address-bar icon or the version-dependent Cast, save, and share → Install page as app menu; Safari instructions describe File → Add to Dock when supported. Readers who install are told to open the Dock/app icon and subscribe in that app's own window. Guidance covers the actual macOS app entry (web app name or Chrome/Safari), Notification Center, Focus, and testing outside private browsing. Existing subscribers can still find this help and are directed to test their connection instead of enabling it again.

An optional native installation button appears only after the browser actually emits a usable `beforeinstallprompt` event and only outside a known installed mode. `prompt()` is called solely from that button's click. The event is consumed once, and `appinstalled` suppresses further offers in the current tab. No event is not proof that an app is absent or installed; ordinary tabs cannot reliably enumerate previous installations. Opening or changing this guide never requests notification permission.

Official references: [Chrome installation](https://support.google.com/chrome/answer/9658361?hl=en), [Chrome notifications](https://support.google.com/chrome/answer/3220216?hl=en), [Chrome macOS notification attribution](https://developer.chrome.com/blog/notification-attribution-macos), [MDN beforeinstallprompt](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeinstallprompt_event), [Safari web apps on Mac](https://support.apple.com/en-us/104996), [WebKit iPhone Web Push](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/).

## Recent new-article alerts

The alert dialog shows the worker's recent received notifications before the device help. It initially shows five records and can expand to twenty. Titles are plain text, links must retain the worker-provided URL on the current origin and scope, and timestamps explicitly mean received time rather than publication time. The frontend never builds this list from the publication catalog or invents earlier notifications for new subscribers.

After the active worker is ready, and on top-level foreground `pageshow`, `focus`, visible `visibilitychange`, or `controllerchange`, the frontend requests `{type: "atr-reader-notification-state"}` with a dedicated MessagePort. The response is `{ok: true, count, notifications: [{id, title, url, receivedAt}]}`. The worker resets the number only after verifying a visible, focused WindowClient; a nonnegative nonzero count remains a valid response if OS focus metadata has not caught up. Confirmation does not claim that individual articles have been read, and the recent list stays after the number is cleared. Native app badges are supported only where the platform allows them; test alerts are not new-article counts.

Requests have a four-second deadline, reuse an in-flight request, debounce repeated events, and ignore outdated-worker or late responses. A missing or old worker does not affect permission, subscription, likes or sharing. Plain modal re-renders never request a confirmation. A worker hint refreshes the list only when its source script URL is exactly the current scoped `sw.js`; hidden/unfocused documents defer that refresh until foreground, and framed documents do not confirm alerts. No new notification API request, app-install prompt, catalog backfill or badge operation is performed by merely rendering the list.

## Local checks

Run the security and error-state tests without launching a browser:

```sh
READER_UNIT_ONLY=1 node --test .automation/reader-engagement/frontend/tests/reader-engagement.test.cjs
node --check .automation/reader-engagement/frontend/reader-engagement.js
node --check .automation/reader-engagement/frontend/sw.js
```

The test file also retains browser regression cases using mocked permissions, service workers, and API responses. Those cases verify UI state transitions, not delivery through Apple's or Google's push infrastructure. Follow the active session's browser-control rules when doing visual QA.

## Manual acceptance checks

1. At 320, 390, 736, and desktop widths, keep the original header, article, footer, images, and app icons. Hubs gain only an alert button. Article pages gain a small like/share/copy/alert bar after the article and an alert button in an existing top header, when present. Both alert buttons open the same settings and stay synchronized. Check for horizontal overflow and 44px touch targets.
2. Open alerts in an ordinary iPhone browser tab. Show home-screen installation instructions without requesting notification permission. Add the site through the actual browser UI, then open its home-screen icon.
3. Inside the installed web app, tap the subscription button. Only this direct action may request OS permission. Declining must show settings instructions; checking again must not repeatedly prompt a denied permission.
4. Allow permission and subscribe. Save review/lecture preferences, unsubscribe, and resubscribe. A granted permission must not be requested again. A failed API save must preserve the existing browser subscription for retry. Permission waiting is bounded to 30 seconds and browser Push operations to 25 seconds. A retry reuses an in-flight browser request, and a late response cannot automatically save a subscription. Cookie failures and incomplete unsubscribe attempts must not display full success.
5. Like and unlike the same article in Korean and English. Both use the same article ID. Reload to verify server state, and check retry messages during API failures.
6. Share an English article. Native sharing should keep its English URL; canceling should remain silent. The adjacent Copy link button stays available even when native sharing is unavailable or unresponsive. Without native sharing, copy the canonical `infant83.io` URL. If clipboard access fails, show a selectable address.
7. Confirm dialog focus stays inside, Escape closes it, focus returns to its opener, and long content remains scrollable. Server text and article titles must be rendered as text, never HTML.
8. After an actual subscription, use **Send a test alert to this device** once. Acceptance means the API queued the request. Separately verify arrival on the physical iPhone lock screen and that tapping opens the exact article. Check denied permission, Focus settings, and network conditions if it does not arrive. Test requests are limited to one per minute and five per day per device by the backend.
9. Open the device guide in normal and installed iPhone/Mac Chrome/Mac Safari contexts. Check the default device, optional/required installation distinction, installed-mode duplicate-install suppression, another-device selection, and persistence after a settings update. With a closed guide, Tab must skip its hidden selector/install button. An actual browser install offer may be opened only by the optional install button; an absent event must not produce a fabricated install button.
10. Receive an actual new-article push and open the app/site in the foreground. On supported installed apps, check the native number clears while the recent list remains. Confirm the list shows received times, safe exact article URLs, at most twenty records and no test alerts or catalog backfill. Background tabs and hidden frames must not confirm or clear alerts; an old worker timeout must not block subscription controls.

No mocked result, queued response, or browser regression test establishes real-device notification delivery. No commit, push, or deployment is performed by these frontend source files.

## Numeric badges and recent article alerts

A genuine article push with a valid article ID and in-scope URL adds one device/browser-local alert. Repeated delivery of the same ID and test alerts are excluded. Opening and focusing the site/app resets the numeric badge while keeping the most recent twenty titles, article links and received times in the alert dialog. This is not a per-article read receipt or cross-device account inbox.

The service worker stores public metadata in IndexedDB, bounded to twenty recent items and 2,000 deduplication IDs. It verifies the real same-origin, in-scope WindowClient before answering the MessageChannel request. Hidden/background requests can read without clearing. Badging API/storage failures do not suppress the existing visible push or delay opening a notification link.

Numeric icon display requires a supported installed app and OS badge permission. iPhone Home Screen apps and supported Mac Dock apps can display it; color and appearance are controlled by the OS. Android Chrome's native notification dots are not a web-controlled numeric badge. See [WebKit](https://webkit.org/blog/14112/badging-for-home-screen-web-apps/), [Chrome Badging API](https://developer.chrome.com/docs/capabilities/web-apis/badging-api), and [Chrome macOS app notification attribution](https://developer.chrome.com/blog/notification-attribution-macos).

Install the test-only dependency and run the frontend plus badge tests without launching a browser:

```sh
cd .automation/reader-engagement/frontend
npm ci
npm run test:unit
```

The native positive badge display should be checked on an installed device after a genuine new article arrives. Test alerts intentionally leave the badge and recent-article list unchanged.
