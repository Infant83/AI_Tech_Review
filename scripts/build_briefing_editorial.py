"""Compile a reviewed bilingual briefing manuscript for the static publisher.

Uses the existing Markdown authoring dependency; publishing the compiled passive
fragments needs only the standard library. No PDF or archive bytes are changed.
"""
from pathlib import Path
import argparse
import json
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id")
    parser.add_argument("--ko", type=Path, required=True)
    parser.add_argument("--en", type=Path, required=True)
    parser.add_argument("--updated", required=True)
    parser.add_argument("--evidence-cutoff", required=True)
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
    compiled = []
    for language in ("ko", "en"):
        supplied = getattr(args, language)
        source = supplied if supplied.is_absolute() else Path.cwd() / supplied
        if (not source.is_relative_to(root) or source.suffix != ".md"
                or any(part.is_symlink() for part in (source, *source.parents))
                or not source.is_file()):
            raise ValueError("Manuscript must be a regular repository Markdown file")
        source = source.resolve()
        rendered = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["extra", "sane_lists"])
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
