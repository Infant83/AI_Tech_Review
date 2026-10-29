# Adult neurogenesis and the science of rehabilitation

A bilingual AI Tech Review developed on 2026-10-30. Korean is canonical; the English edition preserves the same populations, reported values, uncertainty and clinical boundaries.

- Korean title: **뇌의 회복을 다시 묻다: 성인 신경세포 생성과 재활의 과학**
- English title: **How the Brain Recovers: Adult Neurogenesis and the Science of Rehabilitation**
- Publication status: published; final manuscripts, complete output QA and live verification passed.
- Intended reading destinations: [한국어](https://infant83.io/AI_Tech_Review/reviews/2026-10-30_brain-neurogenesis-rehabilitation/), [English](https://infant83.io/AI_Tech_Review/reviews/2026-10-30_brain-neurogenesis-rehabilitation/en/).

## Editorial question

What must connect the birth of a new neuron with useful functional recovery? The article follows human hippocampal evidence into circuit integration, relearning and task/environmental compensation. Adult neurogenesis is itself a form of neuroplasticity. The article distinguishes those processes without setting them up as mutually exclusive alternatives.

The introduction uses bomb-pulse radiocarbon dating as a concrete way into the question of cell birth. The review then examines 1998 birth labeling, competing histological and transcriptomic studies, 2025 proliferating progenitors and 2026 RNA/chromatin findings. It connects these methods to adult TBI memory-rehabilitation trials, the Japanese conditional/time-limited authorization of a particular cell product, and human exercise studies.

No individual history, prognosis or treatment plan is discussed. Only public research and official regulatory/publication records support the article. Raw correspondence, identifying message metadata, source captures and QA screenshots are excluded from public distribution.

## Sources and verification boundaries

Twenty numbered APS references are identical in the Korean and English manuscripts. The curated [reference manifest](artifacts/reference-manifest.json) preserves author credit, original titles, publication versions and links. Published articles use first pages or article numbers. The 2026 Nature update only added omitted funding acknowledgements; it did not revise the study results.

The 2025 Science classifier identified 354 candidate progenitor nuclei within 286,799 adolescent/adult nuclei; 402,660 is the combined childhood-plus-older dataset. The 2026 Nature comparison involved 38 donors and 355,997 nuclei. Cell number, donor number, birth rate, molecular state and inferred lineage are not interchanged.

The 2021 STEMTRA primary report concerns 24-week/6-month outcomes. Its 63 randomized participants led to 61 operated participants in the modified intention-to-treat analysis, 46 across three cell-dose groups and 15 sham controls. The reported 6-point FMMS difference has 95% CI 0.3–11.8. The 2024 report is a post hoc 48-week analysis of the same trial, not independent confirmation: pooled changes were +7.5 versus +4.1 points, p=0.20. Serious adverse-event counts are explicitly tied to their reporting windows: 4/46 versus 2/15 at 24 weeks, 4/46 versus 3/15 through 48 weeks. No participant-level data were reanalysed.

The current Japanese package insert distinguishes an injury at least six months earlier and fixed motor impairment; it does not require that a fixed state lasted six consecutive months. Trial enrollment required at least twelve months after injury. The first postmarketing administration occurred 2 October 2026; its announcement was 5 October.

The New Scientist feature was checked only through its public introduction and byline. The 2026 killifish article is summarized within its public abstract; no animal sample size or full-method replication is claimed. The 2019 fixation paper was checked through its abstract and extended-data material. Other methods/results were checked in available original articles, publisher material or official records as recorded by the source reviewers. No tissue, single-cell, animal or clinical experiment was performed by this review.

## Production files

- `reports/review_ko.md`, `reports/review_en.md`: complete manuscripts.
- `artifacts/hero.webp`: original 1600×900 AI-generated conceptual cover, not anatomical or patient imaging.
- `cover-art-brief.md`, `figure-manifest.json`: three concepts, selection, semantic correspondence, exact final generation prompt and actual inspection scope.
- `review-explanation-brief.md`: argument, terminology, figure interpretation and independent corrections.
- `artifacts/stemtra_reported.json`: attributed 24-week values and 48-week context.
- `artifacts/build_figures.py`, `figure_data.json`: original bilingual explanatory figures, each with desktop and mobile layouts.
- `artifacts/publication.json`: titles, public destinations, actual production roles and scope disclosure.
- `artifacts/build_review.mjs`, `build_fonts.py`, `build_pdf.py`, `review.css`: HTML/font/PDF production with an explicit final-asset allowlist.
- `dist/index.html`, `dist/review_ko.pdf`; `dist/en/index.html`, `dist/en/review_en.pdf`: complete outputs after final build.

The cover was generated with the built-in image_gen tool without reference-image input. Figure geometry is original, and the numerical chart uses reported facts rather than a tracing of a source figure. No third-party figure was reused or adapted. Rights are described in the site's rights and AI-use notice; no blanket license is applied to third-party sources. Fonts retain their source license and are renamed for subsetting.

## Rebuild

Supply a Node runtime with marked and Playwright, Chrome, Python with Matplotlib/fontTools/brotli, suitable source fonts and Poppler/PDF inspection utilities. Runtime/font locations are arguments or environment variables, not embedded private paths. The article contains no mathematical equations, so MathJax is not needed.

From this package directory, supply `REVIEW_NODE`, `REVIEW_PYTHON`, `CODEX_PRIMARY_RUNTIME_NODE_MODULES`, `REVIEW_REGULAR_TTF`, `REVIEW_BOLD_TTF` and `REVIEW_FALLBACK_TTF` for your local environment. If extra Python packages are in a separate directory, add it to `PYTHONPATH` before running:

```sh
"$REVIEW_PYTHON" artifacts/build_figures.py --font "$REVIEW_REGULAR_TTF" --bold "$REVIEW_BOLD_TTF"
"$REVIEW_PYTHON" artifacts/build_fonts.py --regular "$REVIEW_REGULAR_TTF" --bold "$REVIEW_BOLD_TTF" --fallback "$REVIEW_FALLBACK_TTF"
"$REVIEW_NODE" artifacts/build_review.mjs
"$REVIEW_PYTHON" artifacts/build_pdf.py --node "$REVIEW_NODE" --modules "$CODEX_PRIMARY_RUNTIME_NODE_MODULES"
```

These commands build all twelve figure layouts, all three font subsets, both HTML articles and both PDFs. The fallback uses the OFL-licensed [Noto Sans JP source](https://github.com/google/fonts/tree/main/ofl/notosansjp); its full license is retained in `artifacts/fallback-font-OFL.txt`. It covers Japanese references, accented names and the minus sign without relying on installed device fonts. The HTML builder also accepts `--language=ko` or `--language=en`; the PDF builder accepts `--language ko` or `--language en`. Rebuild the font subsets after manuscript or disclosure changes. Keep research captures, browser screenshots and page renders under ignored `notes/` and `tmp/`. The builders do not deploy or register documents.

## Actual roles and review

Responsible editor: 김현중 / Hyun-Jung Kim. AI assistance: OpenAI Codex; exact authoring-model identifier not retained. Editorial Harness 2026.08, Scientific Explanation and Visual Communication Principles 1.0, current writing guidance and APS reference policy apply. The topic, writing and public posting were requested; no line-by-line human approval or reader-comprehension study is claimed.

- `root`: primary-source integration, Korean writing, original conceptual cover, editing and publication.
- `academic_sources`: human hippocampal source research, assay/denominator and independent scientific/bilingual review.
- `rehab_evidence`: clinical rehabilitation/cell-therapy sources, outcome/safety checks and complete English translation.
- `review_format`: original bilingual responsive figures, fonts, HTML/PDF production and full output QA.
- `publish_audit`: independent conceptual-cover, reader-explanation, clinical-source, APS and publication audit.

The independent scientific review corrected the 354 candidate denominator, 69-person trial group attribution and the timing of the 2018 decline finding. Independent explanation/clinical review clarified RNA velocity, the FMMS scale, pooled doses, regulatory time criteria, same-trial follow-up, the figure 1 layout and adverse-event terminology. The TBI-MEM subtitle and APS first-page form were restored. Cover, thumbnail, grayscale and four recent covers were inspected independently. Final output and live checks are recorded below when completed.

## Final local publication checks

The Korean PDF has 10 pages and 4,460,002 bytes (SHA256: 40a0ac93a12c246b30c851a864a6840ba00dc1770924783594304f0ad76da020). The English PDF has 12 pages and 4,148,779 bytes (SHA256: eb915edc1f586fbacdb7780e3f822740112cd05d9da2941e45889fdc827616ce). All 22 pages were rendered and inspected individually with no layout defect. Each language has 62 HTTP(S) URI links, no PDF attachments or private paths, and no missing manuscript glyphs. Three embedded OFL subsets provide consistent Latin/Korean/Japanese rendering, and PDF font programs or Type3 glyphs are included. Desktop 1440px and mobile 390px output passed. All twelve SVG variants were rebuilt in isolation and matched the final source bytes.

The complete local site validator returned no errors. Reader-artifact validation passed 1,649 files and 53 articles. The repository suite ran 144 tests: 143 passed and one optional Python-Markdown dependency test was skipped. The catalogs now contain 50 reviews and 93 archive documents; all 49 previous review and 91 archive records are unchanged. All 84 preexisting reading-copy HTML files remain byte-identical to the baseline after excluding generated formatting churn. The new PDFs have four byte-identical copies each, and archive sizes/hashes match. Only final allowlisted article assets enter reading copies.

Canonical/alternate links in final HTML follow the existing central publisher's GitHub Pages addresses, which resolve through the existing service domain. The frozen PDFs retain working service-domain links. HTML-only metadata normalization did not reprint or change the reviewed PDFs. The existing artifact-based Pages workflow and reader features are preserved. No domain settings changed.

## Live publication: 2026-10-30

The [Korean review](https://infant83.io/AI_Tech_Review/reviews/2026-10-30_brain-neurogenesis-rehabilitation/) and [English edition](https://infant83.io/AI_Tech_Review/reviews/2026-10-30_brain-neurogenesis-rehabilitation/en/) are public, with both PDFs registered in the review and document-archive catalogs. Publication source commit: `313ab56c3df52c73a942bf556e2ebe849723d672`. The [Pages artifact workflow](https://github.com/Infant83/AI_Tech_Review/actions/runs/40960045250) completed successfully, including deployment and its existing reader-publication synchronization.

The live check passed 30 files and both original canonical URLs. Twenty-three files matched their local bytes exactly. Six HTML documents matched after reversing only independently identified Cloudflare analytics/public-contact transformations; the public reader catalog matched the expected deployment revision and all other JSON values. Unrecognized scripts or other content differences were not excluded. Both canonical URLs resolved to the service-domain article with HTTP 200 and the same normalized content. The PDF, CSS, SVG and cover bytes matched the reviewed files.

Actual Chrome checks passed for both languages at 1440px and 390px, including seven loaded images per language, three embedded fonts, all responsive figures, actual Korean-to-English-to-Korean navigation, PDF paths, and both hub cards and expanded summaries. Document overflow, page exceptions and failed requests were zero. Anonymous subscription-state requests returned HTTP 401 in eight console entries across the full route; the same behavior was confirmed on a preexisting article and hub. It did not affect public reading or language/PDF navigation. No subscription or reaction action was taken. Screenshots and detailed checks remain outside public distribution.
