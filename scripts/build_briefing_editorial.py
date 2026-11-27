"""Compile a reviewed bilingual briefing manuscript for the static publisher.

Uses the existing Markdown authoring dependency; publishing the compiled passive
fragments needs only the standard library. No PDF or archive bytes are changed.
"""
from pathlib import Path
import argparse
import json
import re


AI_MODEL_TOKEN = "{{AI_MODEL_DISCLOSURE}}"


def _unique_json_object(pairs):
    values = {}
    for key, value in pairs:
        if key in values:
            raise ValueError("Duplicate AI provenance field")
        values[key] = value
    return values


def model_disclosure_inputs(root, manuscripts, supplied):
    """Resolve a frozen authoring record, never the publisher host's settings."""
    counts = [source.count(AI_MODEL_TOKEN) for source in manuscripts]
    if counts == [0, 0] and supplied is None:
        return None
    if counts != [1, 1]:
        raise ValueError("Both manuscripts need exactly one AI model disclosure token")
    source = supplied
    if source is None:
        raise ValueError("AI model token requires --ai-provenance with a captured authoring record")
    source = source if source.is_absolute() else Path.cwd() / source
    if (not source.is_relative_to(root) or source.suffix != ".json"
            or any(part.startswith(".") or "private" in part.lower()
                   for part in source.relative_to(root).parts)
            or any(part.is_symlink() for part in (source, *source.parents))
            or not source.is_file() or not source.resolve().is_relative_to(root.resolve())
            or source.stat().st_size > 65536):
        raise ValueError("AI provenance must be a regular repository JSON file")
    try:
        from .ai_model_provenance import validate_public_provenance
    except ImportError:
        from ai_model_provenance import validate_public_provenance
    return validate_public_provenance(json.loads(source.read_text(encoding="utf-8"),
                                                object_pairs_hook=_unique_json_object))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id")
    parser.add_argument("--ko", type=Path, required=True)
    parser.add_argument("--en", type=Path, required=True)
    parser.add_argument("--updated", required=True)
    parser.add_argument("--evidence-cutoff", required=True)
    parser.add_argument("--ai-provenance", type=Path,
                        help="Frozen public-safe authoring model record for the AI disclosure token")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*", args.id):
        raise ValueError("Invalid registered briefing ID")
    import markdown
    try:
        from .briefing_editorials import validate_fragment
    except ImportError:
        from briefing_editorials import validate_fragment
    result = {"version": 1, "id": args.id, "updated": args.updated,
              "evidence_cutoff": args.evidence_cutoff}
    sources = []
    for language in ("ko", "en"):
        supplied = getattr(args, language)
        source = supplied if supplied.is_absolute() else Path.cwd() / supplied
        if (not source.is_relative_to(root) or source.suffix != ".md"
                or any(part.is_symlink() for part in (source, *source.parents))
                or not source.is_file()):
            raise ValueError("Manuscript must be a regular repository Markdown file")
        source = source.resolve()
        sources.append(source)
    manuscripts = [source.read_text(encoding="utf-8") for source in sources]
    provenance = model_disclosure_inputs(root, manuscripts, args.ai_provenance)
    if provenance is not None:
        try:
            from .ai_model_provenance import render_disclosure
        except ImportError:
            from ai_model_provenance import render_disclosure
        manuscripts = [text.replace(AI_MODEL_TOKEN, render_disclosure(provenance, language))
                       for text, language in zip(manuscripts, ("ko", "en"))]
    compiled = []
    for source, manuscript, language in zip(sources, manuscripts, ("ko", "en")):
        rendered = markdown.markdown(manuscript, extensions=["extra", "sane_lists"])
        rendered = validate_fragment(rendered) + "\n"
        destination = source.with_suffix(".html")
        if destination.is_symlink():
            raise ValueError("Compiled manuscript cannot be a symlink")
        compiled.append((destination, rendered))
        result[language] = destination.relative_to(root).as_posix()
    registry = root / "publication" / "briefings"
    if (any(part.is_symlink() for part in (registry, *registry.parents))
            or (registry / (args.id + ".json")).is_symlink()):
        raise ValueError("Editorial registration cannot be a symlink")
    for destination, rendered in compiled:
        destination.write_text(rendered, encoding="utf-8")
    registry.mkdir(parents=True, exist_ok=True)
    (registry / (args.id + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Compiled both briefing editions; archive PDF unchanged")


if __name__ == "__main__":
    main()
