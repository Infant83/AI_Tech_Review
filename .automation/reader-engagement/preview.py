#!/usr/bin/env python3
"""Serve only the generated public site for local reader-feature QA."""

import argparse
import functools
import http.server
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


SCOPE = "/AI_Tech_Review/"
CONFIG = re.compile(
    r'(<script\b[^>]*\bid=["\']reader-engagement-config["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, site, api, **kwargs):
        self.site = site
        self.api = api
        super().__init__(*args, directory=str(site), **kwargs)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path == "/":
            self.send_response(302)
            self.send_header("Location", SCOPE)
            self.end_headers()
            return
        if not path.startswith(SCOPE):
            self.send_error(404)
            return
        candidate = (self.site / path[len(SCOPE):]).resolve()
        if not candidate.is_relative_to(self.site):
            self.send_error(404)
            return
        if candidate.is_dir():
            candidate /= "index.html"
        if not candidate.is_file():
            self.send_error(404)
            return
        body = candidate.read_bytes()
        if candidate.suffix == ".html":
            def configure(match):
                config = json.loads(match.group(2))
                config["apiBase"] = self.api
                config["allowLocalApi"] = True
                encoded = json.dumps(config, ensure_ascii=False).replace("<", "\\u003c")
                return match.group(1) + encoded + match.group(3)
            body = CONFIG.sub(configure, body.decode("utf-8")).encode("utf-8")
        content_type = self.guess_type(str(candidate))
        if candidate.suffix == ".webmanifest":
            content_type = "application/manifest+json"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8093)
    parser.add_argument("--api", default="http://localhost:8787")
    args = parser.parse_args()
    api = urlsplit(args.api)
    if api.scheme != "http" or api.hostname != "localhost" or api.username or api.password:
        parser.error("The preview API must use http://localhost with an explicit local port.")
    site = Path(__file__).resolve().parents[2] / "site"
    server = http.server.ThreadingHTTPServer(
        ("localhost", args.port), functools.partial(Handler, site=site.resolve(), api=args.api)
    )
    print(f"Reader preview: http://localhost:{args.port}{SCOPE}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
