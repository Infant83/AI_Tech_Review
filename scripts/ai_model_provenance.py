"""Capture narrowly scoped Codex model settings; render saved public records.

Collection is an explicit authoring-time action, never an import/build side
effect. Local turn_context settings are client records, not an independent
attestation of backend weights. Raw sessions and settings remain private.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import BinaryIO


VERSION = 1
SYSTEM = "OpenAI Codex"
SCOPE = "recorded_editorial_work"
TAIL_BYTES = 8 * 1024 * 1024
MAX_WINDOW_BYTES = 32 * 1024 * 1024
MAX_BYTES_READ = 64 * 1024 * 1024
MAX_METADATA_BYTES = 2 * 1024 * 1024
MAX_CONFIG_BYTES = 256 * 1024
MAX_CONTEXT_RECORDS = 4096
MAX_PARTICIPANTS = 16
MAX_PUBLIC_ROWS = 64
CHUNK_BYTES = 64 * 1024
EFFORTS = frozenset({"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"})
EVIDENCE_KINDS = frozenset({"turn_context", "settings_snapshot", "unconfirmed"})
ROLE_LABELS = {
    "authoring": ("집필", "authoring"),
    "editing": ("편집", "editing"),
    "integration": ("통합", "integration"),
    "source-review": ("원문 대조", "source review"),
    "scientific-review": ("과학 감수", "scientific review"),
    "pdf-production": ("PDF 제작", "PDF production"),
    "independent-review": ("독립 감수", "independent review"),
    "publication-audit": ("발행 검수", "publication audit"),
    "disclosure-correction": ("AI 활용 정보 정정", "disclosure correction"),
    "translation": ("번역", "translation"),
    "figure-production": ("그림 제작", "figure production"),
    "software-validation": ("소프트웨어 검증", "software validation"),
}
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
_MODEL = re.compile(r"(?:gpt|codex)-[a-z0-9][a-z0-9._-]{0,95}|o[1-9](?:-[a-z0-9][a-z0-9._-]{0,95})?")
_HEADER = re.compile(rb'^\s*\{\s*"timestamp"\s*:\s*"([^"\r\n]+)"\s*,\s*(?:"ordinal"\s*:\s*[0-9]+\s*,\s*)?"type"\s*:\s*"([^"\r\n]+)"')
_TOP_KEYS = {"version", "system", "scope", "checked_on", "roles"}
_ROLE_KEYS = {"role", "model_id", "reasoning_effort", "evidence_kind"}


class ProvenanceError(ValueError):
    """An unsupported, unsafe or ambiguous local provenance input."""


def _model(value):
    if value is None:
        return None
    if not isinstance(value, str) or not _MODEL.fullmatch(value) or _UUID.search(value):
        raise ProvenanceError("Unsupported public model identifier")
    return value


def _effort(value):
    if value is not None and (not isinstance(value, str) or value not in EFFORTS):
        raise ProvenanceError("Unsupported reasoning effort")
    return value


def _role(value):
    if not isinstance(value, str) or value not in ROLE_LABELS:
        raise ProvenanceError("Unsupported public editorial role")
    return value


def validate_public_provenance(record: dict) -> dict:
    """Validate/normalize only the saved allowlisted record; read no local state.

    The narrow v1 vocabulary prevents local paths, thread identifiers, freeform
    transcripts or arbitrary settings from becoming public disclosure text.
    New model/role vocabularies require a deliberate schema update.
    """
    if not isinstance(record, dict) or set(record) != _TOP_KEYS:
        raise ProvenanceError("Invalid public provenance fields")
    if type(record["version"]) is not int or record["version"] != VERSION:
        raise ProvenanceError("Unsupported public provenance version")
    if record["system"] != SYSTEM or record["scope"] != SCOPE:
        raise ProvenanceError("Unsupported public provenance scope or system")
    checked = record["checked_on"]
    if not isinstance(checked, str):
        raise ProvenanceError("Invalid provenance confirmation date")
    try:
        parsed = date.fromisoformat(checked)
    except ValueError:
        raise ProvenanceError("Invalid provenance confirmation date") from None
    if parsed.isoformat() != checked:
        raise ProvenanceError("Invalid provenance confirmation date")
    rows = record["roles"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_PUBLIC_ROWS:
        raise ProvenanceError("Invalid public provenance role count")
    normalized = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != _ROLE_KEYS:
            raise ProvenanceError("Invalid public provenance role fields")
        role = _role(row["role"])
        model = _model(row["model_id"])
        effort = _effort(row["reasoning_effort"])
        kind = row["evidence_kind"]
        if not isinstance(kind, str) or kind not in EVIDENCE_KINDS:
            raise ProvenanceError("Unsupported provenance evidence kind")
        if kind == "unconfirmed" and (model is not None or effort is not None):
            raise ProvenanceError("Unconfirmed provenance cannot claim model settings")
        item = {"role": role, "model_id": model, "reasoning_effort": effort, "evidence_kind": kind}
        if item not in normalized:
            normalized.append(item)
    normalized.sort(key=lambda x: (x["role"], x["evidence_kind"], x["model_id"] or "", x["reasoning_effort"] or ""))
    return {"version": VERSION, "system": SYSTEM, "scope": SCOPE, "checked_on": checked, "roles": normalized}


def render_disclosure(record: dict, language: str) -> str:
    """Render a saved record as a Markdown-compatible, scope-limited sentence."""
    data = validate_public_provenance(record)
    if language not in {"ko", "en"}:
        raise ProvenanceError("Unsupported disclosure language")
    en = language == "en"
    pieces = []
    groups = {}
    for row in data["roles"]:
        key = (row["evidence_kind"], row["model_id"], row["reasoning_effort"])
        groups.setdefault(key, []).append(row["role"])
    for (kind, model_id, reasoning_effort), roles in groups.items():
        labels = [ROLE_LABELS[role][1 if en else 0] for role in ROLE_LABELS if role in roles]
        label = (", " if en else "·").join(labels)
        row = {"model_id": model_id, "reasoning_effort": reasoning_effort, "evidence_kind": kind}
        model = ("GPT-6.1 Sol (`gpt-6.1-sol`)" if row["model_id"] == "gpt-6.1-sol"
                 else f'`{row["model_id"]}`' if row["model_id"] else ("model not recorded" if en else "모델 미기록"))
        effort = f'`{row["reasoning_effort"]}`' if row["reasoning_effort"] else ("not recorded" if en else "미기록")
        if row["evidence_kind"] == "unconfirmed":
            pieces.append(f"{label}: writing-time model and reasoning settings unconfirmed" if en else f"{label}: 작성 당시 모델·추론 강도 미확인")
        elif row["evidence_kind"] == "settings_snapshot":
            pieces.append(f"{label}: settings snapshot {model}, reasoning effort {effort} (not writing-time usage evidence)" if en else f"{label}: 확인일 설정 스냅숏 {model}, 추론 강도 {effort}(작성 당시 사용 증거는 아님)")
        else:
            pieces.append(f"{label}: {model}, reasoning effort {effort} (recorded turn settings)" if en else f"{label}: {model}, 추론 강도 {effort}(턴 설정 기록)")
    body = "; ".join(pieces)
    if en:
        return (f'AI assistance: {SYSTEM}; checked on {data["checked_on"]} UTC. {body}. '
                "These are client-setting records for the listed editorial roles; backend weights were not independently identified.")
    return (f'AI 보조: {SYSTEM}; 확인일(UTC) {data["checked_on"]}. {body}. '
            "확인 범위는 기록된 편집 역할의 클라이언트 설정이며, 서버 가중치 판본을 독립 확인한 것은 아니다.")


def _timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ProvenanceError("Invalid provenance time bound")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ProvenanceError("Invalid provenance time bound") from None
    if result.tzinfo is None:
        raise ProvenanceError("Provenance time bounds require a timezone")
    return result.astimezone(timezone.utc)


def _thread_id(value: str) -> str:
    if not isinstance(value, str) or not _UUID.fullmatch(value):
        raise ProvenanceError("Invalid explicit Codex thread identity")
    return value.lower()


def default_participant(role: str = "authoring", environ=None) -> tuple[str, str]:
    """Resolve this worker, never silently substitute its parent's session ID."""
    env = os.environ if environ is None else environ
    identity = env.get("CODEX_THREAD_ID")
    if not identity:
        raise ProvenanceError("CODEX_THREAD_ID unavailable; provide --participant explicitly (CODEX_SESSION_ID may identify a parent)")
    return _role(role), _thread_id(identity)


class _BoundedReader:
    """Cap all reads, including alignment during timestamp binary searches."""
    def __init__(self, raw: BinaryIO):
        self.raw = raw
        self.bytes_read = 0

    def seek(self, *args):
        return self.raw.seek(*args)

    def tell(self):
        return self.raw.tell()

    def _read(self, method, size):
        if size < 0:
            raise ProvenanceError("Unbounded rollout reads are not supported")
        remaining = MAX_BYTES_READ - self.bytes_read
        value = method(min(size, remaining + 1))
        self.bytes_read += len(value)
        if self.bytes_read > MAX_BYTES_READ:
            raise ProvenanceError("Codex model-evidence read budget exceeded; narrow the requested interval")
        return value

    def read(self, size=-1):
        return self._read(self.raw.read, size)

    def readline(self, size=-1):
        return self._read(self.raw.readline, size)


def _discard_line(handle: BinaryIO, first: bytes, limit: int) -> int:
    total = len(first)
    while first and not first.endswith(b"\n") and handle.tell() < limit:
        first = handle.readline(min(CHUNK_BYTES, limit - handle.tell()))
        total += len(first)
    if first and not first.endswith(b"\n"):
        raise ProvenanceError("Incomplete rollout record at the selected snapshot boundary")
    return total


def _next_header(handle: BinaryIO, offset: int, limit: int):
    """Find a line header without parsing or retaining response/transcript data."""
    if offset >= limit:
        return None
    handle.seek(offset)
    if offset:
        handle.seek(offset - 1)
        if handle.read(1) != b"\n":
            _discard_line(handle, handle.readline(min(CHUNK_BYTES, limit - handle.tell())), limit)
    position = handle.tell()
    if position >= limit:
        return None
    first = handle.readline(min(2048, limit - position))
    match = _HEADER.match(first)
    if not match:
        raise ProvenanceError("Unsupported or malformed Codex rollout header")
    _discard_line(handle, first, limit)
    try:
        stamp = _timestamp(match[1].decode("ascii"))
        kind = match[2].decode("ascii")
    except UnicodeError:
        raise ProvenanceError("Malformed Codex rollout header") from None
    return position, handle.tell(), stamp, kind


def _time_offset(handle: BinaryIO, limit: int, target: datetime, *, after=False) -> int:
    """Byte-aligned lower/upper bound for the append-ordered JSONL store."""
    low, high = 0, limit
    for _ in range(64):
        if low >= high:
            break
        mid = (low + high) // 2
        header = _next_header(handle, mid, limit)
        before = header and (header[2] <= target if after else header[2] < target)
        if before:
            low = max(mid + 1, header[1])
        else:
            high = mid
    header = _next_header(handle, low, limit)
    return header[0] if header else limit


def _metadata_at(handle: BinaryIO, start: int, end: int) -> tuple[dict, str]:
    if end - start > MAX_METADATA_BYTES:
        raise ProvenanceError("Selected Codex metadata record exceeds the bounded reader limit")
    handle.seek(start)
    raw = handle.read(end - start)
    try:
        data = json.loads(raw, object_pairs_hook=_unique_object)
    except (ValueError, UnicodeError):
        raise ProvenanceError("Malformed selected Codex metadata record") from None
    if not isinstance(data, dict) or not isinstance(data.get("payload"), dict):
        raise ProvenanceError("Malformed selected Codex metadata payload")
    return data, hashlib.sha256(raw).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProvenanceError("Duplicate fields in selected Codex metadata")
        result[key] = value
    return result


def _settings(payload: dict) -> tuple[str | None, str | None]:
    model = payload.get("model")
    effort = payload.get("effort")
    alternative = payload.get("reasoning_effort")
    if effort is not None and alternative is not None and effort != alternative:
        raise ProvenanceError("Conflicting reasoning settings in a Codex metadata record")
    return _model(model), _effort(effort if effort is not None else alternative)


def _safe_rollout(codex_home: Path, path_value: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise ProvenanceError("Selected thread has no rollout locator")
    source = Path(path_value)
    if not source.is_absolute():
        raise ProvenanceError("Unsupported relative Codex rollout locator")
    if source.is_symlink():
        raise ProvenanceError("Symlinked rollout inputs are not supported")
    source = source.resolve()
    roots = [codex_home / "sessions", codex_home / "archived_sessions"]
    if any(root.exists() and not root.resolve().is_relative_to(codex_home) for root in roots):
        raise ProvenanceError("Codex session stores must remain within the selected Codex directory")
    if not any(source.is_relative_to(p.resolve()) for p in roots) or source.suffix != ".jsonl" or not source.is_file():
        raise ProvenanceError("Rollout locator is outside the allowed Codex session stores")
    return source


def _current_config_defaults(codex_home: Path) -> dict:
    """Read only top-level model fields; do not pretend to resolve overrides."""
    path = codex_home / "config.toml"
    result = {"model": None, "reasoning_effort": None, "source": "user_config_defaults"}
    if not path.is_file() or path.is_symlink():
        return result
    if path.stat().st_size > MAX_CONFIG_BYTES:
        raise ProvenanceError("Codex config exceeds the bounded model-field reader limit")
    fields = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeError:
        raise ProvenanceError("Codex config cannot be read as UTF-8") from None
    in_table = False
    for line in lines:
        if not in_table and ('"""' in line or "'''" in line):
            raise ProvenanceError("Multiline top-level Codex config requires a supported TOML parser; model defaults not inferred")
        if re.match(r"^\s*\[", line):
            in_table = True
        if in_table:
            continue
        name = re.match(r"^\s*(model|model_reasoning_effort)\s*=", line)
        if not name:
            continue
        value = re.fullmatch(r'''\s*(model|model_reasoning_effort)\s*=\s*(?:"([^"\\]*)"|'([^'\\]*)')\s*(?:#.*)?''', line)
        if not value or name[1] in fields:
            raise ProvenanceError("Ambiguous model fields in Codex config")
        fields[name[1]] = value[2] if value[2] is not None else value[3]
    result.update(model=_model(fields.get("model")), reasoning_effort=_effort(fields.get("model_reasoning_effort")))
    return result


def _collect_thread(home: Path, row: dict, identity: str, since, until) -> dict:
    path = _safe_rollout(home, row["rollout_path"])
    size = path.stat().st_size
    with path.open("rb") as raw:
        handle = _BoundedReader(raw)
        first = _next_header(handle, 0, size)
        if first is None or first[3] != "session_meta":
            raise ProvenanceError("Selected rollout has no verifiable session identity")
        meta, meta_hash = _metadata_at(handle, first[0], first[1])
        session = meta["payload"]
        # Current subagent rollouts retain the root conversation's session_id.
        # The per-thread id is authoritative; session_id is a legacy fallback
        # only when no per-thread id exists, never an alternate matching id.
        identity_field = "id" if session.get("id") is not None else "session_id"
        if session.get(identity_field) is None or _thread_id(session[identity_field]) != identity:
            raise ProvenanceError("Thread and rollout session identities do not match")
        if session.get("session_id") is not None:
            _thread_id(session["session_id"])
        filename_ids = _UUID.findall(path.name)
        if filename_ids and any(x.lower() != identity for x in filename_ids):
            raise ProvenanceError("Thread and rollout filename identities do not match")
        end = _time_offset(handle, size, until, after=True) if until else size
        if since:
            start = _time_offset(handle, size, since)
        else:
            header = _next_header(handle, max(0, end - TAIL_BYTES), end)
            start = header[0] if header else end
        if end < start or end - start > MAX_WINDOW_BYTES:
            raise ProvenanceError("Requested model-evidence window exceeds the bounded reader limit")
        records = []
        position = start
        previous = None
        while position < end:
            header = _next_header(handle, position, end)
            if header is None:
                break
            a, z, stamp, kind = header
            if previous is not None and stamp < previous:
                raise ProvenanceError("Selected rollout timestamps are not append ordered")
            previous = stamp
            if (since is None or stamp >= since) and (until is None or stamp <= until) and kind == "turn_context":
                data, digest = _metadata_at(handle, a, z)
                model, effort = _settings(data["payload"])
                records.append({"timestamp": stamp.isoformat(), "byte_offset": a, "record_bytes": z - a,
                                "record_sha256": digest, "model": model, "reasoning_effort": effort,
                                "model_source_field": "payload.model", "effort_source_field": "payload.effort" if data["payload"].get("effort") is not None else "payload.reasoning_effort"})
                if len(records) > MAX_CONTEXT_RECORDS:
                    raise ProvenanceError("Too many context records; narrow the requested interval")
            position = z
    # A requested start denotes an interval. With no start, capture the latest
    # bounded context only, not unrelated settings from earlier editorial work.
    selected = records if since is not None else records[-1:]
    return {"thread_id": identity, "source_file": str(path), "source_file_bytes_at_capture": size,
            "session_identity_verified": True, "session_identity_source_field": "payload." + identity_field,
            "session_meta_sha256": meta_hash,
            "selection": "explicit_interval" if since is not None else "latest_context_in_bounded_tail",
            "range_start_byte": start, "range_end_byte": end, "range_bytes_traversed": end - start,
            "source_bytes_read": handle.bytes_read,
            "records": selected, "contexts_seen_in_selected_range": len(records)}


def collect_participants(participants, *, since=None, until=None, codex_home=None) -> tuple[dict, dict]:
    """Collect exact worker metadata, returning separate public/private records.

    Explicit intervals keep every observed model/effort pair. Missing effort
    is never filled from config. Without historical bounds, settings snapshots
    are allowed only under their separate, non-usage evidence kind.
    """
    if not isinstance(participants, (list, tuple)) or not 1 <= len(participants) <= MAX_PARTICIPANTS:
        raise ProvenanceError("Invalid participant count")
    selected = []
    for item in participants:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ProvenanceError("Invalid participant specification")
        entry = (_role(item[0]), _thread_id(item[1]))
        if entry in selected:
            raise ProvenanceError("Duplicate participant specification")
        selected.append(entry)
    lower = _timestamp(since) if since is not None else None
    upper = _timestamp(until) if until is not None else None
    if lower and upper and lower > upper:
        raise ProvenanceError("Provenance time bounds are reversed")
    now = datetime.now(timezone.utc)
    if lower and lower > now:
        raise ProvenanceError("Requested provenance window has not started")
    if upper and upper > now:
        raise ProvenanceError("Requested provenance window has not finished")
    home = Path(codex_home or os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser().resolve()
    database = home / "state_5.sqlite"
    if not database.is_file() or database.is_symlink():
        raise ProvenanceError("Codex thread metadata store is unavailable")
    rows = []
    connection = None
    try:
        connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        for role, identity in selected:
            row = connection.execute("SELECT id, rollout_path, model, reasoning_effort FROM threads WHERE id = ?", (identity,)).fetchone()
            if row is None:
                raise ProvenanceError("No exact Codex metadata row for a participant")
            rows.append((role, identity, dict(row)))
    except sqlite3.Error:
        raise ProvenanceError("Codex thread metadata schema cannot be read safely") from None
    finally:
        if connection is not None:
            connection.close()
    public_rows = []
    evidence = []
    cache = {}
    for role, identity, row in rows:
        if identity not in cache:
            cache[identity] = _collect_thread(home, row, identity, lower, upper)
        detail = {**cache[identity], "public_role": role}
        contexts = detail["records"]
        if contexts:
            for item in contexts:
                public_rows.append({"role": role, "model_id": item["model"], "reasoning_effort": item["reasoning_effort"], "evidence_kind": "turn_context"})
        elif since is not None or until is not None:
            public_rows.append({"role": role, "model_id": None, "reasoning_effort": None, "evidence_kind": "unconfirmed"})
            detail["no_usage_evidence_reason"] = "No turn_context in the requested historical selection; current settings are not substituted."
        else:
            if row["model"] is not None:
                snapshot = {"model": _model(row["model"]), "reasoning_effort": _effort(row["reasoning_effort"]), "source": "current_thread_settings"}
            else:
                snapshot = _current_config_defaults(home)
            detail["settings_snapshot"] = snapshot
            kind = "settings_snapshot" if snapshot["model"] is not None or snapshot["reasoning_effort"] is not None else "unconfirmed"
            public_rows.append({"role": role, "model_id": snapshot["model"] if kind != "unconfirmed" else None,
                                "reasoning_effort": snapshot["reasoning_effort"] if kind != "unconfirmed" else None, "evidence_kind": kind})
        evidence.append(detail)
    # Normalize duplicate settings before applying the bounded public row count.
    unique = []
    for row in public_rows:
        if row not in unique:
            unique.append(row)
    public = validate_public_provenance({"version": VERSION, "system": SYSTEM, "scope": SCOPE,
                                         "checked_on": now.date().isoformat(), "roles": unique})
    private = {"version": VERSION, "collected_at": now.isoformat(), "codex_home": str(home),
               "requested_since": since, "requested_until": until, "participants": evidence,
               "limits": ["Model and effort are local Codex client settings, not backend weights attestation.",
                          "Only named editorial roles are covered; external source-document authorship is not established.",
                          "No transcript, instructions, account identifiers or authentication fields are retained.",
                          "A settings snapshot is not evidence of historical model use."]}
    return public, private
