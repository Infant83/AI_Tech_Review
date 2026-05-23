---
title: 2026-04-11 Enterprise On-Prem Voice and Meeting Stack
date: 2026-04-11
topic: 2026-04-11_enterprise-onprem-voice-and-meeting-stack
tags:
  - conversation-memo
  - pulse-spin-off
  - stt
  - tts
  - onprem
  - meeting-notes
---

# 2026-04-11 Enterprise On-Prem Voice and Meeting Stack

## Executive Summary

- 오늘 Pulse의 `Picovoice` 관련 STT/TTS 카드를 `교육/교실` 맥락이 아니라 `일반 기업 on-prem 회의 음성 처리` 관점으로 재해석해 별도 주제로 승격했다.
- 현재 결론은 `Picovoice는 로컬 voice I/O 계층으로는 충분히 흥미롭지만, 한국어 기업 회의록의 주력 백본으로 단독 채택하기에는 보완 필요 요소가 많다`는 것이다.
- 특히 `회의록`은 STT/TTS보다 `diarization`, `segmentation`, `summarization`, `action-item extraction`이 더 중요하다.

## What Was Decided

- 이 주제는 root topic package로 분리했다:
  - `2026-04-11_enterprise-onprem-voice-and-meeting-stack/`
- package 안에는 아래를 생성했다:
  - source note
  - deep research prompt
  - research run log
  - memo
  - deep research report
  - NotebookLM-ready source note

## Key Takeaways

- `Leopard`는 한국어 batch STT 기준으로는 유효하다.
- `Orca`는 local/on-prem TTS 계층으로 적합하다.
- `Falcon`은 local diarization component로 의미가 있다.
- `Cheetah`의 한국어 streaming STT 가용성은 공식 docs 표현이 일관되지 않아 사전 확인이 필요하다.
- Picovoice는 AccessKey validation / plan tracking 구조가 있어서 strict air-gap 판단에는 추가 검증이 필요하다.
- 회의록 중심이라면 `Whisper 계열 + pyannote + local LLM` 또는 `NVIDIA Riva`가 더 직접적인 대안이다.

## Package References

- Source note:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_sources.md](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_sources.md)
- Deep research prompt:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_deepresearch_prompt.md](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_deepresearch_prompt.md)
- Memo:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_memo.md](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_memo.md)
- Deep research:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_deepresearch.md](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_deepresearch.md)

## Relationship To Pulse

- originating intake:
  - `daily_research_review/2026-04-11_gpt-pulse-daily-review/`
- promoted card:
  - `온디바이스 한국어 STT·TTS: Picovoice 활용`
- reframed research target:
  - `enterprise on-prem voice and meeting stack`

## Skywork Update

- 이번 시점의 슬라이드 생성은 `NotebookLM`이 아니라 `Skywork` 기준으로 수행했다.
- LGD 템플릿을 적용한 Skywork deck export를 아래에 저장했다:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v1.pptx](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v1.pptx)
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v1.pdf](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v1.pdf)
- export 결과는 `13장`으로 생성되었지만, 품질 검토 결과 일부 장표는 재작업이 필요하다.
- 핵심 품질 이슈:
  - 슬라이드 `4`, `9`, `10`은 실질적으로 비어 있거나 제목 수준만 남았다.
  - 슬라이드 `11`, `12`는 `페이지 제목 / Page title` 같은 템플릿 placeholder가 남아 있다.
  - 전체적으로 draft로는 쓸 수 있지만, 배포본 품질로 보기는 어렵다.
- 이후 `Skywork` 2차 보정을 별도 correction packet으로 다시 수행했다.
- 보정 입력:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_inputs/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_correction_v1.md](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_inputs/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_correction_v1.md)
- 보정 결과 `v2` export를 추가로 저장했다:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v2.pptx](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v2.pptx)
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v2.pdf](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v2.pdf)
- `v2` 품질 검토 결과:
  - 슬라이드 `4`, `9`, `10`, `11`, `12`는 모두 실질 내용이 채워진 상태로 복구되었다.
  - placeholder 텍스트 (`페이지 제목`, `Page title`, `Headline`, `헤드라인`)는 해당 핵심 슬라이드에서 제거되었다.
  - `90일 PoC` 페이지의 이전 wording artifact도 제거되었다.
  - 현재 배포 기준본은 `v2`이며, `v1`은 참조용 draft로 유지한다.
- 실행 로그:
  - [../2026-04-11_enterprise-onprem-voice-and-meeting-stack/notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_project.md](../2026-04-11_enterprise-onprem-voice-and-meeting-stack/notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_project.md)
