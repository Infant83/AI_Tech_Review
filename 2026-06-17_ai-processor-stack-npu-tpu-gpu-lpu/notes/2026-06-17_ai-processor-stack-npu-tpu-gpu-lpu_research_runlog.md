# Research Runlog

- 날짜: 2026-06-17
- 작업 폴더: `2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu`
- 사용자 요청: NPU, LPU, TPU, GPU, CPU, DPU, QPU를 포함한 기술 리뷰. imagegen 3장 이상, Remotion/SVG 활용, 최근 동향과 원리·한계·전망 중심.

## 실행 요약

1. AI_Tech_Review workspace guide와 `.codex/rules/`의 writing, visuals, verification 규칙을 확인했다.
2. 기존 AI Tech Review final_review 사례(`neuromorphic-edge-ai`, `tabpfn-oled...`)를 참고해 Figure 1의 흰 배경·회색 라인·LG red accent 톤을 맞췄다.
3. 최신 공식·1차 출처를 검색해 TPU 8t/8i, NVIDIA Blackwell, AWS Trainium3, Microsoft Copilot+ NPU, Groq LPU, NVIDIA BlueField DPU, Google Willow, Cerebras WSE-3, AMD Versal AI Engine, Lightmatter photonic interconnect 등을 확인했다.
4. `imagegen` 스킬의 OpenAI image generation CLI로 4개 주제 이미지를 생성했다.
5. Remotion으로 `ProcessorRouting` 컴포지션을 만들고 정적 페이지 삽입용 PNG still을 렌더링했다.
6. 정적 HTML 삽입 가능성 확인:
   - `markdown_to_html.py`는 `.final-article img`, `svg`, `video` 스타일을 포함한다.
   - `html_to_dist.py`는 로컬 `src`/`href` 파일을 복사하고 flat dist로 재작성한다.
   - 결론: Remotion 소스/컴포지션 자체는 정적 페이지에 직접 넣지 않고, 렌더링된 PNG still만 삽입한다. 이 PNG는 일반 이미지라 final_review HTML과 향후 dist 패키지에 포함 가능하다.

## Generated Assets

- `artifacts/final_review/figures/imagegen/fig01_processor_stack_hero_v2-web.png`
- `artifacts/final_review/figures/imagegen/fig03_memory_wall_imagegen-web.png`
- `artifacts/final_review/figures/imagegen/fig05_edge_npu_imagegen-web.png`
- `artifacts/final_review/figures/imagegen/fig06_lpu_dataflow_imagegen-web.png`
- `artifacts/final_review/figures/svg/fig02_processor_workload_map.svg`
- `artifacts/final_review/figures/svg/fig08_specialization_curve.svg`
- `artifacts/final_review/figures/remotion/fig04_processor_routing_remotion.png`

## Remotion Notes

- Remotion project: `artifacts/final_review/remotion/`
- Commands:
  - `npm install`
  - `npm run still`
- Rendered still:
  - `artifacts/final_review/figures/remotion/fig04_processor_routing_remotion.png`
- `npm install` reported 6 high severity vulnerabilities in the local Remotion dependency tree. This package is used for local rendering only and is not intended as a deployed web app dependency.
- After rendering, `artifacts/final_review/remotion/node_modules` was removed from the topic folder. `package.json`, `package-lock.json`, source files, and the rendered PNG still remain for reproducibility.

## Imagegen Notes

- Prompt file:
  - `notes/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_imagegen_prompts.jsonl`
- Command:
  - `uv run --with openai --with pillow python C:\Users\angpa\.codex\skills\imagegen\scripts\image_gen.py generate-batch --input ... --out-dir ... --concurrency 2 --max-attempts 3 --downscale-max-dim 1536`
- First Figure 1 candidate included visible English labels, so it was kept as a rejected alternate and replaced with `fig01_processor_stack_hero_v2-web.png`.

## HTML Verification

- Render command:
  - `python scripts\markdown_to_html.py --mode auto 2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu\reports\2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_final_review.md 2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu\reports\2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_memo.md`
- Rendered files:
  - `reports/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_final_review.html`
  - `reports/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_memo.html`
- Browser verification:
  - Local HTTP server: `python -m http.server 8765 --bind 127.0.0.1`
  - URL opened: `http://127.0.0.1:8765/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu/reports/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_final_review.html`
  - Playwright image check: 7 figures, 7 loaded images, 0 broken images.
  - Remotion still confirmed: `hasRemotion=true`.
  - SVG confirmed: `hasSvg=true`.
  - Console warnings/errors: 0.
  - Verification screenshot copied to `output/playwright/2026-06-17_ai-processor-stack-final-review-viewport.png`.
- Local HTTP server stopped after verification.
- After the Korean prose cleanup pass, the final review HTML was re-rendered and rechecked:
  - 7 figures
  - 0 broken images
  - Remotion still present
  - SVG present
  - console warnings/errors: 0

## Hyun-Jung Kim-Style Editorial Pass

- Trigger: user approved distribution but requested continued audit/rewrite to better match Hyun-Jung Kim-style writing.
- References checked:
  - `C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\SKILL.md`
  - `references/korean-review-expression-editor.md`
  - `references/korean-science-prose-patterns.md`
  - `references/ai-tech-review-final-pass.md`
  - `.codex/rules/writing-harness.md`
  - `C:\Users\angpa\.codex\rules\korean-writing-style.md`
  - `C:\Users\angpa\Obsidian_Vault\hkim_Writings\2026-05-10_AI식 글쓰기 감사와 김현중식 문체 레퍼런스.md`
  - `C:\Users\angpa\Obsidian_Vault\hkim_Writings\2026-05-10_KIAS_Quanta_CHEY_참고스타일_체크가이드.md`
- Audit command:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py reports\2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_final_review.md`
- Initial finding count after first draft: 22.
- After rewrite: 7 findings.
- Remaining findings are interpreted as:
  - repeated watch terms `장치`, `병목`: expected topic terms for a processor-stack review; kept where technically necessary.
  - `weak_visual_specificity`: the audit script's concrete visual term list is tuned for agent/harness reviews, not processor hardware reviews. Captions were still tightened and reviewed manually.
- Main rewrites:
  - reduced `A가 아니라 B` contrast pivots.
  - removed reader-facing workflow wording around Remotion source embedding.
  - changed generic headings into claim-bearing headings.
  - rewrote conclusion around workload routing and data path rather than slogan.
  - shortened long SVG text nodes.
  - synchronized memo and Obsidian mirror with the revised thesis.

## Pending

- Optional: generate actual Skywork PPTX/PDF from the prepared prompt packet.

## Distribution Package

- User confirmed distribution, then requested Hyun-Jung Kim-style audit/rewrite before final packaging.
- Package command:
  - `python scripts\html_to_dist.py 2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu\reports\2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_final_review.html --dist 2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu\dist --zip --zip-path 2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu\dist.zip`
- Script result:
  - `[local-ref-check] ok`
- Dist folder:
  - `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu\dist`
- Zip package:
  - `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu\dist.zip`
  - size: 5,572,692 bytes
- Dist verification:
  - local HTTP server on `127.0.0.1:8767`
  - opened `http://127.0.0.1:8767/index.html`
  - title ok
  - 7 figures
  - 7 images
  - broken images: 0
  - Remotion still present
  - SVG present
  - console warnings/errors: 0
  - verification server stopped after check

## Obsidian Mirror

- Saved mirror note:
  - `C:\Users\angpa\Obsidian_Vault\00. Inbox\2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu.md`
- Mirror format:
  - YAML frontmatter
  - TL;DR
  - artifact paths
  - key judgments
  - verification summary
  - source highlights
