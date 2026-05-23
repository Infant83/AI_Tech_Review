# Executive Summary

- [Fact] `Picovoice`는 `Leopard STT`, `Cheetah streaming STT`, `Orca streaming TTS`, `Falcon diarization`, `picoLLM` 등으로 구성된 `local-first voice stack`을 제공하며, 공식 문서와 제품 페이지는 이를 `on-device`, `on-prem`, `privacy/compliance-oriented` 아키텍처로 포지셔닝한다.
  Sources: https://picovoice.ai/docs/leopard/, https://picovoice.ai/docs/cheetah/, https://picovoice.ai/docs/orca/, https://picovoice.ai/docs/falcon/, https://picovoice.ai/blog/on-device-llm-powered-voice-assistant/
- [Fact] `Leopard`는 한국어 batch STT를 공식 지원한다.
  Source: https://picovoice.ai/docs/leopard/
- [Fact] `Orca`는 LLM용 streaming TTS로서 `cloud, on-prem, on-device`를 명시적으로 언급한다.
  Sources: https://picovoice.ai/docs/orca/, https://picovoice.ai/platform/orca/
- [Fact] 그러나 `Cheetah` 문서는 상단 노출 언어와 formal language section 사이에 불일치가 있고, `Languages` 섹션 기준으로는 영어/프랑스어/독일어/이탈리아어/포르투갈어/스페인어만 self-serve로 명시하며 다른 언어는 Enterprise 문의 대상으로 둔다.
  Source: https://picovoice.ai/docs/cheetah/
- [Inference] 따라서 `한국어 실시간 on-prem 회의 전사`를 Picovoice 단독으로 설계하는 것은 `기술 가능성`보다 `상용 제공범위/운영조건 확인`이 먼저다.
- [Fact] Picovoice는 데이터 처리는 로컬이라고 설명하지만, 동시에 `AccessKey` 검증과 plan limit 확인을 위해 엔진이 call-home 한다고 명시한다.
  Source: https://picovoice.ai/pricing/
- [Inference] 이 점은 `strict air-gap` 또는 `fully disconnected` 환경에서 중요한 리스크다. `on-device`라는 표현만으로 `완전 오프라인 운영`을 가정하면 안 된다.
- [Fact] 회의록 품질은 `STT/TTS 자체`보다 `speaker diarization`, `punctuation`, `segmentation`, `summarization`, `action-item extraction`, `system integration`이 더 큰 영향을 미친다. 이 영역에서 `Whisper`, `whisper.cpp`, `faster-whisper`, `pyannote`, `llama.cpp`, `NVIDIA Riva`가 각각 강한 building block을 제공한다.
  Sources: https://github.com/openai/whisper, https://github.com/ggml-org/whisper.cpp, https://github.com/SYSTRAN/faster-whisper, https://github.com/pyannote/pyannote-audio, https://github.com/ggml-org/llama.cpp, https://docs.nvidia.com/deeplearning/riva/user-guide/docs/public/overview.html
- [Inference] 결론적으로 `Picovoice`는 `기업 on-prem 회의록 시스템의 주력 백본`이라기보다 `로컬 음성 인터랙션 계층` 또는 `보조 voice component layer`로 보는 해석이 더 정확하다.

# Scope

이 문서는 `2026-04-11` 기준으로 다음 질문에 답한다.

- Picovoice 계열 기술이 일반 기업의 on-prem 환경에서 STT/TTS 및 회의록 작성 기술로 활용될 수 있는가?
- `활용될 수 있다면 어디까지인가?`
- `회의록 작성`이라는 현실 업무를 기준으로 볼 때 무엇이 빠져 있는가?
- `Whisper 계열`, `pyannote`, `llama.cpp`, `NVIDIA Riva`와 비교하면 어디에 위치하는가?

교실, 특수교육, AAC, 수업 운영 맥락은 여기서 제외한다.

# Why This Question Matters

기업이 `on-prem speech stack`을 검토하는 이유는 대체로 네 가지다.

- 회의 음성이 외부 API로 나가면 안 된다.
- 규제/보안 때문에 private network 또는 폐쇄망이 필요하다.
- 실시간 상호작용은 클라우드 round-trip latency에 민감하다.
- 회의록은 단순 전사보다 `구조화된 업무 산출물`이어야 한다.

이 마지막 항목이 중요하다. `회의록 생성`은 보통 다음 다단계 파이프라인이다.

1. audio capture / denoise / VAD
2. STT
3. punctuation / timestamp normalization
4. diarization / speaker attribution
5. transcript chunking
6. summarization / decision extraction / action items
7. storage / search / compliance logging

[Inference] 따라서 `STT/TTS가 되느냐`와 `회의록 시스템이 되느냐`는 같은 질문이 아니다.

# Picovoice Component Evaluation

## Leopard

- [Fact] Leopard는 on-device STT 엔진이며 `English, French, German, Italian, Japanese, Korean, Portuguese, Spanish`를 공식 지원한다고 적혀 있다.
  Source: https://picovoice.ai/docs/leopard/
- [Fact] custom vocabulary와 keyword boosting을 Picovoice Console에서 제공한다.
  Source: https://picovoice.ai/docs/leopard/
- [Inference] 이는 `도메인 용어가 많은 기업 회의 전사`에 분명한 장점이다.
- [Inference] 하지만 Leopard는 기본적으로 `파일/배치 전사` 성격이 강하므로 `회의 중 실시간 협업 UI`의 핵심 엔진으로 쓸 때는 latency와 UX 요구를 별도 확인해야 한다.

## Cheetah

- [Fact] Cheetah는 on-device streaming STT 엔진이다.
  Source: https://picovoice.ai/docs/cheetah/
- [Fact] docs의 formal language section은 현재 지원 언어를 `English, French, German, Italian, Portuguese, and Spanish`로 적고, 다른 언어는 Enterprise 고객이 문의하라고 적는다.
  Source: https://picovoice.ai/docs/cheetah/
- [Fact] 같은 페이지 상단 노출 영역에는 `Japanese`와 `Korean`이 보이기 때문에 문서 표현이 일관되지 않는다.
  Source: https://picovoice.ai/docs/cheetah/
- [Inference] 이것은 단순한 문서 사소함이 아니라 구매/설계 리스크다. `한국어 실시간 STT`가 self-serve인지, Enterprise custom인지, 혹은 문서 localization 표기인지가 명확하지 않다.
- [Inference] 따라서 `한국어 enterprise meeting copilot`을 Picovoice Cheetah로 전제하는 것은 현재 문서만으로는 방어하기 어렵다.

## Orca

- [Fact] Orca는 streaming TTS이며 LLM 응답이 생성되는 동안 동시에 합성해 humanlike interaction을 만든다고 설명한다.
  Sources: https://picovoice.ai/platform/orca/, https://picovoice.ai/blog/on-device-text-to-speech/
- [Fact] Picovoice는 Orca를 `embedded, mobile, web, desktop, on-prem, private, or public cloud`에 둘 수 있다고 밝힌다.
  Source: https://picovoice.ai/blog/on-device-text-to-speech/
- [Inference] 이는 `로컬 voice assistant`, `회의 비서 playback`, `IVR`, `call-center assist` 같은 use case에는 잘 맞는다.
- [Inference] 하지만 회의록 생성 자체만 본다면 TTS는 핵심이 아니다. TTS는 부가 UX 계층이며, 아키텍처 선택을 좌우하는 1순위가 아니다.

## Falcon

- [Fact] Falcon은 on-device speaker diarization 엔진이다.
  Source: https://picovoice.ai/docs/falcon/
- [Fact] Picovoice는 `who spoke when` 문제를 해결하는 fundamental step으로 diarization을 설명한다.
  Source: https://picovoice.ai/docs/falcon/
- [Inference] 회의록 파이프라인 관점에서 Falcon의 존재는 중요하다. Picovoice가 단순 STT/TTS를 넘어 multi-speaker processing까지 노리고 있음을 보여준다.
- [Inference] 다만 diarization accuracy, overlapping speech behavior, Korean meeting acoustic conditions에 대한 독립 검증은 별도 필요하다.

## AccessKey and deployment model

- [Fact] Picovoice pricing 문서는 엔진이 로컬 처리되며 end-user data를 remote server에 보내지 않는다고 설명한다.
  Source: https://picovoice.ai/pricing/
- [Fact] 동시에 `AccessKey` 검증과 usage limit 확인을 위해 engine이 call-home 한다고 적혀 있다.
  Source: https://picovoice.ai/pricing/
- [Inference] 이 구조는 `private network`에는 적합할 수 있으나, `strict air-gap`에는 별도 예외 처리나 enterprise agreement가 필요할 가능성이 높다.

# Meeting Notes Are Harder Than Speech I/O

## What a meeting-note system actually needs

- high-quality multilingual ASR
- word/segment timestamps
- punctuation and capitalization
- speaker diarization
- optional speaker identification
- long-context summarization
- action item extraction
- document / calendar / chat integration
- governance and retention controls

## Why STT/TTS alone do not solve it

- STT가 좋아도 speaker attribution이 틀리면 회의록 신뢰도가 떨어진다.
- diarization이 좋아도 summary model이 약하면 action item이 빠진다.
- summary model이 좋아도 transcript segmentation이 나쁘면 hallucination risk가 커진다.
- TTS는 회의록 산출물의 핵심 가치가 아니라 보조 인터페이스다.

[Inference] 따라서 `Picovoice가 STT/TTS를 제공한다`는 사실은 `Picovoice가 meeting note platform이다`와 다르다.

# Comparison With Alternative Stacks

## 1. Whisper / whisper.cpp / faster-whisper

- [Fact] OpenAI Whisper는 multilingual speech recognition, speech translation, language identification 등을 수행하는 general-purpose ASR model이다.
  Source: https://github.com/openai/whisper
- [Fact] whisper.cpp는 Whisper를 C/C++로 옮긴 구현으로, CPU-only inference, quantization, Windows/Linux/macOS/Raspberry Pi, fully offline on-device use를 강조한다.
  Source: https://github.com/ggml-org/whisper.cpp
- [Fact] faster-whisper는 CTranslate2 기반 구현으로, openai/whisper 대비 더 빠르고 메모리 사용량이 낮다고 스스로 benchmark를 제시한다.
  Source: https://github.com/SYSTRAN/faster-whisper

[Inference] 회의 전사 자체만 보면 Whisper 계열은 이미 `batch transcription backbone`으로 매우 강한 기본값이다. 특히 `whisper.cpp`는 폐쇄망/온프렘 내장형에, `faster-whisper`는 서버형 throughput 개선에 적합하다.

## 2. pyannote-audio

- [Fact] pyannote는 `community-1` diarization pipeline이 `runs locally`라고 명시한다.
  Source: https://github.com/pyannote/pyannote-audio
- [Fact] pyannote는 diarization을 `who spoke when` 문제로 규정하고, meeting transcription / call center analytics / voice agents에 직접 연결한다.
  Source: https://github.com/pyannote/pyannote-audio
- [Fact] 공식 repo는 optional telemetry에 대해 공개적으로 설명한다.
  Source: https://github.com/pyannote/pyannote-audio

[Inference] 기업 on-prem 회의록 파이프라인에서 pyannote는 Picovoice Falcon의 오픈 대체재이자 비교 기준이다. 다만 Hugging Face token, model acquisition path, optional telemetry governance는 운영 검토가 필요하다.

## 3. llama.cpp

- [Fact] llama.cpp는 local LLM inference 엔진이며 `llama-server`로 OpenAI-compatible HTTP server를 제공한다.
  Source: https://github.com/ggml-org/llama.cpp
- [Inference] 이는 `회의 전사 -> 요약 -> 액션아이템 -> JSON structure`를 사내망에서 처리하는 마지막 계층으로 매우 적합하다.

## 4. NVIDIA Riva

- [Fact] Riva는 GPU-accelerated speech SDK로, on premises or in the cloud deployment, streaming/offline ASR, TTS, punctuation, diarization, gRPC microservices를 제공한다.
  Sources: https://docs.nvidia.com/deeplearning/riva/user-guide/docs/public/overview.html, https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-overview.html
- [Fact] Riva는 pretrained models와 NeMo fine-tuning, Triton inference server, Helm deployment까지 포함한 enterprise platform 성격이 강하다.
  Source: https://docs.nvidia.com/deeplearning/riva/user-guide/docs/public/overview.html

[Inference] GPU 인프라와 vendor-backed 운영모델이 필요한 기업에는 `Riva`가 Picovoice보다 `meeting-note platform`에 더 가깝다.

# Decision Table

| Stack | Strongest fit | Main strengths | Main risks | Best read |
| --- | --- | --- | --- | --- |
| Picovoice-centered | local voice assistant, edge voice UX, privacy-sensitive interaction | on-device design, cross-platform SDKs, local STT/TTS/diarization components | Korean streaming STT ambiguity, AccessKey call-home, meeting-note completeness gap | `voice I/O layer` |
| Whisper.cpp + pyannote + llama.cpp | private enterprise meeting notes on commodity infra | offline ASR, modularity, local summarization, strong controllability | more assembly work, model ops burden, diarization tuning | `best pragmatic local stack` |
| faster-whisper + pyannote + llama.cpp | higher-throughput server transcription + local notes | speed/memory efficiency, server-friendly | integration burden remains | `best software-defined server stack` |
| NVIDIA Riva | GPU-backed enterprise speech platform | ASR/TTS/diarization/punctuation, deployment tooling, vendor ecosystem | GPU cost, platform complexity, NVIDIA dependency | `enterprise speech platform` |

# Korean Enterprise Risk Table

| Risk area | What is known | Why it matters |
| --- | --- | --- |
| Korean batch STT | Leopard officially lists Korean | batch file transcription is viable in principle |
| Korean streaming STT | Cheetah docs are ambiguous; formal language section does not clearly self-serve Korean | real-time meeting copilot commitment is risky without vendor confirmation |
| Air-gap suitability | Picovoice says processing is local but AccessKey validation calls home | strict disconnected deployments need explicit contractual/technical validation |
| Meeting diarization | Falcon exists, pyannote and Riva alternatives also exist | speaker attribution quality directly impacts note reliability |
| Meeting summary quality | requires local LLM layer such as llama.cpp or other on-prem LLM server | ASR alone is not the business output |
| TTS necessity | optional for meeting-note workflows | TTS should not drive stack selection unless voice playback is a real requirement |

# Recommended Reference Architectures

## A. Lightweight local assistant on endpoints

Use when the goal is `private voice interaction`, not high-fidelity meeting notes.

- VAD: Picovoice Cobra
- STT: Picovoice Cheetah where supported
- optional batch STT: Picovoice Leopard
- TTS: Picovoice Orca
- local reasoning: picoLLM or local LLM

[Inference] 이것은 `voice agent` 설계에는 적합하지만 `회의록 시스템`으로 그대로 확대하는 것은 별도 문제다.

## B. Private meeting-note pipeline on commodity infrastructure

Use when the goal is `회의 녹음 -> 회의록 -> action items` and GPU budget is moderate.

- STT: whisper.cpp or faster-whisper
- diarization: pyannote
- summarization / extraction: llama.cpp
- optional TTS: Orca only if voice playback is needed

[Inference] 대부분의 일반 기업 on-prem 환경에서 가장 실용적인 기본값은 이 구조다.

## C. Enterprise-supported GPU speech platform

Use when the goal is `production speech services at scale` with vendor-backed deployment patterns.

- speech backbone: NVIDIA Riva
- model customization: NeMo / Riva pipeline
- summarization: local LLM service
- integration: enterprise workflow systems

[Inference] 인프라 여건이 된다면 Riva가 `speech platform completeness` 측면에서는 Picovoice보다 더 직접적이다.

# Practical Recommendation

## If the enterprise wants meeting notes

기본 권고는 다음과 같다.

1. `Picovoice를 회의록 주력 엔진으로 먼저 잡지 말 것`
2. `Whisper 계열 + diarization + local LLM`을 기준선으로 잡을 것
3. voice playback or local assistant UX가 필요할 때만 `Orca`나 Picovoice 계층을 추가할 것
4. strict air-gap이 필요하다면 AccessKey/call-home 정책을 계약 전에 검증할 것

## If the enterprise wants a local voice assistant

이 경우 Picovoice는 더 강하다.

- CPU/edge deployment
- privacy-first UX
- cross-platform SDK
- low-latency voice loop

[Inference] 요약하면 `회의록`보다는 `음성 인터랙션`에서 Picovoice의 가치가 더 분명하다.

# 90-Day PoC Plan

## Goal

`한국어 기업 회의 음성`을 사내망에서 안전하게 `전사 + 화자 분리 + 요약 + 액션아이템`까지 처리하는 기준 아키텍처를 선정한다.

## Candidate stacks

1. `Leopard + Falcon + local LLM`
2. `whisper.cpp + pyannote + llama.cpp`
3. `faster-whisper + pyannote + llama.cpp`
4. `NVIDIA Riva + local LLM`

## Metrics

- WER
- diarization error or speaker attribution precision
- end-to-end latency
- 60분 회의 처리 시간
- hardware footprint
- network dependency
- admin complexity
- note usefulness score

## Test set

- 한국어 1:1 회의
- 한국어 3~5인 회의
- 혼합 화자 overlap이 있는 회의
- 기술 용어가 많은 내부 회의
- 개인정보/고유명사가 자주 나오는 회의

## Go / No-Go gates

- 한국어 meeting-note usefulness가 baseline human expectation을 넘는가
- private network에서 운영 가능한가
- strict disconnected requirement를 충족하는가
- speaker attribution이 실무 수용 수준인가
- 운영팀이 유지 가능한 복잡도인가

# Bottom Line

`as of 2026-04-11`, Picovoice는 `기업 on-prem 음성 처리`에서 무시할 기술이 아니다. 다만 가장 정확한 포지션은 `회의록 전용 주력 백본`이 아니라 `로컬 음성 인터랙션과 일부 speech components를 위한 고품질 building block`이다.

회의록 생성이 목표라면:

- 기본 축은 `Whisper 계열 + diarization + local LLM`
- Picovoice는 `Orca`, `Falcon`, 일부 STT 보조 계층 또는 endpoint assistant 용도로 붙이는 구조

이 해석이 현재 공식 문서와 운영 제약을 가장 잘 반영한다.

# References

- Picovoice Leopard docs
  - https://picovoice.ai/docs/leopard/
- Picovoice Cheetah docs
  - https://picovoice.ai/docs/cheetah/
- Picovoice Orca docs
  - https://picovoice.ai/docs/orca/
- Picovoice Falcon docs
  - https://picovoice.ai/docs/falcon/
- Picovoice pricing
  - https://picovoice.ai/pricing/
- Picovoice on-device LLM assistant
  - https://picovoice.ai/blog/on-device-llm-powered-voice-assistant/
- Picovoice Orca platform page
  - https://picovoice.ai/platform/orca/
- Picovoice leopard platform page
  - https://picovoice.ai/platform/leopard/
- Picovoice voice command control use case
  - https://picovoice.ai/use-cases/voice-command-control/
- OpenAI Whisper
  - https://github.com/openai/whisper
- whisper.cpp
  - https://github.com/ggml-org/whisper.cpp
- faster-whisper
  - https://github.com/SYSTRAN/faster-whisper
- pyannote-audio
  - https://github.com/pyannote/pyannote-audio
- llama.cpp
  - https://github.com/ggml-org/llama.cpp
- NVIDIA Riva overview
  - https://docs.nvidia.com/deeplearning/riva/user-guide/docs/public/overview.html
- NVIDIA Riva ASR overview
  - https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-overview.html
- NVIDIA Riva TTS quick start
  - https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide/tts.html
