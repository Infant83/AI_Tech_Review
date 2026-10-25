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

No mocked result, queued response, or browser regression test establishes real-device notification delivery. No commit, push, or deployment is performed by these frontend source files.
