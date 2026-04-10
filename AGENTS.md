# AI_Tech_Review Workspace Guide

## Purpose
- This workspace turns user-provided topics, ChatGPT Pulse reviews, local file paths, URLs, transcripts, papers, videos, and notes into research packages and presentation-ready outputs.
- The default operating model is:
  1. the review is initiated from an available intake interface such as a user-provided topic/source pack, a ChatGPT Pulse review, or a future interface-level source
  2. Codex compiles a deep-research prompt using the user-specified ChatGPT GPT `심층리서치 프롬프트 생성기`
  3. GPT deep research is executed
  4. the results are normalized into workspace markdown files
  5. NotebookLM is used as a supporting research and packaging layer when helpful
  6. Skywork is the default slide-generation system
- The goal is not only to summarize material, but to produce practical, technically credible insight that helps engineers, product teams, and decision makers understand a domain and act on it.

## Workspace Root Rule
- `AI_Tech_Review/` is the default workspace root for this reporting system.
- Shared tools belong only at the workspace root:
  - `AI_Tech_Review/scripts/`
  - `AI_Tech_Review/.automation/`
- Shared cross-topic intake and overview reviews should live under:
  - `AI_Tech_Review/daily_research_review/`
- Do not create per-topic `scripts/` or per-topic `.automation/` folders unless there is a specific one-off reason.
- `.automation/` is a persistent shared automation/runtime area for this workspace and should continue to exist.
- Temporary browser profile copies and scratch runtime files should be created under the system temp directory and cleaned up after use, not kept in the repository.

## Where To Start Work
- If the current working directory is `AI_Tech_Review/` and a new review starts, create one new topic folder under it and work inside that folder.
- If the user asks for a daily intake review, overview, or roundup across incoming feeds before selecting a single topic, prefer creating the package under `daily_research_review/` instead of mixing it into a topic folder.
- If the current working directory is already a topic folder, create files directly there and do not create another nested topic folder.
- If the user intentionally opened a dedicated subfolder as the working base for a batch or series, treat that folder as the container and create the topic package beneath it only when that makes the structure clearer.
- The agent should infer the correct working level pragmatically instead of forcing one fixed layout in every case.

## Naming Convention
- Create one topic folder per review target.
- Always name the folder as `YYYY-MM-DD_<topic-slug>`.
- Use stable slugs based on the topic, company, paper, product, or event name.
- Daily overview or intake-review packages under `daily_research_review/` should also use `YYYY-MM-DD_<overview-slug>` naming.
- Conversation-memory notes stored directly under `daily_research_review/` should use the filename `YYYY-MM-DD_<topic-slug>.md`.
- When the same date and same topic reappear in conversation, append to the existing markdown memo instead of creating a new sibling file.
- Use suffixes such as `_2` only when two different memo artifacts must coexist for the same date and topic and appending would be misleading.
- Recommended overview slugs include:
  - `gpt-pulse-daily-review`
  - `daily-intake-review`
  - `weekly-roundup-review`
- Recommended filenames:
  - `notes/YYYY-MM-DD_<slug>_sources.md`
  - `notes/YYYY-MM-DD_<slug>_pulse_review.md`
  - `reports/YYYY-MM-DD_<slug>_overview.md`
  - `notes/YYYY-MM-DD_<slug>_deepresearch_prompt.md`
  - `notes/YYYY-MM-DD_<slug>_research_runlog.md`
  - `reports/YYYY-MM-DD_<slug>_memo.md`
  - `reports/YYYY-MM-DD_<slug>_deepresearch.md`
  - `reports/YYYY-MM-DD_<slug>_notebooklm_sources.md`
  - `skywork_inputs/YYYY-MM-DD_<slug>_skywork_prompt_v1.md`
  - `skywork_inputs/YYYY-MM-DD_<slug>_skywork_revision_v2.md`
  - `skywork_exports/YYYY-MM-DD_<slug>_skywork_<variant>.pptx`
  - `skywork_exports/YYYY-MM-DD_<slug>_skywork_<variant>.pdf`

## Topic Folder Structure
- Topic folders are the unit of work for one review package.
- Recommended structure:
  - `sources/`: raw user-provided files, transcripts, metadata, extracted text, link lists, screenshots, downloaded source assets
  - `notes/`: source note, deep-research prompt, browser run logs, rough observations, validation notes
  - `reports/`: polished memo, deep research report, NotebookLM-ready source pack, optional PDF mirrors
  - `notebooklm_exports/`: NotebookLM screenshots, exported visual outputs, generated briefs, infographic outputs, supporting downloads
  - `skywork_inputs/`: Skywork prompt packets, revision packets, template notes, and run-control markdown
  - `skywork_exports/`: final Skywork decks, viewer captures worth archiving, and Skywork-specific downloadable outputs
  - `artifacts/`: optional holding area for browser downloads, temporary exports worth keeping, and other non-source generated artifacts
- `sources/` is optional when the package only needs markdown notes plus generated exports.
- `artifacts/` is optional when all outputs already fit naturally in the named folders above.

## Export Separation Rule
- Keep NotebookLM outputs and Skywork outputs in different folders.
- Use `notebooklm_exports/` only for:
  - NotebookLM slide exports
  - NotebookLM infographic exports
  - NotebookLM screenshots or supporting downloaded files tied to NotebookLM
- Use `skywork_exports/` only for:
  - final Skywork PPTX files
  - final Skywork PDF files
  - revised Skywork deck versions
  - viewer captures or downloaded files that are specifically produced by Skywork
- Do not place Skywork-generated decks under `notebooklm_exports/`.
- Do not place NotebookLM-generated visuals under `skywork_exports/`.
- If an export is saved into the wrong system folder during a run, move it immediately and update the related notes so the final package reflects the corrected system-specific path.
- Use `artifacts/` only as a temporary or mixed holding area when the output does not yet belong to a finalized system-specific folder.

## Daily Review Structure
- `daily_research_review/` is the shared container for cross-topic intake reviews, daily summaries, and overview markdown that should not be stored inside one specific topic package.
- Recommended structure:
  - `daily_research_review/YYYY-MM-DD_<overview-slug>/sources/`
  - `daily_research_review/YYYY-MM-DD_<overview-slug>/notes/`
  - `daily_research_review/YYYY-MM-DD_<overview-slug>/reports/`
  - `daily_research_review/YYYY-MM-DD_<overview-slug>/artifacts/`
- In addition to overview packages, `daily_research_review/` should also hold direct conversation-memory markdown files at the folder root:
  - `daily_research_review/YYYY-MM-DD_<topic-slug>.md`
- These direct markdown notes are the default Obsidian-friendly running memo for user conversations on a specific date and topic.
- Use this structure for:
  - GPT Pulse daily checks
  - multi-source daily intake reviews
  - summary or prioritization notes that exist before a single deep-research topic is selected
- Use direct root-level markdown memo files for:
  - ongoing user conversation notes tied to one concrete topic
  - review summaries that should be easy to open from Obsidian without navigating a package folder
  - spin-off topic capture before a root topic folder has been promoted into a full research package
- Once a specific topic is chosen for deeper work, create or continue a separate topic folder at the workspace root and reference the originating daily review package from that topic's source note.
- When a root topic folder already exists, reuse its topic slug inside the direct memo filename so the connection is obvious.
- When a spin-off topic does not yet have a root topic folder, create the direct memo first, then decide later whether to promote it into a full root-level topic package.

## Intake Model
- The workspace should tolerate multiple intake interfaces at the front of the workflow instead of hard-coding a single entry route.
- Supported intake sources can include user-provided topics, uploaded source packs, recurring digests such as ChatGPT Pulse, and future interface-level feeds.
- Regardless of where the intake originates, the workflow should converge back to the same normalized outputs: prompt, research run, memo, report, NotebookLM pack, and Skywork inputs.
- Cross-topic overviews and daily intake summaries belong in `daily_research_review/`; topic-specific deep work belongs in topic folders.
- When the intake source is a digest or summary layer such as GPT Pulse, preserve the original artifact in the package and explicitly state which claim set, theme, or subtopic is being promoted into the deeper workflow.
- If one intake artifact contains multiple unrelated stories, either:
  - split them into separate topic folders when they need separate research questions or separate decks
  - keep them together only when the intended output is a true roundup or weekly review deck

## What To Produce
- A source note markdown file that records the original inputs, extracted transcript or excerpts, key links, and rough observations.
- When the intake source is GPT Pulse, an archived copy or normalized capture of the Pulse review text, metadata, screenshots, or exported markdown/PDF should be kept in the topic folder.
- When the user asks to check today's Pulse first, a rough markdown review of the new Pulse items should be produced before any deep-research scope is chosen.
- When the work is an overview or daily intake review, store that markdown in `daily_research_review/.../notes/` or `daily_research_review/.../reports/` rather than in a topic folder.
- A deep-research prompt markdown file prepared for GPT deep research.
- A research run log that records how the prompt was executed, which files were uploaded, what browser path was used, and where downloads were saved.
- A review memo markdown file for quick reading and Obsidian capture.
- A deep research report markdown file with synthesis, comparison, implications, risks, and recommended next actions.
- A NotebookLM-ready source markdown file derived from the deep research report and any essential supporting notes.
- A Skywork prompt packet and revision packets for slide generation.
- Final NotebookLM exports into `notebooklm_exports/`.
- Final Skywork exports into `skywork_exports/`.
- Default Skywork delivery pair:
  - `PPTX` for editable handoff
  - `PDF` for visual fidelity review and archival

## Standard Workflow
1. Receive the review target from the current intake interface, along with any available seed sources or digest artifacts.
2. Create the topic folder as `YYYY-MM-DD_<topic-slug>`.
3. Copy, extract, or reference the seed materials into `sources/`.
4. If the intake source is a digest, summary, or recurring review feed, save the original artifact, capture its metadata, and define the exact research scope that will be promoted into the full workflow.
5. If the source is video or audio, extract a transcript first.
6. Write `notes/..._sources.md` with the original inputs, transcript references, digest references when applicable, preliminary observations, and open questions.
7. Use the user-specified ChatGPT GPT `심층리서치 프롬프트 생성기` at `https://chatgpt.com/g/g-69c236b0ec2481919676d5fc2549d675-simceungriseoci-peurompeuteu-saengseonggi` to compile a deep-research prompt.
8. Save that prompt into `notes/..._deepresearch_prompt.md`.
9. Execute the deep research in GPT using one of these paths:
   - prefer a dedicated research skill or MCP if one exists and is reliable for the task
   - otherwise use Playwright browser automation to drive ChatGPT deep research
10. Save the raw or normalized research results into markdown files under `notes/` and `reports/`, and record the execution details in `notes/..._research_runlog.md`.
11. Normalize the findings into a polished `reports/..._deepresearch.md` and `reports/..._memo.md`.
12. Prepare `reports/..._notebooklm_sources.md` from the deep research report and any high-value supporting notes.
13. Use NotebookLM when it helps with source packaging, Q&A, concept checks, or supplementary exports, but do not treat NotebookLM as the default final slide-authoring system.
14. Use the Skywork skill as the default slide-generation path.
15. Generate an information-dense, technically rigorous deck that is easy to follow without flattening important specialist detail.
16. Audit the generated deck against the deep research report, then create Skywork revision packets if drift, oversimplification, or audience mismatch remains.
17. Download and archive Skywork decks under `skywork_exports/` and NotebookLM outputs under `notebooklm_exports/` so the package remains self-contained and system-separated.
18. Unless the user explicitly opts out, export Skywork outputs in both `PPTX` and `PDF` from the same project/version and store both files together in `skywork_exports/`.

## Daily Pulse Review Workflow
- If the user says something like `check today's Pulse`, `오늘의 Pulse를 체크해줘`, or otherwise asks for the latest Pulse review, first perform an intake-and-triage pass instead of jumping directly into deep research.
- In that mode, Codex should:
  - open GPT Pulse and identify the newly presented report or reports for the current day
  - capture the key items, links, claims, and topic candidates
  - create a daily review package under `daily_research_review/YYYY-MM-DD_gpt-pulse-daily-review/`
  - normalize them into a rough markdown review such as `daily_research_review/YYYY-MM-DD_gpt-pulse-daily-review/notes/YYYY-MM-DD_gpt-pulse-daily-review_pulse_review.md`
  - present that review back to the user as a decision surface for selecting the next deep-research target
- Only after the user picks a direction should Codex promote the chosen Pulse topic into the full `deepresearch -> memo/report -> Skywork slides` workflow.
- If the user wants a roundup deck based on the whole Pulse set, the daily Pulse intake folder can remain the main package.
- If the user wants one specific theme from Pulse, create a separate topic folder for that promoted theme and carry forward the relevant Pulse notes and source links.

## Deep Research Prompting Rules
- Treat the user-provided GPT `심층리서치 프롬프트 생성기` as the default prompt-compilation accelerator for GPT deep research.
- The prompt should be built from the real source pack, not from memory alone.
- When the source pack begins with GPT Pulse, the prompt should explicitly distinguish:
  - what Pulse already claims or summarizes
  - what must still be verified with external or primary sources
  - which Pulse themes are worth expanding into a full technical review
- The prompt should state:
  - topic
  - target audience
  - explicit research questions
  - required source priorities
  - expected deliverables
  - version/date sensitivity
  - required comparison points
  - risks or uncertainty to validate
- If the GPT-generated prompt is weak, incomplete, or overly generic, refine it before running the deep research pass.
- Save prompt versions so the workflow remains auditable and repeatable.

## GPT Deep Research Execution Rules
- Prefer a stable tool path over manual browsing.
- If a dedicated MCP or skill becomes available for deep research, prefer it over brittle UI automation.
- If browser execution is required, use Playwright to:
  - open the relevant GPT
  - submit the compiled prompt
  - attach or reference source files if needed
  - wait for completion
  - download or copy the result
  - capture key screenshots when the run state matters
- Record enough metadata to resume the task later without guessing what happened.

## GPT Pulse Conventions
- GPT Pulse is a supported intake example for this workspace, not a permanently special-case branch.
- Preserve as much of the original Pulse context as possible:
  - issue title
  - date received or published date
  - source URL
  - captured review text
  - screenshots or exported artifacts when useful
- Use Pulse as a discovery and prioritization layer to identify:
  - topics that deserve a full deep-research pass
  - comparisons that need validation
  - emerging themes worth tracking across multiple days or weeks
- The default behavior for Pulse should be:
  - first review and summarize the new Pulse material in markdown
  - then let the user choose which candidate deserves deeper work
- Any concrete factual claim that appears in Pulse should be validated against better sources before it is treated as a report conclusion or slide fact.
- If the user wants a recurring workflow, Pulse items can be promoted daily into the normal package flow without changing the downstream deliverables.

## Writing Rules
- Prefer exact dates and version numbers over relative wording.
- Separate facts, interpretation, and speculation clearly.
- Cite source URLs in the markdown whenever the report depends on external material.
- Use primary sources first for technical claims when they are available.
- Note uncertainty explicitly instead of smoothing it over.
- Keep outputs useful for both self-study and team sharing.
- Default to markdown as the system of record even when downloads exist in other formats.

## NotebookLM Conventions
- Use the deep research report as the core NotebookLM source document.
- Add supporting notes or transcripts only when they improve coverage or reduce ambiguity.
- When browser automation is needed, use Playwright for upload and export flows.
- Download all generated NotebookLM files into the topic folder, not into temporary locations.
- NotebookLM is a support layer for source packaging, Q&A, and visual side artifacts, not the default end-state presentation renderer.

## Skywork Conventions
- Use the `skywork-ppt-workflow` skill as the default slide-generation path.
- Treat Skywork as the renderer and Codex as the orchestrator.
- When a slide-generation run is executed for this workspace, treat `LGD_Template.pptx` as the default presentation template unless the user overrides it.
- When using Skywork, explicitly mention that `LGD_Template.pptx` is the template and upload that template together with the source materials or prompt packet.
- The template does not need to live in the workspace root if the Skywork skill already provides it; prefer the skill-managed asset at `C:\Users\angpa\.codex\skills\skywork-ppt-workflow\assets\LGD_Template.pptx` when available.
- Build the Skywork prompt from:
  - the deep research report
  - the memo
  - the source pack
  - template rules
  - audience and purpose constraints
- Default deck quality bar for technology reviews:
  - information-dense rather than sparse
  - easy to follow without being simplistic
  - suitable for engineers, technical managers, and expert audiences
  - explicit about evidence, tradeoffs, limitations, and implications
  - rich enough to surface non-obvious expert insight
- The deck should not hide technical nuance just to look cleaner.
- Save Skywork prompt versions, screenshots, revision packets, project links, viewer links, and download paths into `skywork_inputs/`.
- Save final downloaded Skywork deck files into `skywork_exports/`.
- When Skywork is used, default to downloading both:
  - `PPTX` as the editable source
  - `PDF` as the visual-reference source
- If the PPTX and PDF differ in perceived quality, treat the PDF as the visual baseline and note the discrepancy in the run log or project note.

## Automation Model
- This workspace uses orchestration automation, not a single one-click pipeline.
- The main automation layers are:
  - file-system automation for folder creation, naming, and artifact organization
  - source-processing automation for transcript extraction, file normalization, and metadata capture
  - research automation for prompt compilation, GPT Pulse intake normalization, GPT deep research execution, and result harvesting
  - browser automation for ChatGPT Pulse, ChatGPT deep research, NotebookLM, and Skywork flows when API or MCP routes are unavailable
  - documentation automation for markdown report generation and packaging
  - review-loop automation for Skywork prompt correction and export tracking
- The intended pattern is `Codex prepares and validates the work, external systems generate or synthesize where useful, and Codex records everything back into the workspace`.

## Obsidian Conventions
- Markdown should remain plain and portable so it renders well in Obsidian.
- Prefer short sections, bullet summaries, callouts only when they add value, and consistent tags/frontmatter when useful.
- The dedicated Obsidian mirror root for this workspace is `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review`.
- Mirror workspace-facing markdown there after it is finalized.
- For direct conversation-memory notes, mirror:
  - `AI_Tech_Review/daily_research_review/YYYY-MM-DD_<topic-slug>.md`
- For promoted topic packages, mirror the relevant memo and deep research report under the corresponding topic folder inside the Obsidian mirror root when needed.
- Until a separate vault path is specified, treat the root-level markdown files under `daily_research_review/` as the default Obsidian-facing memo layer for ongoing conversation history.

## Example Pattern
- User gives a topic plus local files, URLs, or video sources.
- Extract transcript and normalize source files.
- Build a deep research prompt with the specified GPT.
- Run GPT deep research and save the output.
- Alternatively, user provides a GPT Pulse review, Codex promotes one topic or a roundup from it, validates the source pack, and then runs the same prompt-to-research-to-slides flow.
- Alternatively, user asks for today's Pulse check first, Codex reviews the new Pulse report, writes a rough markdown review under `daily_research_review/`, and waits for the user's choice before promoting one topic into deep research and slides.
- Produce:
  - a source note
  - an optional Pulse review note when Pulse is the intake layer
  - a deep-research prompt file
  - a research run log
  - a memo
  - a deep research report
  - a NotebookLM source pack
  - Skywork prompt packets
  - final slide exports

## Current Default
- The first example in this workspace is the March 06, 2026 AI news review based on the provided YouTube video.
- That example package lives under `2026-03-06_ai-updates-weekly/`, while shared scripts and automation live at the workspace root.
