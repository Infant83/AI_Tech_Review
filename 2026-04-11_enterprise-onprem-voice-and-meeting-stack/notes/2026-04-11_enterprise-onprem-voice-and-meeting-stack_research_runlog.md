---
title: 2026-04-11 Enterprise On-Prem Voice and Meeting Stack - Research Run Log
date: 2026-04-11
topic: 2026-04-11_enterprise-onprem-voice-and-meeting-stack
tags:
  - runlog
  - research
  - official-sources
---

# 2026-04-11 Enterprise On-Prem Voice and Meeting Stack - Research Run Log

## Run Summary

- Run date: `2026-04-11`
- Research mode: `direct official-source validation in Codex`
- Intake origin: `2026-04-11_gpt-pulse-daily-review`의 Picovoice/STT 카드
- Scope shift:
  - from `privacy-preserving classroom AI stack`
  - to `enterprise on-prem speech / meeting-note architecture`

## Execution Path

1. Existing Pulse intake note에서 `Picovoice` 관련 카드와 메모를 재확인했다.
2. Picovoice 공식 문서와 공식 페이지를 다시 조회했다.
3. 대체 스택 비교를 위해 공식 GitHub / 공식 문서 기반으로 Whisper, whisper.cpp, faster-whisper, pyannote, llama.cpp, NVIDIA Riva를 확인했다.
4. 그 결과를 토대로:
   - source note
   - deep research prompt
   - memo
   - deep research report
   - NotebookLM-ready source note
   - daily conversation memo
   를 작성했다.

## Important Method Note

- 이번 패스에서는 별도 `ChatGPT Deep Research browser run`은 수행하지 않았다.
- 대신 공식 문서 기반의 직접 리서치 결과를 먼저 정리하고, 이후 필요할 경우 재사용 가능한 `deepresearch_prompt.md`를 같이 생성했다.
- 이유:
  - 이번 요청의 핵심은 `기술성/실용성 판정`이었고
  - 해당 판정은 공식 문서 비교만으로도 충분히 1차 결론을 낼 수 있었기 때문이다.

## Official Sources Checked

### Picovoice

- https://picovoice.ai/docs/leopard/
- https://picovoice.ai/docs/cheetah/
- https://picovoice.ai/docs/orca/
- https://picovoice.ai/docs/falcon/
- https://picovoice.ai/pricing/
- https://picovoice.ai/blog/on-device-llm-powered-voice-assistant/
- https://picovoice.ai/platform/orca/
- https://picovoice.ai/platform/leopard/
- https://picovoice.ai/use-cases/voice-command-control/

### Alternative / complementary stack

- https://github.com/openai/whisper
- https://github.com/ggml-org/whisper.cpp
- https://github.com/SYSTRAN/faster-whisper
- https://github.com/pyannote/pyannote-audio
- https://github.com/ggml-org/llama.cpp

### Enterprise vendor stack

- https://docs.nvidia.com/deeplearning/riva/user-guide/docs/public/overview.html
- https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-overview.html
- https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide/tts.html

## Main Findings Captured In This Run

- Picovoice는 `로컬 voice I/O + diarization building blocks`로는 강하다.
- 하지만 `기업 회의록 완성 파이프라인`으로 보려면 STT/TTS 외의 요소가 더 중요하다.
- 한국어 `streaming STT` availability는 Cheetah docs에서 self-serve 기준이 명확하지 않다.
- Picovoice의 AccessKey / call-home 모델은 `strict air-gap` 검토 포인트다.
- 회의록 생성 중심이라면 `Whisper 계열 + diarization + local LLM` 또는 `Riva`가 더 직접적인 아키텍처가 된다.
- Picovoice는 `회의록 백본`보다 `로컬 음성 인터랙션 계층`에 더 적합하다.

## Output Files

- Source note:
  - `notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_sources.md`
- Deep research prompt:
  - `notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_deepresearch_prompt.md`
- Memo:
  - `reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_memo.md`
- Deep research report:
  - `reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_deepresearch.md`
- NotebookLM-ready source:
  - `reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_notebooklm_sources.md`
- Daily review conversation memo:
  - `daily_research_review/2026-04-11_enterprise-onprem-voice-and-meeting-stack.md`

## Follow-up Options

- 실제 GPT Deep Research로 한 번 더 돌려 vendor landscape와 한국어 benchmark 증거를 더 넓게 모은다.
- Picovoice 측에 `Korean streaming STT`와 `disconnected deployment`를 직접 확인하는 질문 세트를 만든다.
- 이후 필요하면 이 패키지를 기반으로 NotebookLM source pack과 Skywork deck으로 확장한다.
