# Skywork Prompt V1

업로드된 자료와 템플릿을 기반으로 새로운 Korean PowerPoint deck을 생성하라.

기본 템플릿 규칙:
- 사용자가 다른 템플릿을 명시하지 않았다면 `LGD_Template.pptx`를 기본 템플릿으로 사용하라.
- 템플릿은 source pack과 함께 기본 업로드 대상으로 간주하라.

프로젝트명: 기업 On-Prem 음성·회의록 스택 실전 검토
청중: AI 플랫폼 리드, 음성/ML 엔지니어, 인프라/보안 담당자, 기술전략 리더
목적: Picovoice를 중심으로 기업 on-prem STT/TTS/회의록 스택의 실용성을 평가하고, 실제 권장 아키텍처와 PoC 방향을 제시하는 기술 브리핑 deck
권장 분량: 12~14 slides
비율: 16:9

소스 우선순위:
1. 업로드된 `deepresearch.md`, `memo.md`, `sources.md`
2. 필요한 경우에만 문서 안에 이미 인용된 공식 소스 범위

리서치 정책:
- 업로드된 참고자료가 이미 공식 문서 기반으로 정리되어 있으므로 외부 리서치는 최소화하고, 구조화와 표현 정교화에 집중하라.
- 문서에 없는 새로운 수치나 벤더 비교를 임의로 추가하지 말라.
- 시의성 있는 기술 사실과 지원범위는 업로드된 자료의 fact anchor를 우선 기준으로 유지하라.

템플릿 원칙:
- LG Display 템플릿의 white-grid corporate rhythm은 유지하라.
- 브랜드형 sparse marketing deck이 아니라 정보 밀집형 technical briefing 스타일로 전개하라.
- 템플릿 블록이 허용하는 범위 안에서 표, 비교 보드, annotated diagram, dense memo slide를 적극 사용하라.

전체 서사:
- 왜 기업 on-prem speech stack 문제가 중요한지 제시하라.
- `STT/TTS가 된다`와 `회의록 시스템이 된다`는 다른 문제라는 점을 먼저 분리하라.
- Picovoice 각 구성요소의 실제 역할과 한계를 설명하라.
- 한국어 실시간 STT와 strict air-gap 제약을 핵심 리스크로 명확히 드러내라.
- Whisper/pyannote/llama.cpp 및 NVIDIA Riva와 비교해 실전 권고 아키텍처를 도출하라.
- 마지막은 90-day PoC와 의사결정 기준으로 닫아라.

섹션 정책:
- CH00: briefing, density=medium, evidence=explicit
- CH01: analysis, density=high, evidence=explicit
- CH02: internal_report, density=high, evidence=explicit
- CH03: analysis, density=high, evidence=explicit
- CH04: internal_report, density=high, evidence=explicit

반영해야 할 현재 사실:
- `Leopard`는 공식 docs 기준으로 Korean batch STT를 지원한다.
- `Orca`는 on-device / on-prem / LLM-oriented streaming TTS로 포지셔닝되어 있다.
- `Falcon`은 on-device diarization component다.
- `Cheetah`의 공식 docs는 visible language area와 formal language section이 일치하지 않으며, formal section만 보면 Korean streaming STT self-serve availability가 명확하지 않다.
- Picovoice는 local processing을 강조하지만, pricing 문서에는 AccessKey validation 및 plan limit 확인을 위한 call-home behavior가 명시되어 있다.
- 회의록 품질의 핵심 병목은 STT/TTS만이 아니라 diarization, segmentation, summarization, action-item extraction, workflow integration이다.
- 기본 실전 대안은 `whisper.cpp 또는 faster-whisper + pyannote + llama.cpp`이고, GPU-backed enterprise platform 대안은 `NVIDIA Riva`다.

권장 장표 구성:
- Slide 1: title + one-line decision
- Slide 2: why on-prem speech stack matters in enterprise
- Slide 3: `speech I/O` vs `meeting notes system` architecture breakdown
- Slide 4: Picovoice component map: Leopard / Cheetah / Orca / Falcon / picoLLM
- Slide 5: what Picovoice does well
- Slide 6: why Picovoice alone is not enough for enterprise meeting notes
- Slide 7: Korean streaming STT ambiguity + strict air-gap / AccessKey risk
- Slide 8: comparison table: Picovoice-centered vs Whisper stack vs Riva
- Slide 9: reference architecture A: local voice assistant
- Slide 10: reference architecture B: private meeting-note pipeline
- Slide 11: reference architecture C: enterprise-supported GPU speech platform
- Slide 12: 90-day PoC plan and go/no-go criteria
- Slide 13: closing recommendation for technical leaders

시각/레이아웃 정책:
- base template rhythm은 유지하라.
- 같은 카드형을 반복하지 말고 장표 목적에 따라 서브템플릿을 바꿔라.
- compound slide를 허용하되 하나의 상위 인사이트로 수렴시켜라.
- sparse marketing layout보다 구조화된 정보 밀집형 구성을 우선하라.
- 비교표, architecture block diagram, workflow strip, risk matrix를 적극 사용하라.
- 기술 용어, caveat, 운영 제약, deployment nuance는 작은 짙은 녹색 inline annotation text로 옆이나 아래에 붙일 수 있다.
- annotation은 별도 카드처럼 보이지 말고 관련 텍스트나 그림에 밀착시켜라.
- references가 필요한 slide에는 하단 또는 관련 블록 근처에 작은 짙은 회색 text로 공식 출처를 넣어라.

좋은 장표가 되기 위한 규칙:
- 한 슬라이드마다 하나의 상위 메시지를 유지하되, 실무 판단에 필요한 세부 비교는 숨기지 말라.
- 기술 리더가 바로 아키텍처 결정을 논의할 수 있을 정도로 information-dense 하게 만들어라.
- 실전 배치 제약, 한국어 지원 모호성, air-gap 리스크를 절대 흐리지 말라.

피해야 할 것:
- Picovoice를 완성형 enterprise meeting-note platform처럼 과장하지 말라.
- 확인되지 않은 benchmark, 모호한 지원언어, 임의의 수치를 넣지 말라.
- 큰 빈 공간 위주 미려한 deck로 약화시키지 말라.
- STT/TTS만 설명하고 meeting-note pipeline의 나머지 계층을 생략하지 말라.

이 기준으로 전체 deck을 생성하라.
