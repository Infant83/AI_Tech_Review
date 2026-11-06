"""Publish this article through the shared publisher with its saved metrics."""
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[3]
TOPIC = "2026-08-26_quantum-computing-layers"
sys.path.insert(0, str(ROOT / "scripts"))
import publish_public_site as publisher


def main():
    settings = json.loads(Path(__file__).with_name("publication-settings.json").read_text())
    publisher.restore_published_analytics()
    key = publisher.PUBLIC_METRICS_ENDPOINT_ENV
    previous = os.environ.get(key)
    try:
        os.environ[key] = settings["public_metrics"]["endpoint"]
        publisher.public_metrics_endpoint()
        path = ROOT / "site/manifest.json"
        manifest = json.loads(path.read_text())
        review = next(r for r in publisher.REVIEWS if r.folder == TOPIC)
        old = next(r for r in manifest if r["folder"] == TOPIC)
        new = publisher.publish_review(review, old)
        path.write_text(json.dumps([new if r["folder"] == TOPIC else r for r in manifest], ensure_ascii=False, indent=2) + "\n")
    finally:
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous
    return publisher.main(["--hub-only"])


if __name__ == "__main__":
    raise SystemExit(main())
