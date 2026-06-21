---
title: "뉴로모픽 Edge AI 리뷰 runlog"
type: runlog
author: "김현중"
date created: 2026-06-05
date modified: 2026-06-05
status: distributed
tags:
  - ai-tech-review
  - runlog
  - neuromorphic-computing
---

# 뉴로모픽 Edge AI 리뷰 runlog

## 2026-06-05

### 요청

- 사용자 제공 URL: `https://www.sciencetimes.co.kr/nscvrg/view/menu/250?searchCategory=222&nscvrgSn=261508`
- 요청 요지:
  - 기사에 연결된 논문 확인
  - 뉴로모픽 분야의 최신 또는 신뢰도 높은 리뷰 조사
  - physical AI, agentic AI, LLM 한계, edge AI/대안 LLM 가능성과 연결한 리뷰 리포트 작성
  - 기존 AI Tech Review Letters 형식 반영

### 생성 폴더

- Topic folder: `2026-06-05_neuromorphic-edge-ai/`
- 생성 폴더:
  - `sources/`
  - `notes/`
  - `reports/`
  - `artifacts/final_review/figures/`
  - `skywork_inputs/`
  - `skywork_exports/`

### 리서치 방식

- ScienceTimes article 직접 열람.
- ScienceTimes의 `관련 연구 바로 보러 가기` 링크를 통해 Nature Communications 논문 확인.
- Web search로 2025-2026년 최신 리뷰, 벤치마크, Nature/Nature Communications/Nature Electronics/npj 자료 확인.
- OpenAI/ChatGPT `심층리서치 프롬프트 생성기` UI 실행은 이번 pass에서 수행하지 않았다. 대신 deepresearch prompt file을 남기고, Codex web research로 확인 가능한 공개 출처를 직접 검증했다.
- NotebookLM step은 사용하지 않았다.
- Skywork deck generation은 아직 시작하지 않았다. 현 단계는 report/final_review 완성 pass다.

### 핵심 확인 결과

- ScienceTimes 기사는 Wang et al. 2026 Nature Communications 논문을 정확히 연결했다.
- 대상 논문은 MoS2 phototransistor 기반 optoelectronic LIF neuron과 MoS2/HZO ferroelectric synapse를 같은 기판에 통합한 in-sensor neuromorphic vision 연구다.
- 논문 성능 수치:
  - RGB color recognition: 91.7%
  - object detection: 93.5%
- 단, 해당 성능은 작은 하드웨어 구성과 SNN simulation 기반 검증 성격이 강하므로 상용 camera module 수준으로 읽으면 안 된다.
- 최신 리뷰와 상용화 자료는 뉴로모픽의 가까운 시장을 edge/wearable/IoT/sensor-adjacent processing으로 보고 있다.
- LLM 대체 가능성은 "언어 모델 자체 대체"보다 "physical AI의 하위 지각/반응 계층 대체 또는 보조"로 해석하는 것이 안전하다.

### 작성 파일

- `notes/2026-06-05_neuromorphic-edge-ai_sources.md`
- `notes/2026-06-05_neuromorphic-edge-ai_deepresearch_prompt.md`
- `notes/2026-06-05_neuromorphic-edge-ai_research_runlog.md`
- `reports/2026-06-05_neuromorphic-edge-ai_memo.md`
- `reports/2026-06-05_neuromorphic-edge-ai_deepresearch.md`
- `reports/2026-06-05_neuromorphic-edge-ai_final_review.md`
- `artifacts/final_review/figure_manifest.md`
- `artifacts/final_review/figures/neuromorphic_edge_stack.svg`
- `artifacts/final_review/figures/in_sensor_neuromorphic_vision.svg`
- `artifacts/final_review/figures/neuromorphic_maturity_timeline.svg`
- `artifacts/final_review/figures/neuromorphic_workload_fit.svg`
- `artifacts/final_review/figures/imagegen/neuromorphic_physical_ai_hero-web.png`
- `artifacts/final_review/figures/imagegen/neuromorphic_in_sensor_vision_editorial-web.png`
- `artifacts/final_review/figures/imagegen/neuromorphic_edge_commercialization_editorial-web.png`
- `dist/`
- `dist.zip`

### 완료 검증

- HTML companion 생성 완료:
  - `reports/2026-06-05_neuromorphic-edge-ai_memo.html`
  - `reports/2026-06-05_neuromorphic-edge-ai_deepresearch.html`
  - `reports/2026-06-05_neuromorphic-edge-ai_final_review.html`
- editorial audit 완료:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py ...`
  - 1차 결과: `h2_count: 10`, `figure_count: 4`, `figure_density: ok`, `finding_count: 0`
- 2026-06-05 재감사 및 imagegen 강화 pass:
  - OpenAI `imagegen`으로 대표 이미지 포함 3개 생성 일러스트 추가.
  - 추가 검색 반영: Nature Reviews Materials 2026 회고, Journal of Systems Architecture edge-oriented SNN review, Nano Energy memristor in-sensor review, Nano-Micro Letters 2D material/multisensory review, Innatera-Socionext radar 및 Joya consumer audio module 발표.
  - final_review의 abstract/highlight, References, 작성 정보, figure manifest 갱신.
  - editorial audit 재실행 결과: `h2_count: 10`, `figure_count: 7`, `figure_density: ok`, `finding_count: 0`
- Playwright 렌더링 확인:
  - 1차 desktop 1440x1100: `brokenImages: []`, `figureCount: 4`, `imageCount: 4`, `bodyScrollWidth: 1440`, `overflowCount: 0`
  - 1차 mobile 390x900: `brokenImages: []`, `figureCount: 4`, `imageCount: 4`, `bodyScrollWidth: 390`
  - imagegen pass desktop 1440x1100: `brokenImages: []`, `figureCount: 7`, `imageCount: 7`, `bodyScrollWidth: 1440`, `overflowCount: 0`
  - imagegen pass mobile 390x900: `brokenImages: []`, `figureCount: 7`, `imageCount: 7`, `bodyScrollWidth: 390`
  - mobile figure panel은 넓은 SVG 독해를 위해 내부 가로 스크롤이 가능한 CSS 구조이며, 페이지 전체 가로 넘침은 없었다.
  - 검증 스크린샷 복사:
    - `output/playwright/neuromorphic_final_review_desktop.png`
    - `output/playwright/neuromorphic_final_review_mobile.png`
    - `output/playwright/neuromorphic_final_review_imagegen_desktop.png`
    - `output/playwright/neuromorphic_final_review_imagegen_mobile.png`
- Obsidian mirror 동기화 완료:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-06-05_neuromorphic-edge-ai`
  - mirror HTML local reference check: `ref_count: 5`, `missing: []`
- Distribution package:
  - `python scripts\html_to_dist.py ... --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - 결과: `[local-ref-check] ok`
  - `dist.zip` size: 6,619,187 bytes
  - Playwright dist check: `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `bodyScrollWidth: 1440`
- Public site:
  - `scripts/publish_public_site.py`에 `2026-06-05_neuromorphic-edge-ai` 등록.
  - `python scripts\publish_public_site.py`
  - 결과: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`

### 대기 항목

- Skywork:
  - slide prompt packet은 `skywork_inputs/2026-06-05_neuromorphic-edge-ai_skywork_prompt_v1.md`로 준비했다.
  - PPTX/PDF export는 아직 실행하지 않았다.
- OpenProject:
  - 현재 target work package ID가 지정되지 않았으므로, 잘못된 work package 업데이트를 피하기 위해 pending으로 둔다.
- GitHub Pages deployment:
  - site generation 완료.
  - commit: `b5f4fec` (`Publish neuromorphic edge AI review`)
  - `git push origin main` 완료.
  - GitHub Actions `Publish public report hub` run id: `26983007032`
  - workflow status: `completed`, conclusion: `success`
  - public URL: `https://infant83.github.io/AI_Tech_Review/reviews/2026-06-05_neuromorphic-edge-ai/`
  - public URL check: HTTP `200`, title `뉴로모픽, 물리적 AI의 반응 시간을 줄이는 기술`, image count `7`
- Email:
  - user requested sending `dist.zip` to `hyun-jung.kim@lgdisplay.com`.
  - Gmail sender profile: `angpangmokjang@gmail.com`
  - first attempt with scalar `attachment_files` failed because connector expected an array.
  - resent with `attachment_files` array.
  - sent message id: `19e94bc91346fbaa`
  - thread id: `19e94bc91346fbaa`

## 2026-06-16 public review update

### 사용자 요청

- Skywork PPT는 이번 범위에서 제외.
- 기존 공개 리뷰 `https://infant83.github.io/AI_Tech_Review/reviews/2026-06-05_neuromorphic-edge-ai/index.html`의 본문 업데이트.
- 뉴로모픽 기술 설명을 더 친근하게 정리.
- `물리적 AI`/`피지컬 AI`/`physical AI` 표기를 `Physical AI`로 통일.
- Physical AI와 뉴로모픽의 연결을 과장 없이 자연스럽게 설명.
- 제시 논문 외 2025-2026 리뷰 논문과 최신 산업 신호를 반영.
- AI 문체 audit 후 AI 작성 말투 제거.

### 반영 내용

- final review 제목 변경:
  - 이전: `뉴로모픽, 물리적 AI의 반응 시간을 줄이는 기술`
  - 이후: `뉴로모픽, Physical AI의 감각을 가볍게 만드는 기술`
- 본문 구조 업데이트:
  - 도입부를 로봇/센서/전력/지연 문제에서 시작하도록 재작성.
  - `Physical AI의 시간`, `첫 시장은 작은 지능`, `2026년의 연구 방향`, `움직이는 산업 신호` 섹션을 중심으로 문장 흐름 정리.
  - 뉴로모픽을 LLM 직접 대체재가 아니라 Physical AI의 sensor-near perception/reflex layer로 해석.
- 추가/재확인 근거:
  - Communications Engineering 2025 robotic vision perspective.
  - npj Unconventional Computing 2026 AI-native robotic vision review URL 재확인.
  - npj Unconventional Computing 2025 in-sensor/near-sensor AIoT review.
  - Frontiers in Neuroscience 2025 DNN/SNN edge AI comparative review.
  - Synopsys 2026-06-03 Physical AI/neuromorphic edge blog 및 2026-03-02 Innatera-Synopsys 발표.
- SVG figure text:
  - `neuromorphic_edge_stack.svg`, `neuromorphic_maturity_timeline.svg`의 `피지컬 AI`/`physical AI` 표기를 `Physical AI`로 수정.

### 검증

- HTML render:
  - `python scripts\markdown_to_html.py --mode final-review 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
- editorial audit:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - result: `h2_count: 10`, `figure_count: 7`, `figure_density: ok`, `finding_count: 0`
- phrase audit:
  - `물리적 AI`, `피지컬 AI`, lowercase `physical AI`, 주요 AI식 상투어 검색 결과 없음.
- distribution package:
  - `python scripts\html_to_dist.py ... --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
  - `dist.zip` size: 6,620,357 bytes
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local public-site check:
  - target: `site/reviews/2026-06-05_neuromorphic-edge-ai/index.html`
  - desktop 1440x1100: title/h1 updated, `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `bodyScrollWidth: 1440`, `overflowCount: 0`
  - mobile 390x900: title/h1 updated, `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `bodyScrollWidth: 390`, `overflowCount: 0`
  - term check in rendered body: `물리적 AI`/`피지컬 AI`/lowercase `physical AI` count `0`
  - artifacts:
    - `artifacts/final_review/verification/neuromorphic_public_update_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_public_update_mobile.png`
    - `artifacts/final_review/verification/neuromorphic_public_update_check.json`
- Obsidian mirror sync:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-06-05_neuromorphic-edge-ai`
  - updated final review markdown/html, sources note, runlog, revised SVG figures, verification JSON.
- GitHub Pages deployment:
  - commit: `27234dd` (`Update neuromorphic Physical AI review`)
  - `git push origin main` 완료.
  - GitHub Actions `Publish public report hub` run id: `27624494197`, status `completed`, conclusion `success`.
  - GitHub Pages `pages build and deployment` run id: `27624554251`, status `completed`, conclusion `success`.
  - public URL check: HTTP `200`, title `뉴로모픽, Physical AI의 감각을 가볍게 만드는 기술`, image count `7`, old term count `0`.

## 2026-06-17 Tesla FSD / autonomous vehicle update

### 사용자 요청

- Tesla 자율주행차의 센서, AI 연산, 방향 결정, 순간적 움직임이 뉴로모픽 기술과 어떤 관계가 있는지 탐색.
- Tesla의 실제 자율주행 기술과 미래 기술 방향을 정리.
- 의미가 있으면 뉴로모픽 리뷰 본문에 반영.

### 검색 및 확인 자료

- Skywork Search:
  - `Tesla Full Self-Driving 2026 AI architecture cameras neural network planning control official`
  - `Tesla FSD 2026 end-to-end neural network Robotaxi future technology AI4 HW4`
  - `Tesla autonomy sensors cameras radar lidar neuromorphic computing relation autonomous vehicles`
- 확인한 핵심 자료:
  - Tesla FSD page: active supervision, cameras, route navigation, steering/lane change/parking, future FSD Unsupervised/robotaxi/Cybercab framing.
  - Tesla AI & Robotics: advanced AI for vision and planning, efficient inference hardware, per-camera networks, birds-eye-view networks, autonomy algorithms, code foundation latency/determinism.
  - Tesla AI Computer support: custom AI computer, active driver supervision, not fully autonomous today, regulatory approval condition.
  - NHTSA ODI Resume EA26002: FSD reduced visibility investigation, vision-based camera reliance, degradation detection and driver warning timing.
  - Nature 2024 low-latency automotive vision with event cameras.
  - IEEE Signal Processing Magazine 2020 event-based neuromorphic vision for autonomous driving.

### 반영 내용

- final review에 `자율주행차라는 시험대` 섹션 추가.
- 핵심 해석:
  - Tesla FSD는 현재 neuromorphic system으로 보기 어렵다.
  - 현재 Tesla stack은 camera-based dense neural network + in-vehicle AI computer + fleet data + OTA update에 가깝다.
  - 그러나 Tesla가 다루는 sensor bandwidth, latency, visibility degradation, thermal/power budget, split-second control 문제는 뉴로모픽이 겨냥하는 Physical AI 제약과 겹친다.
  - 뉴로모픽은 전체 FSD brain 대체보다 event camera/SNN 기반 peripheral reflex layer 후보로 보는 편이 안전하다.
- References에 Tesla, NHTSA, event camera/autonomous driving 자료 추가.
- sources note에 2026-06-17 Tesla FSD update section 추가.

### 검증

- HTML render:
  - `python scripts\markdown_to_html.py --mode final-review 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
- editorial audit:
  - result: `h2_count: 11`, `figure_count: 7`, `figure_density: ok`, `finding_count: 0`
- phrase audit:
  - `물리적 AI`, `피지컬 AI`, lowercase `physical AI`, 주요 AI식 상투어 검색 결과 없음.
- distribution package:
  - `python scripts\html_to_dist.py ... --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local public-site check:
  - desktop 1440x1100: title/h1 updated, `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `bodyScrollWidth: 1440`, `overflowCount: 0`, `hasTeslaSection: true`, `hasNhtsa: true`
  - mobile 390x900: title/h1 updated, `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `bodyScrollWidth: 390`, `overflowCount: 0`, `hasTeslaSection: true`, `hasNhtsa: true`
  - term check in rendered body: `물리적 AI`/`피지컬 AI`/lowercase `physical AI` count `0`
  - artifacts:
    - `artifacts/final_review/verification/neuromorphic_tesla_update_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_tesla_update_mobile.png`
    - `artifacts/final_review/verification/neuromorphic_tesla_update_check.json`

## 2026-06-17 Physical AI latency layer / Atlas / display trend update

### 사용자 요청

- Tesla FSD나 고속 vision AI가 ms 단위 추론 능력을 갖더라도 운전 특화 모델과 제어기의 결과인지, LLM/VLA 기반 agentic Physical AI와 어떻게 다른지 설명.
- Boston Dynamics Atlas처럼 춤, 계단, 덤블링, 산업 작업을 수행하는 로봇도 정해진 행동 정책과 open-ended 상호작용 사이에 차이가 있는지 정리.
- 이 차이가 왜 뉴로모픽 디바이스의 필요성과 연구 가치를 키우는지, Wang et al. 논문의 위상과 자연스럽게 연결.
- 과거 뉴로모픽과 차세대 디스플레이 연결 논의가 최근에는 덜 보이는 이유와 관심 이동을 함께 반영.

### 검색 및 확인 자료

- Boston Dynamics:
  - `Atlas' Evolution From Research Robot to Industrial Humanoid`
  - `Large Behavior Models and Atlas Find New Footing`
- Neuromorphic / display:
  - `Toward Intelligent Display with Neuromorphic Technology`, Advanced Materials, 2024
  - `Electrically programmable organic in-display neuromorphic computing`, National Science Review, 2025
  - `An all-in-one electrochromic neuromorphic display`, National Science Review, 2025

### 반영 내용

- final review에 `빠른 몸과 느린 판단` 섹션 추가.
- deterministic SVG `physical_ai_latency_layers.svg` 추가.
- Physical AI stack을 fast reflex/safety loop, learned skill policy, slower language/planning/tool-use layer로 설명.
- Tesla FSD와 Atlas 사례를 "빠른 몸이 곧 LLM식 open-ended reasoning을 뜻하지 않는다"는 관점으로 보강.
- 뉴로모픽의 가치를 의지·대화·자율성 부여가 아니라 sensor-near, low-latency, low-power reflex layer를 가볍게 만드는 데서 설명.
- final review에 `디스플레이 논의의 이동` 섹션 추가.
- intelligent display / in-display neuromorphic computing 흐름이 최근 edge AI, in-sensor/near-sensor computing, wearable/AR/robot vision 표현으로 흡수되어 보인다는 해석을 추가.
- References와 sources note에 Atlas/LBM, intelligent display, EP-IDNC 자료 추가.

### 검증

- HTML render:
  - `python scripts\markdown_to_html.py --mode final-review 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
- editorial audit:
  - result: `h2_count: 13`, `figure_count: 8`, `figure_density: ok`, `finding_count: 0`
- phrase audit:
  - `물리적 AI`, `피지컬 AI`, lowercase `physical AI`, 주요 AI식 상투어 검색 결과 없음.
- distribution package:
  - `python scripts\html_to_dist.py ... --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
  - `dist.zip` size: `6,640,323` bytes
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local public-site check:
  - desktop 1440x1100: title/h1 updated, `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 1440`, `unexpectedOverflowCount: 0`, `hasFastSlowSection: true`, `hasDisplaySection: true`, `hasBoston: true`, `hasLargeBehaviorModels: true`
  - mobile 390x900: title/h1 updated, `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 390`, `unexpectedOverflowCount: 0`, `scrollableFigureCount: 5`
  - dist desktop 1440x1000: title/h1 updated, `figureCount: 8`, `imageCount: 8`, `brokenImages: []`
  - term check in rendered body: `물리적 AI`/`피지컬 AI`/lowercase `physical AI` count `0`
  - artifacts:
    - `artifacts/final_review/verification/neuromorphic_physical_ai_layers_update_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_physical_ai_layers_update_mobile.png`
    - `artifacts/final_review/verification/neuromorphic_physical_ai_layers_update_check.json`
- Obsidian mirror sync:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-06-05_neuromorphic-edge-ai`
  - updated final review markdown/html, sources note, runlog, `physical_ai_latency_layers.svg`, and verification JSON.
- GitHub Pages deployment:
  - commit: `31c5930` (`Clarify Physical AI latency layers in neuromorphic review`)
  - `git push origin main` 완료.
  - GitHub Actions `Publish public report hub` run id: `27628063157`, status `completed`, conclusion `success`.
  - GitHub Pages `pages build and deployment` run id: `27628115847`, status `completed`, conclusion `success`.
  - public URL check: HTTP `200`, title `뉴로모픽, Physical AI의 감각을 가볍게 만드는 기술`, `HasFastSlow: true`, `HasDisplay: true`, `HasBoston: true`, `HasLargeBehaviorModels: true`, `HasLatencySvg: true`, image tag count `8`, old term count `0`.

## 2026-06-17 Quanta Magazine historical context update

### 사용자 요청

- Quanta Magazine neuromorphic 검색 결과와 다음 기사들을 현재 리뷰에서 참조할 수 있도록 반영.
  - `AI Overcomes Stumbling Block on Brain-Inspired Hardware`
  - `A Brain Built From Atomic Switches Can Learn`
  - `New Chip Expands the Possibilities for AI`
- 이 주제들이 현시점 어떤 방향으로 재해석되는지, 의미 있는 논의가 진전되고 있는지, 현재 리뷰를 보강하는지, 다른 해석 여지가 있는지 정리.
- 최근 뉴로모픽 이야기가 자주 등장하지 않는 것처럼 보이는 이유를 설명.

### 확인 자료

- [Quanta Magazine search, neuromorphic](https://www.quantamagazine.org/?s=neuromorphic)
- [Quanta Magazine, `A Brain Built From Atomic Switches Can Learn`, 2017](https://www.quantamagazine.org/a-brain-built-from-atomic-switches-can-learn-20170920/)
- [Quanta Magazine, `AI Overcomes Stumbling Block on Brain-Inspired Hardware`, 2022](https://www.quantamagazine.org/ai-overcomes-stumbling-block-on-brain-inspired-hardware-20220217/)
- [Quanta Magazine, `New Chip Expands the Possibilities for AI`, 2022](https://www.quantamagazine.org/a-brain-inspired-chip-can-run-ai-with-far-less-energy-20221110/)

### 반영 내용

- final review에 `퀀타가 남긴 세 질문` 섹션 추가.
- 세 질문으로 정리:
  - 물질 자체가 기억과 계산을 함께 할 수 있는가.
  - analog neuromorphic hardware의 device mismatch를 학습으로 견딜 수 있는가.
  - 큰 AI 모델을 작은 장치에서 돌릴 만큼 compute와 memory를 가까이 둘 수 있는가.
- 2017 atomic-switch mesh는 direct AI product보다 material/physical network computing으로 재해석.
- 2022 BrainScaleS-2는 hardware-aware learning과 device-algorithm co-design의 문제로 재해석.
- 2022 NeuRRAM은 strict SNN neuromorphic보다 analog in-memory / compute-in-memory AI accelerator 흐름으로 재해석.
- 최근 뉴로모픽이라는 용어가 덜 보이는 이유를 compute-in-memory, analog AI, event-based sensing, in-sensor computing, edge AI, Physical AI accelerator로 용어가 분산된 결과로 정리.
- References와 sources note에 Quanta 자료 추가.

### 검증

- HTML render:
  - `python scripts\markdown_to_html.py --mode final-review 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
- editorial audit:
  - result: `h2_count: 14`, `figure_count: 8`, `figure_density: ok`, `finding_count: 0`
- phrase audit:
  - `물리적 AI`, `피지컬 AI`, lowercase `physical AI`, 주요 AI식 상투어 검색 결과 없음.
- distribution package:
  - `python scripts\html_to_dist.py ... --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
  - `dist.zip` size: `6,646,200` bytes
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local public-site check:
  - desktop 1440x1100: title/h1 updated, `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 1440`, `unexpectedOverflowCount: 0`, `hasQuantaSection: true`, `hasAtomicSwitches: true`, `hasBrainScaleS: true`, `hasNeuRRAM: true`, `hasQuantaSearch: true`
  - mobile 390x900: title/h1 updated, `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 390`, `unexpectedOverflowCount: 0`, `scrollableFigureCount: 5`
  - dist desktop 1440x1000: title/h1 updated, `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `hasQuantaSection: true`
  - term check in rendered body: `물리적 AI`/`피지컬 AI`/lowercase `physical AI` count `0`
  - artifacts:
    - `artifacts/final_review/verification/neuromorphic_quanta_update_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_quanta_update_mobile.png`
    - `artifacts/final_review/verification/neuromorphic_quanta_update_check.json`
- Obsidian mirror sync:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-06-05_neuromorphic-edge-ai`
  - updated final review markdown/html, sources note, runlog, and `neuromorphic_quanta_update_check.json`.
- GitHub Pages deployment:
  - commit: `c26ecf6` (`Add Quanta neuromorphic context to review`)
  - `git push origin main` 완료.
  - GitHub Actions `Publish public report hub` run id: `27650153388`, status `completed`, conclusion `success`.
  - GitHub Pages `pages build and deployment` run id: `27650187901`, status `completed`, conclusion `success`.
  - public URL check: HTTP `200`, title `뉴로모픽, Physical AI의 감각을 가볍게 만드는 기술`, `HasQuantaSection: true`, `HasAtomicSwitches: true`, `HasBrainScaleS: true`, `HasNeuRRAM: true`, `HasQuantaSearch: true`, image tag count `8`, old term count `0`.

## 2026-06-17 strict AI prose audit update

### 사용자 요청

- AI식 단정형 문체를 더 엄격하게 감사.
- `~~편이 정확합니다`, `~~입니다`, `~~합니다`가 반복될 때 생기는 선언적·관조적 어조를 줄임.
- `이 지점에서`, `밀고`, `맞다/틀리다`, `정확하다`, `필수`처럼 지식을 판정하는 표현을 줄임.
- 뉴로모픽 분야 전문가가 겸손하지만 professional하게 독자를 논의 안으로 끌어들이는 톤으로 조정.

### 반영 내용

- 도입부를 `LLM 후계자` 판정 대신, 뉴로모픽이 오래 붙들어 온 센서-근접 계산의 물음으로 재구성.
- MoS2/HZO 논문 설명에서 `정확합니다`, `읽는 편이 정확합니다`, `확인된 성과는...` 같은 판정형 문장을 source-bound 설명으로 수정.
- Tesla/FSD와 Boston Dynamics Atlas 대목에서 `필수`, `시험대`, `맞다`, `좋은 사례` 계열 표현을 제거하고, 공개 자료 기준의 계층형 시간 스케일 설명으로 조정.
- Quanta, display, industry signal 섹션에서 `보강합니다`, `분명합니다`, `신호입니다` 같은 확정형 설명을 줄이고, 논점이 어떻게 이동했는지 연구자 관찰형 문장으로 수정.
- 결론부를 처방형 체크리스트보다 `우리 제품과 공정에서 어떤 제약을 묻는가`에 가까운 독자-facing 물음으로 조정.

### 검증

- editorial audit:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - result: `h2_count: 14`, `figure_count: 8`, `figure_density: ok`, `finding_count: 0`
- phrase audit:
  - `정확합니다`, `맞습니다`, `틀립니다`, `필수`, `밀고 있습니다`, `시험대입니다`, `좋은 사례`, `이 지점`, `이 대목`, `보여줍니다`, `드러냅니다`, `분명합니다`, `후보가 됩니다`, `가능성이 큽니다`, `읽는 편`, `보는 편`, `좋습니다`, `중요합니다` 검색 결과 없음.
  - `물리적 AI`, `피지컬 AI`, lowercase `physical AI` 검색 결과 없음.
- HTML render:
  - `python scripts\markdown_to_html.py --mode final-review 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - output: `reports/2026-06-05_neuromorphic-edge-ai_final_review.html`
- distribution package:
  - `python scripts\html_to_dist.py ... --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
  - `dist.zip` size: `6,647,546` bytes
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local browser check:
  - dist desktop 1440x1200 and mobile 390x900: `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `unexpectedOverflowCount: 0`, required sections all present, old phrase hits `[]`, Korean Physical AI term hits `0`.
  - site desktop 1440x1200 and mobile 390x900: `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `unexpectedOverflowCount: 0`, required sections all present, old phrase hits `[]`, Korean Physical AI term hits `0`.
  - artifacts:
    - `artifacts/final_review/verification/neuromorphic_strict_prose_browser_check.json`
    - `artifacts/final_review/verification/neuromorphic_strict_prose_dist_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_strict_prose_dist_mobile.png`
    - `artifacts/final_review/verification/neuromorphic_strict_prose_site_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_strict_prose_site_mobile.png`
- Obsidian mirror sync:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-06-05_neuromorphic-edge-ai`
  - updated final review markdown/html, sources note, runlog, and strict prose browser check JSON.
- GitHub Pages deployment:
  - commit: `88865fe` (`Tighten neuromorphic review prose audit`)
  - `git push origin main` 완료.
  - GitHub Actions `Publish public report hub` run id: `27651994226`, status `completed`, conclusion `success`.
  - GitHub Pages `pages build and deployment` run id: `27652035052`, status `completed`, conclusion `success`.
  - public URL check: HTTP `200`, title `뉴로모픽, Physical AI의 감각을 가볍게 만드는 기술`, desktop/mobile `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `unexpectedOverflowCount: 0`, required sections present, old phrase hits `[]`, Korean Physical AI term hits `0`, new opening/Tesla/Quanta headings reflected.

## 2026-06-17 contrast-pivot prose harness update

### 사용자 요청

- `...하기는 어렵습니다. 다만 ...`, `...보다 ...입니다`, `...가 아니라 ...입니다`처럼 부정이나 대비로 결론을 띄우는 AI 번역투를 더 엄격하게 피할 것.
- 단문을 자연스럽게 연결하되, 과장된 대비나 부정형 도입으로 문단을 시작하지 않을 것.
- `로봇이 복도에서 사람을 피하는 장면을 떠올려 보면...`처럼 출처나 실제 조건이 없는 작위적 장면 도입을 줄일 것.
- 이 기준을 김현중식 글쓰기, 현 작업공간 하네스, global 글쓰기 하네스에 남기고 앞으로도 재사용할 것.

### 하네스 반영

- `C:\Users\angpa\AGENTS.md`
  - Korean writing style baseline에 correction-first / contrast-pivot paragraph 금지 규칙 추가.
  - staged scene-opener 금지와 `observed situation -> constraint -> technical relation -> evidence` 흐름 명시.
- `C:\Users\angpa\.codex\rules\korean-writing-style.md`
  - correction-first 구조, staged scene-opener, short-sentence translationese 감사 항목 추가.
  - editorial audit 항목을 10개에서 12개로 확장.
- `AGENTS.md`
  - AI_Tech_Review workspace의 Korean Human Writing Style Rules에 same rule 추가.
- `.codex/rules/writing-harness.md`
  - 선호 예시에 남아 있던 `선명해집니다`, `이어집니다`, `필요해집니다`식 문장 일부를 실제 조건 기반 문장으로 교체.
  - `Topic-First, Not Negation-First`를 문단 중간 contrast-pivot까지 확장.
- Obsidian 김현중식 글쓰기 참고풀
  - `C:\Users\angpa\Obsidian_Vault\hkim_Writings\2026-05-10_AI식 글쓰기 감사와 김현중식 문체 레퍼런스.md`
  - `C:\Users\angpa\Obsidian_Vault\hkim_Writings\README.md`
  - 2026-06-17 보강 기준으로 `부정-대비형 문단을 피한다` 섹션 추가.

### 리뷰 본문 반영

- 도입부를 `LLM 후계자로 세우면 논의가 좁아진다` 구조에서 `Physical AI가 실제 제품으로 들어갈 때 센서 데이터가 가까운 곳에서 먼저 줄어들어야 한다`는 조건 기반 설명으로 변경.
- 작위적인 `로봇이 복도에서 사람을 피하는 장면을 떠올려 보면...` 문단을 로봇·차량·웨어러블의 실제 전력/지연 조건 설명으로 교체.
- Physical AI 연결부에서 `이 자료들을 뉴로모픽 자체의 성능 근거로 쓰기는 어렵습니다. 다만...` 구조를 제거하고, NVIDIA/Qualcomm 자료가 반복해서 보여주는 실제 제품 조건에서 바로 시작하도록 수정.
- Tesla/FSD 문단에서 `뉴로모픽이 곧장 필요하다`식 가정-부정 구조를 줄이고, dense visual AI와 뉴로모픽이 만나는 위치를 제약 조건과 peripheral reflex layer로 설명.
- Boston Dynamics/Atlas 문단에서 빠른 sensorimotor policy와 느린 agentic layer의 차이를 직접 설명하고, 뉴로모픽의 역할을 감각-반응 계층으로 정리.
- Quanta/디스플레이/LLM 섹션에서 `후보로 보고 싶어집니다`, `귀담아들을 부분`, `사라진 것이 아니라...` 등 평가·대비형 리듬을 줄이고, 2017-2026년 논점 이동을 자료 중심으로 재서술.

### 검증

- editorial audit:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - result: `h2_count: 14`, `figure_count: 8`, `figure_density: ok`, `finding_count: 0`
- phrase audit:
  - `금방 좁아`, `떠올려`, `선명해`, `성능 근거로 쓰기는 어렵`, `다만 왜`, `붙는 자리`, `검토 테이블`, `절반쯤`, `후보로 보고 싶`, `귀담아`, `물리적 AI`, `피지컬 AI`, `가깝습니다`, `맞습니다` 검색 결과 없음.
- HTML render:
  - `python scripts\markdown_to_html.py --mode final-review 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - output: `reports/2026-06-05_neuromorphic-edge-ai_final_review.html`
- distribution package:
  - `python scripts\html_to_dist.py 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.html --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
  - `dist.zip` size: `6,646,564` bytes
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local browser check:
  - dist desktop 1440x1200: `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 1440`, `viewportWidth: 1440`, `unexpectedOverflowCount: 0`, `missingRequired: []`, `forbiddenHits: []`
  - dist mobile 390x900: `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 390`, `viewportWidth: 390`, `missingRequired: []`, `forbiddenHits: []`
  - site desktop 1440x1200: `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 1440`, `viewportWidth: 1440`, `unexpectedOverflowCount: 0`, `missingRequired: []`, `forbiddenHits: []`
  - site mobile 390x900: `figureCount: 8`, `imageCount: 8`, `brokenImages: []`, `bodyScrollWidth: 390`, `viewportWidth: 390`, `missingRequired: []`, `forbiddenHits: []`
  - mobile에서 figure 내부 이미지 5개가 viewport보다 넓게 잡혔으나 `bodyScrollWidth == viewportWidth`로 페이지 수평 스크롤은 없음.
  - screenshots:
    - `artifacts/final_review/verification/neuromorphic_contrast_pivot_check.json`
    - `artifacts/final_review/verification/neuromorphic_contrast_pivot_dist_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_contrast_pivot_dist_mobile.png`
    - `artifacts/final_review/verification/neuromorphic_contrast_pivot_site_desktop.png`
    - `artifacts/final_review/verification/neuromorphic_contrast_pivot_site_mobile.png`
- GitHub Pages deployment:
  - commit: `126cd5a` (`Tighten neuromorphic contrast-pivot prose`)
  - `git push origin main` 완료.
  - GitHub Actions `Publish public report hub` run id: `27667297260`, status `completed`, conclusion `success`.
  - GitHub Pages `pages build and deployment` run id: `27667324232`, status `completed`, conclusion `success`.
  - public URL check: HTTP `200`, title `뉴로모픽, Physical AI의 감각을 가볍게 만드는 기술`, `HasNewHeading: true`, `HasOldPhrase: false`, `HasContrastPivot: false`, `HasPhysicalAI: true`.

## 2026-06-17 unsupported contrast/glue phrase audit update

### 사용자 요청

- `뉴로모픽 컴퓨팅은 큰 언어 모델의 후계자라기보다...`처럼 독자가 아직 세우지 않은 C를 먼저 꺼내고 B로 고치는 구조를 피할 것.
- `...인 흐름입니다`, `이 지점에서 다시 살아납니다`처럼 의미 없이 문단 분위기만 바꾸는 접착 문장을 쓰지 않을 것.
- `무겁습니다`라고 말할 때는 왜 무거운지, 즉 데이터 이동, 메모리 접근, 큰 모델 추론, 네트워크 왕복, 전력, 안전 latency 같은 기술적 브릿지를 둘 것.
- KIAS HORIZON, 최종현학술원 Science Note, Quanta식 설명을 문장 복제가 아니라 한국어 과학·기술 리뷰의 점검 렌즈로 참조할 것.

### 하네스 반영

- `C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py`
  - `라기보다`, `로 두지 않고`, `대신할 새`, `흐름입니다`, `흐름으로`, `이 지점에서`, `다시 살아납니다`, `무거워집니다` 감사 패턴 추가.
  - 테스트 문장 `뉴로모픽 컴퓨팅은 큰 언어 모델의 후계자라기보다... 이 지점에서 다시 살아납니다`에서 `contrast_pivot`과 `micro_cadence`가 검출됨을 확인.
- `C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\references\korean-review-expression-editor.md`
  - 보정형 대비와 빈 접착 문장 금지 예시 추가.
- `C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\references\korean-science-prose-patterns.md`
  - `무겁다/느리다/가볍다` 평가어에 technical bridge를 붙이는 규칙 추가.
- `.codex/rules/writing-harness.md`, `AGENTS.md`, `C:\Users\angpa\AGENTS.md`, `C:\Users\angpa\.codex\rules\korean-writing-style.md`
  - unsupported `A는 C라기보다 B입니다` 구조와 `흐름/이 지점/살아납니다` 접착어 감사를 추가.
- Obsidian 김현중식 글쓰기 참고풀
  - `C:\Users\angpa\Obsidian_Vault\hkim_Writings\2026-05-10_AI식 글쓰기 감사와 김현중식 문체 레퍼런스.md`
  - 2026-06-17 추가 섹션에 사용자 지적 문장, 문제 이유, 대체 방향, technical bridge 기준 기록.

### 리뷰 본문 반영

- 제목을 `뉴로모픽, Physical AI의 감각을 가볍게 만드는 기술`에서 `뉴로모픽, Physical AI의 빠른 감각 계층`으로 수정.
- Highlight를 `LLM 후계자라기보다...` 대비 구조에서 sensor data movement, VLM/perception inference, accelerator time, network round trip, safety control loop 비용을 설명하는 문장으로 교체.
- 첫 본문 문단의 `무거워집니다`를 데이터 이동, 추론 지연, memory/network bandwidth, accelerator 점유 시간, 전력 문제로 풀어 설명.
- Boston Dynamics/Atlas 문단의 `라기보다`, `흐름입니다`를 제거하고 sensorimotor policy, 상위 agentic layer, action chunk inference의 층위 차이를 직접 설명.
- Quanta/디스플레이/산업 신호/LLM 섹션의 `흐름`, `라기보다`, `아니라` 반복을 줄이고 기술적 자리와 검토 조건 중심으로 재작성.
- memo와 SVG 내부 문구도 같은 기준으로 수정.

### 검증

- editorial audit:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - result: `h2_count: 14`, `figure_count: 8`, `figure_density: ok`, `finding_count: 0`
  - memo result: `finding_count: 0`
- phrase audit:
  - `라기보다`, `흐름입니다`, `다시 살아`, `이 지점에서`, `흐름으로`, `로 두지 않고`, `LLM을 대신`, `무거워집니다` 검색 결과 없음.
- HTML render:
  - `python scripts\markdown_to_html.py --mode auto 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - `python scripts\markdown_to_html.py --mode auto 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_memo.md`
- distribution package:
  - `python scripts\html_to_dist.py 2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.html --dist 2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path 2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=7`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local browser check:
  - local dist URL opened through temporary `python -m http.server`: page title `뉴로모픽, Physical AI의 빠른 감각 계층`
  - site review URL opened through temporary `python -m http.server`: page title `뉴로모픽, Physical AI의 빠른 감각 계층`
  - snapshot confirmed updated hero caption and Highlight bridge text.
- GitHub Pages deployment:
  - commit: `1d7a9d8` (`Tighten neuromorphic prose audit bridge`)
  - `git push origin main` 완료.
  - GitHub Actions `Publish public report hub` run id: `27688479873`, status `completed`, conclusion `success`.
  - GitHub Pages `pages build and deployment` run id: `27688520480`, status `completed`, conclusion `success`.
  - public URL check: HTTP `200`, title `뉴로모픽, Physical AI의 빠른 감각 계층`, `HasOldTitle: false`, `HasBadPivot: false`, `HasBridge: true`.

## 2026-06-21 everyday edge AI reframing update

### 사용자 요청

- 자율주행차/Tesla 사례는 뉴로모픽의 필요성을 설명하는 도입부로 적합하지 않으므로 빼고, 생활 가까운 AI 기술에서 뉴로모픽이 실제로 의미 있는 영역을 찾아 글을 다시 쓸 것.
- 해당 주제를 기반으로 deep research를 다시 돌리고, 얻은 결과와 insight를 바탕으로 글을 재작성할 것.

### deep research refresh

- 새 research note:
  - `notes/2026-06-21_neuromorphic-edge-ai_everyday-edge-deepresearch.md`
- 중점 검토 영역:
  - smart home presence sensing
  - always-on audio / sound event recognition
  - wearable / on-body edge computing
  - smart camera / in-sensor vision
- 핵심 근거:
  - Muir and Sheik 2025 Nature Communications commercial success review
  - 2025 npj AIoT in-sensor/near-sensor computing review
  - Socionext-Innatera 60 GHz FMCW radar human presence detection announcement
  - Baek and Lee 2024 SNN sound review
  - Joya Design / Innatera consumer audio module announcement
  - Li et al. 2026 Nature Electronics stretchable neuromorphic circuit
  - SynSense Speck product page
  - Wang et al. 2026 Nature Communications target paper

### 본문 반영

- 제목을 `뉴로모픽, 항상 켜진 AI의 감각층`으로 변경.
- 도입부를 스마트홈, 이어버드, wearable patch, smart camera의 always-on sensor cost로 재작성.
- 자율주행차, Tesla FSD, NHTSA, Boston Dynamics/Atlas 중심 문단과 참고문헌 제거.
- 새 hero image 생성:
  - `artifacts/final_review/figures/imagegen/neuromorphic_everyday_ai_hero.png`
  - `artifacts/final_review/figures/imagegen/neuromorphic_everyday_ai_hero-web.png`
- `항상 켜진 AI의 시간`, `가까운 네 가지 장면` 섹션 추가.
- figure numbering과 `artifacts/final_review/figure_manifest.md` 갱신.

### 검증

- editorial audit:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - result: `h2_count: 13`, `figure_count: 7`, `figure_density: ok`, `finding_count: 0`
- phrase/source audit:
  - final review 본문과 figure manifest에서 `Tesla`, `NHTSA`, `자율주행`, `Boston`, `Atlas`, `Physical AI` 검색 결과 없음.
  - ScienceTimes 원 기사 제목에 포함된 `로봇`은 원문 제목으로만 남김.
- HTML render:
  - `python scripts\markdown_to_html.py --mode auto .\2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - output: `reports/2026-06-05_neuromorphic-edge-ai_final_review.html`
- distribution package:
  - `python scripts\html_to_dist.py .\2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.html --dist .\2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path .\2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
  - zip: `2026-06-05_neuromorphic-edge-ai\dist.zip`, size `6,785,095` bytes
  - stale dist/public assets removed: old physical AI hero image and latency-layer SVG are no longer present in `dist/`, `site/reviews/2026-06-05_neuromorphic-edge-ai/`, or `site/manifest.json`.
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=8`, `reviews/2026-06-05_neuromorphic-edge-ai/index.html`
- Playwright local browser check:
  - dist desktop: `title: 뉴로모픽, 항상 켜진 AI의 감각층`, `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `hasEverydayHero: true`, `hasOldHero: false`, `hasTesla: false`, `bodyScrollWidth == viewportWidth == 1440`
  - dist mobile: `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `hasEverydayHero: true`, `bodyScrollWidth == viewportWidth == 390`
  - site review desktop: `title: 뉴로모픽, 항상 켜진 AI의 감각층`, `figureCount: 7`, `imageCount: 7`, `brokenImages: []`, `hasEverydayHero: true`, `hasOldHero: false`, `hasTesla: false`
  - site index card: title `뉴로모픽, 항상 켜진 AI의 감각층`, tags `Neuromorphic AI`, `Edge AI`, `Always-on AI`, `AIoT`, thumbnail `neuromorphic_everyday_ai_hero-web.png`, old card title absent.
  - screenshots:
    - `artifacts/final_review/verification/2026-06-21_everyday_edge_dist_desktop.png`
    - `artifacts/final_review/verification/2026-06-21_everyday_edge_dist_mobile_viewport.png`
    - `artifacts/final_review/verification/2026-06-21_everyday_edge_site_desktop.png`
- Obsidian mirror sync:
  - target: `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-06-05_neuromorphic-edge-ai`
  - mirror final review title: `뉴로모픽, 항상 켜진 AI의 감각층`
  - mirror final review references `neuromorphic_everyday_ai_hero-web.png`
  - mirror final review/dist search for `Tesla`, `NHTSA`, `자율주행`, `Boston`, `Atlas`, `Physical AI`, `물리적 AI의 반응` returned no hits.
- GitHub Pages deployment:
  - commit: `e0b4f1b` (`Reframe neuromorphic review around everyday edge AI`)
  - `Publish public report hub` run id: `27900978418`, status `completed`, conclusion `success`
  - `pages build and deployment` run id: `27900995407`, status `completed`, conclusion `success`
  - public URL: `https://infant83.github.io/AI_Tech_Review/reviews/2026-06-05_neuromorphic-edge-ai/`
  - public URL check: HTTP `200`, title `뉴로모픽, 항상 켜진 AI의 감각층`, `HasEverydayHero: true`, `HasOldHero: false`, `HasTesla: false`
- Distribution email:
  - sent via Gmail from `angpangmokjang@gmail.com` to `hyun-jung.kim@lgdisplay.com`
  - subject: `[AI Tech Review] 뉴로모픽 Edge AI 리뷰 배포본 공유`
  - attachment: `2026-06-05_neuromorphic-edge-ai\dist.zip`
  - Gmail message id: `19ee9ad32b0c59f5`

## 2026-06-22 Quanta reference flow revision

### 사용자 요청

- `퀀타가 남긴 세 가지 물음` 제목은 Quanta 페이지를 보고 나중에 덧붙인 글처럼 보이므로 수정할 것.
- Quanta Magazine 글들은 독립된 부록처럼 튀지 않게, 뉴로모픽 논의의 흐름 안에서 자연스럽게 참고되도록 전체 문맥을 조정할 것.

### 본문 반영

- H2를 `퀀타가 남긴 세 가지 물음`에서 `오래된 쟁점은 제품 조건으로 남았습니다`로 변경.
- Quanta 검색 결과 링크를 reader-facing References에서 제거하고, 2017 atomic-switch mesh, 2022 BrainScaleS-2, 2022 NeuRRAM 기사만 재료망, device mismatch, 데이터 이동 비용 문맥 안에 배치.
- `Quanta가 오래전부터 추적해 온...`처럼 source를 주어로 세우는 문장을 줄이고, Wang et al. 논문을 sensing-memory-compute 결합 흐름 안의 in-sensor neuromorphic vision 사례로 설명.
- `~라기보다`, `이어집니다`, 반복적인 `질문` 표현을 정리해 source-added 느낌과 AI식 대비 리듬을 줄임.

### 검증

- editorial audit:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
  - result: `h2_count: 13`, `figure_count: 7`, `figure_density: ok`, `finding_count: 0`
- HTML render:
  - `python scripts\markdown_to_html.py --mode auto .\2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.md`
- distribution package:
  - `python scripts\html_to_dist.py .\2026-06-05_neuromorphic-edge-ai\reports\2026-06-05_neuromorphic-edge-ai_final_review.html --dist .\2026-06-05_neuromorphic-edge-ai\dist --zip --zip-path .\2026-06-05_neuromorphic-edge-ai\dist.zip`
  - result: `[local-ref-check] ok`
- public site generation:
  - `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=8`
- Playwright dist check:
  - title: `뉴로모픽, 항상 켜진 AI의 감각층`
  - `hasNewHeading: true`
  - `hasOldHeading: false`
  - `hasSearchPhrase: false`
  - `imageCount: 7`
  - `brokenImages: []`
