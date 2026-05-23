# Skywork 실행 실패 원인과 재발 방지안

date: 2026-04-29
package: `2026-04-28_exploration-vs-fixation-haico-ai-cocreation`
status: Skywork live generation pending

## 판단

이번 패키지는 Skywork live 생성이 완료된 상태로 볼 수 없다. 프롬프트와 템플릿은 준비됐고 로컬 대체 덱도 만들어졌지만, Skywork 프로젝트에서 생성·다운로드했다는 증거가 없다.

## 확인한 증거

- `notes/2026-04-28_exploration-vs-fixation_research_runlog.md`에 `Skywork live UI 실행은 하지 않았다`고 기록되어 있다.
- `skywork_inputs/`에 prompt packet과 `LGD_Template.pptx`는 있다.
- `skywork_inputs/`에 Skywork automation status JSON이 없다.
- `skywork_inputs/` 또는 run log에 `skywork.ai` project/viewer URL이 없다.
- `skywork_exports/`의 `PPTX`와 `PDF`는 `_local_v1` 이름을 가진 로컬 생성물이다.
- 감사 명령 결과:

```text
python scripts/audit_skywork_package.py 2026-04-28_exploration-vs-fixation-haico-ai-cocreation

FAIL missing Skywork automation status JSON
FAIL no Skywork project/viewer URL found
WARN local_fallback_exports pptx=1 pdf=1
FAIL missing non-local Skywork PPTX/PDF export pair
RESULT blocked: this package does not meet the live Skywork completion bar
```

## 원인

1. 실행 게이트가 없었다.
   프롬프트와 source pack 작성 뒤 실제 Skywork 실행 여부를 강제 확인하는 단계가 없었다.

2. 로컬 대체 산출물이 완료 산출물처럼 보였다.
   파일명이 `_local_v1`을 포함하지만 `skywork_exports/`에 있어 최종 Skywork export처럼 읽힐 수 있었다.

3. 기존 Playwright 자동화가 특정 주제에 묶여 있었다.
   `.automation/skywork-playwright/skywork_sxs_retry.cjs` 안에 `2026-04-24_lgd-oled-investment-display-week-signals` 파일명이 남아 있었다. 다른 패키지에서 그대로 실행하면 prompt, status, export 경로가 틀어질 위험이 있었다.

4. 완료 기준이 문서화되어 있지 않았다.
   `AGENTS.md`에는 Skywork 사용 원칙이 있었지만, 프로젝트 URL·viewer URL·status JSON·다운로드 쌍을 완료 조건으로 검사하는 규칙이 없었다.

## 즉시 조치

- `scripts/audit_skywork_package.py`를 추가했다.
  - prompt packet 확인
  - `LGD_Template.pptx` 확인
  - automation status JSON 확인
  - Skywork project/viewer URL 확인
  - non-local Skywork `PPTX`/`PDF` export 쌍 확인
  - PPTX slide count와 PDF page count 확인
- `AGENTS.md`에 Skywork 완료 조건을 추가했다.
- 2026-04-29 사용자 지시에 따라 로컬 대체 덱 생성은 앞으로 금지한다.
- `.automation/skywork-playwright/skywork_sxs_retry.cjs`의 주제명 하드코딩을 제거했다.
  - `TOPIC_DIR` 필수화
  - prompt packet 자동 탐색
  - source pack 자동 수집
  - status JSON과 export 파일명을 현재 topic slug에서 생성

## 다음 실행 절차

1. topic package 준비
   - `skywork_inputs/*_skywork_prompt_v1.md`
   - `skywork_inputs/LGD_Template.pptx`
   - `reports/*.md`, `notes/*sources*.md`, `notes/*claim_audit*.md`, `sources/*.pdf`

2. Skywork 실행
   - `TOPIC_DIR=<topic-folder>`
   - `SKYWORK_PROFILE_DIR=<logged-in browser profile>`
   - `SKYWORK_MODE=submit_wait_download`
   - 필요 시 `SKYWORK_PROMPT_PATH`, `SKYWORK_TEMPLATE_PATH`, `SKYWORK_SOURCE_PATHS` 지정

3. 완료 확인
   - `skywork_inputs/<topic-slug>_skywork_automation_status.json` 생성 확인
   - status 안의 Skywork project URL 확인
   - `skywork_exports/<topic-slug>_skywork_v1.pptx`
   - `skywork_exports/<topic-slug>_skywork_v1.pdf`
   - `python scripts/audit_skywork_package.py <topic-folder>` 통과 확인

4. 실패 처리
   - login blocked: status JSON과 screenshot 경로를 남기고 사용자에게 수동 로그인 요청
   - generation timeout: project URL과 진행 화면을 남기고 나중에 export-only 재시도
   - download timeout: `waitForEvent('download')` 대기만 반복하지 말고 export task URL 또는 notification link를 확인
   - 로컬 대체 덱 생성 금지: Skywork가 막히면 slide deliverable을 만들지 않고 pending/blocked 상태로 둔다

## 현재 패키지 상태

현재 패키지는 리뷰 문서와 로컬 대체 덱은 존재한다. Skywork live 덱은 pending이다.

## 추가 정책, 2026-04-29

앞으로 Skywork deliverable을 로컬 `PPTX` 또는 `PDF`로 대체하지 않는다. 자동화나 로그인 문제로 Skywork가 막히면 원인, screenshot/status, 재시도 조건만 남기고 슬라이드 산출물은 pending으로 둔다.
## 2026-04-29 추가 재시도 결과

- Skywork 실제 프로젝트에서 V1부터 V5까지 생성과 다운로드를 진행했다.
- V1은 실제 Skywork 산출물이지만 표지 오탈자와 일부 표현 문제가 있었다.
- V2/V3는 수정 요청 과정에서 후반부 한국어 품질이 크게 떨어져 폐기했다.
- V4는 10장짜리 clean rebuild로 품질이 개선됐지만, PPTX 내부 텍스트에 `낮출수록`, `대한 탐색`, `낮은 결과`가 남았다.
- V5는 Skywork 화면 미리보기와 PDF에서는 교정된 문구를 보여줬다.
- 같은 V5를 카드 다운로드와 미리보기 툴바 다운로드 두 경로로 내려받았지만 PPTX 내부 텍스트는 동일하게 오래된 문구를 유지했다.
- PowerPoint COM으로 V5 PPTX를 직접 PDF 변환해 확인한 결과, PPTX 렌더도 오래된 문구를 표시했다.

### 확정된 상태

- `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v5.pdf`는 시각 검토용으로 쓸 수 있다.
- `skywork_exports/2026-04-28_exploration-vs-fixation-haico-ai-cocreation_skywork_v5.pptx`는 편집 가능한 최종본으로 쓰기 어렵다.
- 로컬 패치 또는 로컬 대체 덱은 만들지 않았다.

### 다음 대응

- Skywork의 PDF 렌더와 PPTX export/cache가 갈라지는 문제를 별도 이슈로 다룬다.
- editable PPTX가 꼭 필요하면 같은 프로젝트에서 캐시를 비우는 재 export, 새 프로젝트 clean rebuild, 또는 Skywork 편집기/지원 경로를 사용한다.
- 로컬 deck builder나 PowerPoint COM을 사용한 내용 수정은 금지한다.
