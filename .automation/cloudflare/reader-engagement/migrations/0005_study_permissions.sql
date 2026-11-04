-- Preserve existing owner/editor grants while introducing separate read/add grants.
CREATE TABLE study_members_next (
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  account_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK(role IN ('owner','editor','contributor','viewer')),
  position INTEGER NOT NULL DEFAULT 1,
  bookmarks TEXT NOT NULL DEFAULT '[]',
  joined_at INTEGER NOT NULL,
  PRIMARY KEY(notebook_id,account_id)
);
INSERT INTO study_members_next SELECT * FROM study_members;
DROP TABLE study_members;
ALTER TABLE study_members_next RENAME TO study_members;
CREATE INDEX study_members_account ON study_members(account_id,notebook_id);

-- Existing invitations retain their originally promised editing grant.
ALTER TABLE study_invites ADD COLUMN role TEXT NOT NULL DEFAULT 'editor' CHECK(role IN ('editor','contributor','viewer'));
ALTER TABLE study_strokes ADD COLUMN author_id TEXT REFERENCES study_accounts(id);
ALTER TABLE study_strokes ADD COLUMN actor_id TEXT REFERENCES study_accounts(id);
ALTER TABLE study_changes ADD COLUMN author_id TEXT REFERENCES study_accounts(id);
ALTER TABLE study_notebooks ADD COLUMN stroke_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE study_notebooks ADD COLUMN ink_bytes INTEGER NOT NULL DEFAULT 0;
UPDATE study_notebooks SET
  stroke_count=(SELECT count(*) FROM study_strokes WHERE notebook_id=study_notebooks.id),
  ink_bytes=(SELECT COALESCE(sum(length(data)),0) FROM study_strokes WHERE notebook_id=study_notebooks.id);

-- Actor/author fields are filled by the server, never accepted from a client.
-- Guards execute inside the same D1 batch as all ink changes. A forbidden later
-- operation rolls the entire batch back, including earlier valid operations.
CREATE TRIGGER study_stroke_insert_permission BEFORE INSERT ON study_strokes
BEGIN
  SELECT CASE WHEN NEW.actor_id IS NULL OR NOT EXISTS(
    SELECT 1 FROM study_members WHERE notebook_id=NEW.notebook_id AND account_id=NEW.actor_id AND role IN ('owner','editor','contributor')
  ) THEN RAISE(ABORT,'study_permission_denied') END;
  SELECT CASE WHEN NEW.deleted=0 AND NEW.author_id IS NOT NEW.actor_id THEN RAISE(ABORT,'study_author_invalid') END;
  SELECT CASE WHEN EXISTS(
    SELECT 1 FROM study_members WHERE notebook_id=NEW.notebook_id AND account_id=NEW.actor_id AND role='contributor'
  ) AND (
    (NEW.deleted=1 AND NOT EXISTS(
      SELECT 1 FROM study_strokes WHERE notebook_id=NEW.notebook_id AND page=NEW.page AND id=NEW.id AND author_id=NEW.actor_id
    )) OR
    (NEW.deleted=0 AND EXISTS(
      SELECT 1 FROM study_strokes WHERE notebook_id=NEW.notebook_id AND page=NEW.page AND id=NEW.id AND author_id IS NOT NEW.actor_id
    ))
  ) THEN RAISE(ABORT,'study_permission_denied') END;
END;
CREATE TRIGGER study_stroke_update_permission BEFORE UPDATE OF data,deleted,author_id,actor_id ON study_strokes
BEGIN
  SELECT CASE WHEN NEW.actor_id IS NULL OR NOT EXISTS(
    SELECT 1 FROM study_members WHERE notebook_id=NEW.notebook_id AND account_id=NEW.actor_id AND (
      role IN ('owner','editor') OR (role='contributor' AND OLD.author_id=NEW.actor_id)
    )
  ) THEN RAISE(ABORT,'study_permission_denied') END;
  SELECT CASE WHEN NEW.author_id IS NOT OLD.author_id THEN RAISE(ABORT,'study_author_invalid') END;
  SELECT CASE WHEN NOT (NEW.deleted=1 AND NEW.data IS NULL) AND (NEW.deleted IS NOT OLD.deleted OR NEW.data IS NOT OLD.data)
    THEN RAISE(ABORT,'study_immutable_stroke') END;
END;
DROP TRIGGER study_stroke_added;
DROP TRIGGER study_stroke_erased;
CREATE TRIGGER study_stroke_added AFTER INSERT ON study_strokes
BEGIN
  INSERT INTO study_changes(notebook_id,page,stroke_id,kind,data,created_at,author_id)
    VALUES(NEW.notebook_id,NEW.page,NEW.id,CASE NEW.deleted WHEN 1 THEN 'delete' ELSE 'put' END,NEW.data,NEW.updated_at,NEW.author_id);
  UPDATE study_notebooks SET revision=(SELECT MAX(revision) FROM study_changes WHERE notebook_id=NEW.notebook_id),updated_at=NEW.updated_at,
    stroke_count=stroke_count+1,ink_bytes=ink_bytes+COALESCE(length(NEW.data),0) WHERE id=NEW.notebook_id;
END;
CREATE TRIGGER study_stroke_erased AFTER UPDATE OF deleted ON study_strokes WHEN OLD.deleted=0 AND NEW.deleted=1
BEGIN
  INSERT INTO study_changes(notebook_id,page,stroke_id,kind,data,created_at,author_id)
    VALUES(NEW.notebook_id,NEW.page,NEW.id,'delete',NULL,NEW.updated_at,NEW.author_id);
  UPDATE study_notebooks SET revision=(SELECT MAX(revision) FROM study_changes WHERE notebook_id=NEW.notebook_id),updated_at=NEW.updated_at,
    ink_bytes=ink_bytes-COALESCE(length(OLD.data),0) WHERE id=NEW.notebook_id;
END;
