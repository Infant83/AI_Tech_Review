---
title: "Research Runlog - D-Wave 분자 역설계 벤치마크"
date: 2026-08-27
slug: dwave-molecular-inverse-design-benchmark
language: ko
status: runlog
---

# Research Runlog - D-Wave 분자 역설계 벤치마크

## Run Summary

- 작업일: 2026-08-27 KST
- 패키지: 2026-08-27_dwave-molecular-inverse-design-benchmark
- 시작 입력: upstream inverse-design PoC의 real-molecule evidence package
- 공개 계산 앵커: artifacts/final_review/data/benchmark_results.csv
- 설명 원고: reports/2026-08-27_dwave-molecular-inverse-design-benchmark_final_review.md
- figure provenance: artifacts/final_review/figure_manifest.md
- 목표: 계산 결과와 파이프라인을 AI Tech Review 기사, 상세 인포그래픽, 12장 Skywork 발표자료로 정리

## Evidence Reconciliation

1. QM9 derived subset과 split 수를 확인했습니다.
   - total 5,000
   - train 4,058
   - validation 511
   - test 431
2. 동일 test split의 surrogate 결과를 분리했습니다.
   - Chemprop D-MPNN ensemble MAE 0.5308 eV
   - ExtraTrees/Morgan MAE 0.4743 eV
3. 세 생성 경로의 공통 화학 필터 결과를 확인했습니다.
   - governed union 30
   - unique contribution 11 / 8 / 11
4. frozen acquisition BQM을 확인했습니다.
   - 18 variables
   - 153 quadratic interactions
   - batch size 3
5. optimizer별 결과를 대조했습니다.
   - independent exact energy -0.480789127750
   - classical simulated annealing은 exact batch와 일치
   - QPU best energy -0.434455351273
   - QPU exact gap +0.046333776477
6. PySCF 결과를 배치 평균과 단일 best hit로 나눠 기록했습니다.
   - exact batch 3/3 converged, mean target error 0.620 eV
   - QPU batch 3/3 converged, mean target error 0.761 eV
   - QPU batch best single target error 0.119 eV
7. fixed-pool replay의 실행 경계를 확인했습니다.
   - random 0.2813 eV
   - greedy 0.1298 eV
   - exact/QUBO-SA 0.1261 eV
   - QUBO-SA exact batch match 12/12
   - new DFT 0, QPU calls 0, generated-space expansions 0

## Editorial and Figure Decisions

| Decision | Result |
| --- | --- |
| QPU role | 분자 전자구조 계산이 아닌 세 후보 acquisition batch 선택으로 고정 |
| QUBO energy wording | molecular energy가 아닌 acquisition score로 고정 |
| DFT wording | fixed-geometry B3LYP/6-31G(2df,p) Kohn–Sham orbital gap으로 고정 |
| QPU claim | path executed, exact optimum not reproduced |
| DFT interpretation | exact batch의 mean error가 낮고 QPU batch에 best single hit가 있었음을 분리 |
| Replay wording | fixed QM9 pool의 precomputed-label proxy |
| Live loop | 실행 결과와 분리하고 모든 슬라이드에서 PROPOSED로 표시 |
| Hero | 주제형 illustration. 실제 장비·분자 발견·계산 screenshot으로 표현하지 않음 |
| Detailed infographic | deterministic SVG. 실선은 실행, 점선은 제안 |

## Artifact Log

| Artifact | Status |
| --- | --- |
| reports/..._final_review.md | prepared |
| artifacts/final_review/data/benchmark_results.csv | prepared |
| artifacts/final_review/figure_manifest.md | prepared |
| artifacts/final_review/figures/molecular_inverse_design_hero.png | prepared and reviewed |
| artifacts/final_review/figures/molecular_inverse_design_infographic.svg | prepared and reviewed |
| notes/..._sources.md | created |
| notes/..._research_runlog.md | created |
| reports/..._memo.md | created |
| reports/..._deepresearch.md | created |
| skywork_inputs/LGD_Template.pptx | present |
| skywork_inputs/..._skywork_prompt_v1.md | created |
| skywork_inputs/..._skywork_automation_status.json | created as prepared_not_submitted |
| skywork_exports/*.pptx | not generated at this checkpoint |
| skywork_exports/*.pdf | not generated at this checkpoint |
| Skywork project/viewer URL | not created at this checkpoint |

## Skywork Handoff

Skywork 제출 전에 아래 파일을 source pack으로 사용합니다.

1. LGD_Template.pptx
2. reports/..._final_review.md
3. reports/..._memo.md
4. reports/..._deepresearch.md
5. notes/..._sources.md
6. artifacts/final_review/data/benchmark_results.csv
7. artifacts/final_review/figure_manifest.md
8. artifacts/final_review/figures의 hero, infographic, 02–07 charts

완료 조건은 다음 세 가지입니다.

- 실제 Skywork project/viewer URL
- 편집 가능한 PPTX export
- 같은 deck의 PDF export

이 runlog 작성 시점에는 Skywork를 실행하지 않았습니다. 제출 전 상태는 skywork_inputs/..._skywork_automation_status.json에 prepared_not_submitted로 기록했습니다.

## Known Limits

- QPU 결과는 100 reads의 단일 submission입니다.
- QPU 기록에는 실행 timestamp, 제출 시점 Python/Ocean version, source hash, solver timing unit을 고정한 별도 configuration record가 없습니다.
- Chemprop ensemble spread는 calibration되지 않았고 매우 작아 uncertainty term은 탐색용 proxy입니다.
- generator timing은 matched training-cost benchmark가 아닙니다.
- DFT는 force-field geometry의 single point이며 optical excitation, geometry optimization, stability, synthesis, toxicity, experiment를 포함하지 않습니다.
- exact와 QPU의 DFT batch는 각각 세 분자로, optimizer 우열을 일반화할 표본이 아닙니다.
- replay는 persistent ledger와 generated-space retraining을 실행하지 않았습니다.

## Next Verification

1. 최종 리뷰의 Markdown·HTML rendering과 local reference를 검사합니다.
2. Skywork에 template과 source pack을 업로드합니다.
3. 12장 구조, 정량 수치, PROPOSED 표시를 시각적으로 확인합니다.
4. Skywork project/viewer URL과 PPTX·PDF export를 status JSON과 runlog에 기록합니다.
5. 공개 배포본에서는 credential, account identifier, private solver 정보, raw QM9 mirror가 없는지 다시 검사합니다.

## Skywork Execution and Visual QA — 2026-08-27

Skywork API를 LGD template imitation mode로 실행하고 모든 source pack을 원격 업로드했습니다.

| Version | Skywork result | Visual QA | Publication decision |
| --- | --- | --- | --- |
| v1 | 12-slide PPTX export 성공 | slide 4, 6, 7, 9에 깨진 문장, 발명된 분자, 잘못된 수치 확인 | rejected; publish 금지 |
| v2 | 9개 slide를 Skywork edit mode로 재생성하고 12-slide export 성공 | QPU energy, DFT molecule/value, replay chart, conclusion 오류 잔존 | rejected; publish 금지 |
| v3 | 11개 slide를 exact reviewed PNG 한 장씩으로 교체 | remote export 단계에서 180-second timeout | no deliverable; retry 승인 필요 |

v1과 v2는 PowerPoint로 각각 1600×900 PNG 12장을 렌더링하고 contact sheet로 검사했습니다. 두 버전 모두 `Skywork가 export했다`는 형식 조건은 만족했지만, 계산 사실성 기준을 만족하지 못했습니다. 따라서 PPTX/PDF를 공개 site package에 포함하지 않습니다.

v3용으로 다음 exact slide assets를 만들고 시각 검사했습니다.

- `artifacts/final_review/figures/slide_assets/01_snapshot.png`
- `artifacts/final_review/figures/slide_assets/05_qubo.png`
- `artifacts/final_review/figures/slide_assets/10_evidence.png`
- `artifacts/final_review/figures/slide_assets/12_decision.png`

나머지 결과 slide에는 검토된 `01`–`07` figure를 그대로 지정했습니다. Skywork는 11개 교체 slide 생성을 완료했으나, 최종 export 서버가 timeout됐습니다. 동일 작업의 자동 재시도는 하지 않았습니다.

현재 Skywork web session은 로그인되지 않아 project/viewer URL을 만들 수 없었습니다. API가 반환한 download URL은 project/viewer URL을 대신하지 않으므로 공식 완료 조건은 `blocked_after_skywork_qa`로 기록합니다.

기사, 상세 인포그래픽, 계산 CSV는 Skywork deck과 독립적으로 검증됐으므로 public article package는 계속 게시합니다.

## Publication Tracking

- Obsidian mirror: final review, memo, deep research, sources, runlog를 `AI_Tech_Review/2026-08-27_dwave-molecular-inverse-design-benchmark/`에 복사했습니다.
- OpenProject: 인증 변수는 존재했지만 canonical API endpoint가 HTTP 502를 반환해 사용자·project 조회 단계에서 중단했습니다. 대상 work package를 식별하지 못했으므로 mutation은 수행하지 않았습니다.

## Final Render QA — 2026-08-27

- Final-review HTML renderer에 MathJax 3.2.2를 고정하고, 내려받은 bundle의 SHA-384 SRI와 `crossorigin="anonymous"`를 적용했습니다.
- Desktop viewport 1440 px에서 document width 1440/1440, mobile viewport 390 px에서 390/390으로 page-level overflow가 없었습니다.
- MathJax container 6개가 렌더링됐습니다. 긴 QUBO 식은 mobile에서 수식 영역 내부 스크롤로 제한했습니다.
- 공개 review의 broken image는 0개, browser console error는 0개였고 CSV와 full-size infographic 링크를 확인했습니다.
- `dist.zip`은 13개 공개 파일만 포함하며 rejected Skywork deck과 log는 포함하지 않습니다.

## Publication Result — 2026-08-27

- Content commit: `31fead94b0db36ca25bfdf6734ab8754bfeec3ff`
- Public URL: `https://infant83.github.io/AI_Tech_Review/reviews/2026-08-27_dwave-molecular-inverse-design-benchmark/`
- GitHub Actions run `32996770960` completed successfully and updated `gh-pages` to `739154c467d733bdfcae9cc3890e4d58c42003e4`.
- Live GitHub Pages returned HTTP 200. The article rendered 6 MathJax containers and 8 images with no broken image or page-level desktop/mobile overflow.
- The pre-existing public-metrics endpoint `infant83-public-metrics.infant83.workers.dev` returned DNS NXDOMAIN during live QA. Article content and assets are unaffected, but view/read-time counters may remain unavailable until that separate Worker endpoint is restored.
