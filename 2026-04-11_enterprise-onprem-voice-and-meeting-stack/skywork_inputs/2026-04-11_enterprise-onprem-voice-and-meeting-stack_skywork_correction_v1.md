# Skywork Correction Packet V1

현재 deck을 전체 폐기하지 말고, 이미 잘 된 템플릿 스타일과 전체 서사를 유지한 채 `2차 보정`하라.

이번 수정의 목적:

- 현재 draft에서 비어 있거나 placeholder가 남은 장표를 실질적인 기술 브리핑 장표로 완성한다.
- 이미 좋은 장표의 서사, 톤, LGD 템플릿 리듬은 유지한다.

전역 원칙:

- 전체를 다시 만들지 말고 `슬라이드 4, 9, 10, 11, 12`를 중심으로 정밀 보정하라.
- 슬라이드 1, 2, 3, 5, 6, 7, 8, 13은 현재 구조와 메시지를 크게 바꾸지 말고, 필요하면 placeholder나 footer 잡음만 정리하라.
- `페이지 제목 / Page title`, `헤드라인 / Headline` 같은 템플릿 placeholder text를 남기지 말라.
- 비어 있는 architecture 장표를 제목만 있는 slide로 두지 말라.
- 각 장표는 `주장 -> 근거 -> 시사점` 구조가 보이게 하라.
- `PUBLIC`, 날짜, LG Display footer는 유지 가능하지만 중복되거나 깨진 텍스트는 제거하라.
- sparse marketing deck으로 바꾸지 말고 정보 밀도가 높은 technical briefing으로 유지하라.
- 새 수치나 미검증 비교는 추가하지 말고, 업로드된 deepresearch/memo/sources 기준의 사실만 사용하라.

반드시 유지할 사실:

- `Leopard`는 Korean batch STT를 공식 지원한다.
- `Orca`는 on-device / on-prem / streaming TTS 용도다.
- `Falcon`은 diarization component다.
- `Cheetah`의 Korean streaming STT self-serve availability는 문서상 모호하다.
- Picovoice pricing 문서에는 AccessKey validation / plan-limit 확인을 위한 call-home behavior가 있다.
- 회의록 품질 병목은 STT/TTS 자체보다 diarization, segmentation, summarization, action-item extraction, workflow integration이다.
- 실전 기본 대안은 `whisper.cpp 또는 faster-whisper + pyannote + llama.cpp`다.
- GPU-backed enterprise 대안은 `NVIDIA Riva`다.

슬라이드별 수정 지시:

- 슬라이드 4:
  - 현재는 제목만 남아 있으므로 `Picovoice component map`을 실제 내용으로 채워라.
  - 권장 형식은 `component map table + usage lane`.
  - 최소 포함 항목:
    - `Leopard`: batch STT / Korean official support / file transcription fit
    - `Cheetah`: streaming STT / Korean self-serve ambiguity / real-time risk
    - `Falcon`: diarization / speaker attribution role
    - `Orca`: streaming TTS / local voice UX role / meeting notes core는 아님
    - 필요시 `picoLLM` 또는 local orchestration layer는 보조 박스로 표현
  - 핵심 메시지:
    - Picovoice는 하나의 완성형 회의록 플랫폼이 아니라 `voice component stack`이다.

- 슬라이드 9:
  - `Reference Architecture A: local voice assistant`를 실제 diagram으로 완성하라.
  - 권장 구조:
    - `Mic / Wake word / local audio front-end`
    - `intent or local agent layer`
    - `Leopard or Cheetah where available`
    - `Orca TTS`
    - optional `local LLM / tool router`
  - 하단에 작은 note:
    - 이 아키텍처는 `low-latency local voice UX`에는 적합하지만 `meeting minutes backbone`과는 목적이 다르다.

- 슬라이드 10:
  - `Reference Architecture B: private meeting-note pipeline`을 실제 diagram + control points로 완성하라.
  - 권장 구조:
    - `recorded/live meeting audio`
    - `ASR: whisper.cpp or faster-whisper`
    - `diarization: pyannote or Falcon`
    - `segmentation / punctuation`
    - `local LLM summarization`
    - `action item extraction`
    - `document / chat / workflow integration`
  - slide 안에서 명확히 보여줄 것:
    - business value는 STT가 아니라 structured minutes output에서 나온다.

- 슬라이드 11:
  - `NVIDIA Riva` 장표에서 placeholder를 모두 제거하라.
  - 제목은 명확한 한국어 제목으로 바꿔라.
    - 예: `권장 아키텍처 C: NVIDIA Riva 기반 엔터프라이즈 음성 플랫폼`
  - 내용은 아래 블록 중심으로 재구성:
    - `Riva ASR`
    - `Riva diarization / punctuation`
    - `Riva TTS`
    - `NeMo tuning / Triton / deployment tooling`
    - `local LLM summary layer`
    - `GPU infra / vendor dependency / platform complexity`
  - 핵심 메시지:
    - Riva는 GPU 인프라가 있을 때 enterprise speech platform completeness가 높다.

- 슬라이드 12:
  - `90일 PoC 계획` 장표에서 placeholder와 오타성 표현을 모두 정리하라.
  - 3단계 timeline은 유지하되 읽기 쉬운 execution board로 다시 구성하라.
  - 반드시 포함:
    - `Day 1-30`: data set, closed-network deployment, baseline measurement
    - `Day 31-60`: Picovoice vs Whisper stack vs Riva comparative validation
    - `Day 61-90`: workflow integration, operator review, go/no-go decision
    - 정량 지표:
      - WER
      - DER
      - latency / throughput
    - 정성 지표:
      - operator usefulness
      - closed-network operability
      - integration burden
  - 잘못된 문구 예:
    - `오폰소스 기존선 유지`
  - 이런 표현은 제거하고 자연스럽고 전문적인 한국어로 교체하라.

- 전 장표 공통 정리:
  - 중복 footer token, placeholder, 혼합 언어 찌꺼기, 잘린 문구를 제거하라.
  - title은 모두 실제 의미 있는 한국어 제목으로 정리하라.
  - 참고 출처는 필요 시 작은 짙은 회색 텍스트로 유지하라.

표현 형식:

- thesis + evidence rail
- source comparison board
- annotated architecture workflow
- dense internal technical briefing

금지:

- 현재 잘 된 슬라이드 전체를 과도하게 다시 쓰지 말라.
- 비어 있는 장표를 장식성 아이콘 슬라이드로 대체하지 말라.
- placeholder를 남기지 말라.
- Picovoice를 완성형 meeting-note platform처럼 과장하지 말라.
