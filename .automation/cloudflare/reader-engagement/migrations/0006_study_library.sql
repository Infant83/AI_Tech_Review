-- Existing notebook and child records are copied without changing their IDs.
-- Rebuild children before the parent so ON DELETE CASCADE cannot erase saved data.
CREATE TABLE study_documents (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  fingerprint TEXT NOT NULL,
  object_key TEXT NOT NULL UNIQUE,
  byte_size INTEGER NOT NULL CHECK(byte_size>0 AND byte_size<=52428800),
  state TEXT NOT NULL CHECK(state IN ('uploading','ready')),
  created_at INTEGER NOT NULL,
  expires_at INTEGER,
  UNIQUE(owner_id,fingerprint)
);
CREATE INDEX study_documents_owner ON study_documents(owner_id,state);
CREATE TRIGGER study_document_quota BEFORE INSERT ON study_documents
BEGIN
  SELECT CASE WHEN (SELECT COALESCE(sum(byte_size),0) FROM study_documents WHERE owner_id=NEW.owner_id)+NEW.byte_size>524288000
    THEN RAISE(ABORT,'study_document_quota') END;
END;
CREATE TABLE study_notebooks_backup_0006 AS SELECT * FROM study_notebooks;
CREATE TABLE study_members_backup_0006 AS SELECT * FROM study_members;
CREATE TABLE study_strokes_backup_0006 AS SELECT * FROM study_strokes;
CREATE TABLE study_changes_backup_0006 AS SELECT * FROM study_changes;
CREATE TABLE study_invites_backup_0006 AS SELECT * FROM study_invites;
DROP TABLE study_invites;
DROP TABLE study_changes;
DROP TABLE study_strokes;
DROP TABLE study_members;
DROP TABLE study_notebooks;
CREATE TABLE study_notebooks (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  public_id TEXT,
  title TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  page_count INTEGER NOT NULL,
  revision INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  stroke_count INTEGER NOT NULL DEFAULT 0,
  ink_bytes INTEGER NOT NULL DEFAULT 0,
  document_id TEXT REFERENCES study_documents(id),
  document_bytes INTEGER NOT NULL DEFAULT 0,
  source_notebook_id TEXT,
  created_from TEXT NOT NULL DEFAULT 'original' CHECK(created_from IN ('original','copy','reset','version')),
  deleted_at INTEGER
);
INSERT INTO study_notebooks(id,owner_id,public_id,title,fingerprint,page_count,revision,created_at,updated_at,stroke_count,ink_bytes)
  SELECT id,owner_id,public_id,title,fingerprint,page_count,revision,created_at,updated_at,stroke_count,ink_bytes FROM study_notebooks_backup_0006;
CREATE INDEX study_notebooks_owner_fingerprint ON study_notebooks(owner_id,fingerprint,deleted_at);
CREATE TRIGGER study_notebook_quota BEFORE INSERT ON study_notebooks
BEGIN
  SELECT CASE WHEN NEW.deleted_at IS NULL AND (SELECT count(*) FROM study_notebooks WHERE owner_id=NEW.owner_id AND deleted_at IS NULL)>=100
    THEN RAISE(ABORT,'study_notebook_quota') END;
  SELECT CASE WHEN (SELECT count(*) FROM study_notebooks WHERE owner_id=NEW.owner_id)>=200
    THEN RAISE(ABORT,'study_retention_quota') END;
END;
CREATE TRIGGER study_notebook_restore_quota BEFORE UPDATE OF deleted_at ON study_notebooks
WHEN OLD.deleted_at IS NOT NULL AND NEW.deleted_at IS NULL
BEGIN
  SELECT CASE WHEN (SELECT count(*) FROM study_notebooks WHERE owner_id=NEW.owner_id AND deleted_at IS NULL)>=100
    THEN RAISE(ABORT,'study_notebook_quota') END;
END;
CREATE TABLE study_members (
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  account_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK(role IN ('owner','editor','contributor','viewer')),
  position INTEGER NOT NULL DEFAULT 1,
  bookmarks TEXT NOT NULL DEFAULT '[]',
  joined_at INTEGER NOT NULL,
  PRIMARY KEY(notebook_id,account_id)
);
INSERT INTO study_members SELECT * FROM study_members_backup_0006;
CREATE INDEX study_members_account ON study_members(account_id,notebook_id);
CREATE TABLE study_strokes (
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  page INTEGER NOT NULL,
  id TEXT NOT NULL,
  data TEXT,
  deleted INTEGER NOT NULL DEFAULT 0 CHECK(deleted IN (0,1)),
  updated_at INTEGER NOT NULL,
  author_id TEXT REFERENCES study_accounts(id),
  actor_id TEXT REFERENCES study_accounts(id),
  PRIMARY KEY(notebook_id,page,id)
);
INSERT INTO study_strokes SELECT * FROM study_strokes_backup_0006;
CREATE TABLE study_changes (
  revision INTEGER PRIMARY KEY AUTOINCREMENT,
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  page INTEGER NOT NULL,
  stroke_id TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('put','delete')),
  data TEXT,
  created_at INTEGER NOT NULL,
  author_id TEXT REFERENCES study_accounts(id)
);
INSERT INTO study_changes SELECT * FROM study_changes_backup_0006;
CREATE INDEX study_changes_notebook ON study_changes(notebook_id,revision);
CREATE TABLE study_invites (
  token_hash TEXT PRIMARY KEY,
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  created_by TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  expires_at INTEGER NOT NULL,
  used_by TEXT REFERENCES study_accounts(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'editor' CHECK(role IN ('editor','contributor','viewer'))
);
INSERT INTO study_invites SELECT * FROM study_invites_backup_0006;
CREATE INDEX study_invites_expiry ON study_invites(expires_at);
DROP TABLE study_notebooks_backup_0006;
DROP TABLE study_members_backup_0006;
DROP TABLE study_strokes_backup_0006;
DROP TABLE study_changes_backup_0006;
DROP TABLE study_invites_backup_0006;
CREATE TRIGGER study_stroke_insert_permission BEFORE INSERT ON study_strokes
BEGIN
  SELECT CASE WHEN NEW.actor_id IS NULL OR NOT EXISTS(
    SELECT 1 FROM study_members m JOIN study_notebooks n ON n.id=m.notebook_id WHERE m.notebook_id=NEW.notebook_id AND m.account_id=NEW.actor_id AND n.deleted_at IS NULL AND m.role IN ('owner','editor','contributor')
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
    SELECT 1 FROM study_members m JOIN study_notebooks n ON n.id=m.notebook_id WHERE m.notebook_id=NEW.notebook_id AND m.account_id=NEW.actor_id AND n.deleted_at IS NULL AND (
      m.role IN ('owner','editor') OR (m.role='contributor' AND OLD.author_id=NEW.actor_id)
    )
  ) THEN RAISE(ABORT,'study_permission_denied') END;
  SELECT CASE WHEN NEW.author_id IS NOT OLD.author_id THEN RAISE(ABORT,'study_author_invalid') END;
  SELECT CASE WHEN NOT (NEW.deleted=1 AND NEW.data IS NULL) AND (NEW.deleted IS NOT OLD.deleted OR NEW.data IS NOT OLD.data)
    THEN RAISE(ABORT,'study_immutable_stroke') END;
END;
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

ALTER TABLE study_sessions ADD COLUMN verified_at INTEGER NOT NULL DEFAULT 0;
ALTER TABLE study_credentials ADD COLUMN label TEXT NOT NULL DEFAULT 'Passkey';
ALTER TABLE study_credentials ADD COLUMN last_used_at INTEGER;
CREATE TABLE study_challenges_next (
  token_hash TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK(kind IN ('register','login','reauth','add')),
  challenge TEXT NOT NULL,
  origin TEXT NOT NULL,
  rp_id TEXT NOT NULL,
  account_id TEXT,
  display_name TEXT,
  user_handle TEXT,
  expires_at INTEGER NOT NULL
);
INSERT INTO study_challenges_next SELECT * FROM study_challenges;
DROP TABLE study_challenges;
ALTER TABLE study_challenges_next RENAME TO study_challenges;
CREATE INDEX study_challenges_expiry ON study_challenges(expires_at);
CREATE TRIGGER study_last_credential BEFORE DELETE ON study_credentials
WHEN EXISTS(SELECT 1 FROM study_accounts WHERE id=OLD.account_id)
BEGIN
  SELECT CASE WHEN (SELECT count(*) FROM study_credentials WHERE account_id=OLD.account_id)<=1
    THEN RAISE(ABORT,'last_credential_required') END;
END;
CREATE TABLE study_drafts (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  notebook_id TEXT REFERENCES study_notebooks(id),
  title TEXT NOT NULL,
  summary TEXT NOT NULL DEFAULT '',
  body TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','submitted','approved','rejected')),
  submission_id TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX study_drafts_owner ON study_drafts(owner_id,updated_at);
CREATE TABLE study_submissions (
  id TEXT PRIMARY KEY,
  draft_id TEXT NOT NULL REFERENCES study_drafts(id) ON DELETE CASCADE,
  owner_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  notebook_id TEXT REFERENCES study_notebooks(id),
  document_id TEXT REFERENCES study_documents(id),
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  body TEXT NOT NULL,
  fingerprint TEXT,
  status TEXT NOT NULL DEFAULT 'submitted' CHECK(status IN ('submitted','approved','rejected','withdrawn')),
  submitted_at INTEGER NOT NULL,
  reviewer_id TEXT REFERENCES study_accounts(id),
  reviewed_at INTEGER,
  review_note TEXT
);
CREATE INDEX study_submissions_queue ON study_submissions(status,submitted_at);
CREATE TRIGGER study_submission_guard BEFORE INSERT ON study_submissions
BEGIN
  SELECT CASE WHEN (SELECT status FROM study_drafts WHERE id=NEW.draft_id AND owner_id=NEW.owner_id)='submitted'
    THEN RAISE(ABORT,'draft_locked_for_review') END;
  SELECT CASE WHEN NEW.notebook_id IS NOT NULL AND NOT EXISTS(
    SELECT 1 FROM study_notebooks WHERE id=NEW.notebook_id AND owner_id=NEW.owner_id AND deleted_at IS NULL
  ) THEN RAISE(ABORT,'draft_source_unavailable') END;
END;
CREATE TABLE study_presentations (
  notebook_id TEXT PRIMARY KEY REFERENCES study_notebooks(id) ON DELETE CASCADE,
  id TEXT NOT NULL UNIQUE,
  presenter_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  page INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  expires_at INTEGER NOT NULL
);
