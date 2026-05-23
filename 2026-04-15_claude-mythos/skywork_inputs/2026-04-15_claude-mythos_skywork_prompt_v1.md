# Skywork Prompt v1

Project name: Claude Mythos 심층 리뷰

Use the uploaded `LGD_Template.pptx`, deep research report, memo, and sources note to produce a Korean presentation for engineers, security leaders, AI platform builders, and technical executives.

## Core thesis

2026-04-15 기준 `Claude Mythos`는 `완전히 새로운 마법적 agent substrate`라기보다, 범용 frontier model의 코드·추론·자율성 향상이 `exploit-generation threshold`를 넘어선 사건으로 읽는 편이 더 정확하다. 동시에 Anthropic은 `Project Glasswing`를 통해 이 기술적 경고를 `industry standards`, `enterprise trust`, `critical infrastructure`, `public-private coordination`의 아젠다 선점으로 전환하려 하고 있다.

## Non-negotiable content rules

- Mythos를 단순 공포 마케팅으로 축소하지 말 것
- 반대로 Mythos를 `Codex나 다른 agent 생태계로는 상상조차 못 하는 완전 이질적 기술`로 과장하지 말 것
- `facts / interpretation / uncertainty`를 분리할 것
- 날짜를 정확히 쓸 것:
  - 2026-03-06: Anthropic exploit writeup
  - 2026-03-31: Salesforce partnership expansion
  - 2026-04-07: Mythos / Glasswing / system card
  - 2026-04-15: this review date
- Anthropic의 직접 주장과 우리 해석을 반드시 구분할 것
- `MCP`, `AGENTS.md`, Linux Foundation agent standards 맥락을 넣어 `agent infrastructure는 점점 interoperable`하다는 점을 설명할 것
- 따라서 moat는 protocol lock-in보다 `model quality`, `eval operations`, `partner access`, `safety governance`, `enterprise trust`에 있다는 점을 설명할 것

## Must-include factual anchors

- Anthropic says Mythos is a `general-purpose` unreleased frontier model with unusually strong cyber capabilities
- Anthropic says these cyber capabilities `emerged` from gains in code, reasoning, and autonomy, not explicit cyber-specific training
- Mythos benchmark deltas versus Opus 4.6:
  - Firefox JS shell exploit benchmark: 181 successful exploits and 29 additional register-control outcomes for Mythos versus 2 successes for Opus 4.6
  - Internal OSS-Fuzz-style benchmark: Mythos reaches ten tier-5 control-flow hijacks on fully patched targets
  - Glasswing benchmark panel:
    - CyberGym 83.1% vs 66.6%
    - SWE-bench Pro 77.8% vs 53.4%
    - Terminal-Bench 2.0 82.0% vs 65.4%
    - SWE-bench Verified 93.9% vs 80.8%
- Glasswing coalition includes AWS, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, Linux Foundation, Microsoft, NVIDIA, and Palo Alto Networks
- Anthropic commits up to $100M usage credits and $4M donations
- Anthropic says Mythos is not planned for general availability
- Anthropic says it wants to share lessons, publish recommendations, and help shape standards and practices
- System card includes alignment, evaluation awareness, reckless-actions, and model welfare sections, which helps explain the public virality

## Required analytical conclusions

1. **Technology reality**
   - Mythos is a real capability warning
   - The major shift is from bug-finding to exploit generation and chaining
   - The scaffolds are familiar; the capability threshold is the story

2. **Competitive interpretation**
   - Current public evidence suggests Anthropic has stronger published evidence than peers in this narrow cyber slice
   - That does not imply peers cannot get there
   - The right reading is not impossibility but convergence risk

3. **Agenda-setting interpretation**
   - Glasswing is both safety move and power move
   - Anthropic is attempting to define the terms of responsible deployment before rivals normalize similar systems

4. **Practical response**
   - Developers and security teams must assume faster vulnerability discovery and faster exploit prototyping
   - They need secure-by-default development, stronger fuzzing, exploitability-aware triage, agent sandboxing, logging, policy, and human verification

## Recommended slide structure

1. Title and thesis
2. Why Claude Mythos matters now
3. What Anthropic actually announced on 2026-04-07
4. Mythos as technology: what changed versus Opus 4.6
5. Why this is not magic new architecture
6. Why this still counts as a threshold event
7. Project Glasswing as defensive initiative
8. Project Glasswing as agenda-setting move
9. Open ecosystem context: MCP, AGENTS.md, Linux Foundation
10. Can Codex or other agent ecosystems get here?
11. What this means for developers and security teams
12. What researchers should measure next
13. Strategic watchlist for the next 6 to 18 months
14. Closing recommendation

## Style rules

- LG Display white-grid corporate rhythm 유지
- sparse marketing deck 금지
- information-dense technical briefing
- timeline, evidence matrix, benchmark comparison table, and action checklist 적극 사용
- 작은 진회색 reference text 배치
- caveat / uncertainty / interpretation distinction은 작은 짙은 녹색 inline text 또는 명확한 sublabel로 처리
- 전문가가 봐도 싱겁지 않게 깊이를 유지할 것
