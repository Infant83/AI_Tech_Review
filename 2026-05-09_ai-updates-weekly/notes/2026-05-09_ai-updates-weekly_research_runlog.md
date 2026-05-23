---
title: 2026-05-09 AI Updates Weekly Research Runlog
date: 2026-05-09
type: runlog
aliases:
  - Lev Selector AI Updates Weekly Research Runlog 2026-05-09
author: Codex
date created: 2026-05-09
date modified: 2026-05-09
topic: ai-updates-weekly
status: processed
tags:
  - runlog
  - ai
  - weekly-review
---

# 2026-05-09 AI Updates Weekly Research Runlog

## 실행 요약

- 작업일: 2026-05-09
- 대상 영상: [Exciting AI Updates Weekly - May 8, 2026](https://www.youtube.com/watch?v=yDfupTHYshQ)
- 로컬 패키지: `2026-05-09_ai-updates-weekly`
- 산출 범위:
  - source note
  - deep research prompt
  - research runlog
  - memo
  - deep research report
  - article-style final review
  - HTML companion files

## 수집 단계

1. YouTube 채널의 최신 영상 목록을 `yt-dlp --flat-playlist --dump-single-json --skip-download`로 확인했습니다.
2. `yDfupTHYshQ`가 `Exciting AI Updates Weekly - May 8, 2026` 회차임을 확인했습니다.
3. `yt-dlp --dump-single-json --skip-download`로 메타데이터를 저장했습니다.
4. `yt-dlp --write-auto-subs --sub-langs en --sub-format vtt --write-description --skip-download`로 설명란과 자동 자막을 저장했습니다.
5. GitHub API로 `lselector/seminar/2026` 폴더를 확인했고 `2026-05-08-AI-Updates.pptx`를 다운로드했습니다.
6. `python-pptx`로 슬라이드 텍스트를 추출했습니다.
7. VTT 자막은 시간 태그와 중복 line을 제거한 clean transcript로 변환했습니다.

## 저장된 원천 파일

- `sources/2026-05-08_Exciting_AI_Updates_Weekly_May_8_2026_yDfupTHYshQ.info.json`
- `sources/20260508_Exciting AI Updates Weekly - May 8, 2026 [yDfupTHYshQ].description`
- `sources/20260508_Exciting AI Updates Weekly - May 8, 2026 [yDfupTHYshQ].en.vtt`
- `sources/20260508_Exciting AI Updates Weekly - May 8, 2026 [yDfupTHYshQ].en.clean.txt`
- `sources/2026-05-08-AI-Updates.pptx`
- `sources/2026-05-08-AI-Updates_slide-extract.md`

## 검증 단계

웹 검증은 영상 전체 항목을 모두 같은 깊이로 확인하기보다, 리뷰의 중심 결론에 쓰이는 항목을 우선했습니다.

### 공식/1차 출처 확인

- Anthropic:
  - `higher-limits-spacex`
  - `finance-agents`
  - `enterprise-ai-services-company`
  - `claude-code-security`
  - Claude Managed Agents blog
- 논문:
  - arXiv `2604.27891`
  - arXiv `2603.25723`
  - arXiv `2603.28052`
- 프로젝트/문서:
  - DeepSeek-TUI GitHub
  - xAI Grok connectors docs
  - OpenSwarm GitHub
  - Hermes Agent GitHub and Curator docs
  - InsForge GitHub
  - Zed AI docs
  - Jujutsu GitHub
  - Mergiraf docs
  - Weave docs
- 도메인 사례:
  - Google DeepMind AI co-clinician blog

### 낮은 신뢰도로 분류한 항목

- OpenAI `GPT 4.5 Instant` 또는 `GPT 5.5 Instant`
  - 영상 설명과 슬라이드 표기가 다르고, 공식 OpenAI 문서 검색으로 동일 명칭과 수치를 직접 확인하지 못했습니다.
- Codex CLI `/goal` / `goals = true`
  - 공식 OpenAI 도움말과 문서 검색으로 직접 확인하지 못했습니다.
- layoffs와 특정 인원수 주장
  - 이번 패키지에서는 1차 기업 공시나 공식 보도자료로 확인하지 않았습니다.

## 주의 사항

- `yt-dlp` 실행 중 YouTube format fragment 403 경고가 다수 발생했지만, 이번 작업에 필요한 metadata, description, VTT subtitle은 정상 저장되었습니다.
- 이번 문서 패키지는 Lev Selector 영상과 슬라이드를 discovery map으로 사용합니다. 보고서의 결론은 공식 출처와 논문, 저장소 문서로 확인된 항목만 중심 근거로 올렸습니다.
- 별도 Skywork deck은 생성하지 않았습니다. 이번 회차는 원본 발표 슬라이드가 이미 source artifact로 포함되어 있으며, 사용자가 새 발표 deck 생성을 요청하지 않았습니다.
- OpenProject 업데이트는 이번 패키지 작성 범위에서 실행하지 않았습니다. 연결할 대상 work package가 명시되면 이 runlog와 보고서 경로를 기준으로 동기화할 수 있습니다.

## Obsidian mirror

Vault 규칙을 확인한 뒤, 최종 markdown 보고서 3종을 다음 위치로 미러링했습니다.

- `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-09_ai-updates-weekly\2026-05-09_ai-updates-weekly_memo.md`
- `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-09_ai-updates-weekly\2026-05-09_ai-updates-weekly_deepresearch.md`
- `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-09_ai-updates-weekly\2026-05-09_ai-updates-weekly_final_review.md`
