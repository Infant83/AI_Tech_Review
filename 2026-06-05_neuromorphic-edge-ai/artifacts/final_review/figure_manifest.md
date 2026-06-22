---
title: "뉴로모픽 Edge AI figure manifest"
type: figure-manifest
author: "김현중"
date created: 2026-06-05
date modified: 2026-06-22
status: reviewed
tags:
  - ai-tech-review
  - figure-manifest
  - neuromorphic-computing
---

# 뉴로모픽 Edge AI figure manifest

| Figure | File | Purpose | Tool | Source/Reference | Review Notes |
|---|---|---|---|---|---|
| Figure 1 | `figures/imagegen/neuromorphic_everyday_ai_hero-web.png` | 생활형 센서가 작은 이벤트만 local edge chip으로 보내고, 의미 있는 신호만 상위 시스템으로 올리는 always-on event gate hero | OpenAI imagegen | Concept grounded in Muir & Sheik 2025, AIoT in/near-sensor review, Innatera/Socionext/Joya/SynSense public signals | 2026-06-22 재생성. cloud icon과 과한 beam을 제거하고 local chip 중심 구도로 채택 |
| Figure 2 | `figures/neuromorphic_edge_stack.svg` | cloud/LLM layer와 neuromorphic edge layer의 역할 분리 | deterministic SVG | Nature/Nature Communications neuromorphic reviews, AIoT in/near-sensor review | Korean labels controlled directly in SVG |
| Figure 3 | `figures/neuromorphic_in_sensor_boundary.svg` | 기존 camera path와 in-sensor neuromorphic path를 비교해 계산 위치가 센서 쪽으로 당겨지는 메시지 설명 | deterministic SVG | Wang et al. 2026 target paper, AIoT in/near-sensor review | 2026-06-22 교체. 기존 imagegen 컷은 메시지가 implicit해 본문 제외 |
| Figure 4 | `figures/in_sensor_neuromorphic_vision.svg` | Wang et al. 2026 논문의 MoS2 PT, HZO/FeFET, SNN 흐름 설명 | deterministic SVG | Nature Communications 2026 target paper | 성능 수치를 simulation/lab-scale caveat와 함께 배치 |
| Figure 5 | `figures/neuromorphic_workload_fit.svg` | 뉴로모픽에 적합한 workload와 아직 맞지 않는 workload 비교 | deterministic SVG | Muir & Sheik 2025, NeuroBench, edge-oriented SNN review | LLM replacement overclaim을 피하도록 구성 |
| Figure 6 | `figures/neuromorphic_edge_commercialization_map.svg` | radar/audio/event vision/wearable sensing으로 모이는 상용화 신호와 근거 수준 분리 | deterministic SVG | Innatera, SynSense, BrainChip announcements/product pages plus Nature Communications 2025 review | 2026-06-22 교체. 분위기형 데스크 이미지를 source-aware commercialization map으로 변경 |
| Figure 7 | `figures/neuromorphic_maturity_timeline.svg` | 2023-2026 research/commercial maturity signal timeline | deterministic SVG | IBM NorthPole, Intel Hala Point, Nature reviews, 2026 papers | 상용 발표와 peer-reviewed source를 분리해서 표시 |

## 검토 메모

- Figure 1은 OpenAI imagegen hero다. 본문에서는 생성 로그가 아니라 메시지 중심 캡션으로 처리하고, 생성 사실과 채택 기록은 이 manifest에 둔다.
- Figure 3과 Figure 6은 2026-06-22 artwork revision에서 deterministic SVG로 교체했다. 정확한 메시지, 근거 수준, 한국어 라벨을 이미지 모델에 맡기지 않기 위한 조치다.
- Figure 2, 3, 4, 5, 6, 7은 deterministic SVG다. 라벨과 관계는 본문 근거에 맞춰 직접 통제했다.
- 본문에서 각 figure를 설명하고, figure만으로 과장된 결론을 만들지 않도록 caption을 제한했다.
- 모바일 렌더링에서는 SVG가 좌우로 잘려 보이지 않도록 본문 figure에 `figure-panel-fit` 클래스를 적용했다. 세부 라벨보다 전체 메시지와 캡션을 먼저 보이게 하는 쪽을 선택했다.
- 배포본 생성 시 imagegen PNG, SVG, HTML local references를 모두 flat `dist/` 안에 포함하고 local-ref check를 통과해야 한다.

## 본문 제외 후보

| File | Reason |
|---|---|
| `figures/imagegen/neuromorphic_in_sensor_vision_editorial-web.png` | 빛, spike, synapse 분위기는 있으나 센서-연산 경계 이동 메시지가 약해 Figure 3에서 제외 |
| `figures/imagegen/neuromorphic_edge_commercialization_editorial-web.png` | 상용화 신호보다 연구 데스크 분위기가 강해 Figure 6에서 제외 |
