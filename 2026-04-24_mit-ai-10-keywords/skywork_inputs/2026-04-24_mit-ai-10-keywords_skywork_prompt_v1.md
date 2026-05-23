# Skywork Prompt v1 - MIT AI 10 Keywords

이 프롬프트는 Skywork.ai 웹 서비스에서 실제 파워포인트 산출물을 생성하기 위한 입력이다. 로컬 PPTX 생성으로 대체하지 말고, Skywork의 `파워포인트` 모드에서 아래 파일을 업로드한 뒤 새 deck을 생성하라.

## Upload Order

1. `skywork_inputs/LGD_Template.pptx`
2. `reports/2026-04-24_mit-ai-10-keywords_deepresearch.md`
3. `reports/2026-04-24_mit-ai-10-keywords_memo.md`
4. `notes/2026-04-24_mit-ai-10-keywords_sources.md`
5. `notes/2026-04-24_mit-ai-10-keywords_deepresearch_prompt.md`

## Project

- Project name: `2026-04-24 MIT AI 10 Keywords`
- Language: Korean
- Ratio: 16:9
- Target length: 12 slides
- Mode: `파워포인트`, professional / expert technical briefing
- Template: `LGD_Template.pptx`

## Audience

- engineering leaders
- technical strategy leaders
- AI governance / security owners
- research and innovation teams
- executives who need a decision-oriented AI trend briefing

## Core Thesis

MIT Technology Review가 제시한 `AI 10대 키워드`는 유행 키워드 모음이 아니라, 2026년 AI 경쟁축이 `모델 성능`에서 `실행 시스템`, `물리 세계`, `신뢰/안보`, `오픈 생태계`, `과학 자동화`로 이동하고 있음을 보여주는 신호다.

## Source Policy

- Use the deep research report and memo as the primary content source.
- Treat the MIT Technology Review article as the editorial framing source.
- Use official docs, research pages, government references, and official repos as factual anchors.
- Keep exact dates where available.
- Separate confirmed facts, interpretation, and open questions.

## Must-Use Messages

- The public Korean MIT article title says `10 keywords`, but the visible page headings effectively expand into 11 items; analytically the report bundles `AI anxiety` and `backlash` into one socio-political cluster.
- Physical AI is now a data problem as much as a model problem.
- `LLMs+` means model plus tools, memory, reasoning, multimodal inputs, and controlled execution.
- Agent orchestration is becoming the real product layer.
- AI-enabled fraud and weaponized deepfakes make trust infrastructure a core architectural requirement.
- China’s open-model push is an ecosystem strategy, not only a benchmark story.
- AI scientist systems are becoming practical research accelerators in literature search, hypothesis generation, and experiment planning.

## Slide Structure

1. Title: `MIT AI 10대 키워드가 말하는 2026 AI 경쟁축`
2. Executive signal map: 4 macro shifts
3. Keyword list normalized into 10 strategic clusters
4. Physical AI: humanoid robot data + world models
5. Post-LLM stack: LLMs+ + agent orchestration
6. Trust battlefield: fraud, deepfakes, military decision support
7. Social adoption constraints: anxiety and backlash
8. China open-source strategy and ecosystem implications
9. AI scientists: from literature search to research acceleration
10. What is confirmed vs still early
11. 6-12 month preparation agenda
12. Final synthesis: from model adoption to execution-system strategy

## Layout Policy

- Use the LGD template rhythm.
- Prefer dense briefing slides, matrix layouts, timelines, risk grids, and operating-model diagrams.
- Use source footers in small dark-gray text on fact-heavy slides.
- Use small dark-green annotation text for caveats such as `confirmed`, `interpretation`, `open question`.
- Avoid sparse marketing-style slides.
- Each slide should end with a decision-relevant takeaway.

## Avoid

- simple hype narration
- vague claims like `AI will change everything`
- unsupported benchmark chest-thumping
- treating all 10 keywords as disconnected topics
- unlabeled speculation about AGI

## Export Requirement

After generation, provide and download:

- PPTX export for editable handoff
- PDF export for visual fidelity review
- project URL and viewer URL, if available
