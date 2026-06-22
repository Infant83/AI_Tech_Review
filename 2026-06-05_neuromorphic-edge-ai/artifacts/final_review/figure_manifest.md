---
title: "뉴로모픽 Edge AI figure manifest"
type: figure-manifest
author: "김현중"
date created: 2026-06-05
date modified: 2026-06-23
status: reviewed
tags:
  - ai-tech-review
  - figure-manifest
  - neuromorphic-computing
---

# 뉴로모픽 Edge AI figure manifest

| Figure | File | Purpose | Tool | Source/Reference | Review Notes |
|---|---|---|---|---|---|
| Figure 1 | `figures/imagegen/neuromorphic_everyday_ai_hero-web.png` | 생활형 센서가 작은 이벤트만 local edge chip으로 보내고, 의미 있는 신호만 상위 시스템으로 올리는 always-on event gate hero | OpenAI imagegen | Muir & Sheik 2025, AIoT in/near-sensor review, Innatera/Socionext/Joya/SynSense public signals | 2026-06-22 재생성. cloud icon과 과한 beam을 제거하고 local chip 중심 구도로 채택 |
| Figure 2 | `figures/neuromorphic_edge_stack.svg` | 생활형 센서 AI에서 감각 계층, neuromorphic edge layer, NPU/GPU, LLM/Agent의 역할 분리 | deterministic SVG | Nature/Nature Communications neuromorphic reviews, AIoT in/near-sensor review | 2026-06-23 재편집. 하단 문장 넘침을 제거하고 큰 계층 메시지 중심으로 단순화 |
| Figure 3 | `figures/imagegen/neuromorphic_sensor_time_section-web.png` | 뉴로모픽이 의미를 갖는 “항상 켜진 시간”을 생활 공간의 센서, edge chip, 상위 장치 흐름으로 보여주는 section illustration | OpenAI imagegen | Always-on sensing, event-driven AI, low-power wake-up layer 논의 | 2026-06-23 추가. 성능 검증 이미지가 아니라 생활형 맥락을 여는 editorial illustration |
| Figure 4 | `figures/neuromorphic_in_sensor_boundary.svg` | 기존 camera path와 in-sensor neuromorphic path를 비교해 계산 위치가 센서 쪽으로 당겨지는 메시지 설명 | deterministic SVG | Wang et al. 2026 target paper, AIoT in/near-sensor review | 2026-06-23 재편집. 작은 논문식 라벨을 줄이고 기존 경로 vs in-sensor 경로의 두 단 구조로 정리 |
| Figure 5 | `figures/imagegen/neuromorphic_mos2_lab_section-web.png` | MoS2 박막 소자 위의 빛, spike-like signal, synapse array를 실험실 장면으로 연결하는 section illustration | OpenAI imagegen | Wang et al. 2026 target paper | 2026-06-23 추가. 논문 실험의 분위기와 초점을 보여주는 편집 이미지이며 성능 검증 자료로 쓰지 않음 |
| Figure 6 | `figures/in_sensor_neuromorphic_vision.svg` | Wang et al. 2026 논문의 MoS2 LIF neuron, rate/TTFS coding, FeFET synapse, 작은 SNN 흐름 설명 | deterministic SVG | Nature Communications 2026 target paper | 제품 과장 없이 기능 단위를 간결하게 연결 |
| Figure 7 | `figures/neuromorphic_workload_fit.svg` | 뉴로모픽에 적합한 workload, 보완 workload, 아직 맞지 않는 workload 비교 | deterministic SVG | Muir & Sheik 2025, NeuroBench, edge-oriented SNN review | LLM replacement overclaim을 피하고 event layer 관점을 유지 |
| Figure 8 | `figures/neuromorphic_edge_commercialization_map.svg` | radar/audio/event vision/wearable sensing으로 모이는 상용화 신호와 근거 수준 분리 | deterministic SVG | Innatera, SynSense, BrainChip announcements/product pages plus Nature Communications 2025 review | 2026-06-22 교체. 분위기형 데스크 이미지를 source-aware commercialization map으로 변경 |
| Figure 9 | `figures/neuromorphic_maturity_timeline.svg` | 2023-2026 research/commercial maturity signal timeline | deterministic SVG | IBM NorthPole, Intel Hala Point, Nature reviews, 2026 papers | 상용 발표와 peer-reviewed source를 분리해서 표시 |

## 검토 메모

- 본문 최종 그림 수는 9개다. OpenAI `imagegen` illustration 3장과 deterministic SVG 설명도 6장으로 구성했다.
- Figure 3과 Figure 5는 2026-06-23 사용자 요청에 따라 추가했다. 두 그림 모두 제품 검증 또는 성능 테스트 자료가 아니라, 본문 메시지를 여는 editorial illustration으로 캡션에서 용도를 제한했다.
- Figure 2, Figure 4, Figure 6, Figure 7은 Playwright screenshot으로 desktop/mobile 렌더링을 확인했다. 2026-06-23 재검증에서 `figureCount: 9`, `imageCount: 9`, `brokenImages: []`, mobile body overflow `0px`를 확인했다.
- Figure 2와 Figure 4는 작은 설명 문장이 프레임에 닿거나 모바일에서 읽히지 않는 문제가 있어 라벨을 크게 키우고 문장을 줄였다.
- 본문에서 각 figure를 설명하고, figure만으로 과장된 결론을 만들지 않도록 caption을 제한했다.
- 배포본 생성 시 imagegen PNG, SVG, HTML local references를 모두 flat `dist/` 안에 포함하고 local-ref check를 통과해야 한다.

## 본문 제외 후보

| File | Reason |
|---|---|
| `figures/imagegen/neuromorphic_in_sensor_vision_editorial-web.png` | 빛, spike, synapse 분위기는 있으나 센서-연산 경계 이동 메시지가 약해 Figure 4에서 제외 |
| `figures/imagegen/neuromorphic_edge_commercialization_editorial-web.png` | 상용화 신호보다 연구 데스크 분위기가 강해 Figure 8에서 제외 |
