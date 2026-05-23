# 2026-04-11 Enterprise On-Prem Voice and Meeting Stack Memo

## One-Line Take

- `Picovoice는 기업 on-prem 환경에서 privacy-sensitive local voice I/O 계층으로는 유의미하지만, 한국어 회의록 생성의 주력 백본으로 단독 채택하기에는 아직 불확실성과 보완 필요 요소가 크다.`

## What Matters Most

- [Fact] `Leopard`는 한국어를 포함한 on-device batch STT를 공식 지원한다.
  - Source: https://picovoice.ai/docs/leopard/
- [Fact] `Orca`는 on-device / on-prem / LLM-oriented streaming TTS로 명확히 포지셔닝되어 있다.
  - Sources: https://picovoice.ai/docs/orca/, https://picovoice.ai/platform/orca/
- [Fact] `Falcon`이 존재하므로 Picovoice는 STT/TTS만이 아니라 diarization building block도 제공한다.
  - Source: https://picovoice.ai/docs/falcon/
- [Fact] 다만 `Cheetah`의 최신 docs는 상단 노출 언어와 `Languages` 섹션 설명이 일치하지 않는다. 공식 언어 설명에는 한국어가 self-serve 지원 목록에 명확히 들어가 있지 않다.
  - Source: https://picovoice.ai/docs/cheetah/
- [Inference] 따라서 `한국어 실시간 기업 회의 STT`를 Picovoice 단독으로 설계하려면 상용 문의 전제의 검증 항목이 남아 있다.
- [Fact] Picovoice는 처리 자체는 local이라고 밝히지만, plan validation을 위해 `AccessKey` 기반 call-home behavior도 명시한다.
  - Source: https://picovoice.ai/pricing/
- [Inference] 이 때문에 `strict air-gap` 환경에서는 `on-device`라는 표현만 보고 바로 도입 결론을 내리면 안 된다.
- [Fact] 회의록 품질은 STT/TTS보다 `diarization`, `punctuation`, `segmentation`, `summarization`, `action-item extraction`, `workflow integration`에 더 크게 좌우된다.
  - Sources: https://github.com/openai/whisper, https://github.com/pyannote/pyannote-audio, https://github.com/ggml-org/llama.cpp

## Practical Reading

- `Picovoice가 좋은 곳`
  - endpoint voice assistant
  - privacy-first local voice UX
  - local TTS response
  - CPU-friendly on-device interaction layer
- `Picovoice만으로 부족한 곳`
  - 완성형 회의록 생성
  - 한국어 다자 회의 diarized transcription
  - 구조화된 action-item extraction 파이프라인
  - 엄격한 disconnected on-prem 운영

## Recommended Default Architecture

- `회의록 생성`이 목표라면 기본 추천은 아래와 같다.
  - STT: `whisper.cpp` 또는 `faster-whisper`
  - diarization: `pyannote`
  - summarization: `llama.cpp` 기반 local LLM server
  - optional TTS: 필요할 때만 `Orca`
- GPU 기반 기업 표준화가 필요하면 `NVIDIA Riva`도 강한 대안이다.

## Slide Framing If Promoted Later

- `What on-prem speech stack really means`
- `Picovoice as local voice I/O, not full meeting notes`
- `Why meeting notes are harder than STT`
- `Korean enterprise deployment risks`
- `Reference architectures: Picovoice vs Whisper stack vs Riva`
