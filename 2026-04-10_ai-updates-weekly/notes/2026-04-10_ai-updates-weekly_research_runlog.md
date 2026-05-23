# Research Run Log

## Intake
- Started from user-provided review request on `2026-04-14`
- Target asset: `https://www.youtube.com/watch?v=tILZuOvro6I`
- Package root: `2026-04-10_ai-updates-weekly/`

## Local Harvest
- Used `yt-dlp` to extract metadata, description, and English auto captions
- Downloaded creator companion deck from the linked `lselector/seminar` repository
- Parsed the PPTX to plain-text slide extracts and harvested deck links for validation planning

## Research Method
1. Use the weekly video and deck as the intake artifact
2. Extract the main claims and segment them into themes
3. Validate major claims against official blogs, docs, repositories, and release notes
4. Use reporting sources only for legal and labor-market topics
5. Normalize the result into memo, report, and Skywork slide prompt materials

## Verified Highlights
- Anthropic `Managed Agents` officially launched in public beta on `2026-04-08`, with standard token pricing plus `$0.08` per active session-hour
- Anthropic published a trustworthy-agents framing that distinguishes the model from the harness, tools, and environment
- Claude `Microsoft 365 connector` is documented as a read-only connector across Microsoft 365 content surfaces
- Google announced `Gemma 4` with multimodal support, agentic workflow support, and Apache 2.0 licensing
- Meta announced `Muse Spark` through Meta Superintelligence Labs as a closed product offering
- Microsoft Azure AI Foundry Labs published new `MAI` models in April 2026
- Cursor officially launched `Cursor 3` on `2026-04-02`
- Anthropic `Mythos Preview` is a controlled security preview, not a mainstream general release

## Judgment Calls
- The video is directionally strong on the rise of agents, memory, and tool-use surfaces
- The video is weaker when it treats the category as if traditional software is about to collapse immediately
- The `third-party Claude restriction` item remains insufficiently verified as a first-party policy change and is handled as a weak-signal item
- Labor-market data is mixed: layoffs remain elevated while some hiring indicators recovered

## Package Artifacts Produced
- source note
- deep-research prompt
- review memo
- deep research report
- Skywork prompt packet

## Skywork Runs
- First run:
  - project URL: `https://skywork.ai/project/2043732912911245312?from=home_query&is_new_project=false`
  - mode: `skill_id=102`, `Pro Mode`
  - upload bundle: `LGD_Template.pptx`, `deepresearch.md`, `memo.md`, `sources.md`, `slide-extract.md`, `skywork_prompt_v1.md`
  - outcome: generation completed and archived as the primary export set
  - export task:
    - `PPTX` task id: `2043739855718907904`
    - `PPTX` direct URL: `https://static-us-img.skywork.ai/html-to-pptx/presentations/4bd96f3c-57be-42e8-a825-a9fdfba15c53_2043735153985826816/2026-04-10%20AI%20Updates%20Weekly%20%EC%8B%AC%EC%B8%B5%20%EB%A6%AC%EB%B7%B0%3A%20%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8%20%EC%9A%B4%EC%98%81%20%EA%B3%84%EC%B8%B5%EC%9D%98%20%EB%B6%80%EC%83%81.pptx`
    - `PDF` task id: `2043740590691753984`
    - `PDF` direct URL: `https://static-us-img.skywork.ai/prod/doc/2026-04-13/3597530450966544533/2043740839150096384/2026-04-10_AI_Updates_Weekly_%EC%8B%AC%EC%B8%B5_%EB%A6%AC%EB%B7%B0%3A_%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8_%EC%9A%B4%EC%98%81_%EA%B3%84%EC%B8%B5%EC%9D%98_%EB%B6%80%EC%83%81.pdf`
  - archived exports:
    - `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-04-10_ai-updates-weekly\skywork_exports\2026-04-10_ai-updates-weekly_skywork_v1.pptx`
    - `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-04-10_ai-updates-weekly\skywork_exports\2026-04-10_ai-updates-weekly_skywork_v1.pdf`
- Second run:
  - project URL: `https://skywork.ai/project/2043736382242381824?from=home_query&is_new_project=false`
  - mode: `skill_id=102`, `Pro Mode`
  - upload bundle: `LGD_Template.pptx`, `deepresearch.md`, `memo.md`, `sources.md`, `slide-extract.md`, `skywork_revision_v2.md`
  - control change: explicitly disabled external web search and constrained generation to attached files only
  - current state: generation completed as a source-bound backup project, but the archived delivery pair was taken from the first completed export set above

## Downstream Sync
- OpenProject `TechReview`:
  - work package: `https://infant.tailcb5184.ts.net:8443/work_packages/56`
  - `PPTX` size: `11,891,369` bytes
  - `PDF` size: `26,391,777` bytes
  - attachment attempt failed because the current OpenProject per-file limit is `5,242,880` bytes (`5 MB`)
  - work package description was updated with local archive paths and direct Skywork download URLs instead
- Obsidian vault:
  - mirrored memo, deep research report, and daily review memo into `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review`
- Workspace docs:
  - updated daily review memo
  - regenerated root `README.md`
