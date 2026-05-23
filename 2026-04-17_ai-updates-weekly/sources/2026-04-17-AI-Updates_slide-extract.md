## Slide 1: Slide 1
- Crowd-sourced "LM Arena" Leaderboard
- Anthropic Plugins
- MCP = Model Context Protocol
- Claude Mythos
- Claude Opus 4.7
- Claude Agent SDK
- AI Updates - Apr 17, 2026
- Jobs & Layoffs
- OpenClaw Updates
- Claude Code & Claude Desktop Updates
- Claude Code Skills, Plugins, CLIs
- Work with Google Work Space (GWS)
- 33 Claude Skills and more resources
- InfraNodus - Generate Ideas
- Cognee gives your AI a persistent memory
- Adding Workflow Builder to your Agent
- More Desktop Agents
- Seedance 2.0 Video Generation
- Topview AI Agent V2 uses Seedance 2.0
- Railway Deployment
- Moonshots Podcast #246
- AI is no longer Optional
- AI Agency "SureThing"
- How to setup Hermes Agent
- Convert Claude Code into ClaudeClaw
- Anthropic ARR $30B vs $25B OpenAI
- "Anthropic's 30x growth in 15 months is not a trend. It's a phase transition."
- Anthropic ARR:
- $1 Bln in Jan 2025
- $30 Bln in April 2026

## Slide 2: Slide 2
- Starting Elo rating = 1000
- https://en.wikipedia.org/wiki/Elo_rating_system
- "LM Arena" Leaderboard
- English - https://lmarena.ai/leaderboard/text
- Coding - https://lmarena.ai/leaderboard/text/coding
- https://lmarena.ai/leaderboard/text
- Design Arena - https://www.designarena.ai
- https://openlm.ai/chatbot-arena/
- https://beta.lmarena.ai
- Web Leaderboard - 1T params https://web.lmarena.ai/leaderboard
- LLM Leaderboard - by @LlmStats - https://llmworld.net/llm_leaderboards/
- LLM Leaderboard - by StackAI - https://www.stack-ai.com/llm-leaderboard
- LLM Leaderboard - by Artificial Analysis - https://artificialanalysis.ai/leaderboards/models
- Open LLM Leaderboard - by Hugging Face - https://huggingface.co/open-llm-leaderboard
- LLM Leaderboard - by Vellum - https://www.vellum.ai/llm-leaderboard
- AI Benchmarking Hub - https://epoch.ai/data/ai-benchmarking-dashboard
- Grok 4 Benchmarks - https://artificialanalysis.ai/models/grok-4
- Image arena (alibaba) - http://aiarena.alibaba-inc.com/corpora/arena/leaderboard?arenaType=T2I
- image arena - https://lmarena.ai/leaderboard/text-to-image
- Data for April 14
- deepseek-v3.2 - 671B
- ernie-5.0 - 2.4T
- glm-5.0 - 744B
- kimi-k2.5-thinking - 1T
- qwen3.5-397B
- Xiaomi MiMo-V2-Pro - 1T+
- Waiting:
- Opus 4.7
- Kimi K2.6 - better coding

## Slide 3: Slide 3
- Anthropic Plugins
- In January Anthropic launched Claude Cowork and released the 11 open-source plugins on GitHub
- Within days $285 Bln in market cap wiped out
- Legal Plugin
- LICENSE
- .claude-plugin/plugin.json - name and description
- .mcp.json - lists 8 MCP servers
- CONNECTORS.md
- README.md
- skills/brief/SKILL.md
- skills/compliance-check/SKILL.md
- skills/legal-response/SKILL.md
- skills/legal-risk-assessment/SKILL.md
- skills/meeting-briefing/SKILL.md
- skills/review-contract/SKILL.md
- skills/signature-request/SKILL.md
- skills/triage-nda/SKILL.md
- skills/vendor-check/SKILL.md
- https://github.com/anthropics/knowledge-work-plugins - 11 plugins: (Productivity, Enterprise Search, Sales, Finance, Data, Legal, Marketing, Customer Support, Product Management, Engineering, Plugin Builder)
- Financial Services Plugins: https://github.com/anthropics/financial-services-plugins - 7 plugins (claude-in-office, equity-research, financial-analysis, investment-banking, partner-built, private-equity, wealth-management)
- Claude Plugins: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/example-plugin - 33 plugins (agent-sdk-dev, clangd-lsp, claude-code-setup, claude-md-management, code-review, code-simplifier, commit-commands, csharp-lsp, example-plugin, explanatory-output-style, feature-dev, frontend-design, gopls-lsp, hookify, jdtls-lsp, kotlin-lsp, learning-output-style, lua-lsp, math-olympiad, mcp-server-dev, php-lsp, playground, plugin-dev, pr-review-toolkit, pyright-lsp, ralph-loop, ruby-lsp, rust-analyzer-lsp, security-guidance, session-report, skill-creator, swift-lsp, typescript-lsp)
- How to create your own marketplace in your repo to store plugins
- https://code.claude.com/docs/en/plugin-marketplaces
- Example:
- https://github.com/zilliztech/memsearch/blob/main/.claude-plugin/marketplace.json
- /plugin marketplace add zilliztech/memsearch
- /plugin install memsearch
- # Restart Claude Code to activate the plugin

## Slide 4: Slide 4
- MCP = Model Context Protocol
- from mcp.server.fastmcp import FastMCP
- mcp = FastMCP("hello-world")
- @mcp.tool()
- def say_hello(name: str = "World") -> str:
- """Say hello to someone."""
- return f"Hello, {name}!"
- @mcp.resource("greeting://info")
- def greeting_info() -> str:
- """A simple greeting resource."""
- return "This is a minimal MCP Hello World server."
- if __name__ == "__main__":
- mcp.run()
- Agent
- running around and shooting
- uses tools (guns)
- Context = data, info,
- docs, instructions,
- Library, Files, Databases
- MCP exposes three distinct primitive types
- Tools (list, call)
- Resources (list, templates/list, read, subscribe)
- Prompts (templates — list, get)
- MCP

## Slide 5: Slide 5
- Claude Mythos
- Claude Mythos - revealed accidentally in March 2026
- Its architecture is described as "cyclic" (flywheel) because it forms a self-reinforcing loop
- Mythos is used internally to build better products and generate richer training data for smaller models, which lowers costs and raises revenue, which funds more compute for the next Mythos-class training run
- This flywheel explains how Anthropic's public models have been getting simultaneously more capable and cheaper
- Mythos also appears to serve as a long-running context engine inside Claude Code, helping agents maintain coherent understanding of complex, multi-session tasks
- Mythos's first public deployment was in cybersecurity, where it reportedly found thousands of zero-day vulnerabilities
- The full model has not been publicly released
- https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf - 245 pages "System Card"
- The word mythos comes from the Ancient Greek μῦθος (mûthos), meaning speech, word, utterance, story, tale, narrative (orally), legend or myth, plot
- In modern English, mythos means a pattern of beliefs or narrative that expresses the characteristic attitudes of a culture or group.
- Mythos
- Opus - many lines
- Sonnet - 14 lines
- Haiku - 3 lines
- Anthropic's Claude Mythos model is generating concerns among financial regulators, including Treasury Secretary Scott Bessant and Fed Chair Jerome Powell, who held emergency meetings with Wall Street leaders about its cybersecurity implications
- The model can autonomously chain multiple vulnerabilities together, with top researcher Nicholas Carlini noting he found more bugs in weeks than in his entire prior career
- Mythos also showed a sharp, unexpected capability jump, delivering a reported 4x productivity uplift for Anthropic staff
- However, a technical error during training may have inadvertently affected the model's "opaque reasoning," raising questions about whether its impressive alignment scores and capability leap are fully understood

## Slide 6: Slide 6
- Claude Opus 4.7
- Claude Opus 4.7 - April 16
- stronger performance across coding, vision, and complex multi-step tasks. It's more thorough and consistent on difficult work, with better results across professional knowledge work. 1M context is the default.
- https://www.anthropic.com/claude/opus
- https://www.youtube.com/watch?v=N4ZWCc_Fr3U&t=887s

## Slide 7: Slide 7
- Claude Agent SDK
- Claude Agent SDK is an embeddable library
- When you install it via pip, you get both a thin Python wrapper and a bundled Claude Code CLI executable compiled with Bun
- It is a fast JavaScript runtime written in TypeScript that ships as a single self-contained binary approx 12MB in size
- When your Python code calls the SDK's query() function, it doesn't talk to the Anthropic API directly. Instead, it spawns the bundled Bun-compiled Claude Code CLI as a separate subprocess. Your Python process and the CLI then communicate over stdin/stdout using a structured JSON control protocol.
- Inside that subprocess, Claude Code runs its full agent loop: it sends your prompt to the model, receives a response, checks whether Claude requested any tool calls, executes those tools, feeds the results back to the model, and repeats until Claude produces a final answer with no more pending tool calls
- All LLM calls, built-in tool execution (Read, Edit, Bash, Glob, etc.), context management, and MCP server coordination happen inside that subprocess — not in your Python code
- Your Python process acts as the controller. It defines permissions, handles custom tool callbacks, processes streamed messages, and receives the final result. Custom tools you define run as in-process MCP servers, meaning Claude Code calls them over the MCP protocol, bridging the subprocess boundary.
- Python Wrapper
- CC-CLI Agentic Loop
- Bun 12MB
- Your Python Script
- Claude Model in Cloud

## Slide 8: Slide 8
- Claude Agent SDK
- TypeScript
- npm install @anthropic-ai/claude-agent-sdk
- Rust
- npm install -g @anthropic-ai/claude-code
- cargo add claude-agent-sdk
- https://github.com/louloulin/claude-agent-sdk
- https://docs.rs/claude-agent-sdk/latest/claude_agent_sdk/
- Python
- pip install claude-agent-sdk
- Golang
- go get github.com/yhy0/claude-agent-sdk-go
- Also Kotlin & C++
- Anthropic's Advisor Strategy
- Use a powerful model like Opus as an "advisor" with a cheaper model like Sonnet or Haiku as the "executor."
- The executor handles most tasks independently and only calls the adviser when it encounters something genuinely difficult
- This approach delivers near-Opus quality at a fraction of the cost
- In Anthropic's benchmarks, Sonnet with Opus as adviser improved SWE-bench scores by 2.7 percentage points and reduced cost per agentic task by nearly 12%
- Haiku with Opus as adviser more than doubled performance on BrowseComp compared to Haiku alone
- In Claude Code, you can replicate this by using "opus plan" mode for planning, then letting Sonnet handle execution automatically.

## Slide 9: Slide 9
- We do these weekly videos every Friday
- Stats: 6.54K subscribers, 277 videos
- 1. Subscribe to this channel https://www.youtube.com/@lev-selector
- 2. Download slides from GitHub using links under the videos
- 3. Please pause the video - and answer the pinned question in comments under the video

## Slide 10: Slide 10
- OpenClaw Updates
- OpenClaw Updates https://github.com/openclaw/openclaw - 355K stars https://github.com/openclaw/openclaw/releases
- v2026.4.15 - Apr 16 - Defaults Anthropic model selections and `opus` aliases to Claude Opus 4.7; adds Gemini TTS support (WAV/PCM output); fixes stale Codex transport routing, `dist` chunk pruning on npm upgrades, BlueBubbles inbound attachment handling on Node 22+, and gateway tool name-collision security.
- v2026.4.14 - Apr 14 - Model provider & quality pass: adds `gpt-5.4-pro` Codex support, Telegram forum topic names in agent context; fixes Ollama timeouts, Slack allowlist bypass, browser SSRF regressions, markdown-it ReDoS fix in Control UI, and 40+ security/routing hardening patches.
- v2026.4.12 - Apr 13 - Broad quality release: LM Studio provider added, plugin loading and memory reliability fixes, Active Memory and diary UI cleanup, `exec-policy` CLI and `commands.list` RPC refinements, Feishu setup hardening, and shell security improvements.
- v2026.4.10 - Apr 10 - Adds bundled Codex provider with plugin-owned app-server harness, Active Memory sub-agent plugin, experimental local MLX speech for macOS Talk Mode, Seedance 2.0 video generation, Microsoft Teams message actions, `openclaw exec-policy` CLI, and `commands.list` RPC; broad security hardening across browser/sandbox, exec preflight, and WebSocket handling

## Slide 11: Slide 11
- Claude Code Updates
- Claude Code Releases https://github.com/anthropics/claude-code/releases
- v2.1.112 - April 16 - Fixes "claude-opus-4-7 is temporarily unavailable" error
- v2.1.111 - April 15–16 - Reverts v2.1.110 non-streaming fallback retry cap; fixes display tearing in iTerm2+tmux and stale LSP diagnostics causing Claude to re-read recently edited files
- v2.1.110 - April 15 - Adds MCP scope doctor in /doctor for multi-scope conflicts, scheduled task recovery via --resume/--continue; fixes --resume losing context on large sessions and subagent chain bridging
- v2.1.108 - April 14–15 - Adds ENABLE_PROMPT_CACHING_1H env var for 1-hour prompt cache TTL; adds /recap session recap command configurable in /config; support Bedrock, Vertex, Foundry
- v2.1.107 - April 14 - Improves thinking hints display for better UX during extended operations; stability and rendering improvements for long-running agentic tasks
- v2.1.104 - April 13 - Brings important updates and improvements for developers and power users; stability and performance fixes across core tooling
- v2.1.101 - April 10 - Adds /team-onboarding command, OS CA cert trust, auto cloud env for /ultraplan; fixes command injection in LSP, memory leak, Bedrock SigV4 auth, subagents not inheriting MCP tools, and many rendering/settings bugs
- How Anthropic shipped 120 features in 90 days
- https://www.news.aakashg.com/p/anthropic-q1-features
- Anthropic Claude desktop is now more developer-focused
- Up to 4 parallel Claude Code instances in a split-view layout
- Integrated browser preview for real-time UI feedback
- Dedicated terminals per session
- Code diff viewing
- Direct Pull Request handling (GitHub)
- "Routines" (formerly scheduled tasks) runs cloud-side, meaning automations execute even when your machine is off
- Routines can be triggered via API endpoints
- Routines templates - email triage or news aggregation.
- Problems - lag and UI bugs

## Slide 12: Slide 12
- 10 Claude Code Skills, Plugins, CLIs
- Top 10 Claude Code Skills, Plugins & CLIs https://www.youtube.com/watch?v=KjEFy5wjFQg
- Codex Plugin - adversarial code reviews - https://github.com/openai/codex-plugin-cc
- Obsidian Skills - lightweight RAG system for Obsidian - https://github.com/kepano/obsidian-skills
- AutoResearch by Andrej Karpathy - run ML experiments - https://github.com/karpathy/autoresearch
- Awesome Design MD - collection of DESIGN.md files - https://github.com/VoltAgent/awesome-design-md
- Firecrawl CLI + Skill - web scraping with anti-bot bypass - https://www.firecrawl.dev/blog/claude-code-skill
- Playwright CLI - browser automation CLI https://playwright.dev/docs/getting-started-cli
- NotebookLM-py CLI + Skill - https://github.com/teng-lin/notebooklm-py
- Skill Creator Skill - creates new skills - https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- LightRAG - lightweight alternative to GraphRAG - https://github.com/hkuds/lightrag
- GWS (Google Workspace CLI) - connects Claude Code to Gmail, Drive, Calendar & Docs with 92 pre-built workflow skills - https://github.com/WadeWarren/gws-claude-plugin Comes with pre-built workflow skills (e.g., reschedule meeting, organize Drive). Setup requires enabling things in Google Cloud, but it's the best option for using Claude Code as a personal assistant
- Top 10 Claude Code Web Design Skills, Plugins & CLIs https://www.youtube.com/watch?v=Q9ty3eopOPs
- Impeccable - https://github.com/pbakaus/impeccable
- SkillUI - https://github.com/amaancoderx/npxskillui
- WebGPU Claude Skill - https://github.com/dgreenheck/webgpu-claude-skill
- Awesome Design MD - https://github.com/VoltAgent/awesome-design-md
- Stitch by Google - https://stitch.withgoogle.com
- UI/UX Pro Max Skill - https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- 21st.dev - https://21st.dev/home
- Taste Skill - https://github.com/Leonxlnx/taste-skill
- Google Fonts - https://fonts.google.com
- Playwright CLI - https://github.com/microsoft/playwright-cli
- Skills to Reduce Coding Mistakes Inspired by Andrej Karpathy
- https://github.com/forrestchang/andrej-karpathy-skills
- https://www.youtube.com/watch?v=sKx8g4ilCKQ
- think before coding - state assumptions and surface confusion;
- write minimum code that solves the problem;
- make surgical edits that touch only what's necessary;
- define verifiable success criteria before executing

## Slide 13: Slide 13
- Work with Google Work Space (GWS)
- How to work with Google Work Space (GWS)
- https://github.com/googleworkspace/cli - Google gws CLI - includes a CLAUDE.md file and .claude directory; 100+ agent skill files; built in Rust; 89 skills available as a Claude Code plugin via npx claudepluginhub tuannvm/plugins --plugin google-workspace
- For python you can use Composio (commercial solution): pip install composio-anthropic claude-agent-sdk https://composio.dev/toolkits/googledocs/framework/claude-agents-sdk
- Alternatively you can use "Google Workspace MCP Server" https://github.com/taylorwilsdon/google_workspace_mcp It is Open Source (MIT)
- # Install and run locally (no paid service)
- export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
- export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
- uvx workspace-mcp --tools gmail drive calendar docs sheets
- # ----------- Python -------------
- from claude_agent_sdk import ClaudeSDKClient
- async with ClaudeSDKClient(
- mcp_servers=[{"url": "http://localhost:8000/mcp/", "type": "http"}]
- ) as client:
- async for msg in client.query("Summarize my unread Gmail threads"):
- print(msg)

## Slide 14: Slide 14
- 33 Claude Skills and more resources
- https://www.youtube.com/watch?v=2BFN2DtcQMw - all links here
- 1. Frontend Design - 277,000 installs
- 2. Superpowers - 20+ skills for test-driven development; 100K+ GitHub stars
- 3. AutoResearch by Karpathy - runs experiments, 50K+ stars
- 4. Context7 - #1 MCP server for docs for software libraries
- 5. gstack by Garry Tan - Y Combinator president's Claude setup & prompts
- 6. Task Master AI - Breaks your PRD into tasks with dependencies; 36 MCP tools
- 7. Playwright MCP (Microsoft) - browser control (clicks, forms, screenshots)
- 8. Tavily - Search engine built for AI agents; tools: search, extract, crawl, map
- 9. Codebase Memory MCP - persistent knowledge graph across sessions
- 10. PDF Processing - Read, extract tables, fill forms, merge, and split PDFs
- 11. XLSX - Excel formulas, data analysis, and charts from plain English
- 12. PPTX - Slide decks with layouts, charts, and speaker notes
- 13. Doc Co-Authoring - AI writing, like Google Docs with an AI co-author
- 14. Canvas Design — Social graphics, posters, and covers; text in, PNG/PDF out
- 15. Web Artifacts Builder - Calculators, dashboards, interactive widgets
- 16. Marketing Skills - 20+ sub-skills: CRO, copywriting, SEO, email sequences
- 17. Claude SEO - Full website audits, schema validation, 12 sub-skills
- 18. Brand Guidelines - Encodes your brand voice, colors, and tone
- 19. Deep Research Skill — 8-phase research pipeline with source credibility scoring
- 20. GPT Researcher - researches a topic and compiles a full report
- 21. Obsidian Skills - Auto-tagging, linking, vault-native AI
- 22. Remotion - Vibe-code motion graphic promo videos
- 23. Context Optimization - reduces token usage via KV cache tricks
- 24. promptfoo - security testing, red teaming, edge case testing for prompts
- 25. Skill Creator - Anthropic meta-skill; generates skill file from description
- ## GitHub Repos (Paste Link into Claude Code)
- 26. n8n - Open-source workflow automation
- 27. Firecrawl - turns any website into LLM-ready markdown/structured data
- 28. Langflow - visual drag-and-drop AI agent pipeline builder
- 29. claude-squad - run multiple Claude Code agents in parallel terminals
- 30. container-use by Dagger - containerized isolated environments for agents
- 31. Ghost OS - AI agents that control every app on your Mac
- ## Where to Find More
- 32. Awesome Claude Skills: https://github.com/travisvn/awesome-claude-skills
- 32. Official Anthropic Skills Repo: https://github.com/anthropics/skills
- 33. SkillsMP: https://skillsmp.com
- 33. SkillHub: https://skillhub.club
- 33. MAGI Archive: https://tom-doerr.github.io/repo_posts/

## Slide 15: Slide 15
- InfraNodus - Generate Ideas
- Claude Code + Obsidian + InfraNodus https://www.youtube.com/watch?v=yYSTsKo8moU https://infranodus.com
- Andrej Karpathy's 'LLM Wiki' summary produces most probably answer
- InfraNodus maps your concepts as a network, identifies the main topic clusters, and finds the gaps - pairs of clusters that are weakly connected. Those gaps are where novel ideas live
- Feeding the LLM the graph structure of the gap (not just the documents) forces it to reason about underexplored connections rather than rehashing what's already well-covered.
- Cognee gives your AI a persistent memory that actually understands - not just recalls. Instead of storing facts as isolated sticky notes, it builds a knowledge graph - a web of connected concepts. Tell it "my pet is Biscuit" and "dogs are animals," and it links them automatically.
- The pipeline is three steps: .. add() ingests documents, audio, or text; .. cognify() builds the connection map; .. search() retrieves answers by meaning and relationship (better than vector search
- Connections that lead to good answers strengthen over time via the Memify pipeline
- Under the hood, Cognee runs three databases: Kuzu (graph), LanceDB (vectors), SQLite (metadata) all local files by default, swappable for Neo4j or Postgres in production
- https://github.com/topoteretes/cognee
- https://x.com/i/status/2043745099792953508
- https://x.com/akshay_pachaar/status/2044329897603244093

## Slide 16: Slide 16
- Adding Workflow Builder to your Agent
- How to add workflow builder GUI your agent (similar to langflow)
- Option 1: Langflow - as a separate server, runs its own LangChain-based runtime https://www.langflow.org ; https://github.com/langflow-ai/langflow
- Option 2: React Flow - a canvas library used by Langflow and many others. MIT-licensed, pure UI with no runtime opinions. You build your own node types mapped to your agent's capabilities, and your Python backend handles execution https://reactflow.dev ; https://reactflow.dev/examples/interaction/drag-and-drop - example
- https://reactflow.dev/learn - quick start
- Option 3: Litegraph.js - lightweight canvas, pure vanilla JS, easy to embed https://github.com/Comfy-Org/litegraph.js/ https://github.com/jagenjo/litegraph.js - original repo https://github.com/Comfy-Org/ComfyUI_frontend - current maintained version
- Many other options - https://github.com/xyflow/awesome-node-based-uis
- Litegraph.js is a pure vanilla JavaScript node graph library with no dependencies, making it ideal for projects that don't use React.
- Maintained as part of the ComfyUI ecosystem, it renders on an HTML5 Canvas and supports draggable nodes, bezier edge connections, pan/zoom, and JSON graph serialization out of the box.
- For a Python-based agent with an existing local web server, Litegraph.js drops in with a single `<script>` tag — no npm, no bundler, no framework required. You define custom node types in JavaScript that map directly to your agent's capabilities (e.g., ClaudeCall, MemoryRead, ScheduleTrigger), and on execution, the graph serializes to JSON and POSTs to your Python backend.
- In comparison, React Flow requires a full React app setup and is harder to embed into an existing HTML interface. Litegraph.js delivers the same visual workflow canvas with far less overhead.
- https://github.com/jagenjo/litegraph.js
- Litegraph.js

## Slide 17: Slide 17
- More Desktop Agents
- Google Gemini desktop app
- Just released for MacOS and Windows
- The macOS app is built natively in Swift, requires macOS 15 Sequoia, and offers features like screen sharing, file access, image/video generation, and quick-access keyboard shortcuts
- The Windows app is similar to Microsoft Copilot
- Neither app has deep OS-level integration yet
- Linux has no official native app (only CLI)
- Google added Skills to Gemini in Chrome, available on Mac, Windows, and Chrome OS
- Notes about Google "Agent Mode":
- Gemini Ultra - has "Agent" toggle or the Tools icon
- Gemini Code Assist in VSCode or IntelliJ have "Agent Mode"
- Google Search now has "AI Mode"
- Perplexity Pro subscription for AI websearch and research. It answers questions. Uses models in cloud. Access via browser, desktop and mobile app versions.
- Perplexity Computer - like search subscription, but can perform multi-step actions. Using different models/agents. Designed for complex, long-running tasks. Different payment model (credits)
- Perplexity Personal Computer (waiting list) - a locally installed app (ideally on a Mac mini) that runs 24/7 and gives Computer autonomous access to your local files, native apps (Notes, iMessage, email), and the web
- OpenAI desktop app
- For both macOS and Windows
- The macOS app supports a quick-access shortcut, app integrations with tools like VS Code and Notion, and voice conversations
- The Windows app, available on the Microsoft Store, offers a companion window for instant queries, file uploads, and image generation
- Both apps are free to download, with some advanced features reserved for paid plans
- Looking ahead, OpenAI announced plans in March 2026 to build a unified desktop "superapp" combining ChatGPT, its Codex coding platform, and its AI browser (internally called Atlas)
- The superapp is being designed around agentic AI and is aimed primarily at developers and enterprise users. No launch date has been confirmed yet
- https://help.openai.com/en/articles/9982051-using-the-chatgpt-windows-app
- No Linux app

## Slide 18: Slide 18
- AI Updates
- Seedance 2.0 is public
- AI video generation model by ByteDance
- Proprietary closed narrative-driven, multi-shot video from text, images, audio, and video inputs (plans: free, basic, standard)
- Seedance is built to produce complete, multi-shot scenes in one pass. It understands cuts, angles (wide, medium, close-up), and shot transitions while maintaining character and environment consistency
- It's trained on ByteDance's vast repository of short-form video content from TikTok, giving it a strong grasp of narrative structure and visual storytelling
- https://seed.bytedance.com/en/seedance
- https://seed.bytedance.com/en/seedance2_0
- https://seed.bytedance.com/en/seedance1_5_pro
- https://www.byteplus.com/en/product/seedance
- https://fal.ai/seedance-2.0 - API
- Topview AI Agent V2 uses Seedance 2.0 model
- Agent V2 focuses on long-form storytelling by automatically breaking prompts into structured, multi-scene storyboards
- Users can interact with the AI agent through chat to refine visual styles, composition, and tone for each scene
- Designed for marketers and content creators, the tool enables the production of cinematic product demos and YouTube explainers without requiring a full production team
- http://www.youtube.com/watch?v=xjVmEEtYB58
- https://www.topview.ai

## Slide 19: Slide 19
- Railway Deployment
- Railway (railway.com) is an all-in-one cloud deployment platform
- Founded in 2020, easy to build, deploy, and scale applications
- Users simply connect a GitHub repository or Docker image, and Railway automatically handles building, networking, SSL, and environment configuration
- It supports instant provisioning of databases like PostgreSQL, MySQL, MongoDB, and Redis, along with 2K+ templates
- Pricing is usage-based, starting at $5/month
- Railway is SOC 2 Type II certified
- RILQy is used by 23% of Fortune 500 companies.
- Railway is a cloud deployment platform — not a vibe coding tool
- Vibe coding platforms like Lovable, Bolt.new, and Replit let you build full apps from plain English prompts, making them ideal for non-coders and rapid prototyping
- Railway, by contrast, takes existing code and handles deploying, scaling, and hosting it in the cloud
- The two categories are complementary rather than competitive: developers often prototype on a vibe coding platform, then push the code to Railway for production-grade hosting with more control and better pricing
- If you want to build an app fast with no code, use Lovable or Bolt
- If you want to deploy and run it reliably, use Railway
- Claude Code
- GitHub
- Railqay
- CloudFlare
- domain + DNS

## Slide 20: Slide 20
- Moonshots Podcast #246
- SpaceX's planned $2 trillion IPO, driven largely by Starlink's revenues
- Race among SpaceX, OpenAI, and Anthropic to go public
- NASA's Artemis II has successfully concluded - it was the first crewed lunar mission since Apollo 17 in 1972, sending four astronauts on a 10-day journey around the Moon and back
- Anthropic's powerful but unreleased "Mythos" model, which reportedly escaped its sandbox during testing
- Anthropic has overtaken OpenAI in ARR (Annual Recurring Revenue)
- OpenAI shut down Sora and refocuses on enterprise
- The rise of one-person AI unicorns
- The data center crunch pushing compute toward orbit
- Sam Altman's warnings about imminent large-scale cyberattacks
- The episode closes with an optimistic "proof of abundance" segment highlighting falling battery prices, renewable energy growth, and lab-grown diamonds
- Skills to survive in new world:
- Agency - The ability to identify problems, act independently, and build solutions without relying on others
- Taste & Perspective - Your unique life experiences create an unfair advantage when everyone has access to the same AI
- Judgment - Knowing the long-term consequences of decisions; AI handles execution, but not final calls
- Deep Generalism - Cross-domain synthesis - still beyond AI's current strength
- https://hussainibarra.substack.com/p/most-high-income-skills-will-be-irrelevant

## Slide 21: Slide 21
- AI Updates
- AI is no longer Optional
- Half of CEOs believe their jobs depend on successful AI implementation
- Companies must undergo true transformation by redesigning their operating models around AI capabilities
- Productivity gap between AI-enabled startups and traditional firms
- The rise of autonomous agents
- To succeed, leaders should follow a five-step model:
- inventorying current usage,
- automating revenue-linked workflows,
- defining autonomy levels,
- establishing governance,
- tracking ROI
- Ultimately, businesses must choose to lead or lag as the window for gaining a competitive advantage rapidly closes
- https://www.youtube.com/watch?v=WsFWFi5bcFw
- AI Agency "SureThing"
- https://surething.io/chat-index
- https://theresanaiforthat.com/ai/surething/
- A team of autonomous AI agents working together, on cloud, persistent memory and integrations with over 1,000 apps like Slack, Notion, and HubSpot
- Company - Super Intent, Inc., San Francisco, CA
- Cenning Yu, Co-founder,
- 3 Valuable AI Skills
- Agent Orchestration
- AI Human Interface Design
- AI Safety and Alignment Translation
- https://www.youtube.com/watch?v=qYGGTH2rgI8

## Slide 22: Slide 22
- How to setup Hermes Agent
- How to setup Hermes Agent https://www.youtube.com/watch?v=3jNp14bJpgs - Wes Roth https://github.com/nousresearch/hermes-agent
- In Greek mythology, Hermes is the Olympian god of boundaries, travel, commerce, and communication. He is best known as the Messenger of the Gods, a role he fulfills thanks to his incredible speed and ability to move freely between the mortal world, the divine realm of Olympus, and the Underworld
- The video is a guide to setting up and using "Hermes Agent" - an open-source AI agent developed by Nous Research - with ability to learn, develop skills, and improve over time through persistent memory
- It comes with 74 pre-installed skills, supports hundreds of models via OpenRouter, includes a security bot that monitors and warns users before executing potentially dangerous commands
- Can be installed on a Virtual Private Server (VPS) via Hostinger
- Can be paired with your Telegram account
- Can be integrated with WhatsApp and Gmail

## Slide 23: Slide 23
- Convert Claude Code into ClaudeClaw
- Mark Kashef "ClaudeClaw"
- A custom-built command center that turns a standard Claude Code subscription into a sophisticated multi-agent ecosystem
- Uses Anthropic’s free SDK to bridge local terminal sessions to external interfaces like Telegram and web browsers
- Specialized Agent Council - uses dedicated agents for Ops, Comms, and Content that coordinate via a "Hive Mind" to share task history and data.
- Web dashboard for task management and a "War Room" for real-time voice and video interaction using Pipecat
- Smart Memory - uses Gemini Flash to "wash" and categorize conversations into SQLite and Obsidian, separating temporary context from permanent "pinned" facts
- Benefits: Cost Savings, leveraging new open-source frameworks, Privacy & Security (Chat ID allow-list and local hosting)
- https://www.youtube.com/watch?v=rVzGu5OYYS0

## Slide 24: Slide 24
- Anthropic ARR $30B vs $25B OpenAI
- Anthropic $30B ARR vs OpenAI's $25B
- Anthropic has overtaken OpenAI in annualized revenue
- This represents 30x growth for Anthropic in just 15 months, driven almost entirely by enterprise customers - over 1,000 companies are now each spending $1M+ annually with Anthropic
- About 80% of Anthropic's revenue comes from businesses, versus OpenAI's more consumer-focused model
- Anthropic is achieving this while spending four times less on model training than OpenAI
- OpenAI still holds a massive user base of 900 million+ weekly ChatGPT users

## Slide 25: Slide 25
- Jobs
- https://layoffs.fyi
- https://trueup.io/layoffs
- Tech Layoffs by year (US only):
- 73.2K in 2026 (as of April 17, 2026)
- 124K in 2025
- 153K in 2024
- 264K in 2023
- 165K in 2022 https://layoffs.fyi
- The Tech Layoff Tracker
- In 2026: 95,021 people laid off (888 per day)
- In 2025: 245,953 people laid off (674 per day)
- In 2024: 238,461 people laid off (653 per day)

## Slide 26: Slide 26
- About the Speaker
- Lev Selector, Ph.D.
- 40+ years of software engineering, data science, and building teams (hiring, training, and managing)
- Ph.D. in mathematical modeling and computer simulations
- Interests:
- Generative AI, Using LLM with your data
- Local AI for Local Private Data
- Cloud architecture, fin-tech, application security
- Find/connect: Linkedin, GitHub, YouTube, Google
- https://eais.ai
- Enterprise AI Systems

## Slide 27: Slide 27
- Thank You!
