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

## Public reader activity counters

Only the exact review hub index gains a compact summary after its existing article statistics, with the user-selected label **방문자수 / Visitors**. Article pages retain only open and share/copy counts within the existing reader action bar. Supplementary methods, archive, briefing and lecture-list pages gain no summary or additional main-grid child. Existing content, header links, artwork, app identity and like/share controls are retained. The hub links once to **methods/#reader-metrics**; detailed definitions belong on that dedicated page instead of disclosures on every article. Root personal landing-page traffic is outside this integration.

`GET /v1/metrics?articleId=<canonical-id>` and `POST /v1/metrics/events` use `credentials: "omit"` and never create an authentication device. POST accepts only `{type: "open" | "share" | "copy", visitorId, eventId, articleId}`. No URL query, email address, user agent or IP is supplied by this frontend. A random UUIDv4 is retained in first-party `localStorage` under `atr-reader-metrics-visitor:/AI_Tech_Review/`, separately from the API's HttpOnly authentication session. The backend hashes it for duplicate counting. Clearing site storage or using another browser can count as another visiting browser; these are not unique people.

The frontend starts one open event per visible, top-level page lifecycle and ignores hidden/frame/prerendered pages until activation. The backend deduplicates lifetime visiting browsers, daily visiting browsers and daily per-article opens (Korea time); Korean/English pages retain one article ID. Do Not Track (`1` or `yes`) and Global Privacy Control disable event recording, while public aggregate totals remain readable. If storage or secure randomness is unavailable, the frontend only reads totals instead of creating a fresh visitor on each page load.

Privacy exclusions remain honored without adding a current-browser participation paragraph to the reader interface, following the user’s preference for a compact page.

Native sharing counts only after `navigator.share()` resolves, and copying counts only after `clipboard.writeText()` succeeds. Cancellations, failed attempts and manual copy-address fallbacks do not count. A completed share can resolve after switching apps, so its completion is recorded even if the original page has become hidden. These actions cannot prove that another person received or opened the link. Each event uses a new UUID; metrics do not block the share/copy gesture, require notification permission or alter its feedback.

Counter requests have a five-second UI deadline, do not poll, and cannot display an older response over a newer action's counts. Subscription changes queue one fresh summary read behind any older pending read. Missing/malformed/error results leave em-dash values and a small accessible availability message rather than invented zeroes. An analytics failure never prevents reading, likes, sharing, subscription or push delivery.

Returning through the browser's back/forward cache (`pageshow.persisted`) refreshes public totals when the page is visible and top-level. It does not record another open or create an identifier. The coalesced read waits behind pending metrics writes, preventing an older pre-write snapshot from replacing their updated count.

## Immediate like feedback

A like or unlike immediately updates the heart and a known count, with `aria-busy`, a temporarily disabled button and **Saving… / 저장 중…** feedback. An initial unknown count stays an em dash until the server returns a valid total. Only one user mutation runs at a time. A successful response must contain `ok: true`, a boolean `liked` matching the requested state, and a nonnegative integer count; initial reads use the same strict type validation. The server's count replaces the provisional count, including other readers' activity.

A failure or twelve-second operation deadline restores the previous heart/count and offers an explicit retry for the same desired value. Late initial reads cannot replace newer user intent. A registration that finishes after that operation expires cannot issue a late like write. If a like write is already pending after an ambiguous timeout, a retry for the same state reuses it; a changed intent waits behind it. These protections preserve the backend's idempotent desired-state PUT contract without new API endpoints.

Anonymous device registration is single-flight across actions. The page retains only an in-memory boolean proving that a successful device registration or protected session endpoint has been observed, and reuses that session until a credentialed request returns 401. This avoids an unnecessary registration round trip for known sessions. It never stores authentication tokens in JavaScript or registers a device automatically when a page opens.

## Compact review discovery

The publisher's review hub preserves its hero, navigation, topic chips and review cards. It adds one compact sort selector (latest / opens / likes), one activity-period selector (all / 7 / 30 / 90 days / custom), and optional custom-date inputs. Periods refer to when opens and likes occurred, not when a review was published. Card labels remain all-time open/like totals. In a popularity sort, the topic selector is also ordered by the sum of that period's article activity, with All first; latest sorting restores its original order. Existing topic chips retain their positions.

`GET /v1/discovery` supplies one bounded batch for all active article counters. The hub uses omitted credentials, an eight-second deadline, a maximum of 500 validated rows, aborts outdated range requests and keeps only a short in-memory cache. It makes no per-card requests. Missing or malformed data stays an em dash; the latest sort and content-only search remain usable offline. Popularity options are unavailable until the selected period's data is ready, and errors offer an explicit retry. Korean and English variants share the article identity.

Search uses a publisher-escaped static `data-search` value containing title, subtitle, summary, topic and tags, excluding counter labels and dynamic numbers. Latest ordering uses the original publication date, then stable source order. The default page shows twelve cards, reveals twelve more per button press, resets to twelve after filter changes and announces the result count. Load-more focuses the first newly revealed article link without scrolling the page. Back-cache refresh preserves the expanded count and filters. No infinite auto-scroll or periodic polling is used.

The footer exposes the previously public business contact `hyun-jung.kim@lgdisplay.com` as a mail link. It does not send messages automatically.

## Article controls at the top and bottom

A compact view-count, like and share row follows the article's first `h1`, including formats whose title is in a separate hero. If a title is itself a grid/flex item, the row follows the containing layout rather than becoming another grid item. If no headline exists, the row begins inside the article. Bottom controls are kept inside the article when its parent is a grid/flex layout, preserving sidebar columns. The existing full bottom action row remains. Both like buttons, counts, pending indicators and feedback text share one state and a single mutation path. View-count fields update as a group from the same metrics response, without another request. Only the bottom feedback region is live to avoid duplicate screen-reader announcements; top feedback remains visible. Article text, covers and the existing icons are not replaced.
