# daily_research_review

Shared container for daily intake reviews, cross-topic summaries, and overview markdown that should not live inside a single topic package.

Use this folder for:
- GPT Pulse daily checks
- multi-source daily intake reviews
- roundup notes used to choose the next deep-research target

Recommended package pattern:
- `daily_research_review/YYYY-MM-DD_<overview-slug>/sources/`
- `daily_research_review/YYYY-MM-DD_<overview-slug>/notes/`
- `daily_research_review/YYYY-MM-DD_<overview-slug>/reports/`
- `daily_research_review/YYYY-MM-DD_<overview-slug>/artifacts/`

Report deliverables in `reports/` should be kept as markdown system-of-record files and rendered to same-basename `.html` companions for polished local reading, section navigation, and direct link access.

Once a specific topic is chosen for deeper work, continue that work in a separate topic folder at the workspace root.
