"""Bound recovery-artifact count after a successful production deployment."""
from __future__ import annotations
import argparse
import json
import re
import subprocess

NAME = "publication-recovery"


def deletion_plan(artifacts: list, keep=3):
    if type(keep) is not int or keep < 1:
        raise ValueError("Keep at least one complete recovery artifact")
    matching = [row for row in artifacts if row.get("name") == NAME and not row.get("expired")]
    if any(type(row.get("id")) is not int or row["id"] <= 0 or not isinstance(row.get("created_at"), str) for row in matching):
        raise ValueError("Invalid recovery artifact record")
    matching.sort(key=lambda row: (row["created_at"], row["id"]), reverse=True)
    return {"keep": [row["id"] for row in matching[:keep]], "delete": [row["id"] for row in matching[keep:]]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--keep", type=int, default=3)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("Use owner/repository")
    response = subprocess.run(["gh", "api", "--paginate", "--slurp", f"repos/{args.repository}/actions/artifacts?per_page=100&name={NAME}"], check=True, capture_output=True, text=True)
    pages = json.loads(response.stdout)
    plan = deletion_plan([row for page in pages for row in page["artifacts"]], args.keep)
    if args.apply:
        # The CI caller only reaches here after uploading the current complete
        # verified archive. No source, Pages artifact or private backup is touched.
        for identifier in plan["delete"]:
            subprocess.run(["gh", "api", "--method", "DELETE", f"repos/{args.repository}/actions/artifacts/{identifier}"], check=True, capture_output=True)
    print(json.dumps({**plan, "applied": args.apply}))

if __name__ == "__main__": main()
