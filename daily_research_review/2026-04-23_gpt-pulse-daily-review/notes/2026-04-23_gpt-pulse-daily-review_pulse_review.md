# 2026-04-23 GPT Pulse Review

## Topline
- `2026-04-23` Pulse는 단일 AI 뉴스 라운드업이 아니라 `포용교육`, `MLOps/에이전트 거버넌스`, `중동 지정학 리스크`, `온디바이스 음성 실험`, `OLED 상용화 신호`를 섞은 개인화 피드였다.
- 심층리서치로 바로 승격할 가치가 가장 큰 묶음은 `OTel 기반 에이전트 추적성 + GitLab OIDC/CI_JOB_TOKEN 운영 보안`이다.
- 기존 워크스페이스 흐름과 이어지는 후속 후보는 `LGD OLED 인프라 투자 + Fraunhofer 2K OLED microdisplay + SID Display Week 2026`이다.
- Pulse의 상세 카드에서는 source label은 보였지만 외부 URL이 DOM에 노출되지 않았다. 따라서 이 리뷰의 결론은 `Pulse intake triage`이며, 승격 전에는 공식 문서와 원문 보도로 재검증해야 한다.

## Card Review

### 1. Education and Inclusion
- `2026년 4-5월 포용교육 마이크로 그랜트 모집`은 한국문화예술교육진흥원, KERIS, KODDI, 사랑의열매 계열 공모/입찰을 한 묶음으로 제시했다.
- 실무 가치는 있다. 교육방송연구대회, 포용교육 콘텐츠, 현장 연구계획서 작성과 바로 연결될 수 있다.
- 다만 마감일과 신청 자격이 민감하므로, 이 카드는 깊게 쓰기 전에 각 기관 공고 원문 확인이 필요하다.
- `포용교육 단편 영상 콘티 제안`은 이미 실행 산출물에 가깝다. 90-120초 영상 콘티, 교사 언어 모델링, 또래 지원, 부모 성찰 질문까지 포함한다.
- 이 묶음은 기술 리뷰보다는 교육 콘텐츠 제작 패키지로 승격하는 편이 자연스럽다.

### 2. MLOps and Agent Governance
- `OIDC ID 토큰과 CI Job 토큰 수명 관리`는 GitLab CI/CD 보안 운영에 직접 연결된다.
- Pulse의 핵심 메시지는 레거시 `CI_JOB_JWT*` 대신 `id_tokens` 기반 OIDC 흐름을 쓰고, `aud` 지정, 수신측 claim 바인딩, 민감 job의 timeout 단축, `CI_JOB_TOKEN` allowlist 최소화를 하라는 것이다.
- 이 카드는 실무 체크리스트와 마이그레이션 diff로 바로 바꿀 수 있다.
- `OTel 기반 에이전트 추적성 청사진`은 에이전트 계획을 root trace로, tool call을 child span으로 남기는 구조를 제안한다.
- Pulse가 제안한 속성 세트는 `trace_id`, `actor`, `plan`, `tool`, input/output hash/ref, artifact id, provenance signature, redaction flag, retention policy까지 포함한다.
- 이 묶음은 `엔터프라이즈 에이전트 운영 감사성` 심층리서치의 가장 좋은 후보이며, Skywork deck으로도 확장 가치가 크다.

### 3. Geopolitical Risk
- `미군, 오만만서 이란 화물선 'Touska' 나포`와 `미국, 이라크 달러 현금 수송 중단`은 Pulse가 지정학/해운/금융 리스크 신호로 제시한 항목이다.
- Touska 카드는 미군의 이란 선박 나포, 이란 측 반발, 해상 보험 및 에너지 항로 리스크를 강조한다.
- 이라크 달러 현금 수송 중단 카드는 약 4.5억-5억 달러 규모의 물리적 현금 수송 지연과 일부 안보 협력 유예를 금융/외교 레버리지로 해석한다.
- 두 카드는 중요하지만 현재 뉴스성 주제라 사실관계 변화가 빠르다. 이 워크스페이스의 기본 기술리뷰 흐름에서는 `monitor`로 두고, 별도 전략/리스크 브리프를 원할 때만 승격하는 편이 맞다.

### 4. On-Device STT/TTS
- `온디바이스 STT/TTS 10분 미니 벤치마크`는 `whisper.cpp`, `VOSK`, `jiwer`, Coqui/OpenTTS 계열을 써서 로컬 한국어 STT 품질과 지연시간을 빠르게 측정하는 실험안을 제시했다.
- 이 카드는 이전 `교실 프라이버시 도구`, `온프레미스 음성/회의 스택`과 이어지는 실험형 후속 과제다.
- 심층리서치보다는 `로컬 벤치마크 스크립트 + 결과표 + 프라이버시 평가` 형태의 짧은 실험 패키지로 승격하는 것이 가장 실용적이다.

### 5. OLED / Display Week Signals
- `SID 전 10일 주목 신호 - LGD/Fraunhofer`와 `LG디스플레이 OLED 투자, 연구개발에 미칠 영향`은 기존 `blue OLED / Display Week` 흐름과 직접 이어진다.
- Pulse는 LG Display의 2026년 4월 OLED 인프라 투자와 Fraunhofer IPMS의 OLED microdisplay 발표를 함께 묶어 `대형 패널 제조 인프라 + 마이크로디스플레이 프로토타입 readiness` 신호로 읽는다.
- 이 해석은 유용하지만, blue emitter/TADF/PHOLED 상용화 자체를 증명하는 것은 아니다.
- 승격한다면 질문은 `LGD capex가 blue OLED 상용화와 어디까지 직접 연결되는가`가 아니라 `Display Week 2026 전후 OLED 생태계 신호를 어떻게 분류할 것인가`로 잡는 편이 정확하다.

## Promotion Candidates
- 1순위: `Agent observability and CI workload identity governance`
  - 이유: GitLab OIDC, CI job token scoping, OTel GenAI/agent span, provenance를 한 번에 다룰 수 있다.
  - 예상 산출물: 실무 체크리스트, reference architecture, migration risk matrix, Skywork technical deck.
- 2순위: `Display Week 2026 OLED signal review`
  - 이유: 기존 OLED 패키지와 연결성이 높고, LGD/Fraunhofer 신호를 검증형 리뷰로 확장할 수 있다.
  - 예상 산출물: signal taxonomy, evidence ladder, what-to-watch checklist.
- 3순위: `On-device Korean STT/TTS privacy benchmark`
  - 이유: 작은 실험으로 바로 결과를 만들 수 있고, 교실/회의/온프레미스 음성 스택과 연결된다.
  - 예상 산출물: benchmark script, WER/latency table, deployment note.
- 보류: `Education grant intake`
  - 이유: 신청 마감과 자격 확인이 핵심이라, 기술 심층리서치보다는 공모 대응/콘텐츠 제작 워크플로가 더 적합하다.
- 보류: `Touska / Iraq dollar shipment risk`
  - 이유: 뉴스성 사실관계 변동성이 높고, 기술리뷰 기본 흐름과 거리가 있다. 별도 지정학 리스크 브리프로 요청될 때 다루는 것이 적절하다.

## Immediate Recommendation
- 다음 심층리서치 대상으로는 `Agent observability and CI workload identity governance`를 추천한다.
- 이유는 단순하다. 오늘 Pulse 안에서 기술적 밀도, 실무 적용성, 기존 워크스페이스의 DevOps/agent 운영 관심사와의 접점이 가장 크다.
- OLED 신호는 두 번째 후보로 유지한다. 기존 Display Week 패키지의 연장선으로 좋지만, 오늘 새로 시작하기에는 이미 유사 패키지가 있다.
