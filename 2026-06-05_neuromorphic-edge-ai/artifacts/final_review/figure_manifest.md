---
title: "뉴로모픽 Edge AI figure manifest"
type: figure-manifest
author: "김현중"
date created: 2026-06-05
date modified: 2026-06-21
status: reviewed
tags:
  - ai-tech-review
  - figure-manifest
  - neuromorphic-computing
---

# 뉴로모픽 Edge AI figure manifest

| Figure | File | Purpose | Tool | Source/Reference | Review Notes |
|---|---|---|---|---|---|
| Figure 1 | `figures/imagegen/neuromorphic_everyday_ai_hero-web.png` | 스마트홈, 오디오, 웨어러블, smart camera가 작은 local chip과 연결되는 생활형 always-on edge AI 대표 이미지 | OpenAI imagegen | Concept grounded in Muir & Sheik 2025, AIoT in/near-sensor review, Innatera/Socionext/Joya/SynSense public signals | 생성 일러스트. 특정 논문 장치나 회사 제품 사진이 아니며 증거로 쓰지 않음 |
| Figure 2 | `figures/neuromorphic_edge_stack.svg` | cloud/LLM layer와 neuromorphic edge layer의 역할 분리 | deterministic SVG | Nature/Nature Communications neuromorphic reviews, AIoT in/near-sensor review | Korean labels controlled directly in SVG |
| Figure 3 | `figures/imagegen/neuromorphic_in_sensor_vision_editorial-web.png` | 빛, spike, synapse 흐름을 감각적으로 설명 | OpenAI imagegen | Wang et al. 2026 target paper | 생성 일러스트. 실제 장치 사진이 아니며 Figure 4와 논문 원문으로 근거 확인 |
| Figure 4 | `figures/in_sensor_neuromorphic_vision.svg` | Wang et al. 2026 논문의 MoS2 PT, HZO/FeFET, SNN 흐름 설명 | deterministic SVG | Nature Communications 2026 target paper | 성능 수치를 simulation/lab-scale caveat와 함께 배치 |
| Figure 5 | `figures/neuromorphic_workload_fit.svg` | 뉴로모픽에 적합한 workload와 아직 맞지 않는 workload 비교 | deterministic SVG | Muir & Sheik 2025, NeuroBench, edge-oriented SNN review | LLM replacement overclaim을 피하도록 구성 |
| Figure 6 | `figures/imagegen/neuromorphic_edge_commercialization_editorial-web.png` | research board에서 radar/audio/wearable/smart camera로 이동하는 상용화 신호 설명 | OpenAI imagegen | Innatera, SynSense, BrainChip company announcements plus Nature Communications 2025 review | 생성 일러스트. 회사 발표 claim과 peer-reviewed evidence를 분리해 캡션 처리 |
| Figure 7 | `figures/neuromorphic_maturity_timeline.svg` | 2023-2026 research/commercial maturity signal timeline | deterministic SVG | IBM NorthPole, Intel Hala Point, Nature reviews, 2026 papers | 상용 발표와 peer-reviewed source를 분리해서 표시 |

## 검토 메모

- Figure 1, 3, 6은 OpenAI imagegen 생성 일러스트다. 본문 캡션에서 생성 이미지임을 밝혔고, 실제 논문 장치나 회사 제품 사진으로 해석하지 않도록 제한했다.
- Figure 2, 4, 5, 7은 deterministic SVG다. 라벨과 관계는 본문 근거에 맞춰 직접 통제했다.
- 본문에서 각 figure를 설명하고, figure만으로 과장된 결론을 만들지 않도록 caption을 제한했다.
- 배포본 생성 시 imagegen PNG, SVG, HTML local references를 모두 flat `dist/` 안에 포함하고 local-ref check를 통과해야 한다.
