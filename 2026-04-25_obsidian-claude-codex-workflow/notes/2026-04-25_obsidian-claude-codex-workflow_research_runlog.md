# Research Run Log - Obsidian + Claude + Codex Workflow

Date: 2026-04-25

## Scope

- Goal: review the YouTube topic `Obsidian + Claude` and translate it into actionable insight for the current `Obsidian + Codex` environment
- Source URL: `https://www.youtube.com/watch?v=rJo7_HZridY`
- Review language: Korean

## Execution Log

### 1. Workspace and memory checks

- confirmed current workspace root: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
- checked workspace guide in local `AGENTS.md`
- checked memory entries related to:
  - `AI_Tech_Review`
  - `Obsidian_Vault`
  - `Obsidian mirror`
  - `Claude Mythos`
- checked:
  - `C:\Users\angpa\AGENTS.md`
  - `C:\Users\angpa\Obsidian_Vault\AGENTS.md`

### 2. Source capture

- fetched video metadata with `yt-dlp --dump-single-json --skip-download`
- downloaded English auto subtitles with:
  - `yt-dlp --skip-download --write-auto-subs --sub-langs "en" --sub-format "vtt" -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=rJo7_HZridY"`
- saved raw subtitle into:
  - `sources/rJo7_HZridY.en.vtt`

### 3. Transcript normalization

- parsed VTT into a cleaned transcript by:
  - removing `WEBVTT` headers
  - removing inline caption tags
  - collapsing repeated overlapping cue text
- saved outputs:
  - `sources/2026-04-25_obsidian-claude-codex-workflow_transcript_en.txt`
  - `sources/2026-04-25_obsidian-claude-codex-workflow_transcript_sentences_en.txt`

### 4. Local environment grounding

- confirmed current Obsidian vault root:
  - `C:\Users\angpa\Obsidian_Vault`
- confirmed current AI_Tech_Review mirror root:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review`
- confirmed current repo-side package structure and existing mirrored topic folders

### 5. Output authoring

- wrote source note
- wrote memo
- wrote deep research style report
- rendered HTML companions from the markdown reports
- mirrored final markdown reports into the Obsidian mirror root

## What Was Not Done

- no external web research beyond the direct YouTube source and subtitle retrieval
- no separate GPT deep research run
- no Skywork deck generation
- no OpenProject update

## Reason For Skipping Those Steps

- this request was handled as a source-grounded contextual review tied to one video and the user's current workflow
- the requested output was practical insight and utilization planning, not a slide package or work-package handoff

## Output Paths

- Source note: [2026-04-25_obsidian-claude-codex-workflow_sources.md](./2026-04-25_obsidian-claude-codex-workflow_sources.md)
- Memo: [2026-04-25_obsidian-claude-codex-workflow_memo.md](../reports/2026-04-25_obsidian-claude-codex-workflow_memo.md)
- Report: [2026-04-25_obsidian-claude-codex-workflow_deepresearch.md](../reports/2026-04-25_obsidian-claude-codex-workflow_deepresearch.md)
