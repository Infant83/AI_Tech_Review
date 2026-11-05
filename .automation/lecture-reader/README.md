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

Undo and redo store inverse deltas for each local action. Ordinary synchronization retains this history and applies an inverse only to the IDs that action changed, preserving unseen remote additions and erasures. Restorations receive fresh IDs and still obey the current role and stroke ownership. Notebook, account and role changes, document reopening and explicit backup replacement clear the history.

Operations are saved durably before transmission and sent in bounded batches. Ambiguous network failures retain the pending operations for idempotent retry. A reload compares the saved working baseline with the independently saved device notebook to recover edits made before a queue checkpoint. Drawing and PDF import/export operations defer synchronization; incoming changes preserve the current reading position. The initial explicit cloud opening can restore the account’s remote reading position. Positions and bookmarks belong to the signed-in member rather than all notebook editors collectively.

The interface distinguishes device saving, pending cloud work and confirmed synchronization. It describes periodic synchronization; it does not promise instantaneous classroom updates or WebSocket delivery.

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

## Product scope and UX audit

`ux-audit.json` records the November 5 browser acceptance, fixed defects and remaining product gaps. The personal-library entry opens its device library. A private cloud notebook first tries its cached original, then opens visible guidance for selecting the identical file; a mismatched file preserves the document and ink already displayed. Sign-out restores anonymous writing only for unbound device documents and keeps account-bound copies locked. Export/help stays visible in the phone header, original PDF export preserves source bytes, and shared-page erasure explicitly describes its effect on other members.

Importing a PDF is device-local and does not publish it. Signed-in cloud storage currently carries ink and progress rather than PDF bytes. Member file hosting, public post submission, whole-notebook deletion/reset/duplication, account recovery and additional passkey management are not implemented. Public lecture registration still follows the administrator GitHub workflow. The current polling collaboration is not a classroom session with presenter following or streamed pen gestures. Browser PDF bytes and mutable metadata also share a storage record; separating them and paginating the library are needed before claiming large personal-archive performance.

## Verification

```sh
node --test .automation/lecture-reader/*.test.mjs
python3 -m unittest discover -s tests -p test_document_archive_site.py
python3 -m unittest discover -s tests -p test_reader_engagement_publish.py
python3 -m unittest discover -s tests -p test_publish_public_site_privacy.py
```

The cloud-core cases cover two-writer additions, unseen remote strokes, offline stale writes, tombstones, immutable ID conflicts, operation limits, incremental feeds, same-PDF notebook/account switching, explicit unbound-note consent and operation filtering across the three sharing permissions. The race harness executes the actual cloud orchestration functions with delayed durable writes: a reader mutation revision prevents an exported snapshot from replacing a stroke completed during an await, including before its save event, and a stale notebook switch restores the previous working binding. Reader guards cover view-only drawing/import, contributor erasing/undo, legacy-ink protection and cross-notebook attribution. A role-downgrade case confirms no blocked ink is uploaded and its device backup is retained. Browser/API acceptance must additionally exercise passkey registration/sign-in, persistent retry, two editor contexts, invitation acceptance and access removal. Synthetic browser passkeys do not establish physical iPad Face ID or Apple Pencil acceptance.

For loopback QA only, a reader served on `localhost`, `127.0.0.1` or `[::1]` can select another loopback API origin using the `api` query parameter. Public pages always use `https://api.infant83.io`; credentials, user info, non-root paths and arbitrary origins are rejected as overrides.
