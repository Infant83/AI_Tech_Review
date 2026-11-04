# Lecture PDF study reader

`scripts/document_archive_site.py` publishes only the reviewed reader application files and the exact paths in `vendor/manifest.json` to `site/lectures/reader/`. The vendor manifest pins upstream bytes by SHA-256; its dependencies are also checked against npm tarball integrity when acquired. Tests, this README, private PDFs, browser databases and notebook backups are outside the publication allowlist.

All lecture cards enter the shared reader by registered archive ID. The Korean and English catalogs keep the original online notes, raw PDF and download links. The reader resolves IDs through `archive-manifest.json`; it accepts no arbitrary remote PDF URL. A separately selected local PDF remains on the device.

## Device storage and explicit cloud storage

The original PDF, local ink, bookmarks and reading position live in the origin’s IndexedDB through `storage.mjs`. Saving locally does not require signing in. Browser storage can be removed by the user, browser or operating system; portable notebook backups and annotated PDF exports remain available in the reader.

`cloud.mjs` uses the existing fixed HTTPS API host. Every authenticated request includes the browser’s secure cookie; JavaScript stores no bearer token. Passkey registration and sign-in use SimpleWebAuthn and the browser’s native authentication UI. Face ID, Touch ID, a security key or another available passkey method depends on the device. There is no Google OAuth or email-account flow.

Sign-in alone does not publish or upload local notes. **Sync this notebook** explicitly connects the selected notebook. Only the notebook title, PDF fingerprint, page count, optional public archive ID, ink, bookmarks and reading position are sent. PDF bytes are never sent to the study API. To open a shared notebook for a private PDF, each participant selects the identical PDF locally.

The independent `atr-study-cloud-sync` database retains pending operations and notebook working copies under both account ID and notebook ID. A separate working-view marker identifies which notebook is currently displayed in the fingerprint-indexed PDF reader. Switching notebooks or accounts first preserves the previous working copy, then restores the target before computing new edits. A durable transition marker protects an interrupted switch. Previously bound ink is never silently merged into another account or notebook; only unbound local ink can be merged through an explicit user action.

## Synchronization and sharing

Each stroke has an immutable ID. A first connection obtains a full snapshot; subsequent visible, active sessions check the incremental revision feed about every four seconds. Idle checks do not export, rewrite or retransmit the full notebook. Added strokes merge by ID. Deletes create permanent tombstones, so stale offline clients cannot resurrect erased strokes. The reader assigns new IDs when restoring erased ink through undo. An explicitly confirmed backup restore also creates fresh stroke IDs so earlier cloud tombstones cannot erase the restored copy; silent remote snapshots retain their existing IDs.

Operations are saved durably before transmission and sent in bounded batches. Ambiguous network failures retain the pending operations for idempotent retry. A reload compares the saved working baseline with the independently saved device notebook to recover edits made before a queue checkpoint. Drawing and PDF import/export operations defer synchronization; incoming changes preserve the current reading position. The initial explicit cloud opening can restore the account’s remote reading position. Positions and bookmarks belong to the signed-in member rather than all notebook editors collectively.

The interface distinguishes device saving, pending cloud work and confirmed synchronization. It describes periodic synchronization; it does not promise instantaneous classroom updates or WebSocket delivery.

Owners create time-limited private invitation links and can remove member access. The token stays in the URL fragment, which is not sent in the initial page request. A recipient signs in and explicitly accepts before gaining access. Acceptance removes the fragment. Notebook titles and display names are rendered as text. Personal notes never enter the public publication catalog, repository, analytics or service-worker notification state.

The reader page is excluded from the site’s reader-engagement injection, automatic refresh and standalone pull-to-refresh behavior. It creates no additional service worker. The existing push-only worker is retained.

## Verification

```sh
node --test .automation/lecture-reader/*.test.mjs
python3 -m unittest discover -s tests -p test_document_archive_site.py
python3 -m unittest discover -s tests -p test_reader_engagement_publish.py
python3 -m unittest discover -s tests -p test_publish_public_site_privacy.py
```

The cloud-core cases cover two-writer additions, unseen remote strokes, offline stale writes, tombstones, immutable ID conflicts, operation limits, incremental feeds, same-PDF notebook/account switching and explicit unbound-note consent. The race harness executes the actual cloud orchestration functions with delayed durable writes: a reader mutation revision prevents an exported snapshot from replacing a stroke completed during an await, including before its save event, and a stale notebook switch restores the previous working binding. Browser/API acceptance must additionally exercise passkey registration/sign-in, persistent retry, two editor contexts, invitation acceptance and access removal. Synthetic browser passkeys do not establish physical iPad Face ID or Apple Pencil acceptance.

For loopback QA only, a reader served on `localhost`, `127.0.0.1` or `[::1]` can select another loopback API origin using the `api` query parameter. Public pages always use `https://api.infant83.io`; credentials, user info, non-root paths and arbitrary origins are rejected as overrides.
