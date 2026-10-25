-- Public aggregates begin at this migration. Existing visits are not inferred.
CREATE TABLE metrics_state (
  id INTEGER PRIMARY KEY CHECK(id = 1),
  since TEXT NOT NULL,
  visitors INTEGER NOT NULL DEFAULT 0,
  opens INTEGER NOT NULL DEFAULT 0,
  shares INTEGER NOT NULL DEFAULT 0,
  copies INTEGER NOT NULL DEFAULT 0,
  subscription_registrations INTEGER NOT NULL DEFAULT 0,
  article_notifications_sent INTEGER NOT NULL DEFAULT 0
);
INSERT INTO metrics_state(id,since) VALUES(1,strftime('%Y-%m-%dT%H:%M:%fZ','now'));

-- Seed real historical sends; retain an aggregate without rescanning deliveries per page.
ALTER TABLE deliveries ADD COLUMN metrics_counted INTEGER NOT NULL DEFAULT 0;
UPDATE deliveries SET metrics_counted=1 WHERE status='sent'
  AND event_id IN (SELECT id FROM publication_events WHERE kind='article');
UPDATE metrics_state SET article_notifications_sent=(SELECT COUNT(*) FROM deliveries WHERE metrics_counted=1) WHERE id=1;
CREATE TRIGGER metrics_accepted_article_notification AFTER UPDATE OF status ON deliveries
  WHEN NEW.status='sent' AND NEW.metrics_counted=0
    AND EXISTS (SELECT 1 FROM publication_events WHERE id=NEW.event_id AND kind='article')
BEGIN
  UPDATE deliveries SET metrics_counted=1 WHERE event_id=NEW.event_id AND device_id=NEW.device_id;
  UPDATE metrics_state SET article_notifications_sent=article_notifications_sent+1 WHERE id=1;
END;
CREATE TRIGGER metrics_inserted_article_notification AFTER INSERT ON deliveries
  WHEN NEW.status='sent' AND NEW.metrics_counted=0
    AND EXISTS (SELECT 1 FROM publication_events WHERE id=NEW.event_id AND kind='article')
BEGIN
  UPDATE deliveries SET metrics_counted=1 WHERE event_id=NEW.event_id AND device_id=NEW.device_id;
  UPDATE metrics_state SET article_notifications_sent=article_notifications_sent+1 WHERE id=1;
END;

-- Salted, domain-separated hashes only; no raw browser identifier or IP.
CREATE TABLE metrics_visitors (
  visitor_hash TEXT PRIMARY KEY
);
CREATE TRIGGER metrics_new_visitor AFTER INSERT ON metrics_visitors BEGIN
  UPDATE metrics_state SET visitors=visitors+1 WHERE id=1;
END;

CREATE TABLE metrics_daily_counts (
  day TEXT PRIMARY KEY,
  visitors INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE metrics_daily_visitors (
  day TEXT NOT NULL,
  visitor_hash TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  PRIMARY KEY(day,visitor_hash)
);
CREATE INDEX metrics_daily_visitors_expiry ON metrics_daily_visitors(expires_at);
CREATE TRIGGER metrics_new_daily_visitor AFTER INSERT ON metrics_daily_visitors BEGIN
  INSERT INTO metrics_daily_counts(day,visitors) VALUES(NEW.day,1)
    ON CONFLICT(day) DO UPDATE SET visitors=visitors+1;
END;

CREATE TABLE metrics_articles (
  article_id TEXT PRIMARY KEY REFERENCES articles(id),
  opens INTEGER NOT NULL DEFAULT 0,
  shares INTEGER NOT NULL DEFAULT 0,
  copies INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE metrics_daily_opens (
  day TEXT NOT NULL,
  visitor_hash TEXT NOT NULL,
  article_id TEXT NOT NULL REFERENCES articles(id),
  expires_at INTEGER NOT NULL,
  PRIMARY KEY(day,visitor_hash,article_id)
);
CREATE INDEX metrics_daily_opens_expiry ON metrics_daily_opens(expires_at);
CREATE TRIGGER metrics_new_article_open AFTER INSERT ON metrics_daily_opens BEGIN
  UPDATE metrics_state SET opens=opens+1 WHERE id=1;
  INSERT INTO metrics_articles(article_id,opens) VALUES(NEW.article_id,1)
    ON CONFLICT(article_id) DO UPDATE SET opens=opens+1;
END;

-- Short-lived idempotency ledger; no page URL, visitor hash, or raw event ID.
CREATE TABLE metrics_actions (
  event_hash TEXT PRIMARY KEY,
  article_id TEXT NOT NULL REFERENCES articles(id),
  kind TEXT NOT NULL CHECK(kind IN ('share','copy')),
  expires_at INTEGER NOT NULL
);
CREATE INDEX metrics_actions_expiry ON metrics_actions(expires_at);
CREATE TRIGGER metrics_new_share_action AFTER INSERT ON metrics_actions BEGIN
  UPDATE metrics_state SET
    shares=shares+CASE WHEN NEW.kind='share' THEN 1 ELSE 0 END,
    copies=copies+CASE WHEN NEW.kind='copy' THEN 1 ELSE 0 END
    WHERE id=1;
  INSERT INTO metrics_articles(article_id,shares,copies)
    VALUES(NEW.article_id,CASE WHEN NEW.kind='share' THEN 1 ELSE 0 END,CASE WHEN NEW.kind='copy' THEN 1 ELSE 0 END)
    ON CONFLICT(article_id) DO UPDATE SET
      shares=shares+excluded.shares,copies=copies+excluded.copies;
END;
