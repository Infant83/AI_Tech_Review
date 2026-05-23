# Skywork prompt v1

## Template

Use `LGD_Template.pptx` as the default template.

Template path:
`C:\Users\angpa\.codex\skills\skywork-ppt-workflow\assets\LGD_Template.pptx`

## Deck purpose

Create a technically credible Korean paper-review deck for engineers, product managers, AI tool users, and internal decision makers.

The deck should focus on the insight from Wen et al. `Exploration vs. Fixation`, not on the AI Matters article. The article can appear only as the discovery route.

## Audience

- Engineers and technical managers who use AI for research, design, coding, writing, slides, and planning.
- People who already use ChatGPT/Claude/Copilot but may be overusing direct execution prompts.

## Main judgment

The paper does not say "do not use ChatGPT for ideas." It shows that immediate artifact generation can narrow exploration. AI users need a workflow that delays the first final-looking output, surfaces remote alternatives, and makes refinement intent inspectable before execution.

## Voice

- Korean.
- Internal technical reviewer tone.
- Avoid AI-sounding contrast phrases such as `A가 아니라 B이다`, `단순히 A가 아니다. B다`, `A뿐만 아니라 B`.
- Avoid empty phrases such as `핵심은`, `시사하는 바는`, `결론적으로`, `요컨대`.
- Use concrete claims, dates, sample sizes, and metrics.

## Source pack

- `reports/2026-04-28_exploration-vs-fixation_deepresearch.md`
- `reports/2026-04-28_exploration-vs-fixation_memo.md`
- `notes/2026-04-28_exploration-vs-fixation_claim_audit.md`
- `notes/2026-04-28_exploration-vs-fixation_sources.md`
- `sources/2512.18388v2_exploration_vs_fixation.pdf`

## Slide plan

1. Title
   - Title: `AI 협업은 첫 산출물을 늦출수록 넓어진다`
   - Subtitle: `Exploration vs. Fixation 논문 기반 실무 리뷰`

2. Why this paper matters
   - Immediate execution creates a first artifact too early.
   - First artifact becomes a hidden anchor.
   - The practical issue is workflow design.

3. Problem model
   - Premature convergence
   - Design fixation
   - Gulf of envisioning
   - Use a simple flow diagram from prompt to artifact to local edits.

4. HAICo design
   - Divergent mode: idea grid, remote conceptual ideas.
   - Convergent mode: semantic parameters and options.
   - Non-linear switching and history preservation.

5. Experiment results
   - N=24 within-subjects poster task.
   - CSI all p<0.002.
   - UMUX 81.25 vs 64.24.
   - Novelty 3.22 vs 2.41.
   - Diversity 0.48 vs 0.36.
   - Fluency/usefulness not significant.

6. Learning shift
   - ChatGPT: system learning and prompting strategies.
   - HAICo: task-specific knowledge, new directions, workflow learning.
   - Brainstorm-first transfer is preliminary.

7. Strengthened evidence
   - Wadinambiarachchi et al. 2024: GenAI image exposure can increase fixation.
   - Doshi and Hauser 2024: individual creativity improves, collective diversity can fall.
   - Anderson et al. 2024: ChatGPT ideation can homogenize ideas across users.
   - Parallel prototyping: parallel alternatives can outperform serial refinement.

8. User workflow
   - Problem frame
   - Divergent card pass
   - Selection criteria
   - Convergent parameter pass
   - Artifact generation
   - Audit and branch archive

9. Prompt patterns
   - Idea card request.
   - Selection matrix request.
   - Semantic parameter request.
   - Team diversity assignment.

10. Where it applies
   - Research, slides, product planning, coding, image/design, meetings.
   - For coding: compare architectures before implementation.
   - For slides: compare narratives before formatting.

11. Limits and risks
   - N=24, CS/IT skew, image task, single session, self-reported learning.
   - Scaffolding can slow clear tasks.
   - Agency and ownership remain mixed.
   - HAICo is a research system.

12. Operating rule
   - Make AI show alternatives before artifacts.
   - Make AI expose interpretation before execution.
   - Measure diversity at the team level.
   - Keep rejected branches and reasons.

## Visual density

- Information-dense, not sparse.
- Use matrices, two-mode diagrams, and workflow lanes.
- References should appear in small text at the bottom of evidence-heavy slides.
