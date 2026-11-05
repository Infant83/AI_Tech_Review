# Lecture PDF study reader

`scripts/document_archive_site.py` publishes only the reviewed reader application files and the exact paths in `vendor/manifest.json` to `site/lectures/reader/`. The vendor manifest pins upstream bytes by SHA-256; its dependencies are also checked against npm tarball integrity when acquired. Tests, this README, private PDFs, browser databases and notebook backups are outside the publication allowlist.

All lecture cards enter the shared reader by registered archive ID. The Korean and English catalogs keep the original online notes, raw PDF and download links. The reader resolves IDs through `archive-manifest.json`; it accepts no arbitrary remote PDF URL. A separately selected local PDF remains on the device until its owner explicitly chooses cloud storage for that original.

## Device storage and explicit cloud storage

The original PDF, local ink, bookmarks and reading position live in the origin’s IndexedDB through `storage.mjs`. Saving locally does not require signing in. Version 2 separates mutable metadata and pages from immutable PDF bytes, so listing the library or saving a stroke does not read/rewrite the original. The upgrade copies only v1 metadata and keeps legacy original records intact. Chrome and WebKit migration checks preserve original hashes, ink and progress, including concurrent original saves and trash/restore. Browser storage can still be removed by the user, browser or operating system; portable editable backups and annotated PDF exports remain available. After upgrading the browser database, a code rollback must keep the v2 storage adapter; loading the old v1 adapter causes a VersionError.

`cloud.mjs` uses the existing fixed HTTPS API host. Every authenticated request includes the browser’s secure cookie; JavaScript stores no bearer token. Passkey registration and sign-in use SimpleWebAuthn and the browser’s native authentication UI. Face ID, Touch ID, a security key or another available passkey method depends on the device. There is no Google OAuth or email-account flow.

Sign-in alone does not publish or upload local notes. **Sync this notebook** explicitly connects the selected notebook. This sends notebook metadata, ink, bookmarks and reading position. A separate owner action, **Store original PDF in cloud**, can upload the exact original through the authenticated study API when private R2 storage is configured. The server checks size, PDF header and SHA-256 before connecting an immutable object. Current members can then retrieve the original; every GET rechecks membership. If cloud file storage is unavailable or the owner has not selected it, another device must import the identical original. Default import and sign-in do not upload PDF bytes.

The independent `atr-study-cloud-sync` database retains pending operations and notebook working copies under both account ID and notebook ID. A separate working-view marker identifies which notebook is currently displayed in the fingerprint-indexed PDF reader. Switching notebooks or accounts first preserves the previous working copy, then restores the target before computing new edits. A durable transition marker protects an interrupted switch. Previously bound ink is never silently merged into another account or notebook; only unbound local ink can be merged through an explicit user action.

## Synchronization and sharing

Each stroke has an immutable ID. A first connection obtains a full snapshot; subsequent visible, active sessions check the incremental revision feed about every four seconds. Idle checks do not export, rewrite or retransmit the full notebook. Added strokes merge by ID. Deletes create permanent tombstones, so stale offline clients cannot resurrect erased strokes. The reader assigns new IDs when restoring erased ink through undo. An explicitly confirmed backup restore also creates fresh stroke IDs so earlier cloud tombstones cannot erase the restored copy; silent remote snapshots retain their existing IDs.

Undo and redo store inverse deltas for each local action. Ordinary synchronization retains this history and applies an inverse only to the IDs that action changed, preserving unseen remote additions and erasures. Restorations receive fresh IDs and still obey the current role and stroke ownership. Notebook, account and role changes, document reopening and explicit backup replacement clear the history.

Operations are saved durably before transmission and sent in bounded batches. Ambiguous network failures retain the pending operations for idempotent retry. A reload compares the saved working baseline with the independently saved device notebook to recover edits made before a queue checkpoint. Drawing and PDF import/export operations defer synchronization; incoming changes preserve the current reading position. The initial explicit cloud opening can restore the account’s remote reading position. Positions and bookmarks belong to the signed-in member rather than all notebook editors collectively.

The interface distinguishes device saving, pending cloud work and confirmed synchronization. Presentation sessions let an owner/editor publish the current page and members explicitly opt in to follow it. Following uses the existing periodic synchronization, expires after four hours, and preserves notebook editing permissions. It does not stream pen gestures, audio/video or WebSocket updates.

Owners create time-limited private invitation links and can remove member access. The token stays in the URL fragment, which is not sent in the initial page request. A recipient signs in and explicitly accepts before gaining access. Acceptance removes the fragment. Notebook titles and display names are rendered as text. Personal notes never enter the public publication catalog, repository, analytics or service-worker notification state.

Invitations are single-use and expire after 24 hours. A failed invitation preview keeps the member's notebook list available and offers an explicit dismissal; it never offers acceptance for an invalid preview. Closing the invitation removes only its fragment parameter and permits the normal personal notebook to resume.

### Sharing permissions

Every new invitation selects one explicit permission; the default is **View only**. An authenticated preview shows the permission before acceptance. An invitation does not change an existing member’s permission. The owner changes an existing member through **Save permission**, or removes access.

| Permission | Read/export | Add shared ink | Erase own additions | Erase existing/other ink | Manage members |
| --- | --- | --- | --- | --- | --- |
| View only (`viewer`) | Yes | No | No | No | No |
| Add own notes (`contributor`) | Yes | Yes | Yes | No | No |
| Co-edit (`editor`) | Yes | Yes | Yes | Yes | No |
| Owner (`owner`) | Yes | Yes | Yes | Yes | Yes |

Contributed ink is visible to every member. Server-authored ownership metadata determines which strokes a contributor may erase; existing unattributed strokes remain protected. The reader disables ink tools for viewers and limits contributor eraser/undo to their own strokes. Destructive whole-page clearing and backup replacement are unavailable to viewers and contributors. Reading position and bookmarks remain personal and editable in every role.

The server remains authoritative. Every incremental poll returns the current role even when no stroke changed. Before uploading queued offline edits, the client rechecks them against that role and stroke authorship. Disallowed changes are retained in a private device-only backup available from the sync panel, then the permitted shared view is restored. This avoids an unauthorized retry loop or silently discarding unsent ink. Edit permissions are bound to the account and notebook; a same-PDF switch cannot carry a stroke ownership grant across notebook boundaries.

Reopening a cached notebook reconciles the latest snapshot and durable pending ink before advancing its remote cursor. Explicit cloud notebook opening restores that member's remote progress; automatic resume retains device progress so offline reading is not silently replaced. Historical delta events for currently erased strokes return deletion markers without old coordinates. This redacts API responses; it does not physically purge the stored change log or remove earlier exports.

The reader page is excluded from the site’s reader-engagement injection, automatic refresh and standalone pull-to-refresh behavior. It creates no additional service worker. The existing push-only worker is retained.

## Personal learning space

The shared entry combines the signed-in account, cloud notebooks, device metadata, published lectures and separate device/cloud trash. The current notebook title, owner, sharing permission and original-file availability are visible. Paginated cloud lists are read through a bounded cursor loop; PDF bytes are not loaded for library listings.

Every reading role can create a private copy or a fresh notebook with a new ID. A copied notebook gets fresh stroke IDs and no inherited members; another owner's private file permission is not inherited. A fresh notebook keeps the source PDF and prior notebook/ink. The active source is flushed and synchronized before creating either kind. Device trash only hides its metadata; cloud trash stops member access while preserving data for owner restoration. There is no permanent-delete button or general version-history UI. Limits are 100 active owned notebooks and 200 retained owned notebooks including trash, 25,000 stroke IDs and 12 MB active ink JSON per notebook, 50 MiB per original and 500 MiB uploaded originals per account. Trash does not reclaim those retained originals automatically.

Account settings manage additional passkeys. Adding/removing a key requires a fresh assertion by an existing key; registration remains attached to the current account and the last key cannot be removed. Platform passkey availability still governs sign-in and there is no email/password fallback or recovery after every registered key is lost.

Members can save private text drafts and optionally attach an owned original for publication review. Submission records an immutable snapshot after explicit rights confirmation; submitted drafts are locked until withdrawal. Only configured reviewer account IDs can access the editorial queue or approve/reject. Approval does not publish to the static website. An editor still prepares and validates the public GitHub publication, preserving the site's editorial policy. Personal ink is not silently attached to submissions.

Private R2 file hosting is capability-gated. The default Worker config omits the R2 binding until the operator reconnects and provisions the private bucket. `wrangler.r2.example.jsonc` documents the intended binding. The same API/UI was tested with a local R2 binding: private upload, a recipient without the original, independent viewer copies, reset, trash/restore, passkey addition, drafts and presenter following. This local acceptance does not claim a live R2 connection, a paid-plan change, maximum-file CPU acceptance or physical iPad/Face ID validation.

`ux-audit.json` preserves the earlier audit; `learning-space-validation.json` records this follow-up implementation and rollout. Classroom scale, presence/cursors, streamed ink and storage sharding remain separate work.

## Verification

```sh
node --test .automation/lecture-reader/*.test.mjs
python3 -m unittest discover -s tests -p test_document_archive_site.py
python3 -m unittest discover -s tests -p test_reader_engagement_publish.py
python3 -m unittest discover -s tests -p test_publish_public_site_privacy.py
```

The cloud-core cases cover two-writer additions, unseen remote strokes, offline stale writes, tombstones, immutable ID conflicts, operation limits, incremental feeds, same-PDF notebook/account switching, explicit unbound-note consent and operation filtering across the three sharing permissions. The race harness executes the actual cloud orchestration functions with delayed durable writes: a reader mutation revision prevents an exported snapshot from replacing a stroke completed during an await, including before its save event, and a stale notebook switch restores the previous working binding. Reader guards cover view-only drawing/import, contributor erasing/undo, legacy-ink protection and cross-notebook attribution. A role-downgrade case confirms no blocked ink is uploaded and its device backup is retained. Browser/API acceptance must additionally exercise passkey registration/sign-in, persistent retry, two editor contexts, invitation acceptance and access removal. Synthetic browser passkeys do not establish physical iPad Face ID or Apple Pencil acceptance.

For loopback QA only, a reader served on `localhost`, `127.0.0.1` or `[::1]` can select another loopback API origin using the `api` query parameter. Public pages always use `https://api.infant83.io`; credentials, user info, non-root paths and arbitrary origins are rejected as overrides.
