# Publication validation record

## Completed before pull request

- Current main fetched; clean clone based on `115e167398a26a9222dc413f8ce550261de39445`. Weekly branch created without modifying existing user work.
- New source package rendered through `scripts/markdown_to_html.py`, packaged through `scripts/html_to_dist.py`, published through `scripts/publish_public_site.py --review 2026-09-13_avatar-scientific-workflow-control`.
- Existing unittest suite: 16/16 passed (math protection, public privacy and allowlist behavior).
- Full public-site validator: zero errors after repairing the pre-existing September 11 OLED pages' missing standardized disclosure and broken private-Markdown link. Only the established publisher's refresh function was used for that repair; scientific text, images, captions, manifest record and social image are unchanged.
- The publisher also normalized whitespace and asset order in unrelated older pages. Those incidental generated edits were discarded. All 26 prior manifest objects are byte-semantically unchanged, including the corrected quantum-vacuum thumbnail.
- Package assertions: 27 hub cards match all 27 manifest thumbnails; ko/en titles and Open Graph titles agree; ko/en/x-default alternates present; descriptions are 151 and 159 characters; tables have consistent columns; local images exist with alt text; 1600×900 hero contains no EXIF/XMP; no support Markdown/JSON/Python in public review directories.
- Scientific text audit: no rhythm warning in either language. Two Korean binary contrasts retained because they distinguish scientific-task identity and the object being evaluated. Source attribution, conditional metrics, QM9-lookup boundary, rule-based executor, unit uncertainty, stronger-baseline gap, and total-cost uncertainty retained. Internal copyediting assessment: directness 9/10, rhythm 8/10, trust 9/10, naturalness 8/10, density 8/10, precision 9/10, fidelity 9/10 = 60/70; these are editorial judgments, not independent validation.
- Quantitative arithmetic: 5/12 = 41.666…%; explicitly not a GPU-time reproduction.
- Local browser preview was unavailable: the managed browser does not allow localhost or local-file navigation. No bypass was attempted. Static layout/CSS checks were completed; visual inspection is reserved for the authorized deployed public pages.

## Final main integration

- The pre-push fetch found new main commit `c036d5efe539fcf7f0b1b9bc3888589713a297dd`, publishing a separate multiphoton-reservoir review. Its full Korean text and citations were checked for overlap; it does not duplicate Avatar.
- Main was merged without force or deletion. Both new registry/manifest entries and hub cards were retained. The OLED repairs already arrived in main and are no longer changes introduced by this pull request.
- The final preservation check covers all 27 prior manifest objects, with 28 hub cards. Existing public pages remain identical to the refreshed main.
- Both original SVG diagrams were rendered and visually inspected; background masks keep connector lines from crossing labels. Korean font support was added only to the local renderer, not as a public asset.
- All 12 unique pre-deployment external/reference URLs returned HTTP 200. Sixteen unit tests and the public-site/package checks were rerun after integration.

Machine-readable results are in `package_validation.json` and `link_validation.json`. These files are support records, not public-site assets. Publication deployment evidence will be recorded in the pull request after merge.

## Rebuild commands

From repository root (Python with Markdown 3.10.3, beautifulsoup4 4.15.0 and Pillow 12.3.0 used here):

```bash
python 2026-09-13_avatar-scientific-workflow-control/build_support.py
python scripts/markdown_to_html.py 2026-09-13_avatar-scientific-workflow-control/reports/2026-09-13_avatar-scientific-workflow-control_final_review.md 2026-09-13_avatar-scientific-workflow-control/reports/2026-09-13_avatar-scientific-workflow-control_final_review_en.md
python scripts/html_to_dist.py 2026-09-13_avatar-scientific-workflow-control/reports/2026-09-13_avatar-scientific-workflow-control_final_review.html --dist 2026-09-13_avatar-scientific-workflow-control/dist
python scripts/html_to_dist.py 2026-09-13_avatar-scientific-workflow-control/reports/2026-09-13_avatar-scientific-workflow-control_final_review_en.html --dist 2026-09-13_avatar-scientific-workflow-control/dist/en
python scripts/publish_public_site.py --review 2026-09-13_avatar-scientific-workflow-control
python -m unittest discover -s tests -v
python 2026-09-13_avatar-scientific-workflow-control/validate_package.py
python 2026-09-13_avatar-scientific-workflow-control/check_links.py
```

Review generated diffs before committing: the shared publisher refreshes older page formatting and alphabetizes asset lists. The strict preservation assertion intentionally flags such unrelated manifest changes; do not waive it silently. Hero image generation is not deterministic; the committed WebP and recorded prompt preserve the selected artwork.
