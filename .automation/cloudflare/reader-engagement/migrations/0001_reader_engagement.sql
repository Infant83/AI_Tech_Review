PRAGMA foreign_keys = ON;

CREATE TABLE devices (
  id TEXT PRIMARY KEY,
  token_hash TEXT NOT NULL UNIQUE,
  user_id TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE rate_limits (
  key TEXT PRIMARY KEY,
  hits INTEGER NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE INDEX rate_limits_expiry ON rate_limits(expires_at);

CREATE TABLE articles (
  id TEXT PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  published_at TEXT NOT NULL,
  topic TEXT NOT NULL CHECK(topic IN ('review', 'lecture')),
  active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE likes (
  article_id TEXT NOT NULL REFERENCES articles(id),
  device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  user_id TEXT,
  created_at INTEGER NOT NULL,
  PRIMARY KEY(article_id, device_id)
);

CREATE TABLE subscriptions (
  device_id TEXT PRIMARY KEY REFERENCES devices(id) ON DELETE CASCADE,
  endpoint_hash TEXT NOT NULL UNIQUE,
  endpoint TEXT NOT NULL,
  p256dh TEXT NOT NULL,
  auth TEXT NOT NULL,
  expiration_time INTEGER,
  review_enabled INTEGER NOT NULL CHECK(review_enabled IN (0, 1)),
  lecture_enabled INTEGER NOT NULL CHECK(lecture_enabled IN (0, 1)),
  version TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX subscriptions_review ON subscriptions(review_enabled, device_id);
CREATE INDEX subscriptions_lecture ON subscriptions(lecture_enabled, device_id);

CREATE TABLE publication_state (
  id INTEGER PRIMARY KEY CHECK(id = 1),
  revision TEXT NOT NULL,
  initialized_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE TABLE sync_revisions (
  revision TEXT PRIMARY KEY,
  feed_hash TEXT NOT NULL,
  applied_at INTEGER NOT NULL
);
CREATE TABLE operation_locks (
  name TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);

CREATE TABLE publication_events (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK(kind IN ('article', 'test')),
  article_id TEXT REFERENCES articles(id),
  revision TEXT,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  path TEXT NOT NULL,
  topic TEXT CHECK(topic IN ('review', 'lecture')),
  created_at INTEGER NOT NULL,
  fanout_cursor TEXT NOT NULL DEFAULT '',
  fanout_completed INTEGER NOT NULL DEFAULT 0,
  lease_owner TEXT,
  lease_until INTEGER NOT NULL DEFAULT 0,
  UNIQUE(kind, article_id)
);

CREATE TABLE deliveries (
  event_id TEXT NOT NULL REFERENCES publication_events(id) ON DELETE CASCADE,
  device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  subscription_version TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK(status IN ('pending', 'retry', 'sending', 'sent', 'dead', 'suppressed', 'failed')),
  attempts INTEGER NOT NULL DEFAULT 0,
  lease_owner TEXT,
  lease_until INTEGER NOT NULL DEFAULT 0,
  retry_at INTEGER NOT NULL DEFAULT 0,
  last_http_status INTEGER,
  last_error TEXT,
  created_at INTEGER NOT NULL,
  sent_at INTEGER,
  PRIMARY KEY(event_id, device_id)
);
CREATE INDEX deliveries_outbox ON deliveries(status, retry_at, lease_until);
