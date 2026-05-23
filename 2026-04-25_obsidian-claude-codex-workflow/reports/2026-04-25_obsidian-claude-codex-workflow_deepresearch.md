# Obsidian + Claude Video Review For Current Obsidian + Codex Environment

Date: 2026-04-25

## Summary

- 이 영상의 핵심 문제 정의인 `AI amnesia`는 유효하다. 다만 해결책의 본질은 `Claude`가 아니라 `지속 맥락을 주는 메모리 구조`다.
- 당신의 현재 환경은 이미 `Obsidian memory + repo execution + Codex orchestration + AGENTS.md hierarchy`를 갖추고 있어서, 영상의 기본 골격을 상당 부분 선점하고 있다.
- 따라서 최선의 다음 단계는 새 툴 도입이 아니라 `entity note`, `single source of truth`, `topic handoff`, `link hygiene`를 강화하는 것이다.
- 영상의 구조를 그대로 복제하기보다, 현재 Obsidian의 lifecycle 구조와 `AI_Tech_Review` 패키지 구조를 유지한 채 agent-readable 맥락을 늘리는 편이 더 맞다.

## 문제 정의

영상은 생성형 AI가 세션을 새로 시작할 때마다 사용자와 프로젝트의 맥락을 거의 잃는 문제를 `AI amnesia`라고 부른다. 이 문제 정의 자체는 과장이 아니다. 실제로 대화형 LLM은:

- 이전 프로젝트의 판단 이유
- 사람/조직/프로젝트 간 관계
- 장기 축적된 선호와 규칙
- 파일 변경의 역사와 중요도

를 자동으로 안정적으로 유지하지 못한다.

영상이 제시하는 해법은 Obsidian을 기억 계층으로, Claude Code를 실행 계층으로 결합하는 것이다. 이 조합은 충분히 설득력이 있다. 다만 당신의 경우 여기서 더 중요한 것은 `Claude`라는 상표가 아니라 `에이전트가 읽을 수 있는 장기 기억 구조`다.

## 영상의 핵심 주장

## 1. note app은 혼자서는 기억 창고일 뿐이다

발표자는 전통적인 note app이 정보 저장에는 좋지만, 생각을 대신하거나 맥락을 연결해 주지는 못했다고 본다. 그래서 저장량이 늘수록 생산성이 높아지기보다 검색 부담만 커졌다고 말한다.

이 진단은 부분적으로 맞다. 정리되지 않은 vault는 AI 이전에도 다시 찾기 어려운 창고가 되기 쉽다. AI가 붙었다고 자동으로 해결되지는 않는다. 오히려:

- 링크가 약한 노트
- 중복된 truth source
- 폴더 의미가 불명확한 구조
- 사람이 이해하기 어렵게 쌓인 raw note

는 AI에게도 애매한 입력이 된다.

## 2. 좋은 vault는 `human-friendly + AI-friendly`해야 한다

영상에서 가장 실무적인 포인트는 여기다. 발표자는 vault가:

- 사람이 쓰기 편해야 하고
- AI가 읽고 탐색하기 쉬워야 하며
- 검색이 아니라 연결과 합성까지 가능해야 한다

고 말한다.

이건 현재 환경에 거의 그대로 적용된다. `AI_Tech_Review`는 이미 주제 패키지 구조가 강하고, Obsidian은 장기 메모리를 맡고 있다. 따라서 해야 할 일은 `더 많은 노트`가 아니라 `더 잘 연결된 노트`다.

## 3. 계층형 instruction file이 중요하다

영상의 `Claude.md` 설명은 본질적으로:

- 루트 공통 지침
- 하위 폴더 전용 지침
- 프로젝트별 특화 지침

을 함께 읽히는 구조다.

이 부분은 현재 환경과 특히 잘 맞는다. 이미 `AGENTS.md`가:

- 사용자 글로벌 규칙
- vault 규칙
- workspace 규칙

으로 분화되어 있다. 즉, 기능상 필요한 토대는 이미 있다. 차이는 이름뿐이다.

## 현재 환경에 맞춘 재해석

## 1. 당신은 영상을 `복제`할 필요가 없다

영상은 Obsidian 안에 기억과 실행을 함께 둔 작업공간을 보여준다. 하지만 당신은 이미 더 나은 분리 모델을 갖고 있다.

### 현재 구조의 장점

| 역할 | 현재 위치 | 장점 |
| --- | --- | --- |
| 장기 기억 | `C:\Users\angpa\Obsidian_Vault` | 사람이 읽는 기록과 장기 맥락 보존에 적합 |
| 실행 패키지 | `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review` | raw source, transcript, reports, exports 관리가 명확 |
| 에이전트 제어 | `AGENTS.md` 계층 | Codex 행동 규칙과 저장 규칙을 명시 가능 |
| 지식 승격 | `Obsidian_Vault\AI_Tech_Review` mirror | 장기 재활용 가능한 memo/report 축적 |

즉, 당신은 이미 `기억과 실행의 분리`를 해 두었다. 이건 단일 vault 운영보다 재현성과 파일 관리 측면에서 더 강하다.

## 2. 영상의 `people network`는 당신에게 `entity network`가 되어야 한다

발표자는 사람 노트를 강조한다. 이건 좋지만, 현재 업무에는 더 넓은 단위가 필요하다.

### 우선순위가 높은 entity

1. 사람
2. 조직
3. 프로젝트
4. OpenProject work package
5. 반복 연구 주제
6. 운영 규칙
7. 템플릿과 deliverable 형식

예를 들어 지금 환경에서는 사람 노트만큼 다음이 중요하다.

- `LG Display`
- `Anthropic`
- `Palantir`
- `Display Week`
- `Daily Pulse`
- `Skywork`
- `AI_Tech_Review` 패키지 규칙

즉, 사람 노트만 강화하면 절반만 맞다. 당신에게는 `entity graph`가 더 실무적이다.

## 3. 영상의 `single source of truth`를 더 엄격하게 써야 한다

영상에서는 제품 레지스트리를 single source of truth로 둔다고 설명한다. 현재 환경에서 이 개념은 더 넓게 쓸 수 있다.

### single source of truth 후보

- 주제별 최종 memo
- 주제별 deep research report
- 운영 규칙 note
- canonical template path
- OpenProject 연동 기준
- Obsidian 저장 위치 규칙

이 규칙이 명확해질수록 Codex는 매번 같은 질문을 다시 하지 않고 더 일관되게 작업할 수 있다.

## 바로 적용할 활용안

## 1. `Obsidian = durable memory`, `repo = execution` 원칙을 더 명시한다

이 원칙은 이미 암묵적으로 작동 중이다. 이제는 명시적으로 운영하면 된다.

### Obsidian에 남길 것

- 왜 이 주제를 시작했는지
- 어떤 해석 프레임을 썼는지
- 어떤 엔티티와 연결되는지
- 어떤 규칙이 반복적으로 등장하는지
- 어떤 판단이 바뀌었는지

### repo에 남길 것

- 원본 파일
- transcript
- 조사 메모
- 산출물
- 자동화 로그
- export 파일

## 2. topic package마다 `briefing block`을 추가한다

현재 source note와 run log는 이미 좋다. 여기에 아래 네 항목을 더 고정하면 Codex 활용성이 올라간다.

### 권장 briefing block

- `Current thesis`
- `What is already confirmed`
- `What still needs validation`
- `Next best action`

이 네 줄만 있어도 다음 세션에서 에이전트의 재가동 비용이 크게 줄어든다.

## 3. `daily_research_review -> promoted package` 연결을 더 명시한다

영상은 기억 연결을 강조한다. 현재 워크플로우에서는 그 연결점이 daily intake와 promoted topic 사이에 있다.

여기서 강화할 포인트는:

- 이 주제가 어느 daily review에서 나왔는지
- 왜 별도 패키지로 승격했는지
- 원래 후보군 중 무엇을 버렸는지

이 세 가지다. 이 정보는 나중에 `선택의 역사`를 복기할 때 중요하다.

## 4. entity note를 Obsidian에 축적하되 top-level 구조는 유지한다

영상의 폴더 체계를 그대로 베끼는 것은 권하지 않는다. 현재 vault는 lifecycle 기반이다.

- `00. Inbox`
- `01. Meetings`
- `30. Permanent Notes`
- `80. References`
- `81. System_Agent_Rules`

이 체계는 이미 일관성이 있다. 따라서 새 top-level folder를 여러 개 만드는 것보다:

- 사람/조직/entity note는 `30. Permanent Notes` 또는 `80. References`
- 반복 workflow 규칙은 `81. System_Agent_Rules`
- 회의성 메모는 `01. Meetings`

식으로 현재 질서를 유지하는 편이 낫다.

## 5. `Claude.md`를 흉내 내지 말고 `AGENTS.md + note` 조합을 강화한다

이건 이 영상을 당신 환경에 적용할 때 가장 중요한 번역 포인트다.

### 영상

- `Claude.md`가 루트와 폴더에서 instruction stack을 형성

### 현재 환경

- `AGENTS.md`가 이미 전역, vault, workspace 레벨에서 instruction stack을 형성

따라서 새로 필요한 것은 또 하나의 instruction file 포맷이 아니라:

- topic별 handoff note
- entity note
- reusable rule note

이다.

## 6. 사람 노트는 `follow-up memory`에 초점을 둔다

영상에서 인상적인 부분은 사람 노트가 단순 연락처가 아니라 follow-up 문맥을 묶는다는 점이다. 이건 현재 환경에서도 바로 쓸 수 있다.

예를 들어 사람/조직 노트에:

- 마지막 접점
- 열린 액션
- 관련 프로젝트
- 참고한 자료
- 다음 확인 포인트

를 붙이면, Codex가 이후 메일/회의/리서치 작업에서 더 좋은 질문을 만들 수 있다.

## 하지 말아야 할 것

## 1. vault를 raw artifact 창고로 만들기

raw transcript, export, 자동화 산출물까지 vault에 다 넣으면 링크는 많아져도 실제 사용성은 떨어진다.

## 2. 지침 파일을 늘리는 것 자체를 목표로 삼기

instruction stack은 중요하지만, 파일 수가 많다고 좋아지지 않는다. 중요한 것은 `누가 무엇의 single source of truth인지`가 분명한가다.

## 3. 사람 노트만 만들고 프로젝트/주제/규칙 노트를 비워 두기

현재 업무는 research packaging과 agent orchestration이 핵심이므로, 사람보다 프로젝트/규칙/entity 노트의 비중이 더 높다.

## 4. 영상의 폴더 체계를 현재 vault 위에 그대로 덮어씌우기

지금 구조는 lifecycle 기준으로 이미 정리돼 있다. 영상의 구조는 참고 프레임이지, 그대로 복제할 템플릿은 아니다.

## Recommended operating model

## Layer 1. Obsidian

- 장기 맥락
- entity graph
- 규칙
- 판단 로그
- 인간 중심 회고

## Layer 2. AI_Tech_Review repo

- 실제 실행 패키지
- source capture
- transcript normalization
- report authoring
- export management

## Layer 3. Codex

- source note를 읽고
- AGENTS.md를 따르고
- package structure를 유지하며
- 실행과 문서화를 오케스트레이션

## Layer 4. Mirror loop

- 최종 memo/report를 Obsidian mirror로 승격
- 이후 주제에서 장기 기억으로 재활용

## Final assessment

이 영상은 현재 환경에 잘 맞는다. 다만 `Obsidian + Claude`라는 표면 조합만 가져오면 절반만 가져오는 것이다. 당신에게 더 중요한 메시지는 다음 한 줄로 요약된다.

`Obsidian을 지식 저장소로만 두지 말고, Codex가 다시 불러와 실행할 수 있는 장기 맥락 계층으로 다뤄라. 다만 실행 산출물 저장소까지 Obsidian으로 밀어 넣지는 마라.`

이미 구축된 `Obsidian_Vault + AI_Tech_Review + AGENTS.md` 구조는 이 영상을 적용하기에 충분히 성숙해 있다. 지금 필요한 것은 새 툴이 아니라, `entity 중심 연결`, `briefing note`, `single source of truth`, `mirror hygiene`를 더 엄격하게 운영하는 것이다.

## External References

- Video: https://www.youtube.com/watch?v=rJo7_HZridY
- Source note: [2026-04-25_obsidian-claude-codex-workflow_sources.md](../notes/2026-04-25_obsidian-claude-codex-workflow_sources.md)
- Raw subtitle: [rJo7_HZridY.en.vtt](../sources/rJo7_HZridY.en.vtt)
- Clean transcript: [2026-04-25_obsidian-claude-codex-workflow_transcript_en.txt](../sources/2026-04-25_obsidian-claude-codex-workflow_transcript_en.txt)
