---
title: "Neuromorphic everyday edge AI deep research refresh"
type: research-note
author: "김현중 with Codex Agent | AI Governance Team"
date: 2026-06-21
status: source-refresh
tags:
  - ai-tech-review
  - neuromorphic-computing
  - edge-ai
  - always-on-ai
  - aiot
---

# Neuromorphic everyday edge AI deep research refresh

## 질문

2026-06-21 재작성의 질문은 "뉴로모픽이 왜 필요한가"를 자율주행차 사례가 아니라 생활 가까운 AI 기술에서 설명할 수 있는가였습니다. 검토 초점은 스마트홈 presence sensing, 항상 듣는 오디오, wearable/on-body computing, smart camera/in-sensor vision으로 좁혔습니다.

## 확인한 근거

- [Muir and Sheik 2025, Nature Communications](https://www.nature.com/articles/s41467-025-57352-1): 가까운 상용화 시장을 battery-powered system, local compute for IoT, consumer wearable, audio/visual wake phrase, gesture interaction, condition/anomaly detection으로 제시합니다. 자율주행보다 생활형 always-on sensor AI가 도입부에 더 적합하다는 판단의 핵심 근거입니다.
- [Edge intelligence through in-sensor and near-sensor computing for AIoT, npj Unconventional Computing, 2025](https://www.nature.com/articles/s44335-025-00040-6): AIoT에서 sensor node가 단순 수집기가 아니라 계산 node가 되는 방향을 설명합니다. in-sensor/near-sensor computing, dynamic vision camera, silicon cochlea가 같은 설계 묶음으로 연결됩니다.
- [Socionext and Innatera 60 GHz FMCW radar announcement, 2026](https://www.innatera.com/newsroom/socionext-and-innatera-introduce-integrated-60-ghz-fmcw-radar-and-neuromorphic-edge-ai-for-human-presence-detection/): human presence detection을 sub-milliwatt power level과 3-6배 battery life extension이라는 회사 claim으로 제시합니다. peer-reviewed benchmark가 아니므로 본문에서는 회사 발표 claim으로 제한했습니다.
- [Baek and Lee 2024, SNN and sound review](https://pmc.ncbi.nlm.nih.gov/articles/PMC11362401/): sound recognition에서 SNN이 low-power, low-latency embedded real-time application에 맞는 후보임을 정리합니다. 항상 듣는 AI의 기술적 근거로 사용했습니다.
- [Joya Design and Innatera consumer audio module announcement, 2026](https://www.innatera.com/newsroom/joya-design-takes-neuromorphic-chip-from-design-to-device-with-first-innatera-powered-consumer-audio-product-at-awe-china/): Pulsar 기반 consumer audio product 신호입니다. 제품 발표 자료이므로 성능 결론은 제한했습니다.
- [Li et al. 2026, Nature Electronics](https://www.nature.com/articles/s41928-026-01639-8): on-body edge computing을 위한 stretchable neuromorphic circuit 연구입니다. wearable/patch형 AI에서 센서 가까운 전처리와 분류가 왜 중요한지 설명하는 근거로 사용했습니다.
- [SynSense Speck product page](https://www.synsense.ai/products/speck-2/): Dynamic Vision Sensor와 SNN processor를 single chip으로 묶는 상용 edge vision 신호입니다. 제품 자료이므로 기술 방향 설명에만 사용했습니다.
- [Wang et al. 2026, Nature Communications](https://www.nature.com/articles/s41467-026-68905-3): ScienceTimes 기사의 대상 논문입니다. MoS2 optoelectronic LIF neuron과 HZO/MoS2 FeFET synapse를 통합한 in-sensor neuromorphic vision 연구로, 생활형 smart camera/in-sensor vision 논지의 핵심 논문으로 재배치했습니다.

## 재작성 insight

1. 자율주행차는 뉴로모픽의 필요성을 설명하기에 너무 큰 시스템입니다. 안전 검증, fleet data, dense perception, 규제 문제가 섞여서 독자가 "뉴로모픽이 테슬라를 대체해야 하나"라는 잘못된 질문으로 이동하기 쉽습니다.
2. 뉴로모픽의 가까운 강점은 "더 깊게 생각하는 능력"이 아니라 "오래 깨어 있다가 작은 event를 낮은 전력으로 잡는 능력"입니다.
3. 스마트홈 radar, 오디오 wake/event detection, wearable biosignal, smart camera privacy filtering은 모두 데이터 이동, 배터리, privacy, latency가 함께 제약으로 등장합니다.
4. 생활형 AI 관점에서는 뉴로모픽을 LLM의 후계자가 아니라 wake-up layer, event gate, sensor-near low-power classifier로 설명하는 편이 더 정확합니다.
5. 생성 이미지는 제품 사진이나 논문 장치로 오해되면 안 됩니다. 새 hero image는 "생활형 always-on edge AI"의 문제를 여는 편집 일러스트로만 사용하고, 근거는 본문 링크와 deterministic SVG에 둡니다.

## 본문 반영

- 제목을 `뉴로모픽, 항상 켜진 AI의 감각층`으로 변경했습니다.
- 도입부를 스마트홈, 이어버드, 웨어러블, smart camera의 always-on cost로 재작성했습니다.
- 자율주행차, Tesla FSD, NHTSA, Boston Dynamics/Atlas 섹션과 참고문헌을 제거했습니다.
- 새 hero image `neuromorphic_everyday_ai_hero-web.png`를 생성해 대표 그림으로 교체했습니다.
- `항상 켜진 AI의 시간`, `가까운 네 가지 장면` 섹션을 추가했습니다.
- 작성 정보와 figure manifest를 2026-06-21 재작성 기준으로 갱신했습니다.
