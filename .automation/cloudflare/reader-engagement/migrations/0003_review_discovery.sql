-- Durable daily aggregates contain public article totals, never visitor identities.
ALTER TABLE metrics_articles ADD COLUMN likes INTEGER NOT NULL DEFAULT 0;
ALTER TABLE metrics_state ADD COLUMN discovery_activity_since TEXT;
UPDATE metrics_state SET discovery_activity_since=MAX(date(since,'+9 hours'),date('now','+9 hours','-1 day')) WHERE id=1;
CREATE TABLE metrics_article_daily (
  day TEXT NOT NULL,
  article_id TEXT NOT NULL REFERENCES articles(id),
  opens INTEGER NOT NULL DEFAULT 0,
  likes INTEGER NOT NULL DEFAULT 0,
  shares INTEGER NOT NULL DEFAULT 0,
  copies INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(day,article_id)
);

-- Recover only daily events still present; do not distribute all-time totals into invented days.
INSERT INTO metrics_article_daily(day,article_id,opens)
  SELECT day,article_id,COUNT(*) FROM metrics_daily_opens GROUP BY day,article_id;
INSERT INTO metrics_article_daily(day,article_id,shares,copies)
  SELECT date((expires_at-604800000)/1000,'unixepoch','+9 hours'),article_id,
    SUM(CASE WHEN kind='share' THEN 1 ELSE 0 END),SUM(CASE WHEN kind='copy' THEN 1 ELSE 0 END)
  FROM metrics_actions GROUP BY 1,article_id
  ON CONFLICT(day,article_id) DO UPDATE SET shares=excluded.shares,copies=excluded.copies;
INSERT INTO metrics_articles(article_id,likes)
  SELECT article_id,COUNT(*) FROM likes GROUP BY article_id
  ON CONFLICT(article_id) DO UPDATE SET likes=excluded.likes;
INSERT INTO metrics_article_daily(day,article_id,likes)
  SELECT date(created_at/1000,'unixepoch','+9 hours'),article_id,COUNT(*) FROM likes GROUP BY 1,article_id
  ON CONFLICT(day,article_id) DO UPDATE SET likes=excluded.likes;

DROP TRIGGER metrics_new_article_open;
CREATE TRIGGER metrics_new_article_open AFTER INSERT ON metrics_daily_opens BEGIN
  UPDATE metrics_state SET opens=opens+1 WHERE id=1;
  INSERT INTO metrics_articles(article_id,opens) VALUES(NEW.article_id,1)
    ON CONFLICT(article_id) DO UPDATE SET opens=opens+1;
  INSERT INTO metrics_article_daily(day,article_id,opens) VALUES(NEW.day,NEW.article_id,1)
    ON CONFLICT(day,article_id) DO UPDATE SET opens=opens+1;
END;

DROP TRIGGER metrics_new_share_action;
CREATE TRIGGER metrics_new_share_action AFTER INSERT ON metrics_actions BEGIN
  UPDATE metrics_state SET
    shares=shares+CASE WHEN NEW.kind='share' THEN 1 ELSE 0 END,
    copies=copies+CASE WHEN NEW.kind='copy' THEN 1 ELSE 0 END WHERE id=1;
  INSERT INTO metrics_articles(article_id,shares,copies)
    VALUES(NEW.article_id,CASE WHEN NEW.kind='share' THEN 1 ELSE 0 END,CASE WHEN NEW.kind='copy' THEN 1 ELSE 0 END)
    ON CONFLICT(article_id) DO UPDATE SET shares=shares+excluded.shares,copies=copies+excluded.copies;
  INSERT INTO metrics_article_daily(day,article_id,shares,copies)
    VALUES(date((NEW.expires_at-604800000)/1000,'unixepoch','+9 hours'),NEW.article_id,
      CASE WHEN NEW.kind='share' THEN 1 ELSE 0 END,CASE WHEN NEW.kind='copy' THEN 1 ELSE 0 END)
    ON CONFLICT(day,article_id) DO UPDATE SET shares=shares+excluded.shares,copies=copies+excluded.copies;
END;

CREATE TRIGGER discovery_like_insert AFTER INSERT ON likes BEGIN
  INSERT INTO metrics_articles(article_id,likes) VALUES(NEW.article_id,1)
    ON CONFLICT(article_id) DO UPDATE SET likes=likes+1;
  INSERT INTO metrics_article_daily(day,article_id,likes)
    VALUES(date(NEW.created_at/1000,'unixepoch','+9 hours'),NEW.article_id,1)
    ON CONFLICT(day,article_id) DO UPDATE SET likes=likes+1;
END;
CREATE TRIGGER discovery_like_delete AFTER DELETE ON likes BEGIN
  UPDATE metrics_articles SET likes=MAX(likes-1,0) WHERE article_id=OLD.article_id;
  UPDATE metrics_article_daily SET likes=MAX(likes-1,0)
    WHERE day=date(OLD.created_at/1000,'unixepoch','+9 hours') AND article_id=OLD.article_id;
END;
CREATE TRIGGER discovery_like_update AFTER UPDATE OF article_id,created_at ON likes BEGIN
  UPDATE metrics_articles SET likes=MAX(likes-1,0) WHERE article_id=OLD.article_id;
  UPDATE metrics_article_daily SET likes=MAX(likes-1,0)
    WHERE day=date(OLD.created_at/1000,'unixepoch','+9 hours') AND article_id=OLD.article_id;
  INSERT INTO metrics_articles(article_id,likes) VALUES(NEW.article_id,1)
    ON CONFLICT(article_id) DO UPDATE SET likes=likes+1;
  INSERT INTO metrics_article_daily(day,article_id,likes)
    VALUES(date(NEW.created_at/1000,'unixepoch','+9 hours'),NEW.article_id,1)
    ON CONFLICT(day,article_id) DO UPDATE SET likes=likes+1;
END;
