# Reader engagement validation — 2026-10-25

## Implemented behavior

GitHub Pages continues to serve the existing HTML and artwork. A separate Cloudflare Worker, D1 database and Queue provide anonymous device sessions, article likes, review/lecture notification preferences, unsubscribe and a rate-limited test alert. Stable article IDs and nullable user IDs leave room for later account linking and editorial publication events.

The official GitHub Pages artifact is deployed before its immutable catalog is synchronized. Every main push schedules a run, including documentation changes, so a superseding commit cannot suppress deployment without a replacement run. The first synchronization establishes a silent baseline. Editing an existing article ID does not create a new-article notification.

## Completed checks

- Backend: 16 tests passed using Miniflare D1 and Workers APIs. Independent `http_ece` decryption and VAPID signature verification passed. Scenarios cover ownership, HttpOnly cookies, CSRF/Origin, SSRF rejection, session expiry, rate limits, baseline/edits/new IDs/replays, 500-article batches, paginated fanout, duplicate/concurrent delivery, unsubscribe, endpoint changes, expired endpoints and retry recovery.
- Frontend: 36 Node VM tests passed. Eight retained browser regression cases were skipped in this run; they are not counted as execution evidence. Checks include rapid likes, late responses, safe retries, partial unsubscribe failure, denied/unsupported notifications, safe configuration, scoped links, invalid push payloads, bounded permission/Push API waits and reuse of pending browser requests.
- Badge/history service worker: 20 tests passed using real fake-indexeddb transactions and mocked native Badging APIs. Cases cover restart persistence, two overlapping worker globals, duplicate delivery, foreground/background clients, source validation, bounded storage/native failures and late badge reconciliation.
- Publisher: 22 tests passed; existing privacy checks: 6 passed.
- Current output: 90 HTML documents are byte-identical after removing the two added integration blocks. Existing icons and site stylesheet are byte-identical. Reader JS/CSS URLs carry content hashes to avoid stale release assets. The full site validator reported zero errors; the publication guard accepted 1,523 public files and 50 articles.
- Actual local browser and local Worker/D1: 320px, 390px, 736px landscape and 1280px layouts; 44px controls; Korean and English article controls; real like/unlike persistence; API-unavailable recovery; empty topic validation; dialog focus loop/Escape; reading position and opener focus restoration. An inherited article heading border was isolated from the new dialog during visual QA.
- Production API: valid HTTPS and configuration, exact-origin credentialed CORS, private/no-store responses, nosniff, rejection of foreign/null/development origins, missing Origin on mutation, unauthenticated publisher access and unauthenticated subscription access.
- Live GitHub workflow `40159327572`: build, Pages deploy and notification sync succeeded. Initial synchronization registered a 50-article baseline without creating new-article events. The live browser saved, reloaded and removed a like through the production API. The actual embedded browser also demonstrated the 30-second permission-wait recovery.
- Physical iPhone acceptance: on 2026-10-25 the tester confirmed that the test notification arrived and tapping it opened AI Tech Review normally. D1 independently records a successful test delivery on its first attempt, provider HTTP 201 and no delivery error. The event was created at 04:24:01 UTC and marked sent at 04:24:04 UTC (13:24:01–13:24:04 KST). This three-second interval measures server processing through provider acceptance; it is not a measurement of device display latency.
- Cloudflare dashboard: Workers Free is the current plan; recorded invocation errors and CPU-limit failures were zero during initial verification and after the physical iPhone test. These are aggregate metrics rather than the CPU measurement of an isolated push invocation.
- Backend and frontend-test dependency audits: zero reported vulnerabilities at implementation time.

## Security review and remaining acceptance

Device secrets are generated randomly, stored only in an HttpOnly API-host cookie and hashed in D1. Publisher and VAPID private secrets remain server-side. Mutation routes require the expected Origin. Subscription endpoints are restricted to supported push providers, redirects are refused, requests and catalog fields are bounded, database operations are parameterized, and UI text is rendered without HTML interpolation. Publication input is compared against a fixed HTTPS public feed under a writer lock.

Delivery records and leases recover interrupted work. A push-provider acceptance followed by a process interruption can still cause a retry; stable notification tags reduce repeated visible alerts. Anonymous likes identify a browser/device rather than a verified person. Clearing browser storage can create a new identity.

The physical iPhone test establishes test-alert receipt and opening the review hub. A new-article notification opening its exact article and an entire new GitHub publication reaching that device have not yet been observed physically; automated integration tests cover the corresponding publication and deep-link logic. Other devices and Android still need separate device acceptance. Queue acceptance alone does not establish delivery. Production CPU for the particular encrypted push invocation has not been isolated from aggregate metrics. The site and API do not provide a server-side administrator editor or user accounts yet.

## Installation help, numeric badges and recent alerts

The alert dialog now contains device-specific help for iPhone/iPad, Mac Chrome and Mac Safari. Installation is required for iPhone web alerts and optional for Mac browser alerts. Installed app sessions are not asked to reinstall. An optional install button appears only after a real browser install-offer event, and install/notification permission prompts still require an explicit reader action. Guide choice, disclosure state, keyboard focus and reading position survive dialog updates. The close control remains reachable while scrolling long help or history.

A supported installed app can show a device-local count of newly received article alerts. Opening and focusing the app/site resets that number; the recent list remains available in the dialog. The list shows public titles, verified in-scope article links and received times, initially five entries and progressively up to twenty. Test alerts and repeated delivery of the same article do not enter the list or increase the count. These are notification acknowledgements rather than per-article read receipts. Android numeric badges are not implemented through the Badging API; native OS badge permissions and appearance remain platform-controlled.

IndexedDB stores only a count, up to 2,000 public article IDs for deduplication, and up to twenty public article metadata records. No subscription endpoints, device credentials or authentication tokens are stored there. Badge/storage failure does not block visible notifications or notification-click navigation.

Actual Chrome QA used an explicit localhost-only fixture outside the public site: three public article records were seeded through visible QA controls, then the normal UI cleared the count to zero while retaining the three titles and links. Clicking a recent title opened the matching article. A literal HTML-like title remained text and a foreign URL was discarded. Twenty records expanded in five-entry steps; 320px/390px portrait and 736px landscape layouts remained inside the viewport with usable controls and scrolling. These fixture records and screenshots are not publication output and were not sent as production notifications.

Positive numeric badge appearance on a physical Home Screen/Dock icon still needs confirmation after a genuine new article alert. Unit tests exercise native count calls, but do not establish OS display. Earlier physical iPhone test-alert receipt and tap-to-open confirmation remain recorded above.

See the backend README for deployment, key backup, quotas, recovery and future hosting migration. Keep the existing origin, service-worker scope and VAPID key when migrating hosting to preserve existing subscriptions where the browser permits it.
