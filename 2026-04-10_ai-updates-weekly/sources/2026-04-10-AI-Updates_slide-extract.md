## Slide 1: Slide 1
- Crowd-sourced "LM Arena" Leaderboard
- MemPalace Memory System
- Claude Buddy - virtual pet built into Claude Code
- Anthropic Restricts Third-Party Claude Usage
- Anthropic Managed Agents
- Agentic AI Solutions
- AI Updates - Apr 10, 2026
- Jobs & Layoffs
- OpenClaw Updates
- Claude Code Updates
- Matt Berman challenged Hacker
- Journey, a registry for AI agent workflow kits
- Google Gemma 4 family of open-source models
- OpenAgents - Multi-Agent Platform
- Abacus CoWork
- Meta Muse Spark
- Perplexity Computer Tax Prep
- Anthropic acquired Coefficient Bio
- Deep Learning NYU Course 2020
- Edgeclaw open-source privacy for AI agents
- OpenClaw + Ollama + Qwen 3.5
- The Anthropic vs. Pentagon dispute
- Claude Code with the Qwen 3.6 Plus model
- TRIZ & AI
- HERE.NOW
- HeyGen Avatar V
- Ole Lehmann Used Council Approach
- Hermes Agent - open-source, self-improving
- Karpathy's wiki + Hermes Agent
- Karpathy's Obsidian RAG + Claude Code
- Graphify - Claude Code + Obsidian wiki
- Obsidian plus Claude
- Microsoft MAI Models
- Cursor 3.0 - a major update
- Alibaba Wan 2.1 AI video model - open-source
- Claude's Microsoft 365 connector
- Anthropic Claude Mythos Preview
- Caveman" plugin/skill for Claude Code
- "Intelligence is the ability to adapt to change."
- — Stephen Hawking

## Slide 2: Slide 2
- Periods of social instability are historically the best times for individual growth, career advancement, wealth creation, and access to resources.
- Frightening, yes.
- Extraordinarily interesting, absolutely.
- As Benjamin Franklin said: "God helps those who help themselves."
- Originally posted by Linus Torvalds on Twitter (now X) on January 29, 2013

## Slide 3: Slide 3
- Starting Elo rating = 1000
- https://en.wikipedia.org/wiki/Elo_rating_system
- "LM Arena" Leaderboard
- English - https://lmarena.ai/leaderboard/text
- Coding - https://lmarena.ai/leaderboard/text/coding
- https://lmarena.ai/leaderboard/text
- Design Arena - https://www.designarena.ai
- https://openlm.ai/chatbot-arena/
- https://beta.lmarena.ai
- Web Leaderboard - 1T paramshttps://web.lmarena.ai/leaderboard
- LLM Leaderboard - by @LlmStats - https://llmworld.net/llm_leaderboards/
- LLM Leaderboard - by StackAI - https://www.stack-ai.com/llm-leaderboard
- LLM Leaderboard - by Artificial Analysis - https://artificialanalysis.ai/leaderboards/models
- Open LLM Leaderboard - by Hugging Face - https://huggingface.co/open-llm-leaderboard
- LLM Leaderboard - by Vellum - https://www.vellum.ai/llm-leaderboard
- AI Benchmarking Hub - https://epoch.ai/data/ai-benchmarking-dashboard
- Grok 4 Benchmarks - https://artificialanalysis.ai/models/grok-4
- Image arena (alibaba) - http://aiarena.alibaba-inc.com/corpora/arena/leaderboard?arenaType=T2I
- image arena - https://lmarena.ai/leaderboard/text-to-image
- Data for April 9
- deepseek-v3.2 - 671B
- ernie-5.0 - 2.4T
- glm-5.0 - 744B
- kimi-k2.5-thinking - 1T
- qwen3.5-397B
- Xiaomi MiMo-V2-Pro - 1T+
- ■
- Claude
- Gemini
- OpenAI
- Open Source
- Code
- Model
- Score
- claude-opus-4-6-thinking
- 1555
- claude-opus-4-6
- 1545
- gpt-5.4-high
- 1535
- gemini-3.1-pro-preview
- 1532
- claude-opus-4-5-20251101-thinking-32k
- 1531
- glm-5.1
- 1521
- claude-sonnet-4-6
- grok-4.20-multi-agent-beta-0309
- 1520
- gemini-3-pro
- 1519
- claude-sonnet-4-5-20250929-thinking-32k
- 1518
- claude-opus-4-5-20251101
- 1517
- grok-4.20-beta1
- gpt-5.2-chat-latest-20260210
- dola-seed-2.0-pro
- 1516
- grok-4.20-beta-0309-reasoning
- muse-spark - Meta
- 1514
- claude-opus-4-1-20250805-thinking-16k
- 1512
- gpt-5.4-mini-high
- 1510
- kimi-k2.5-thinking
- gpt-5.4
- 1509
- claude-sonnet-4-5-20250929
- gemini-3-flash
- longcat-flash-chat-2602-exp
- 1508
- qwen3.5-max-preview
- 1507
- gpt-5.3-chat-latest
- 1506
- 1504
- 1496
- 1492
- 1487
- 1486
- 1484
- 1479
- 1476
- 1475
- 1474
- 1473
- 1471
- grok-4.1-thinking
- 1468
- 1467
- 1466
- gemini-3-flash (thinking-minimal)
- 1463
- 1462
- grok-4.1
- 1461
- 1458
- 1456
- glm-5
- 1455
- gpt-5.1-high
- 1454

## Slide 4: Slide 4
- MemPalace Memory System
- MemPalace Memory System - by Milla Jovovich & Ben Sigman
- https://github.com/milla-jovovich/mempalace - 26.9K stars
- https://www.youtube.com/shorts/ROKgDeeFAnk - short video
- Free & open-source (MIT) AI memory system that claims the highest score on the LongMemEval benchmark (96.6%)
- Unlike other memory tools that use AI to extract and summarize key points (often discarding valuable context) MemPalace stores every conversation verbatim in ChromaDB and organizes them using a spatial structure inspired by the ancient Greek "memory palace" technique
- Conversations are grouped into wings (people/projects), halls (memory types), and rooms (specific ideas), making them navigable rather than just searchable
- It runs entirely locally with no external APIs
- An experimental compression layer called AAAK exists for token efficiency at scale, though it currently underperforms raw storage mode
- Milla Jovovich is a famous actress: Resident Evil, The Fifth Element
- She has envisioned the architecture of MemPalace (using ChatGPT and Claude), developed the conceptual framework for how the memory system should work
- The actual engineering was done by her collaborator Ben Sigman, a developer and CEO of Bitcoin lending platform Libre Labs, who turned her architectural vision into working code
- Tech stack: 54 python files and 32 md files (skills, commands, ...)
- ChromaDB - stores raw text and embeddings for semantic search
- SQLite — for the knowledge graph (temporal entity-relationship triples)
- skills - to be used with Claude Code plugin and a Codex CLI plugin

## Slide 5: Slide 5
- Anthropic Managed Agents
- in public beta on April 7
- A new infrastructure layer on the Claude Platform for running long-lived, stateful AI agents
- Available to anyone with API billing access via the Claude Console, it is API-only (can not use subscription plans (Pro, Max) are excluded
- In practice, the pricing model strongly favors enterprise customershttps://www.reworked.co/digital-workplace/anthropic-launches-claude-managed-agents-to-speed-up-ai-development/
- Pricing = Claude token rates plus $0.08 per session-hour of active runtime. For context, agent task costs can range from $0.50 to $2.00 per taskhttps://www.reddit.com/r/AI_Agents/comments/1scdq0o/anthropic_effectively_ends_the_unlimited_claude/
- The broader enterprise agents program, announced in late February 2026, also includes pre-built plug-ins for finance, engineering, and design workflows, private software marketplaces, and controlled data flows — all clearly pitched at corporate IT buyers
- https://platform.claude.com/docs/en/managed-agents/overview

## Slide 6: Slide 6
- Agentic AI Solutions
- =========== Universal Desktop Agents
- OpenClaw - desktop autonomy, multi-task, local & cloud modelsThere are multiple variants - look here:https://github.com/T31K/awesome-openclaw-alternatives https://github.com/e2b-dev/awesome-ai-agents
- Anthropic Claude Desktop and Claude Code - "gold standard"
- Abacus AI Desktop App (CoWork)
- Hermes Agent - Conversational and local task execution.
- Cursor - Agentic coding IDE with multi-file editing and debugging
- OpenAI Operator - web and OS tasks
- Manus AI / Meta Manus (Meta) - autonomous agent
- Perplexity Computer - runs in isolated cloud compute and can work with MacOS local files using PerplexityXPC app and dedicated Filesystem MCP (github.com/modelcontextprotocol/servers)
- Mistral Devstral 2 (France) - Desktop-capable coding agent
- Gemini CLI
- =========== Cloud / Platform Agentsoperate within specific cloud ecosystems such as Google Workspace, Microsoft 365, Salesforce CRM, WeChat, ...
- OpenAI Deep Research & AgentKit - cloud-hosted agents
- Microsoft Copilot Studio - build agents for Microsoft 365, OneDrive, Teams, SharePoint
- Google Agentspace - Enterprise agentic platform for the Google Workspace, Drive, and Gmail
- Salesforce Agentforce - autonomous workflows across Sales Cloud, Service Cloud, and Marketing Cloud
- Abacus DeepAgent - Cloud-based
- Moveworks - Cloud IT support, works with ServiceNow
- Aisera - Enterprise cloud automation for IT and HR
- Sierra - Cloud-based conversational AI agent - customer experience.
- =========== Asia - Cloud / Platform
- Tencent QClaw - WeChat-bound agent - bookings, ride-hailing, file tasks, and PC control within the WeChat cloud ecosystem
- Alibaba Qwen Agent - used across Alibaba Cloud and DingTalk
- Baidu ERNIE Agent - Baidu Cloud and enterprise SaaS
- =========== Europe - Cloud / Platform
- Mistral Le Chat Agent (France) - Cloud-based
- Gemini Agent (UK)
- Aleph Alpha (Germany) - enterprise/governments agentic AI
- AutogenAI (UK) - cloud-based - proposals and bids
- ===========
- Apple Intelligence Agents
- DeepSeek Agent (China)
- MultiOn - web actions - https://docs.multion.ai/welcome

## Slide 7: Slide 7
- We do these weekly videos every Friday
- Stats: 6.54K subscribers, 277 videos
- 1. Subscribe to this channel https://www.youtube.com/@lev-selector
- 2. Download slides from GitHub using links under the videos
- 3. Please pause the video - and answer the pinned question in comments under the video

## Slide 8: Slide 8
- AI
- Claude Buddy - virtual pet built into Claude Code
- Released on April 1 as a funny feature
- Activated via the `/buddy` command, can be toggled on/off
- Each user gets a unique pet determined by their account ID
- The pet makes funny alive comments. It makes you feel good
- Buddy doesn't cost you tokens.
- Anthropic Restricts Third-Party Claude Usage
- It officially barred subscription credits for tools like OpenClaw
- They are citing engineering constraints around prompt caching efficiency. Their systems are optimized for Claude Code's specific workload, and third-party harnesses break caching, consuming more compute
- Users can still access Claude via API key
- Users have been burning through Claude Code usage limits faster than expected due to tighter limits and larger context windows
- The broader trend points toward the end of heavily subsidized AI subscriptions across the industry.

## Slide 9: Slide 9
- OpenClaw
- OpenClaw Updateshttps://github.com/openclaw/openclaw - 353K starshttps://github.com/openclaw/openclaw/releases
- v2026.4.8: Fixes npm build startup failures across Telegram and 9 bundled channels; aligns plugin metadata with release version; improves Slack proxy/token handling; fixes SSRF DNS pinning for proxy sandboxes.
- v2026.4.7: Adds openclaw infer CLI, memory-wiki restore, webhook ingress plugin, session compaction/restore, Gemma 4 & Arcee AI providers, Ollama vision detection, pluggable compaction, and dreaming memory ingestion.
- v2026.4.5: Adds video/music generation tools, ComfyUI plugin, Qwen/Fireworks/StepFun providers, 12-language UI, memory dreaming overhaul, prompt cache improvements, iOS/Matrix exec approvals, and ClawHub in-UI install.
- v2026.4.2: Restores Task Flow for multi-step autonomous tasks; adds Android/Google Assistant support; migrates xAI & Firecrawl configs to plugins; adds Feishu Drive comments, Matrix mentions, and exec auto-approvals.

## Slide 10: Slide 10
- Claude Code Updates
- Claude Code Releaseshttps://github.com/anthropics/claude-code/releases
- ============ v2.1.96 - April 8 ============Fixed Bedrock requests failing with 403 "Authorization header is missing" when using AWS_BEARER_TOKEN_BEDROCK or CLAUDE_CODE_SKIP_BEDROCK_AUTH (regression in 2.1.94)
- ============ v2.1.94 - April 7 ============Bedrock/Mantle support, default effort raised to high, Slack MCP channel links, plugin skill name fixes, plus numerous bug fixes for rate-limit errors, macOS login, tmux hyperlinks, CJK text corruption, and VS Code improvements
- ============ v2.1.92 - April 3 ============Bedrock setup wizard, forceRemoteSettingsRefresh policy, per-model cost breakdown, interactive release notes, hostname-based Remote Control names, plus bug fixes for tmux, hooks, feedback surveys, and 60% faster Write tool diffs
- How Anthropic shipped 120 features in 90 days
- https://www.news.aakashg.com/p/anthropic-q1-features

## Slide 11: Slide 11
- OpenClaw
- Matt Berman challenged Hacker Ply the Liberator, a well-known AI hacker, to break into his personal AI email system called OpenClaw
- Ply made six attempts using techniques like token flooding, jailbreak templates, and fake system commands
- Despite knowing the system used Claude Opus 4.6, every attack was caught and quarantined
- The key takeaways: using a powerful reasoning model as your first line of defense and keeping humans in the loop are the best protections against AI prompt injection attacks.
- Journey, a registry for AI agent workflows called "kits"
- https://www.youtube.com/watch?v=vn_kU928nww .
- Journey solves the problem of sharing and discovering agent workflows by packaging complete end-to-end solutions including skills, tools, learnings, memories, and tests into installable packages.
- Similar to npm for code, agents can easily install these workflow packages without reinventing functionality.
- Journey features version control, community feedback, reputation scoring, and team collaboration capabilities including shared contexts and credentials management.
- The platform allows private organizational kits alongside public ones, with audit logs and analytics for teams.
- Installation is agent-first - users can simply copy a prompt to their AI agent to install workflows.

## Slide 12: Slide 12
- Google Gemma 4
- Google Gemma 4 family of open-source models (Apache 2.0)
- Four sizes: E2B, E4B, 26B (MoE), and 31B (dense)
- 31B model ranks 3rd on the Arena AI leaderboard, competing with much larger models like Qwen 3.5 397b-a17b
- The models support advanced reasoning, agentic workflows, function calling, structured JSON output, multimodal input (video, images, audio), and are ideal for local/edge deployment
- https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/

## Slide 13: Slide 13
- OpenAgents
- https://openagents.org
- https://github.com/openagents-org/openagents
- https://www.reddit.com/r/AgentsOfAI/comments/1saupc0/
- https://studio.openagents.org
- https://discord.gg/openagents
- Multi-agent platform where agents share the same browser, files, and chat context simultaneously
- OpenAgents started as a Python SDK for multi-agent networking and evolved into a full platform, a Workspace for real-time human-agent collaboration
- It is open-source under the Apache 2.0 license and can be self-hosted with a single command, requiring no Docker or accounts
- conda create -n openagents python=3.12
- conda activate openagents
- pip install openagents
- openagents init ./my_first_network
- openagents network start ./my_first_network
- openagents studio -s
- # Then open `http://localhost:8050` in your browser
- # ./my_first_network/simple_agent.py
- from openagents.agents.worker_agent import WorkerAgent, \
- ChannelMessageContext
- class SimpleWorkerAgent(WorkerAgent):
- default_agent_id = "charlie"
- async def on_startup(self):
- ws = self.workspace()
- ss = "Hello from Simple Worker Agent!"
- await ws.channel("general").post(ss)
- if __name__ == "__main__":
- agent = SimpleWorkerAgent()
- agent.start(network_host="localhost", network_port=8700)
- agent.wait_for_stop()

## Slide 14: Slide 14
- Abacus CoWork
- https://www.youtube.com/watch?v=hkGSbJnhqhc
- Abacus has released CoWork - a desktop AI tool
- Combines GPT-4 for reasoning, Gemini Flash for speed, Claude for long context work, and Gemini Pro for multimodal output
- CoWork runs on Mac, Windows, and Linux as part of Abacus AI's desktop environment (supports 40+ AI models
- AI Updates
- Awesome DESIGN.md
- https://github.com/VoltAgent/awesome-design-md
- Copy a DESIGN.md into your project, tell your AI agent "build me a page that looks like this" and get pixel-perfect UI
- Meta Muse Spark proprietary model - April 8, 2026
- This is the first AI model from its newly formed Superintelligence Labs, led by Alexandr Wang
- The model is designed to be small and fast while capable of deep reasoning across science, math, health, legal documents, and image or video analysis
- It features a fast mode for simple queries and a deeper reasoning mode for complex tasks, plus a shopping mode that draws on creator content across Meta's platforms
- Currently available only in the US, powering Meta AI, Facebook, Instagram, WhatsApp, Messenger, and Ray-Ban Meta smart glasses
- Not good at coding yet

## Slide 15: Slide 15
- Perplexity Can Prepare Federal Taxes
- Perplexity Computer Tax Prep
- Perplexity can now help prepare your federal tax return.
- Click on “Navigate my taxes” on Computer to give it a shot
- https://x.com/perplexity_ai/status/2039740898830073889
- Anthropic acquired Coefficient Bio (drug discovery) for $400M
- https://www.rdworldonline.com/anthropics-400m-acquisition-of-coefficient-bio-signals-a-deeper-push-into-drug-discovery/
- Deep Learning NYU Course 2020https://github.com/Atcold/NYU-DLSP20
- Website (static, Jekyll-based):https://atcold.github.io/NYU-DLSP20/
- The contents is in jupyter notebooks, markdown files, PDFs, images
- The website is generated via GitHub Actions
- Jekyll processes the Markdown files and content converted from Jupyter notebooks using Liquid templates and outputs a fully static HTML website

## Slide 16: Slide 16
- AI Updates
- Edgeclaw - free, open-source privacy layer for AI agents
- It prevents sensitive data from reaching the cloud
- Uses a three-tier system: safe requests go to the cloud (S1), sensitive data is sanitized before sending (S2), and highly private data like passwords never leaves your device (S3)
- Detection uses both a rule-based engine (near-instant) and a local LLM for context-aware classification
- Edgeclaw also routes 60–80% of routine tasks to cheaper models, cutting costs significantly
- It runs as a plugin inside OpenClaw, requiring Ollama and minimal configuration
- https://www.youtube.com/watch?v=gVXnjfsFJKE
- OpenClaw + Ollama + Qwen 3.5
- install Ollama, pull Qwen 3.5 via terminal, then connect it to OpenClaw by selecting Ollama as your model provider
- You can then link OpenClaw to 8,000+ apps via Zapier MCP, and stack multiple agents into full automated pipelines
- https://www.youtube.com/watch?v=-Pn3FBOjkgM

## Slide 17: Slide 17
- AI Updates
- The Anthropic vs. Pentagon dispute
- The gist: DOD labeled Anthropic a "supply chain risk" after the company refused to let Claude be used for autonomous weapons and mass surveillance
- A federal judge granted Anthropic a preliminary injunction on March 26, calling the Pentagon's actions "First Amendment retaliation"
- The GSA (General Services Administration) complied by restoring Anthropic to government platforms on April 2
- However, the Trump administration simultaneously appealed to the Ninth Circuit (9 Western States), with briefs due April 30
- A separate parallel case also continues in the D.C. Circuit
- The injunction holds for now, but the legal battle is far from over
- https://www.cnbc.com/2026/03/26/anthropic-pentagon-dod-claude-court-ruling.html
- Use Claude Code with the Qwen 3.6 Plus model via Claude Code Router (CCR) and Open Router
- https://www.youtube.com/watch?v=wyLtTz4S03c
- Here's the prompt: Install claude-code-router (npm install -g @musistudio/claude-code-router) and configure it with OpenRouter using this api key: API_KEY_HEREand set qwen/qwen3.6-plus:free as the model for everything
- Then after run this inside Claude Code: /model openrouter,qwen/qwen3.6-plus:free

## Slide 18: Slide 18
- TRIZ & AI
- TRIZ (Theory of Inventive Problem Solving)
- A systematic methodology for making inventions developed by Soviet engineer Genrich Altshuller (1926–1998)
- Altshuller screened over 200K patents to uncover repeatable patterns in how inventions are made
- Most problems resolve contradictions where solving one aspect creates another problem
- He formulated 40 ways to resolve these contradictions
- He created a step by step algorithm ARIZ for figuring out these contradictions - and then resolve them; it replaces random brainstorming with a proven, teachable method
- Most practical and useful tool included in TRIZ is Scientific Effects guide - which is now available via Accuris Goldfire AI-powered knowledge discovery platform - https://accuristech.com/solutions/goldfire/
- TRIZ links:
- TRIZ: The Right Solution at the Right Time - https://vietnamwcm.files.wordpress.com/2008/07/inovative-problem-solving.pdf
- - An Introduction to TRIZ by Stan Kaplan - https://arvindvenkatadri.com/teaching/1-play-and-invent/modules/70-triz-resources/pdf/TRIZ/Stan%20Kaplan-Intro-to-TRIZ.pdf
- TRIZ: A Theory of Inventive Problem Solving (Concordia University) - https://spectrum.library.concordia.ca/36055/1/triz.pdf
- The Innovation Algorithm by Altshuller (2007) - http://www.evolocus.com/Textbooks/Altshuller2007.pdf
- Classical TRIZ - https://www.trizinfor.org/store/TRIZclassEn.pdf
- TRIZ for Engineers by Karen Gadd (Internet Archive) — https://archive.org/details/trizforengineers0000gadd
- OpenSourceTRIZ.com - Free eBooks & Teaching Materials — https://www.opensourcetriz.com
- TRIZ Level 1 Training Manual (MATRIZ) - https://matriz.org/wp-content/uploads/2019/01/Level-1-Manual-Word.pdf
- TRIZ Material for Beginners (Scribd) - https://www.scribd.com/document/803435517/TRIZ-Material-for-Beginners
- Simplified TRIZ (Academia.edu) - https://www.academia.edu/36931592/Simplified_TRIZ
- TRIZ Theory of Inventive Problem Solving (Academia.edu) — https://www.academia.edu/79649423/TRIZ_Theory_of_Inventive_Problem_Solving
- Prompt: I want to create a skill for Claude Code named "triz". Please create a SKILL.md file in standard format to use with Claude. It should contain the step by step instructions for using ARIZ (TRIŹ) algorithm

## Slide 19: Slide 19
- AI Updates
- https://HERE.NOW
- here.now is a static file hosting service for "agent-to-agent" info
- You upload files through the API - and they are served on a unique subdomain. There is no server-side code or databases
- https://www.youtube.com/shorts/8uPMM8HhRUc
- HeyGen Avatar V
- https://www.youtube.com/watch?v=sGJGCq10gc0
- Create a hyper-realistic AI avatar from just one photo and a 15-second video - combines flexibility and realism
- Avatar V captures your unique motion, expressions, and gestures, then applies them to any outfit, setting, or camera angle, including side views and close-ups, while keeping your identity consistent throughout long-form content
- Setup involves recording a short expressive video, optionally cloning your voice, and selecting a base photo look
- You can then remix appearances using templates or custom prompts

## Slide 20: Slide 20
- AI Updates
- Ole Lehmann Used Council Approach to Counter Claude's Tendency to Agree
- He used five AI advisors with distinct thinking styles to independently analyze a question:
- Contrarian
- First Principles Thinker
- Expansionist
- Outsider
- Executor
- They peer-review each other's responses, and a chairman delivers a final synthesized verdict
- The approach is inspired by Andrej Karpathy's LLM Council concept
- The author credits this method with helping him choose a live workshop over a self-paced course - a decision that resulted in 180 sign-ups and a 4.8-star rating
- https://www.youtube.com/@itsolelehmann
- https://x.com/itsolelehmann/status/2038661433626333649
- https://docs.google.com/document/d/e/2PACX-1vSvw_Mk4iq4DkeMM3YVcvHgkzY-bsmnkXBC2TaEVBUDMjU4RtwDrKdxenpc-x7Vnzw5THGA4wVJd-LX/pub - skill

## Slide 21: Slide 21
- AI Updates
- Hermes Agent - open-source, self-improving AI agent
- By Nous Research, an alternative to OpenAI's OpenClaw
- Its core innovation is GAPA - a system that automatically reviews tool calls, identifies failures, and updates its own prompts, similar to backpropagation but for behavior rather than model weights
- Over time, it builds memory, learns from past conversations, and auto-generates reusable skills
- Written in python.
- https://github.com/nousresearch/hermes-agent
- Karpathy's wiki + Hermes Agent
- Andrej Karpathy published LLM Wiki on April 4, 2026, a system where an AI builds and maintains a persistent, structured wiki of markdown files from your raw sourceshttps://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Hermes Agent has integrated LLM Wiki as a built-in skill
- Run a single command and the agent ingests sources, updates cross-references, and flags contradictions automatically
- The result is a self-maintaining knowledge base that grows smarter with every source you add.
- https://www.youtube.com/watch?v=Mb5N08xcxtg
- Awesome Hermes Agenthttps://github.com/0xNyk/awesome-hermes-agent
- Agent Skills - Dec 2025 - by Anthropichttps://agentskills.io

## Slide 22: Slide 22
- AI Updates
- Karpathy's Obsidian RAG + Claude Code
- https://www.youtube.com/watch?v=OSZdFnQmgRw
- Obsidian-based knowledge system - like RAG but without vectors
- This lightweight system uses a simple file structure with a "raw" folder for data ingestion and a "wiki" folder for organized content.
- Users can add documents via the Obsidian Web Clipper extension or have Claude Code conduct research automatically.
- The system leverages Obsidian's markdown format and linking capabilities, allowing Claude Code to easily navigate and answer questions about stored documents.
- Graphify - Claude Code + Obsidian wiki
- open-source tool that turns any folder into a navigable knowledge graph with a single command inside Claude Code
- https://github.com/safishamsi/graphify
- It outputs an Obsidian vault, a concept-mapped wiki, and plain English Q&A over your codebase
- Supporting 13 languages, PDFs, images, and Markdown
- The standout claim is 71.5x token efficiency versus reading raw files
- No vector DB or config required
- Install with pip install graphify && graphify install
- https://x.com/socialwithaayan/status/2041192946369007924
- Obsidian plus Claude
- Install Obsidian - a markdown-based note-taking app
- Add a browser web clipper extension and a local images plugin
- Articles, transcripts, and web pages are saved directly into Obsidian's raw folder
- Claude Code (desktop) is then connected to the same Obsidian vault folder, where a provided prompt instructs Claude to automatically process raw materials, and organize them into structured wiki pages with cross-linked navigation
- Finally, a scheduled daily Claude agent is configured to automatically review and update the knowledge base every morning at 9 AM
- https://www.youtube.com/watch?v=JtjfYS9hfWw - in Russian

## Slide 23: Slide 23
- AI Updates
- Microsoft MAI Models
- MAI Transcribe 1 ; MAI Voice 1 ; MAI Image 2
- Performance, speed, and aggressive pricing
- http://www.youtube.com/watch?v=tDW6VoyWWqo
- Cursor 3.0 - a major update
- Cursor has been rewritten in Rust for performance and memory
- The update introduces Composer 2, an in-house model that reportedly outperforms leading AI models like Claude 4.6. It is based on Moonshot K2 model
- The new interface shifts the developer's role from writing code to acting as an "air traffic controller" for AI agents
- Users can now manage multiple agents in parallel across different repositories and remote servers to automate complex features
- https://www.youtube.com/watch?v=JSuS-zXMVwE
- Alibaba Wan 2.1 AI video model - open-source
- Professional grade tool, instruction-based editing, modify existing videos, changing weather, clothing, or camera angles using plain text without regenerating from scratch
- Multi-reference inputs, utilizing up to five videos to maintain a subject's appearance and voice across shots
- Model offers improved motion fluidity for clips up to 15 seconds at 1080p; has "first and last frame control" to dictate specific narrative transitions
- https://www.youtube.com/watch?v=3pj-KLBKcvc

## Slide 24: Slide 24
- AI Updates
- Claude's Microsoft 365 connector
- Read-only access to Enterprize Outlook, OneDrive, SharePoint, and Microsoft Teams
- Retrieve and analyze emails, documents, and meeting notes through simple chat prompts, no manual uploading required. Access is read-only, meaning Claude cannot send, edit, or delete anything
- https://www.youtube.com/watch?v=Vk5_2mBXHQ8
- Anthropic Claude Mythos - successor to Claude Opus 4.6
- A preview showcased through "Project Glasswing", a cybersecurity initiative (with Microsoft, Google, Cisco, AWS, and Nvidia)
- Mythos preview scored 93% on SWE-bench Verified and 83% on the CyberGym benchmark - far outpacing Opus 4.6's 66%
- 72.4% on Firefox JavaScript shell exploitation, vs 14.4% Opus 4.6's
- The model autonomously discovered decades-old vulnerabilities in OpenBSD, FFmpeg, and the Linux kernel; In a sandbox escape test, it gained unauthorized internet access and even emailed a researcher
- https://www.youtube.com/watch?v=Q0vLGvcdJZ8
- "Caveman" plugin/skill for Claude Code
- forces Claude Code to use terse, caveman-style language
- Up to 75% reduction in tokens, improved accuracy
- https://www.youtube.com/watch?v=4FO1Liu-ttk
- https://github.com/JuliusBrussee/caveman

## Slide 25: Slide 25
- AI Updates
- Google's Coding Agent (Jitro = Jules V2)
- Shifts from prompt-driven tasks to goal-driven autonomy
- Expected to be presented at Google IO 2026 in May
- https://jules.google
- https://developers.google.com/jules/api
- https://www.testingcatalog.com/google-prepares-jules-v2-agent-capable-of-taking-bigger-tasks/
- https://www.youtube.com/watch?v=73ATKg42oJk
- https://www.youtube.com/watch?v=8d3E-XZX3u4
- Flova AI video production platform - https://www.flova.ai
- from California
- Designed to replace the fragmented stack of separate subscriptions
- It is a conversational AI agent that builds scripts, storyboards, visual assets, and final edits inside a single interface
- It integrates over 20 models (Sora 2, Cling 3.0, MidJourney, Suno, ElevenLabs, ...)
- Multi-shot character consistency, tail-to-head frame stitching for seamless cuts, and Omnihuman 1.5 for lip-synced music videos from a single image
- At $19/mo replaces tools costing $120/mo
- Digits AI-powered Accounting
- An alternative to QuickBooks
- It auto-classifies 97% of transactions
- It learns from your firm's classification behavior to build custom AI models, applying consistent coding logic across all client files
- Automated bank reconciliation, auto-fetching statements and reconciling them without manual input, bill pay, invoicing, receipt matching, and customizable dashboards and reports
- Security - AICPA SOC 2 Type 2 standards, the client's data kept fully isolated
- Plans start at $10/month
- Digits can also connect to an existing QuickBooks file, making it easy to try
- https://digits.com

## Slide 26: Slide 26
- Jobs
- https://layoffs.fyi
- https://trueup.io/layoffs
- Tech Layoffs by year (US only):
- 71.5K in 2026 (as of April 10, 2026)
- 124K in 2025
- 153K in 2024
- 264K in 2023
- 165K in 2022 https://layoffs.fyi
- The Tech Layoff Tracker
- In 2026: 91,739 people laid off (917 per day)
- In 2025: 245,953 people laid off (674 per day)
- In 2024: 238,461 people laid off (653 per day)

## Slide 27: Slide 27
- AI-Linked Job Losses
- https://jobloss.ai
- More Software Jobs in 2026 (publ. April 6)
- Software engineer job listings have risen 30% so far in 2026, reaching about 67,000 openings
- The increase challenges fears that AI is rapidly replacing coding jobs
- https://gizmodo.com/report-says-software-engineer-job-listings-are-up-30-this-year-2000742638

## Slide 28: Slide 28
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

## Slide 29: Slide 29
- Thank You!

