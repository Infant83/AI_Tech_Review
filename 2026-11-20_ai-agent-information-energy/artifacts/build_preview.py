"""Build a local editorial preview; this does not register or publish a review."""
from pathlib import Path
import hashlib
import html
import json
import re
import shutil
import markdown

TOPIC = Path(__file__).resolve().parents[1]
DIST = TOPIC / "preview"
ASSETS = DIST / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
source = TOPIC / "reports/review_ko.md"
text = source.read_text(encoding="utf-8")
body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
main, references = body.split("<h2>참고문헌</h2>", 1)

def citation(m):
    nums = [int(n.strip()) for n in m.group(1).split(",")]
    return '<span class="cite">[' + ",".join(
        f'<a href="#ref-{n}" aria-label="참고문헌 {n}">{n}</a>' for n in nums
    ) + "]</span>"

main = re.sub(r"\[(\d+(?:,\s*\d+)*)\]", citation, main)
body = main + '<h2 id="references">참고문헌</h2>' + references
body = body.replace("../artifacts/", "assets/")
assets = [TOPIC / "artifacts/hero.png"]
assets += sorted(p for p in (TOPIC / "artifacts/figures").glob("fig[1-5]_*.svg") if not p.stem.endswith("_en"))
if len(assets) != 11:
    raise SystemExit(f"Expected cover + 10 responsive SVG assets, found {len(assets)}")
for src in assets:
    rel = src.relative_to(TOPIC / "artifacts")
    dest = ASSETS / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)

css = """
:root{--paper:#f7f4eb;--ink:#293d42;--muted:#586865;--teal:#316a67;--line:#d6d9cc}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:2rem}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'Apple SD Gothic Neo','Noto Sans CJK KR',sans-serif;font-size:18px;line-height:1.95;word-break:keep-all;overflow-wrap:anywhere}
.preview-bar{border-bottom:1px solid var(--line);padding:14px 24px;font-size:12px;letter-spacing:.07em;display:flex;justify-content:space-between;gap:20px;color:var(--muted)}
main{width:min(100% - 48px,760px);margin:68px auto 90px}
h1{font-size:clamp(30px,4.4vw,46px);line-height:1.32;letter-spacing:-.045em;font-weight:750;margin:0 0 20px;text-wrap:balance}
h1+p{font-size:18px;line-height:1.65;color:var(--teal);margin:0 0 32px}h1+p em{font-style:normal}
p{margin:0 0 1.38em}h2{font-size:26px;line-height:1.48;letter-spacing:-.035em;margin:62px 0 26px;font-weight:720}
a{color:var(--teal);text-decoration-thickness:1px;text-underline-offset:4px}.cite{font-size:.77em;white-space:nowrap;vertical-align:super;line-height:0}.cite a{text-decoration:none}
figure{margin:42px -130px 46px}figure img{display:block;max-width:100%;height:auto;width:100%}figure picture{display:block}figcaption{font-size:13px;line-height:1.8;color:var(--muted);padding:14px 12px 0;word-break:keep-all}.hero{margin-top:34px;margin-bottom:44px}.hero img{border-radius:2px}.hero figcaption{padding-top:12px}
.equation{font-family:'Times New Roman','Apple SD Gothic Neo',serif;font-size:23px;text-align:center;background:#eeeee2;padding:24px 12px;margin:26px 0 30px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);line-height:1.6}
.theory-note{border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:26px 0 32px;padding:15px 0;font-size:15px;line-height:1.9}.theory-note summary{cursor:pointer;color:var(--teal);font-weight:600}.theory-note p{margin:18px 0 4px}
#references~p{font-size:14px;line-height:1.8;margin-bottom:20px;word-break:normal}#references~h2{font-size:22px}
@media(max-width:1100px){figure{margin-left:-24px;margin-right:-24px}}
@media(max-width:640px){body{font-size:17px;line-height:1.96}main{width:calc(100% - 38px);margin-top:38px}h1{font-size:31px}h1+p{font-size:16px}h2{font-size:23px;margin-top:46px;margin-bottom:22px}figure{margin:30px -9px 34px}figcaption{font-size:12px;padding:12px 9px 0}.hero{margin-left:-19px;margin-right:-19px}.hero figcaption{padding-left:19px;padding-right:19px}.equation{font-size:20px;padding:21px 8px}.preview-bar{padding:11px 19px;font-size:11px;letter-spacing:0}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""
title = re.search(r"^# (.+)$", text, re.M).group(1)
document = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><link rel="icon" href="data:,"><title>{html.escape(title)} · 국문 초안</title><style>{css}</style></head>
<body><div class="preview-bar"><span>ATRL · 편집 미리보기</span><span>2026-11-20 · 국문 초안</span></div><main>{body}</main></body></html>'''
(DIST / "index.html").write_text(document, encoding="utf-8")
manifest = {
    "status": "editorial_preview_not_published",
    "source": str(source.relative_to(TOPIC)),
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "assets": [{"path": str(p.relative_to(TOPIC)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in assets],
    "preview_sha256": hashlib.sha256(document.encode()).hexdigest(),
}
(TOPIC / "artifacts/preview-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"preview": str((DIST / "index.html").relative_to(TOPIC)), "assets": len(assets)}, ensure_ascii=False))
