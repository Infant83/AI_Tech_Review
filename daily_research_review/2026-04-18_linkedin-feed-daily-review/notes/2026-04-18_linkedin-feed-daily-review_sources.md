# 2026-04-18 LinkedIn Feed Sources

## Intake Context
- LinkedIn feed daily recap was proposed on `2026-04-18` KST as an additional intake lane for `daily_research_review/`.
- The purpose of this lane is to summarize the dominant themes, repeated claims, notable authors, and possible deep-research candidates emerging from the user's LinkedIn home feed.
- The initial trial scope is:
  - posts visible on `2026-04-18` KST
  - recent posts from `2026-04-17` KST when still surfaced in the feed

## Why This Intake Is Useful
- It captures `network-level signal` rather than only publisher-curated digests.
- It can highlight what practitioners, operators, founders, recruiters, and vendors are amplifying at the same time.
- It creates a practical bridge between:
  - weak social signal detection
  - candidate-topic promotion into deeper research
  - recurring market narrative tracking over time

## Target Normalization Shape
- For each notable post, capture:
  - author
  - role / company when visible
  - post timestamp
  - core claim or message
  - evidence quality
  - why it matters
  - follow-up / verification need
- Aggregate across posts into:
  - repeated topics
  - sentiment / framing patterns
  - possible blind spots
  - deep-research promotion candidates

## Access Status
- Direct navigation to `https://www.linkedin.com/feed/` in a fresh Playwright session redirected to the LinkedIn login page.
- Reusing the local Chrome profile is the intended access path because it may already hold the user's authenticated LinkedIn session.
- As of this note, the local Chrome profile is locked by running Chrome processes, so automated feed access is blocked until Chrome is closed.
- `Chrome Local State` indicates that the last active profile is `Default`.
- A temp-copy retry with `Profile 1` was possible, but that profile had no visible LinkedIn cookie state and still landed on the LinkedIn login page.
- A deeper retry showed that neither `Chrome Default` nor `Chrome Profile 1` currently contains visible `linkedin.com` cookies.
- A later retry after the user closed Chrome windows still showed remaining Chrome background processes, and `Chrome Default` continued to show `0` visible `linkedin.com` cookies.
- `Microsoft Edge Default` is active on this machine and is now the more credible candidate for an existing LinkedIn login session.
- However, Edge is also running, so its profile cannot be attached directly by Playwright and its live cookie DB cannot be copied while the browser remains open.
- The only credible remaining automation paths are:
  - reuse `Edge Default` after Edge is closed
  - reuse `Chrome Default` after a fresh LinkedIn login is performed there
  - or have the user explicitly log into LinkedIn in an automation-compatible browser session

## Workspace Package
- Package path: `daily_research_review/2026-04-18_linkedin-feed-daily-review/`
- Planned outputs:
  - `notes/2026-04-18_linkedin-feed-daily-review_sources.md`
  - `notes/2026-04-18_linkedin-feed-daily-review_runlog.md`
  - `reports/2026-04-18_linkedin-feed-daily-review_overview.md`
  - `reports/2026-04-18_linkedin-feed-daily-review_overview.html`
  - optional root memo if this becomes a recurring conversation-memory lane

## Captured Feed Artifacts
- Main feed screenshots captured from the logged-in Chrome window:
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_01.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_02.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_03.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_07.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_09.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_10.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_11.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_12.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_13.png`
  - `artifacts/2026-04-18_linkedin-feed-daily-review_feed_capture_14.png`

## Observation Boundary
- This was a `visible-feed sampling pass`, not a full export of every post published on `2026-04-18` or `2026-04-17`.
- The note is based on:
  - items surfaced by LinkedIn's current home-feed ranking
  - a limited manual scroll sample
  - the right-rail `LinkedIn 뉴스` headlines visible during capture
