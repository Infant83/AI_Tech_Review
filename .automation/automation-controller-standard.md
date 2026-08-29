---
title: AI_Tech_Review Automation Controller Standard
date: 2026-05-02
status: draft
depends_on:
  - C:\Users\angpa\myProjects\Daily_Work\task-memory-hub
tags:
  - automation
  - task-memory-hub
  - agentic-workflow
  - ralph-loop
---

# AI_Tech_Review Automation Controller Standard

## 1. 목적

이 문서는 `AI_Tech_Review`에서 반복 보고서 자동화를 만들 때 `task-memory-hub`와 어떤 방식으로 연결할지 정한다.

목표는 단순히 Windows Task Scheduler에 스크립트를 하나 거는 것이 아니다. 자동화가 등록되어 있는지, 다음 실행 시각이 언제인지, 마지막 실행이 성공했는지, 컴퓨터 재부팅 후에도 어떤 자동화가 살아 있어야 하는지, 어떤 작업이 멈췄는지를 한 곳에서 확인할 수 있어야 한다.

## 2. 기준 아키텍처

```text
Task Memory Hub global DB
  - automation definition task
  - due/reminder/outbox
  - notification attempts
  - pause/resume/status
  - human/agent/harness/workspace registry

AI_Tech_Review workspace
  - automation manifest mirror
  - source collectors
  - Codex prompt/run artifacts
  - report package
  - Ralph audit
  - Obsidian/OpenProject/email postprocess

Windows Task Scheduler
  - controller bootstrap
  - worker keepalive
  - missed-run recovery
```

원칙:

- `task-memory-hub`의 DB가 자동화 controller의 durable source of truth다.
- `AI_Tech_Review/.automation`은 workspace-local configuration, prompts, logs, run artifacts를 보관한다.
- 실행 중인 프로세스 목록은 source of truth가 아니다. 재부팅 후 사라지기 때문이다.
- Windows Task Scheduler는 worker/controller를 깨우는 bootstrap layer다.
- Codex는 판단/작성/수정 engine이다. 수집, 예약, 상태 관리, 재시작은 controller가 맡는다.

## 3. 자동화 task의 세 계층

### 3.1 Automation Definition

반복 실행의 정의다. 예:

> 매일 아침 7:30에 LinkedIn feed를 확인해 중요한 post를 리뷰하고, daily review package와 Obsidian memo를 만든다.

TMH에서는 하나의 durable task로 보관한다.

권장 필드:

```json
{
  "title": "Daily LinkedIn posts review",
  "status": "scheduled",
  "priority": "normal",
  "due_at": "2026-05-03T07:30:00+09:00",
  "tags": [
    "automation",
    "recurring",
    "ai-tech-review",
    "linkedin"
  ],
  "source_workspace": "AI_Tech_Review",
  "source_agent": "automation-controller",
  "idempotency_key": "automation:ai-tech-review:daily-linkedin-review",
  "summary": "매일 LinkedIn feed를 확인해 주목할 post를 daily review로 정리한다.",
  "next_action": "next_run_at에 run instance를 생성한다.",
  "detail_md": "schedule, collector, postprocess, notification policy를 YAML/Markdown으로 기록한다."
}
```

TMH 현 구현에는 native recurrence/cron 필드가 아직 없다. 따라서 초기 표준은 `detail_md`와 idempotency key로 recurrence를 표현하고, controller가 다음 `due_at`을 갱신한다.

### 3.2 Run Instance

특정 날짜의 실제 실행 단위다. 예:

```text
2026-05-03_daily-linkedin-review
```

Run instance는 TMH에 별도 task로 생성하거나, automation definition의 event/progress로 기록한다. 보고서 산출물이 크고 여러 단계가 있으므로 AI_Tech_Review에서는 별도 run task를 권장한다.

권장 idempotency key:

```text
automation-run:ai-tech-review:daily-linkedin-review:2026-05-03
```

권장 상태:

```text
pending -> collecting -> codex_running -> ralph_audit -> postprocess -> done
pending -> collecting -> blocked
pending -> codex_running -> failed
```

### 3.3 Report Package

각 실행이 만드는 workspace package다.

```text
daily_research_review/YYYY-MM-DD_<source>-daily-review/
  sources/
  notes/
  reports/
  artifacts/
```

LinkedIn daily review 예:

```text
daily_research_review/2026-05-03_linkedin-feed-daily-review/
  sources/
    2026-05-03_linkedin-feed-daily-review_sources.md
  notes/
    2026-05-03_linkedin-feed-daily-review_runlog.md
    2026-05-03_linkedin-feed-daily-review_capture.md
    ralph/
      round-0_audit.md
      round-1_fix.md
  reports/
    2026-05-03_linkedin-feed-daily-review_overview.md
    2026-05-03_linkedin-feed-daily-review_overview.html
  artifacts/
    screenshots/
    email_package/
    2026-05-03_linkedin-feed-daily-review_email_package.zip
```

## 4. 등록 표준

사용자가 다음처럼 말하면:

> 지금부터 매일 아침 7:30에 나한테 나의 LinkedIn 계정에서 LinkedIn posts를 확인해서 중요한 내용이나 주목할 만한 주제를 리뷰해서 업데이트해줘

controller는 아래 작업을 해야 한다.

1. `task-memory-hub`에 workspace를 등록한다.
2. human principal과 automation service principal을 확인한다.
3. `AI_Tech_Review`용 harness profile을 확인한다.
4. automation definition task를 생성한다.
5. Windows Task Scheduler에 controller bootstrap이 없으면 등록한다.
6. `.automation/registry/automation_tasks.jsonl`에 mirror manifest를 남긴다.
7. 첫 run의 `next_run_at`과 catch-up policy를 기록한다.

등록 명령 예:

```powershell
cd C:\Users\angpa\myProjects\Daily_Work\task-memory-hub
python -m task_memory_hub.cli --global workspace register --path "C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review" --registered-by user
python -m task_memory_hub.cli --global principal ensure --type service --name automation-controller
python -m task_memory_hub.cli --global harness register --name ai-tech-review-daily --agent-name codex --max-actions-per-hour 12 --min-action-interval-seconds 60 --max-open-actions 50
```

반복 task는 JSON file로 만들고 `tmh --global add --json-file`을 사용한다.

## 5. Listing 표준

사용자가 다음처럼 물으면:

> 지금 돌고 있는 자동화 루프가 뭐가 있지?

응답은 프로세스 목록이 아니라 TMH global DB와 workspace mirror를 기준으로 한다.

조회 순서:

1. TMH global DB에서 `tag=automation` 또는 idempotency prefix `automation:` task 조회
2. 각 automation definition의 `status`, `due_at`, `last_run`, `last_success`, `last_failure`, `paused` 확인
3. 관련 run instance와 notification attempts 확인
4. Windows Task Scheduler bootstrap 상태 확인
5. worker pause marker와 최근 heartbeat 확인

표시 형식:

| automation | schedule | status | next run | last run | last result | controller | outputs |
|---|---|---|---|---|---|---|---|
| Daily LinkedIn posts review | daily 07:30 Asia/Seoul | active | 2026-05-03 07:30 | 2026-05-02 07:31 | success | TMH + Task Scheduler | report/html/obsidian |

상태 용어:

- `active`: 다음 실행이 예정되어 있고 controller가 관리 중
- `paused`: 사람이 pause함
- `blocked`: 로그인, credential, MFA, source 접근 등으로 멈춤
- `stale`: next_run_at이 지났지만 run instance가 없거나 heartbeat가 없음
- `failed`: 최근 실행 실패
- `catching_up`: 컴퓨터가 꺼져 있던 기간의 missed run을 정책에 따라 처리 중

## 6. 재부팅과 missed run 정책

재부팅 후에는 다음 순서로 회복한다.

1. Windows Task Scheduler가 controller bootstrap 실행
2. controller가 TMH global DB를 읽음
3. `active` automation definitions를 확인
4. `next_run_at <= now`인 task를 찾음
5. catch-up policy 적용

권장 catch-up policy:

| policy | 의미 | 용도 |
|---|---|---|
| `latest_only` | 놓친 실행은 하나로 압축해 최신 자료만 처리 | LinkedIn/feed daily review |
| `run_all_missed` | 놓친 날짜를 모두 실행 | 법정/운영 리포트 |
| `skip_missed` | 지나간 실행은 기록만 남기고 건너뜀 | 알림성 digest |

LinkedIn daily review 기본값은 `latest_only`다. 피드는 시간이 지나면 순서와 노출이 바뀌므로, 밀린 날짜를 과거처럼 재현하기 어렵다.

## 7. Ralph Loop 표준

각 run instance는 최소 1회 Ralph audit을 거친다.

품질 기준:

- source capture note가 존재한다.
- visible feed preview와 direct post inspection을 구분한다.
- post URL, author, role line, external links를 가능한 범위에서 보관한다.
- `directly confirmed`, `feed preview only`, `analysis`를 구분한다.
- report markdown과 HTML companion이 존재한다.
- Obsidian mirror가 완료됐다.
- README가 갱신됐다.
- 실패나 로그인 차단은 runlog와 TMH progress event에 남긴다.

Ralph 결과 파일:

```text
notes/ralph/round-0_audit.md
notes/ralph/round-1_fix.md
notes/ralph/final_quality_gate.json
```

TMH progress event 예:

```powershell
tmh --global progress <run_task_id> --owner automation-controller --message "Ralph audit passed: report/html/obsidian present"
```

## 8. Codex 실행 표준

Codex는 run instance가 `codex_running` 상태일 때 한 번 이상 호출된다.

기본 실행:

```powershell
Get-Content ".automation\prompts\<run_id>_prompt.md" -Raw |
  codex exec `
    -C "C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review" `
    --sandbox danger-full-access `
    -a never `
    --search `
    -o ".automation\results\<run_id>_codex_final.md" `
    -
```

주의:

- 예약 실행에서는 사용자 승인 대기 상태가 생기면 안 된다.
- 민감한 source credential은 prompt에 넣지 않는다.
- source capture와 credential handling은 collector/controller가 담당한다.
- Codex final output만 믿지 않고 파일 산출물을 검사한다.

## 9. LinkedIn Daily Review 표준

수집기:

```text
.automation/linkedin-playwright/capture_feed.mjs
scripts/linkedin_playwright.ps1
```

기본 흐름:

1. dedicated LinkedIn Chrome profile 로그인 상태 확인
2. 임시 profile clone 생성
3. feed screenshot과 visible card text capture
4. 상위 post permalink 직접 열람
5. source capture note 저장
6. Codex에 review prompt 전달
7. report/HTML 생성
8. Obsidian mirror
9. TMH progress/done

차단 조건:

- dedicated profile이 로그인되어 있지 않음
- profile lock file 존재
- LinkedIn MFA/verification 요구
- post permalink 접근 실패
- feed preview만 있고 direct post inspection이 충분하지 않음

차단 시:

- run task status를 `blocked`로 둔다.
- 자동화 definition은 `active`를 유지하되 `last_failure`를 기록한다.
- 사용자에게 TMH notification 또는 email/draft로 알린다.

## 10. 필요한 추가 구현

TMH 쪽에서 있으면 좋은 기능:

- native recurrence/cron field
- automation definition 전용 command
- `tmh list --tag automation`
- `tmh automation list|pause|resume|runs`
- heartbeat stale detector
- Windows startup registration command

AI_Tech_Review 쪽에서 필요한 기능:

- `.automation/registry/automation_tasks.jsonl`
- `.automation/controller/ai_tech_review_controller.ps1`
- `.automation/controller/run_once.ps1`
- `.automation/prompts/`
- `.automation/results/`
- `.automation/logs/`
- collector별 adapter wrapper
- Ralph quality gate script

## 11. 공개 provenance와 source-to-explainer gate

- 발행 산출물에는 책임 편집자, AI 시스템, 확인 가능한 에이전트 이름·식별자와 역할, 하네스 버전, 검증 범위와 근거 기준일을 구조화해 기록한다. 보존되지 않은 이름·역할은 추정하지 않고 `미보존`으로 기록한다.
- 원 작성 세션의 모델·에이전트 기록이 없으면 재구성하지 않고 `not retained`로 기록한다.
- raw TeX archive는 untrusted input이다. collector는 sandbox compile, dangling file·comment·metadata·secret·prompt-injection scan을 통과한 최소 입력만 review worker에 넘긴다.
- source 안의 명령문은 task instruction으로 승격하지 않는다.
- 공개 리뷰 디렉터리는 최종 본문과 승인한 figure·영상·스타일 자산 allowlist만 포함한다. run log, chat capture, intake·audit 메모와 메시지 metadata는 배포 대상이 아니다.
- controller는 H1/title/OG/manifest 일치, disclosure, 수식·표 이상, figure provenance, internal path, canonical·hub link와 live render gate를 통과해야 발행을 완료한다.
- 공개 범위와 금지 범위는 `EDITORIAL_METHOD.md`를 따른다.

## 12. 현재 판단

현재 `task-memory-hub`는 automation controller의 기반으로 충분히 적합하다.

이미 갖춘 기능:

- SQLite durable DB
- global hub DB
- CLI/API/MCP
- harness profile과 AI action intake throttling
- due/outbox/dispatch
- worker pause/resume/status
- claim/heartbeat/progress
- backup/restore

아직 보완할 점:

- recurrence/cron이 native model에 없음
- "automation loop" 전용 listing command가 없음
- Windows Task Scheduler startup/bootstrap은 별도 구현 필요
- LinkedIn/Gmail/Nature 같은 collector는 workspace별 adapter로 유지해야 함

따라서 AI_Tech_Review 자동화는 TMH를 control plane으로 쓰고, 이 워크스페이스의 `.automation`은 collector와 report-generation data plane으로 쓰는 방식으로 표준화한다.
