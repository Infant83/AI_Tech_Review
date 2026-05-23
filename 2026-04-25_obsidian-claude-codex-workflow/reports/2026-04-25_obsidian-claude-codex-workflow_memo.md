# Obsidian + Claude + Codex Workflow Memo

Date: 2026-04-25

## One-line thesis

이 영상의 본질은 `Obsidian + Claude` 조합 자체가 아니라, `장기 기억 저장소 + 실행 에이전트 + 계층형 지침 파일`을 한 흐름으로 묶는 운영 모델에 있다. 당신의 현재 환경에서는 이것이 이미 `Obsidian + Codex + AGENTS.md + AI_Tech_Review 패키지` 형태로 거의 구현돼 있다.

## Bottom line

- 당신은 이 영상을 처음부터 새로 도입할 단계가 아니라, 이미 갖고 있는 구조를 `agent-readable`하게 더 다듬는 단계에 있다.
- 영상의 `Claude.md` 개념은 현재 환경에서는 `AGENTS.md`와 주제별 운영 노트로 치환하는 편이 맞다.
- Obsidian은 장기 기억과 판단 기록에 집중시키고, 실제 파일 생성/리서치 패키징/자동화는 repo workspace에서 계속 수행하는 편이 더 안정적이다.
- 따라서 최적 해법은 `단일 툴 통합`이 아니라 `Obsidian memory + repo execution + Codex orchestration`의 역할 분리를 유지하면서 링크를 촘촘히 만드는 것이다.

## Why this matters

- 영상은 AI의 `대화 단위 기억 단절` 문제를 정확히 짚는다.
- 현재 워크플로우도 주제 폴더, source note, run log, memo/report, Obsidian mirror를 이미 갖고 있기 때문에 구조적 기반은 충분하다.
- 부족한 것은 도구가 아니라:
  - entity 단위 기억
  - 폴더별 지침의 일관성
  - 주제 간 연결 링크
  - 에이전트가 바로 쓸 수 있는 briefing note

## Practical interpretation for your setup

### 1. 영상의 `Claude.md`는 현재의 `AGENTS.md`다

- 글로벌 지침: `C:\Users\angpa\AGENTS.md`
- vault 지침: `C:\Users\angpa\Obsidian_Vault\AGENTS.md`
- workspace 지침: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\AGENTS.md`

즉, 계층형 지침 구조는 이미 있다. 여기서 더 필요한 것은 폴더/주제 단위의 운영 메모를 꾸준히 남기는 것이다.

### 2. 영상의 `single workspace`는 당신에게 그대로 맞지 않는다

영상은 Obsidian 안에 기억과 실행을 함께 두는 쪽에 가깝다. 반면 현재 환경은:

- Obsidian = 장기 기억, 회의/규칙/요약
- `AI_Tech_Review` repo = 실행 패키지, 산출물, 자동화

이 분리가 오히려 더 좋다. vault를 실행 산출물 저장소로 오염시키지 않으면서도, 최종 memo/report만 durable note로 남길 수 있기 때문이다.

### 3. 사람 노트보다 더 중요한 것은 entity 노트다

영상은 `people network`를 강조하지만, 당신에게는 다음 entity가 더 중요하다.

- 사람
- 조직
- 프로젝트
- work package
- 반복 주제
- 규칙/운영 모드

즉, `people network`를 더 넓은 `entity network`로 확장해서 보는 편이 실무적으로 맞다.

## Recommended next moves

1. `AI_Tech_Review` 주제 패키지마다 `briefing` 성격의 운영 노트를 명시적으로 남긴다.
2. Obsidian에는 사람/조직/프로젝트/entity 노트를 축적하되, raw artifact는 repo에 남긴다.
3. `daily_research_review`에서 promoted topic package로 넘어갈 때, 원인-결과 링크를 더 명시한다.
4. 반복적으로 참고되는 판단 규칙은 `81. System_Agent_Rules` 쪽 note로 승격한다.
5. Codex가 바로 활용할 수 있는 `single source of truth` note를 늘린다.

## Immediate 활용안

### A. Obsidian을 `판단 기억`으로 강화

- 왜 이 주제를 골랐는지
- 어떤 가설을 세웠는지
- 어떤 기준으로 deep research 범위를 잘랐는지
- 무엇을 보류했는지

이런 판단 메모를 Obsidian에 남기면, 다음 주제에서 Codex가 재사용할 수 있는 맥락이 커진다.

### B. repo는 계속 `실행 공간`으로 유지

- raw source
- transcript
- notes
- reports
- exports

이것은 지금 구조가 이미 맞다. 바꿀 필요가 없다.

### C. topic package에 `agent handoff` 성격을 더한다

현재의 source note와 run log에 다음 항목이 조금 더 명시되면 좋다.

- 이 주제의 핵심 질문
- 이번 턴에서 확정한 판단
- 다음 턴에서 이어서 할 일
- 재사용할 링크/엔티티

## Final judgment

이 영상은 당신에게 새로운 툴 추천이라기보다, 이미 잘 만들어 둔 `Obsidian + Codex` 운영 모델을 더 날카롭게 다듬으라는 신호에 가깝다. 핵심은 Claude를 Codex로 바꿔 읽고, `Claude.md`를 `AGENTS.md`와 주제별 운영 노트로 번역하는 것이다.

## Source

- YouTube: https://www.youtube.com/watch?v=rJo7_HZridY
- Source note: [2026-04-25_obsidian-claude-codex-workflow_sources.md](../notes/2026-04-25_obsidian-claude-codex-workflow_sources.md)
