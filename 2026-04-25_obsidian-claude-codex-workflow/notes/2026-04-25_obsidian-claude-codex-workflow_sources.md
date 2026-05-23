# Source Note - Obsidian + Claude + Codex Workflow

Date: 2026-04-25

## Source

- Video: [Your AI Has Amnesia? Fix It With Obsidian + Claude!](https://www.youtube.com/watch?v=rJo7_HZridY)
- Channel: `Gen AI University`
- Video ID: `rJo7_HZridY`
- Published: `2026-04-22`
- Duration: `15:43`
- Raw subtitle: [rJo7_HZridY.en.vtt](../sources/rJo7_HZridY.en.vtt)
- Clean transcript: [2026-04-25_obsidian-claude-codex-workflow_transcript_en.txt](../sources/2026-04-25_obsidian-claude-codex-workflow_transcript_en.txt)
- Sentence transcript: [2026-04-25_obsidian-claude-codex-workflow_transcript_sentences_en.txt](../sources/2026-04-25_obsidian-claude-codex-workflow_transcript_sentences_en.txt)

## Chapter Map

- `00:00-01:22` AI Plans Your Week
- `01:22-02:29` AI Amnesia Problem
- `02:29-04:23` Intelligent Work Environment
- `04:23-04:50` Mindset Shifts Needed
- `04:50-06:14` Vault Folder Walkthrough
- `06:14-08:05` People Network Linking
- `08:05-09:10` Running Claude Code
- `09:10-09:58` Build Your Own Vault
- `09:58-13:08` Organize With AI Help
- `13:08-13:53` Claude MD Instructions
- `13:53-15:43` Wrap Up And Prompt

## Directly Observed Claims From The Video

### Confirmed from the video

- 발표자는 생성형 AI의 기본 문제를 `AI amnesia`로 설명한다. 새 대화가 시작될 때마다 맥락이 거의 0에서 다시 시작된다는 주장이다.
- 발표자는 Obsidian을 장기 기억 저장소, Claude Code를 실행 주체로 묶어 `intelligent work environment`를 만든다고 설명한다.
- 발표자는 vault를 단순 보관함이 아니라 사람이 일하고 AI가 탐색할 수 있는 작업 공간으로 보라고 강조한다.
- 발표자는 `Claude.md` 계층 구조를 통해 루트 지침과 폴더별 세부 지침을 함께 주는 방식을 핵심 운영 패턴으로 제시한다.
- 발표자는 사람 노트와 위키링크를 통해 정보 간 연결성을 높이고, 이것이 AI가 맥락을 엮는 데 유리하다고 본다.
- 발표자는 Obsidian 안에서 주간 계획, 프로젝트, 목표, 사람 네트워크, 제품 레지스트리 같은 단위를 정리해 두고 Claude가 이를 바탕으로 실행하게 한다.

### Interpretation, not direct claim

- 이 영상의 핵심은 `Obsidian + Claude` 자체보다 `장기 기억 계층 + 실행 계층 + 계층형 지침 파일`의 조합에 있다.
- 따라서 현재 사용 중인 `Obsidian + Codex` 환경에서도 거의 같은 원리를 적용할 수 있다.
- 사용자 환경에서는 영상의 `Claude.md`를 그대로 복제하기보다 이미 쓰고 있는 `AGENTS.md` 체계와 Obsidian의 운영 노트를 연결하는 편이 더 자연스럽다.

## Translation To Current Environment

### Already present in the current setup

- 장기 기억 계층:
  - `C:\Users\angpa\Obsidian_Vault`
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review`
- 실행 작업 계층:
  - `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
- 계층형 에이전트 지침:
  - `C:\Users\angpa\AGENTS.md`
  - `C:\Users\angpa\Obsidian_Vault\AGENTS.md`
  - `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\AGENTS.md`
- 장기 규칙/라우팅 노트:
  - `81. System_Agent_Rules`
  - `mode-registry.md` 계열 노트

### Key mapping

- Video `Claude + Obsidian` -> Current `Codex + Obsidian`
- Video `Claude.md` -> Current `AGENTS.md`
- Video single workspace vault -> Current split model:
  - Obsidian for durable memory and operating notes
  - repo topic package for production artifacts and automation

## What Seems Most Useful

1. vault를 `AI가 읽을 수 있는 구조물`로 다루는 관점
2. 사람/조직/프로젝트/제품을 단일 노트 단위로 관리하는 관점
3. root instruction + folder-specific instruction의 계층형 운영
4. 단순 보관보다 `지속 briefing` 상태를 만드는 운영 습관

## Risks If Copied Blindly

1. 현재 Obsidian은 `lifecycle-based` 구조인데, 영상의 분류 체계를 그대로 도입하면 오히려 충돌이 생길 수 있다.
2. 모든 실행 산출물을 vault 안으로 밀어 넣으면 재현성과 파일 관리가 약해질 수 있다.
3. `Claude.md`를 그대로 흉내 내기보다, 이미 검증된 `AGENTS.md`와 주제 패키지 구조를 강화하는 편이 낫다.

## Open Questions

- 사람/조직/entity 노트를 어느 vault 영역에 둘지 더 명확한 기준이 필요한가
- `AI_Tech_Review` 패키지별로 agent-readable handoff note를 추가할지
- `daily_research_review`와 promoted topic package 사이의 링크 구조를 더 강화할지

## Reference Paths

- Workspace package root: [2026-04-25_obsidian-claude-codex-workflow](../)
- Memo: [2026-04-25_obsidian-claude-codex-workflow_memo.md](../reports/2026-04-25_obsidian-claude-codex-workflow_memo.md)
- Report: [2026-04-25_obsidian-claude-codex-workflow_deepresearch.md](../reports/2026-04-25_obsidian-claude-codex-workflow_deepresearch.md)
