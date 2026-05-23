# Research run log

date: 2026-04-28
cwd: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
package: `2026-04-28_exploration-vs-fixation-haico-ai-cocreation`

## 사용자 요구

- AI Matters 기사와 arXiv 논문을 기반으로 리뷰를 진행.
- 기사보다 논문 인사이트, 고민할 지점, 사용자가 AI를 어떻게 활용해야 하는지에 초점.
- 필요 시 외부 소스와 근거를 찾아 논지를 강화하고 audit한 뒤 슬라이드 작성.
- AI스러운 말투를 줄이고, 관련 기준을 AGENTS 및 `.codex` 쪽에 반영.

## 실행

1. 기사 원문과 arXiv abstract/html을 웹으로 확인.
2. 주제 폴더 생성:
   - `2026-04-28_exploration-vs-fixation-haico-ai-cocreation`
3. 원문 보관:
   - `sources/aimatters_40718_article.html`
   - `sources/2512.18388v2_exploration_vs_fixation.pdf`
   - `sources/2512.18388v2_exploration_vs_fixation.html`
   - `sources/2512.18388v2_exploration_vs_fixation.txt`
4. `pdftotext`로 PDF 텍스트 추출.
5. 보강 근거 확인:
   - Wadinambiarachchi et al. 2024, GenAI and design fixation.
   - Doshi and Hauser 2024, individual creativity and collective diversity.
   - Anderson, Shah, Kreminski 2024, LLM ideation homogenization.
   - Stanford d.school summary of Dow et al. parallel prototyping.
   - Parsons et al. 2021, fixation in data visualization design.
6. 말투 기준 확인:
   - OpenAI classifier limitation note.
   - Herbold et al. Scientific Reports 2023.
   - Juzek and Ward arXiv:2412.11385.
   - Geng and Trotta arXiv:2404.08627.
   - VU Amsterdam ALP guide.
7. 운영 규칙 업데이트:
   - `AI_Tech_Review/AGENTS.md`
   - `C:\Users\angpa\AGENTS.md`
   - `C:\Users\angpa\.codex\rules\korean-writing-style.md`
8. Markdown 보고서 HTML companion 생성:
   - `reports/2026-04-28_exploration-vs-fixation_memo.html`
   - `reports/2026-04-28_exploration-vs-fixation_deepresearch.html`
9. 로컬 슬라이드 생성:
   - `skywork_exports/2026-04-28_exploration-vs-fixation_skywork_local_v1.pptx`
   - `skywork_exports/2026-04-28_exploration-vs-fixation_skywork_local_v1.pdf`
   - 생성 스크립트: `artifacts/build_local_exploration_vs_fixation_deck.py`
10. 슬라이드 검증:
   - PPTX slide count: 12
   - PDF page count: 12
   - PDF 렌더링: `artifacts/pdf_render/slide-*.png`
   - PDF text audit에서 금지 말투 패턴은 발견되지 않음.

## GPT deep research 경로

이번 작업은 논문 원문과 보강 논문을 직접 확인해 로컬 패키지로 정리했다. 별도 ChatGPT deep research UI 실행은 하지 않았다. 이유는 다음과 같다.

- 핵심 소스가 모두 공개되어 있고 논문 수치 검증이 로컬 PDF 텍스트에서 가능했다.
- 사용자가 기사 요약보다 논문 인사이트와 말투 기준을 지시해, 외부 UI 생성보다 source-grounded audit가 더 적합했다.
- Skywork 입력용 prompt packet은 별도로 작성해 재실행 가능성을 남긴다.

## 말투 감사

- `A가 아니라 B이다`식 대비 문장을 기본 서술 습관으로 쓰지 않는다.
- `핵심은`, `시사하는 바는`, `결론적으로` 같은 빈 연결어를 줄인다.
- 수치와 제한을 숨기지 않는다.
- 슬라이드 제목은 근거가 있는 판단으로 작성한다.

## Skywork 상태

Skywork live UI 실행은 하지 않았다. 대신 다음을 남겼다.

- Skywork prompt packet: `skywork_inputs/2026-04-28_exploration-vs-fixation_skywork_prompt_v1.md`
- 기본 템플릿 복사본: `skywork_inputs/LGD_Template.pptx`
- 로컬 fallback deck: `skywork_exports/2026-04-28_exploration-vs-fixation_skywork_local_v1.pptx`
- 로컬 fallback PDF: `skywork_exports/2026-04-28_exploration-vs-fixation_skywork_local_v1.pdf`

## Obsidian mirror

다음 파일을 Obsidian mirror root에 복사하고 vault frontmatter를 추가했다.

- `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-04-28_exploration-vs-fixation-haico-ai-cocreation\2026-04-28_exploration-vs-fixation_memo.md`
- `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-04-28_exploration-vs-fixation-haico-ai-cocreation\2026-04-28_exploration-vs-fixation_deepresearch.md`

## OpenProject update state

OpenProject API 확인 중 `HTTP 502 Bad Gateway`가 발생했다.

- attempted endpoint: `https://infant.tailcb5184.ts.net:8443/api/v3`
- live update: pending
- prepared payload: `notes/2026-04-28_exploration-vs-fixation_openproject_update_payload.md`

## Skywork audit update, 2026-04-29

Skywork live generation completion evidence is missing.

- audit command: `python scripts/audit_skywork_package.py 2026-04-28_exploration-vs-fixation-haico-ai-cocreation`
- result: `blocked`
- missing: automation status JSON, Skywork project/viewer URL, non-local Skywork `PPTX`/`PDF` export pair
- local fallback exists: `skywork_exports/2026-04-28_exploration-vs-fixation_skywork_local_v1.pptx`, `skywork_exports/2026-04-28_exploration-vs-fixation_skywork_local_v1.pdf`
- incident note: `notes/2026-04-29_skywork_failure_root_cause_and_recovery.md`

Policy update from 2026-04-29: do not create local replacement decks for Skywork deliverables. If Skywork is blocked, leave the slide state as pending/blocked and record the blocker instead of producing local `PPTX` or `PDF`.
## 2026-04-29 Skywork live retry and export audit

- Skywork project: `https://skywork.ai/project/2049150433118978048?from=home_query&is_new_project=false`
- Template used: `C:\Users\angpa\.codex\skills\skywork-ppt-workflow\assets\LGD_Template.pptx`
- Local replacement deck generation was not used. Earlier local replacement files were moved to `artifacts/historical_local_replacement_deck/` and no new local replacement deck was created.

### Live Skywork versions

- V1 exported from Skywork:
  - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v1.pptx`
  - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v1.pdf`
  - Audit: 12 slides / 12 PDF pages. Rejected for visible title typo and wording drift.
- V2 and V3 correction attempts:
  - Exported as real Skywork PPTX/PDF pairs.
  - Rejected because correction passes degraded some Korean slide text.
- V4 clean rebuild:
  - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v4.pptx`
  - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v4.pdf`
  - Audit: 10 slides / 10 PDF pages. Visual PDF improved, but PPTX text extraction found meaning-changing typos.
- V5 targeted correction:
  - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v5.pptx`
  - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v5.pdf`
  - Also downloaded through preview toolbar:
    - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v5_preview_toolbar.pptx`
    - `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v5_preview_toolbar.pdf`

### Verification result

- `python scripts/audit_skywork_package.py 2026-04-28_exploration-vs-fixation-haico-ai-cocreation` passed live Skywork evidence checks.
- V5 PDF render from Skywork showed corrected visible text on checked pages:
  - `artifacts/skywork_v5_pdf_render/slide-01.png`
  - `artifacts/skywork_v5_pdf_render/slide-02.png`
  - `artifacts/skywork_v5_pdf_render/slide-03.png`
  - `artifacts/skywork_v5_pdf_render/slide-07.png`
- V5 PPTX text extraction and PowerPoint COM export still showed stale text:
  - `낮출수록`
  - `대한 탐색`
  - `낮은 결과`
- PowerPoint-rendered verification PDF:
  - `artifacts/2026-04-29_skywork_v5_pptx_powerpoint_export.pdf`
  - rendered images under `artifacts/skywork_v5_pptx_powerpoint_render/`

### Current handoff status

- Use `skywork_v5.pdf` as the visual review artifact.
- Do not treat the downloaded V5 PPTX as a clean editable handoff until the Skywork PPTX export/cache issue is resolved.
- Do not create a local patched deck as a fallback. If an editable deck is required, retry Skywork export after clearing the project/version cache or use Skywork editor support/export recovery.
