---
title: "Figure Manifest - TabPFN OLED AI Tech Review Letters"
date: 2026-05-21
slug: tabpfn-oled-manufacturing-foundation-model
status: active
---

# Figure Manifest

| Figure | File | Purpose | Tool / Route | Prompt Summary | Review Notes |
|---|---|---|---|---|---|
| Figure 1 | `figures/tabpfn_oled_hero_imagegen.png` | 웹진 hero. OLED 후보, 표 데이터, 실험 queue를 한 장면으로 열기 | OpenAI imagegen | OLED research desk, OLED panel sample, molecule cards, tabular matrix, prediction instrument sorting candidates | 채택. 가짜 로고와 긴 텍스트 없음. 제목 overlay 여백 충분. |
| Figure 2 | `figures/tabpfn_pretraining_context_generalization.svg` | 모델 제작 단계의 pretraining과 사용자 적용 단계의 fit/predict를 구분 | Deterministic SVG | model development -> released fixed weights -> user-time labeled/query rows -> y prediction with uncertainty | 2026-05-21 재작성. 1400x780 캔버스의 3단 구조로 구성하고, 하단은 `하는 일/하지 않는 일` 구분 대신 `사전학습 prior`, `사용 시 context`, `예측 출력`의 작동 특징으로 정리했다. 정확한 한국어 라벨과 표 표현이 필요해 deterministic SVG로 유지. |
| Figure 3 | `figures/tabpfn_oled_data_junction_imagegen.png` | 세 데이터 흐름이 표 데이터 접점으로 모이는 editorial infographic | OpenAI imagegen | molecular cards, device stack, manufacturing recipe / inspection tiles converging into sorting prism | 채택. 2026-05-21 OLED 계산 역설계 세부 내용을 후속 노트로 분리한 뒤 Figure 3으로 번호 조정. 내부 숫자 배지는 사실 claim이 아니며 caption으로 역할을 제한. |

## Archived / Not Used In Current Body

| File | Reason |
|---|---|
| `figures/tabpfn_in_context_prediction.svg` | 2026-05-17 Figure 2를 더 직관적인 imagegen+SVG hybrid로 교체하면서 본문에서 제외. |
| `figures/tabpfn_qchem_provenance_gate.svg` | 계산화학 provenance 메시지를 본문 문단과 compact table로 낮추면서 본문에서 제외. SVG 자체는 archive로 보존. |
| `figures/tabpfn_context_learning_bridge.svg` | 외부 SVG 안에서 base PNG를 참조하는 방식은 HTML `<img>` 렌더링에서 base image가 보이지 않아 본문에서 제외. 현재 본문은 base PNG와 inline SVG overlay를 직접 사용. |
| `figures/tabpfn_context_learning_bridge_base.png` | 2026-05-18 Figure 2를 pretraining/generalization 질문에 맞춘 deterministic SVG로 교체하면서 본문에서 제외. |
| `figures/tabpfn_context_learning_bridge_base-web.png` | 위와 같은 이유로 본문에서 제외. |
| `figures/tabpfn_adoption_boundary.svg` | 2026-05-21 사용자 피드백에 따라 `회사 PoC와 업무 판단 경계` 섹션을 삭제하면서 본문에서 제외. 라이선스 메시지는 본문 한 문단으로 최소화. |
| `figures/tabpfn_inverse_design_filter.svg` | 2026-05-21 OLED 계산 역설계 세부 내용을 후속 리뷰 노트로 분리하면서 본문에서 제외. 후속 노트 `notes/2026-05-21_tabpfn-qchem-inverse-design_followup.md`에서 재사용 후보로 보존. |

## Imagegen Prompts

### Figure 1 Hero

```text
Editorial science-and-technology magazine hero illustration for a Korean webzine article about TabPFN and OLED manufacturing intelligence. Show a clean OLED research desk and pilot-line control surface: a thin glowing OLED panel sample, a small stack of molecule cards, a spreadsheet-like tabular matrix made of small paper tiles, and a compact prediction instrument sorting candidate cards into a narrow experiment queue. The scene should communicate: tabular foundation models help choose which expensive OLED material or process experiments deserve the next step. Warm white background, restrained ink, muted teal and deep red accents, soft paper texture, high-end science magazine illustration, no readable text, no logos, no brand marks, no fake UI labels, no neural-network cloud, no photorealistic stock style. Leave quiet negative space in the upper-left for article title overlay.
```

### Figure 3 Data Junction

```text
Editorial infographic-style illustration without readable text for a Korean technology review about TabPFN as a tabular junction in OLED R&D and manufacturing. Show three streams converging into one quiet analytic table: molecular structure cards and quantum-calculation sheets from the left, OLED device stack samples and measurement traces from the center, and manufacturing recipe / inspection tiles from the right. At the convergence point, a compact transparent sorting prism ranks a few candidate cards toward DFT, device experiment, and pilot-line check trays. Clean white background, restrained magazine science style, muted teal, graphite, small deep red accents, crisp hierarchy, no long labels, no logos, no fake text, no corporate stock-photo feeling, no abstract AI cloud. Leave enough margin so exact Korean labels can be added later in HTML/SVG if needed.
```

## Skywork Image Status

Skywork Image는 이번 리뷰에서 `one-cut editorial infographic`, `poster-like section opener`, `social card` 후보로 적합하다고 판단했다. 다만 현재 세션에는 직접 실행 가능한 Skywork Image tool이 노출되어 있지 않아 실제 export 파일을 본문에 삽입하지 않았다. 실제 Skywork Image 실행용 프롬프트는 `skywork_inputs/2026-05-07_tabpfn-oled-manufacturing-foundation-model_skywork_image_prompt_pack.md`에 보관했다. Workspace 규칙에 따라, 실제 PNG export와 project/artifact URL이 확보되기 전에는 Skywork 생성 이미지를 본문 figure로 표기하지 않는다.
