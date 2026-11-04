CREATE TABLE study_accounts (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE study_credentials (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  public_key TEXT NOT NULL,
  counter INTEGER NOT NULL DEFAULT 0,
  user_handle TEXT NOT NULL,
  transports TEXT NOT NULL DEFAULT '[]',
  created_at INTEGER NOT NULL
);
CREATE INDEX study_credentials_account ON study_credentials(account_id);
CREATE TABLE study_sessions (
  token_hash TEXT PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  expires_at INTEGER NOT NULL
);
CREATE INDEX study_sessions_expiry ON study_sessions(expires_at);
CREATE TABLE study_challenges (
  token_hash TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK(kind IN ('register','login')),
  challenge TEXT NOT NULL,
  origin TEXT NOT NULL,
  rp_id TEXT NOT NULL,
  account_id TEXT,
  display_name TEXT,
  user_handle TEXT,
  expires_at INTEGER NOT NULL
);
CREATE INDEX study_challenges_expiry ON study_challenges(expires_at);
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
  UNIQUE(owner_id,fingerprint)
);
CREATE TABLE study_members (
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  account_id TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK(role IN ('owner','editor')),
  position INTEGER NOT NULL DEFAULT 1,
  bookmarks TEXT NOT NULL DEFAULT '[]',
  joined_at INTEGER NOT NULL,
  PRIMARY KEY(notebook_id,account_id)
);
CREATE INDEX study_members_account ON study_members(account_id,notebook_id);
CREATE TABLE study_strokes (
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  page INTEGER NOT NULL,
  id TEXT NOT NULL,
  data TEXT,
  deleted INTEGER NOT NULL DEFAULT 0 CHECK(deleted IN (0,1)),
  updated_at INTEGER NOT NULL,
  PRIMARY KEY(notebook_id,page,id)
);
CREATE TABLE study_changes (
  revision INTEGER PRIMARY KEY AUTOINCREMENT,
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  page INTEGER NOT NULL,
  stroke_id TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('put','delete')),
  data TEXT,
  created_at INTEGER NOT NULL
);
CREATE INDEX study_changes_notebook ON study_changes(notebook_id,revision);
CREATE TRIGGER study_stroke_added AFTER INSERT ON study_strokes
BEGIN
  INSERT INTO study_changes(notebook_id,page,stroke_id,kind,data,created_at)
    VALUES(NEW.notebook_id,NEW.page,NEW.id,CASE NEW.deleted WHEN 1 THEN 'delete' ELSE 'put' END,NEW.data,NEW.updated_at);
  UPDATE study_notebooks SET revision=(SELECT MAX(revision) FROM study_changes WHERE notebook_id=NEW.notebook_id),updated_at=NEW.updated_at WHERE id=NEW.notebook_id;
END;
CREATE TRIGGER study_stroke_erased AFTER UPDATE OF deleted ON study_strokes WHEN OLD.deleted=0 AND NEW.deleted=1
BEGIN
  INSERT INTO study_changes(notebook_id,page,stroke_id,kind,data,created_at)
    VALUES(NEW.notebook_id,NEW.page,NEW.id,'delete',NULL,NEW.updated_at);
  UPDATE study_notebooks SET revision=(SELECT MAX(revision) FROM study_changes WHERE notebook_id=NEW.notebook_id),updated_at=NEW.updated_at WHERE id=NEW.notebook_id;
END;
CREATE TABLE study_invites (
  token_hash TEXT PRIMARY KEY,
  notebook_id TEXT NOT NULL REFERENCES study_notebooks(id) ON DELETE CASCADE,
  created_by TEXT NOT NULL REFERENCES study_accounts(id) ON DELETE CASCADE,
  expires_at INTEGER NOT NULL,
  used_by TEXT REFERENCES study_accounts(id) ON DELETE CASCADE
);
CREATE INDEX study_invites_expiry ON study_invites(expires_at);
