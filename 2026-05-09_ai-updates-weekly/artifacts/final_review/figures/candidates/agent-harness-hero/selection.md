# Agent Harness Hero Selection

Selected figure: `../../agent-harness-hero-v2-web.png`

Reason:

- The base image has article-quality texture and avoids a slide-only look.
- It shows concrete objects tied to the review subject: permission card, checklist, connectors, documents, and a central work engine.
- It reads more naturally as an article hero than the annotated hybrid candidate.
- The deterministic label layer in `../../agent-harness-hero-annotated.svg` made the message explicit, but the result felt heavier and more slide-like than the opening section needs.
- NotebookLM was retried through Playwright CLI and produced an exported infographic candidate, but the image contains internal text quality issues and a NotebookLM watermark.
- Skywork was retried through Playwright CLI, but login/authentication blocked project and export creation.
