---
title: "뉴로모픽 Edge AI 리뷰 - source note"
type: source-note
author: "김현중"
date created: 2026-06-05
date modified: 2026-06-05
status: draft
tags:
  - ai-tech-review
  - neuromorphic-computing
  - edge-ai
  - physical-ai
  - in-sensor-computing
---

# 뉴로모픽 Edge AI 리뷰 - source note

## 검토 범위

- 사용자 제공 기사: [사이언스타임즈, 「로봇의 눈이 스스로 생각도 하는 뉴로모픽 비전」, 2026-03-04](https://www.sciencetimes.co.kr/nscvrg/view/menu/250?nscvrgSn=261508&searchCategory=222)
- 대상 논문: [Wang et al., "Homogeneous integration of two-dimensional material-based optoelectronic neurons and ferroelectric synapses for neuromorphic vision", Nature Communications, 2026-02-09](https://www.nature.com/articles/s41467-026-68905-3)
- 확장 주제: physical AI, agentic AI, edge AI, on-device intelligence, 대안적 AI 하드웨어, 뉴로모픽 컴퓨팅의 상용화 가능성
- 작성 목표: AI Tech Review Letters 스타일의 한국어 기술동향 리포트

## 원 기사 확인

사이언스타임즈 기사는 2026년 CES의 피지컬 AI 분위기에서 출발해 로봇/자율주행 시스템의 시각 처리 지연과 전력 문제를 설명한다. 핵심 연결은 다음과 같다.

- 기존 카메라-프로세서 분리 구조는 센서 데이터 전송, 중앙 처리, 결과 반환 과정에서 지연과 전력 낭비가 생긴다.
- 뉴로모픽 반도체는 계산과 저장을 같은 자리에서 처리하는 뇌의 구조를 모사한다.
- Nature Communications 논문은 MoS2 기반 광전자 LIF neuron과 MoS2/HZO ferroelectric synapse를 같은 기판에 통합해 in-sensor SNN을 시연했다.
- 기사에서 인용한 성능 수치인 색상 인식 91.7%, 객체 검출 93.5%는 Nature Communications 논문 초록과 본문에서 확인된다.

claim status:

- `confirmed`: 기사에 링크된 논문 제목, 저널, 핵심 소자 구조, rate coding/TTFS coding, 91.7%/93.5% 수치.
- `caution`: "로봇의 눈이 스스로 생각한다"는 표현은 대중적 비유다. 실제 논문은 센서-시냅스 통합 하드웨어와 SNN 시뮬레이션을 보여준 실험실 규모의 장치다.
- `caution`: 상용 edge AI 또는 LLM 대체 가능성은 해당 논문 하나에서 직접 결론 낼 수 없다. 리뷰 논문, 상용 제품, 벤치마크 자료를 함께 봐야 한다.

## 대상 논문 확인

논문 정보:

- title: "Homogeneous integration of two-dimensional material-based optoelectronic neurons and ferroelectric synapses for neuromorphic vision"
- journal: Nature Communications 17, Article 2538 (2026)
- published: 2026-02-09
- authors: Jiarong Wang, Keqin Liu, Pek Jun Tiw, ... Yuchao Yang
- DOI: `10.1038/s41467-026-68905-3`

핵심 구조:

- MoS2 phototransistor를 광전자 LIF neuron으로 사용한다.
- HZO ferroelectric layer를 이용한 MoS2 FeFET가 비휘발성 synapse weight storage 역할을 한다.
- optoelectronic neuron과 ferroelectric synapse를 homogeneous MoS2 platform 위에 통합한다.
- rate coding과 time-to-first-spike (TTFS) coding을 함께 사용한다.
- 실험적 하드웨어 규모는 1 x 4 phototransistor array와 4 x 4 FeFET array로 작다.
- 색상 인식과 객체 검출은 integrated hardware dynamics를 바탕으로 한 SNN system simulation 성격이 강하다.

논문이 주장하는 기여:

- multispectral optical sensing
- capacitor-less membrane potential integration
- threshold-triggered spiking with automatic reset
- volatile optical encoding과 non-volatile weight storage의 통합
- 색상 인식 91.7%, 객체 검출 93.5%

논문이 직접 인정하는 제한:

- current hardware limitations 때문에 RGB color classification은 simulation으로 검증했다.
- system scale과 energy efficiency는 mature neuromorphic platforms 대비 개선 영역으로 남아 있다.
- 2D material-based neuromorphic devices의 potential과 limitations는 supplementary discussion에 별도 분석되어 있다.

리포트에서의 해석:

- 이 논문은 "뉴로모픽이 LLM을 대체한다"는 논문이 아니라, physical AI의 시각 지능에서 센서와 계산의 경계를 당겨오는 연구다.
- 중요한 점은 성능 수치 자체보다 센서, spike encoding, synaptic weight storage를 같은 소자/기판 계열에서 묶으려는 방향이다.
- 피지컬 AI 로봇의 빠른 반응, 항상 켜진 감지, 저전력 인식에서는 이 구조가 매우 강한 신호다.

## 신뢰도 높은 리뷰/전망 자료

### 2026-06-05 추가 검색 및 근거 audit

- 사용자의 재요청에 따라 최신 리뷰/산업 신호를 추가 검색했다.
- 추가 검색의 목적은 다음 네 가지였다.
  - 기존 final_review의 링크가 부족한 주장 보강
  - 생성 이미지와 근거 자료의 경계 분리
  - 뉴로모픽을 LLM 대체재로 과장하지 않으면서 physical edge intelligence 논지를 강화
  - 2026년 상용화 신호가 vision 외 radar/audio/wearable까지 넓어지는지 확인
- 새로 반영한 핵심 인사이트:
  - 2026년 edge-oriented SNN review는 대형 neuromorphic research platform이 작은 edge workload에는 과할 수 있고, 실제 제품에는 small-scale SoC/NoC 기반 플랫폼이 필요하다고 정리한다.
  - 2026년 Nature Reviews Materials 회고는 neuromorphic을 memristor, analogue in-memory computing, physical neural networks, edge learning을 잇는 다학제 하드웨어 문제로 본다.
  - 2D material artificial neuron/synapse review와 multisensory neuromorphic devices review는 MoS2 기반 대상 논문을 더 넓은 device/material 흐름 안에 놓게 해준다.
  - Innatera-Socionext radar, Joya Design consumer audio module 발표는 vision만이 아니라 radar/audio always-on edge sensing 쪽 상용화 신호를 보강한다. 단, 회사 발표 claim이므로 peer-reviewed evidence와 분리해서 사용한다.

### 종합 로드맵과 상용화

- [Kudithipudi et al., "Neuromorphic computing at scale", Nature, 2025](https://www.nature.com/articles/s41586-024-08253-8)
  - 대규모 뉴로모픽 시스템의 아키텍처, 생태계, 소프트웨어 격차, 확장 과제를 다룬 권위 있는 리뷰 성격의 Nature 논문.
  - 대형 시스템, 생태계, software stack, benchmark readiness를 해석할 때 사용.

- [Muir and Sheik, "The road to commercial success for neuromorphic technologies", Nature Communications, 2025](https://www.nature.com/articles/s41467-025-57352-1)
  - 뉴로모픽 상용화의 핵심 병목을 programming model, scale deployment, benchmark, edge/wearable/IoT market fit로 정리.
  - 본 리포트의 시장 전망과 "killer app" 해석의 핵심 근거.

- [Yik et al., "The neurobench framework for benchmarking neuromorphic computing algorithms and systems", Nature Communications, 2025](https://www.nature.com/articles/s41467-025-56739-4)
  - NeuroBench를 통해 neuromorphic algorithms and systems의 공통 benchmark framework를 제안.
  - 뉴로모픽 분야가 "멋진 소자 시연"에서 "비교 가능한 시스템 평가"로 넘어가고 있음을 보여준다.

- [Goswami, "Reflections on the past decade of neuromorphic computing", Nature Reviews Materials, 2026](https://www.nature.com/articles/s41578-026-00924-4)
  - 지난 10년의 뉴로모픽 흐름을 재료, 소자, in-memory computing, physical neural network 관점에서 회고한다.
  - AI가 기존 컴퓨팅 시스템을 넘어서는 방향으로 커졌고, 해결책은 한 분야만으로 충분하지 않다는 문제의식을 제공한다.

- [Gunawardana et al., "Neuromorphic architectures for edge-oriented spiking neural networks: A review", Journal of Systems Architecture, 2026](https://www.sciencedirect.com/science/article/pii/S1383762126001876)
  - edge-oriented SNN architecture review.
  - small-scale neuromorphic SoC, NoC communication, ASIC/FPGA platform, software framework를 함께 검토한다.
  - extreme edge와 embedded edge를 구분해 practical edge deployment 관점을 강화한다.

### In-sensor / near-sensor vision

- [Kim et al., "AI-native robotic vision systems enabled by in-sensor computing", npj Unconventional Computing, 2026](https://www.nature.com/articles/s44335-025-00047-z)
  - robotic vision에서 AI-native data format, in-sensor feature extraction, spike encoding, hierarchical retinal processing을 정리한 최신 리뷰.
  - physical AI와 뉴로모픽 vision의 연결 고리로 사용.

- [Zhu et al., "Bio-inspired optoelectronic devices and systems for energy-efficient in-sensor computing", npj Unconventional Computing, 2025](https://www.nature.com/articles/s44335-025-00031-7)
  - optoelectronic memristors, in-sensor neural network architectures, static/motion/event-driven processing을 다룬 리뷰.
  - 대상 논문을 더 넓은 optoelectronic in-sensor computing 계열 안에 위치시킨다.

- [Kim et al., "A Review on Memristor-Based In-Sensor Computing for Neuromorphic and Edge Intelligence", Nano Energy, 2026](https://www.sciencedirect.com/science/article/abs/pii/S2211285526003137)
  - memristor 기반 in-sensor computing을 sensing, memory, adaptive processing의 통합 문제로 정리한다.
  - optical, chemical, mechanical stimulus가 직접 memristive state를 바꾸는 stimulus-driven in-sensor intelligence 관점을 제공한다.

- [Liu et al., "Dedicated and Reconfigurable Artificial Neurons and Synapses based on Two-Dimensional Materials for Efficient Neuromorphic Application", Nano-Micro Letters, 2026](https://link.springer.com/article/10.1007/s40820-026-02139-2)
  - 2D material 기반 artificial neuron/synapse의 biomimetic model, physical mechanism, integration role을 검토한다.
  - Wang et al.의 MoS2 platform을 더 넓은 2D material neuromorphic device 흐름 안에 배치하는 근거.

- ["Multisensory Neuromorphic Devices: From Physics to Integration", Nano-Micro Letters, 2026](https://link.springer.com/article/10.1007/s40820-025-01940-9)
  - visual, tactile, thermal, chemical stimulus를 처리하는 multimodal neuromorphic hardware 리뷰.
  - physical AI가 multi-sensor system으로 갈 때 signal fusion과 encoding compatibility가 핵심 제약이 됨을 보강.

- [An et al., "Retinocortical in-sensor neuromorphic vision platform for NIR-augmented artificial vision", Nature Communications, 2026](https://www.nature.com/articles/s41467-026-71678-4_reference.pdf)
  - 저조도/멀티스펙트럼 환경에서 NIR sensitivity를 갖는 in-sensor neuromorphic vision platform을 제안.
  - 한국 연구진과 LG Display 소속 저자가 포함된 Article in Press PDF. 현재 단계에서는 peer-reviewed Nature Communications article-in-press로 조심스럽게 인용.

### 소자/아키텍처 최신 연구

- [Tong et al., "Signal-folding-based neuromorphic hardware for energy-efficient computing", Nature Electronics, 2026](https://www.nature.com/articles/s41928-026-01626-z)
  - MoS2 기반 compute-in-memory hardware에서 weight precision과 energy efficiency trade-off를 signal folding으로 완화.
  - vector-matrix multiplication power consumption을 up to 90% 줄였다는 preview abstract 수치를 확인.

- [Li et al., "A large-scale stretchable neuromorphic circuit for on-body edge computing", Nature Electronics, 2026](https://www.nature.com/articles/s41928-026-01639-8)
  - stretchable OECT array와 on-body edge computing 응용. 2026-05-20 발행.
  - wearable/implantable physical AI에서 edge neuromorphic의 응용 범위를 보여준다.

- [Nature Communications Electronic Devices article feed, 2026-05](https://www.nature.com/subjects/electronic-devices/ncomms)
  - 2026년 5월 말에 neuromorphic spintronic hardware, volatile memristive neuron, ferroelectric-ionic transistor 등 다수의 뉴로모픽/인메모리 연구가 집중적으로 게재됨.
  - "분야 활발성"의 보조 근거로만 사용한다.

### 상용/산업 신호

- [Intel Newsroom, "Intel Builds World's Largest Neuromorphic System to Enable More Sustainable AI", 2024-04-17](https://newsroom.intel.com/artificial-intelligence/intel-builds-worlds-largest-neuromorphic-system-to-enable-more-sustainable-ai)
  - Hala Point: 1.15B neurons, 128B synapses, 1,152 Loihi 2 processors, 2,600 W max power, research prototype.
  - Intel 자체 claim이므로 수치는 "Intel announced/characterized"로 표기.

- [IBM Research, "Neural inference at the frontier of energy, space, and time", Science, 2023](https://research.ibm.com/publications/neural-inference-at-the-frontier-of-energy-space-and-time)
  - NorthPole은 off-chip memory를 없애고 compute와 memory를 chip 내부에서 결합한 neural inference architecture.
  - ResNet50 기준 comparable 12nm GPU 대비 25x FPS/W, 5x FPS/transistor, 22x lower latency를 보고.
  - 엄밀한 의미의 SNN neuromorphic은 아니지만 memory-compute integration과 spatial computing의 산업 신호로 사용.

- [Innatera, "Redefining the Cutting Edge: Innatera Debuts Real-World Neuromorphic Edge AI at CES 2026", 2025-12-10](https://innatera.com/press-releases/redefining-the-cutting-edge-innatera-debuts-real-world-neuromorphic-edge-ai-at-ces-2026)
  - Pulsar neuromorphic microcontroller가 SNN, RISC-V CPU, CNN/DSP accelerator를 결합하고 smart home, industrial IoT, wearables, healthcare를 겨냥한다고 발표.
  - 상용 claim이므로 "company announcement"로 분리.

- [Socionext and Innatera, integrated 60 GHz FMCW radar and neuromorphic edge AI for human presence detection, 2026-02-23](https://www.innatera.com/newsroom/socionext-and-innatera-introduce-integrated-60-ghz-fmcw-radar-and-neuromorphic-edge-ai-for-human-presence-detection/)
  - 60 GHz FMCW radar와 Innatera Spiking Neural Processor를 결합한 presence detection 발표.
  - 회사 발표 기준 sub-milliwatt power level, 3-6x battery life extension을 주장한다. peer-reviewed 결과가 아니므로 commercial signal로만 사용.

- [Innatera and Joya Design, Pulsar-powered consumer audio module, 2026-03-12](https://www.innatera.com/newsroom/joya-design-takes-neuromorphic-chip-from-design-to-device-with-first-innatera-powered-consumer-audio-product-at-awe-china/)
  - Pulsar 기반 consumer audio module 발표.
  - 뉴로모픽 상용화 신호가 vision/radar뿐 아니라 audio always-on intelligence로도 확장되고 있음을 보여준다.

- [SynSense Speck product page](https://www.synsense.ai/products/speck-2/)
  - Dynamic Vision Sensor와 SNN processor를 single chip으로 결합한 event-driven neuromorphic vision SoC.
  - in-sensor / near-sensor commercial product signal.

- [BrainChip Radar Reference Platform, 2026-04-06](https://investor.brainchip.com/brainchip-unveils-radar-reference-platform-to-bridge-the-identification-gap-in-edge-ai/)
  - Akida neuromorphic intelligence를 radar data classification at the edge에 적용한다는 회사 발표.
  - 상장사/투자자 포털 자료이므로 commercial signal로만 사용.

### Physical AI 맥락

- [NVIDIA Newsroom, Physical AI Data Factory Blueprint, 2026-03-16](https://nvidianews.nvidia.com/news/nvidia-announces-open-physical-ai-data-factory-blueprint-to-accelerate-robotics-vision-ai-agents-and-autonomous-vehicle-development)
  - robotics, vision AI agents, autonomous vehicles를 위한 physical AI training data factory를 발표.
  - physical AI가 2026년 산업 키워드로 강화되었음을 보여주는 배경 자료.

- [Qualcomm, robotics technologies for Physical AI, 2026-01-05](https://www.qualcomm.com/news/releases/2026/01/qualcomm-introduces-a-full-suite-of-robotics-technologies-power)
  - robotics SoC, VLA/VLM, edge AI, humanoid robotics를 physical AI stack으로 묶어 발표.
  - 뉴로모픽 자체 근거는 아니며 physical AI 컴퓨팅 수요의 배경으로만 사용.

## 2026-06-16 업데이트 패스

- 목적: 공개 리뷰의 독자 친화적 설명을 강화하고, `물리적 AI`/`피지컬 AI`/`physical AI`로 섞여 있던 표현을 `Physical AI`로 통일한다.
- 추가 확인한 문헌/자료:
  - [Chowdhury et al., "Neuromorphic computing for robotic vision: algorithms to hardware advances", Communications Engineering, 2025](https://www.nature.com/articles/s44172-025-00492-5)
    - event-based camera, SNN/SNN-ANN hybrid, dedicated neuromorphic hardware를 robotic vision system design 문제로 묶어 설명한다.
    - Physical AI와 뉴로모픽의 연결을 "상위 모델 대체"가 아니라 low-power/low-latency robotic vision stack의 관점에서 보강하는 근거로 사용.
  - [Kim et al., "AI-native robotic vision systems enabled by in-sensor computing", npj Unconventional Computing, 2026](https://www.nature.com/articles/s44335-025-00047-z)
    - URL 재확인 완료. DOI는 `10.1038/s44335-025-00047-z`, published 2026-01-07.
    - 기존 final_review의 링크는 맞았으며, 검색 중 나타난 `s44335-025-00040-6`은 별도 AIoT in-sensor/near-sensor computing 리뷰로 분리.
  - [Edge intelligence through in-sensor and near-sensor computing for the artificial intelligence of things, npj Unconventional Computing, 2025](https://www.nature.com/articles/s44335-025-00040-6)
    - neuromorphic architecture, dynamic vision camera, silicon cochlea, in-memory computing을 AIoT edge intelligence 흐름으로 정리한다.
  - [A comparative review of deep and spiking neural networks for edge AI neuromorphic circuits, Frontiers in Neuroscience, 2025](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1676570/full)
    - DNN은 도구와 정확도에서 강하지만 전력 부담이 크고, SNN은 event-driven 효율이 있으나 학습 도구와 benchmark가 더 성숙해야 한다는 균형점을 제공.
  - [Synopsys, "From Tokens to Physics: How Neuromorphic Computing Will Power Physical AI", 2026-06-03](https://www.synopsys.com/blogs/chip-design/neuromorphic-computing-physical-ai-edge.html)
    - peer-reviewed 기술 근거가 아니라 산업 framing 자료로만 사용. Physical AI와 neuromorphic edge computing을 실시간·저전력 edge 설계 문제로 묶는 최신 산업 신호.
  - [Synopsys, Innatera Selects Synopsys Simulation to Scale Brain-Inspired Processors for Edge Devices, 2026-03-02](https://news.synopsys.com/2026-03-02-Innatera-Selects-Synopsys-Simulation-to-Scale-Brain-Inspired-Processors-for-Edge-Devices)
    - Innatera neuromorphic edge processor와 Physical AI 응용을 EDA/회로 검증 맥락에서 연결한 회사 발표.

## 2026-06-17 Tesla FSD / autonomous vehicle update

- 목적: 사용자의 질문에 따라 Tesla FSD와 자율주행차의 sensor-compute-planning-control stack이 뉴로모픽과 어떤 관계를 갖는지 검토한다.
- 판단:
  - Tesla FSD는 현재 공개 자료 기준으로 neuromorphic architecture가 아니라 camera-based dense neural network + in-vehicle AI computer + fleet data + OTA update 중심의 architecture다.
  - 그러나 Tesla가 풀고 있는 문제는 뉴로모픽이 겨냥하는 Physical AI 문제와 직접 겹친다. 핵심 제약은 latency, sensor bandwidth, power/thermal budget, visibility degradation detection, instantaneous control이다.
  - 리뷰에는 "Tesla가 뉴로모픽을 쓴다"가 아니라 "자율주행차는 뉴로모픽이 들어갈 수 있는 peripheral reflex layer의 필요성을 보여준다"는 관점으로 반영한다.

### Tesla official / regulatory sources

- [Tesla, Full Self-Driving (Supervised)](https://www.tesla.com/fsd)
  - FSD는 route navigation, steering, lane changes, parking 등을 active supervision 아래 수행한다고 설명한다.
  - Tesla는 현재 enabled features가 active driver supervision을 필요로 하며 vehicle을 autonomous로 만들지 않는다고 명시한다.
  - Future section은 FSD Unsupervised, robotaxi fleet, Cybercab를 미래 방향으로 제시한다.

- [Tesla, AI & Robotics](https://www.tesla.com/AI)
  - Tesla는 Full Self-Driving, bipedal robotics 등을 위해 advanced AI for vision and planning, efficient inference hardware를 핵심 접근으로 설명한다.
  - per-camera network: raw images -> semantic segmentation, object detection, monocular depth estimation.
  - birds-eye-view network: video from all cameras -> road layout, static infrastructure, 3D objects in top-down view.
  - autonomy algorithms: world representation 안에서 trajectory planning.
  - code foundations: throughput, latency, correctness, determinism, sensor data capture, multi-SoC compute pipeline.

- [Tesla Support, AI Computer Installations](https://www.tesla.com/support/ai-computer)
  - AI computer는 neural network를 빠르게 처리하도록 설계되었다고 설명한다.
  - Tesla vehicles require active driver supervision and are not fully autonomous today라는 제한을 명시한다.
  - autonomy activation은 reliability far in excess of human drivers와 regulatory approval에 달려 있다고 설명한다.

- [NHTSA ODI Resume EA26002, FSD Collisions in Reduced Roadway Visibility Conditions, 2026-03-18](https://static.nhtsa.gov/odi/inv/2026/INOA-EA26002-10023.pdf)
  - Tesla FSD가 vision-based cameras와 FSD software에 의존한다고 설명한다.
  - reduced roadway visibility 조건에서 degradation detection system이 degraded state를 감지하고 운전자에게 충분히 경고하는지 Engineering Analysis를 개시.
  - glare, airborne obscurants, lead vehicle detection failure, late alert가 조사 포인트로 등장한다.

### Autonomous driving / neuromorphic vision sources

- [Tulyakov et al., "Low-latency automotive vision with event cameras", Nature, 2024](https://www.nature.com/articles/s41586-024-07409-w)
  - 자동차 vision에서 image-based RGB camera가 bandwidth-latency trade-off를 만든다고 설명.
  - event camera는 brightness change를 asynchronous하게 측정해 high temporal resolution과 sparsity를 제공한다.

- [Event-Based Neuromorphic Vision for Autonomous Driving, IEEE Signal Processing Magazine, 2020](https://mediatum.ub.tum.de/doc/1550369/s510t7a878tkqb3bjfp1dku59.Event-Based_Neuromorphic_Vision_for_Autonomous_Driving_A_Paradigm_Shift_for_Bio-Inspired_Visual_Sensing_and_Perception.pdf)
  - event-based neuromorphic vision sensor가 low latency, HDR, motion blur 저감에서 autonomous driving perception에 유리할 수 있다고 정리한다.
  - 현재 Tesla architecture와 동일하다는 근거가 아니라, 자율주행차에서 뉴로모픽 sensor/reflex layer가 의미를 가질 수 있는 기술 배경으로 사용.

## 리포트 핵심 해석

1. 뉴로모픽은 LLM의 직접 대체재라기보다 Physical AI의 reflex/perception substrate에 가깝다.
2. 가장 가까운 상용화 시장은 데이터센터 LLM 훈련이 아니라 항상 켜진 센서, wearables, industrial IoT, radar/audio/vision wake-up, 로봇의 빠른 시각/촉각 반응이다.
3. 양자 AI와 비교하면, 뉴로모픽은 훨씬 가까운 시점에 edge AI 제품과 연구 prototype으로 검증되고 있다. 다만 "AI 전반의 지능 한계"를 한 번에 넘어서는 기술로 과장해서는 안 된다.
4. 대상 논문은 in-sensor neuromorphic vision의 좋은 대표 사례지만, system scale과 energy efficiency가 아직 숙제로 남은 실험실 규모 연구다.
5. 2025-2026년에 주목할 변화는 소자 성능 하나가 아니라 programming model, benchmark, commercial interface, hybrid edge stack의 성숙이다.
