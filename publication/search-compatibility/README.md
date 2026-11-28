# Search v1 compatibility snapshot

The existing `assets/search-records.json` URL preserves these exact public bytes for cached v1 loaders. The source is deployed revision `0fa2a07b73ce4afee3e4f326768930286dd7eead`, 192 records, 384051 bytes, SHA-256 `3d8616f8fd622eeddf0a462ab1f4e06a74e497ab100b4f01c47832259271f5de`.

This pin provides decoding compatibility with the cutover dataset. It does not receive later publications. Reloading a current listing page selects the versioned v2 transport, which restores all current metadata before the unchanged search core runs. A v2 failure does not silently fall back to this older dataset.

ADOPT owns the snapshot and its source/hash checks. Preserve the old URL until a separately reviewed compatibility retirement establishes that cached loaders no longer need it. Age alone is not a retirement condition. This is public search metadata, not a scientific source, PDF edition, or private-data backup.

The payload guard counts each complete, mutually exclusive v1/v2 request closure under the same 100000-byte gzip limit. Both paths and the initial loader remain checked. The v1 snapshot is validated against this pin; v2 restored records are validated against current public catalogs.
