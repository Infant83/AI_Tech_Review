# 2026-05-08-AI-Updates.pptx

## Slide 1

Crowd-sourced "LM Arena" Leaderboard
Deepseek-TUI Harness
Anthropic Wall Street $1.5 Bln Partnership
Anthropic SpaceX Compute Deal
Anthropic Claude Security
New in Claude Managed Agents
xAI Grok Connectors
OpenSwarm AI - open-source multi-agent system
Agentic AI Communication Chain
Perplexity Workflows
Miscellaneous AI news
OpenClaw Updates
Hermes Agent Curator
No AI Agent Orchestration Needed
Harness more important than the model
InsForge - Backend for AI Coding Agents
Google Deepmind AI co-clinician
TradingAgents
Superpowers Agentic Framework
AI Updates -May 8, 2026
Jack Dorsey Lays off 4K workers
Mo Gawdat on How to Position Yourself
Jobs & Layoffs
"In 2026, your agents have agents."
Andre Karpathy - talk at Sequoia Event
Boris Cherny: Why Coding Is Solved
How Claude Code Works
Higgsfield AI - Cinematic AI Videos
Suno AI Music Generation
Microsoft Copilot Actions and Cowork
Codex CLI's new "/goal" feature
Hermes Agent "goals" system
Google Remy competes with OpenClaw
OpenAI GPT 4.5 Instant
HyperFrames open-source HTML-to-video
Unity AI in open beta for  Unity 6 developers
Zed Editor vs VS Code
Jujutsu Version Control
Weave and Mergiraf - Better Merge

## Slide 2

Starting Elo rating = 1000
https://en.wikipedia.org/wiki/Elo_rating_system
"LM Arena" Leaderboard
English - https://lmarena.ai/leaderboard/text
Coding - https://lmarena.ai/leaderboard/text/coding
https://lmarena.ai/leaderboard/text
Design Arena -
https://www.designarena.ai
https://openlm.ai/chatbot-arena/
https://beta.lmarena.ai
Web Leaderboard -  1T params
https://web.lmarena.ai/leaderboard
LLM Leaderboard - by @LlmStats -
https://llmworld.net/llm_leaderboards/
LLM Leaderboard - by StackAI -
https://www.stack-ai.com/llm-leaderboard
LLM Leaderboard - by Artificial Analysis -
https://artificialanalysis.ai/leaderboards/models
Open LLM Leaderboard - by Hugging Face -
https://huggingface.co/open-llm-leaderboard
LLM Leaderboard - by Vellum -
https://www.vellum.ai/llm-leaderboard
AI Benchmarking Hub -
https://epoch.ai/data/ai-benchmarking-dashboard
Grok 4 Benchmarks -
https://artificialanalysis.ai/models/grok-4
Image arena (alibaba) -
http://aiarena.alibaba-inc.com/corpora/arena/leaderboard?arenaType=T2I
image arena - https://lmarena.ai/leaderboard/text-to-image
Data for May 07
deepseek-v4 - 1.6T
Baidu Ernie-5.0 - 2.4T
GLM-5.1 - 744B
kimi-k2.6 - 1T
Qwen3.5-397B
Xiaomi MiMo-V2-Pro - 1T+
Meta muse-spark  30B
ByteDance dola-seed-2.0-pro 400B
deepseek-v4-pro-thinking
Qwen-3.6-plus
is on 36th place

## Slide 3

Deepseek-TUI Harness
DeepSeek-TUI is an open-source terminal coding agent
TUI = Terminal User Interface (same as CLI)
Only works with DeepSeek models
Built by Hunter Bown
Written in Rust using ratatui (Rust crate)
Works on MacOS, Windows, Linux (pre-built binaries)
https://github.com/Hmbown/DeepSeek-TUI  - 21.4K stars
https://github.com/Hmbown/DeepSeek-TUI/blob/main/docs/ARCHITECTURE.md
https://github.com/ratatui/ratatui
https://ratatui.rs
https://www.youtube.com/watch?v=MWgTWsZjris - video
Edit files, run shell commands, make  git commits, use MCP
Native thinking-mode streaming (you watch the chain-of-thought live)
1M-token context window
RLM (Recursive Language Model) - a parallel sub-agent system that fans out up to 16 DeepSeek V4-Flash workers in one call
DeepSeek-specific. Can use DeepSeek via DeepSeek, or via inference providers like NVIDIA NIM, Fireworks, and SGLang
Does NOT support any other models (GPT, Claude, etc.)

## Slide 4

Anthropic Updates
Anthropic Wall Street $1.5 Bln Partnership
Enterprise AI joint venture with Blackstone, Goldman Sachs, and Hellman & Friedman to deploy Claude directly inside portfolio companies.
Also General Atlantic, Leonard Green, Apollo Global Management, GIC, Sequoia Capital
Then on May 5, CEO Dario Amodei appeared on stage with JPMorgan's Jamie Dimon in New York, unveiling ten financial services AI agents, a Microsoft 365 integration, a Moody's data partnership, and a co-built financial crimes detection tool with banking infrastructure giant FIS
The moves signal Anthropic shifting from AI vendor to embedded operating layer for Wall Street
Anthropic SpaceX Compute Deal
Anthropic gains access to the FULL CAPACITY of SpaceX's Colossus 1 data center in Memphis, TN (equiv. 220K Nvidia GPUs)
https://www.anthropic.com/news/higher-limits-spacex
The partnership allowed Anthropic to double 5-hour token allowance for paying subscribers and remove peak-hour throttling
The two companies also planning building orbital AI compute
Anthropic compute use:
57% - AWS, 40% Google, 3% SpaceX / xAI, 1% Microsoft, ...
Anthropic + SpaceX = compute in low Earth orbit. 'Cloud computing' is now technically accurate.

## Slide 5

Anthropic Claude Security - in public beta for Claude Enterprise
AI-powered security tool built directly into Claude.ai
Uses Claude Opus 4.7 to reason through entire codebases, trace data flows, and detect vulnerabilities across multiple files the way a real security engineer would
A multi-stage validation process filters out false positives before any findings reach the developer, dramatically cutting alert noise
Validated issues come with suggested patches that teams can review and approve. Nothing is applied without human sign-off
The tool consolidates scanning, validation, and patching into one seamless workflow, replacing the fragmented security tooling most teams currently rely on.
https://www.anthropic.com/news/claude-code-security
Anthropic Updates
New in Claude Managed Agents:
dreaming - a scheduled background process periodically reviews past sessions for an agent, looks for patterns in successes/failures, and then curates or compresses those into higher-quality memories (infinite context windows)
outcomes - "goal + spec → graded loop → acceptable outcome"
multiagent orchestration - coordinator agent spawns additional session threads at runtime, each mapped to a specialist agent with its own isolated conversation history
https://claude.com/blog/new-in-claude-managed-agents

## Slide 6

We do these weekly videos every Friday
Stats: 6.68K subscribers, 283 videos
1. Subscribe to this channel https://www.youtube.com/@lev-selector
2. Download slides from GitHub using links under the videos
3. Please pause the video - and answer the pinned question in comments under the video

## Slide 7

xAI Grok Connectors
xAI Grok Connectors
OAuth-based access to Gmail, Google Drive, Google Docs/Sheets, Google Calendar, GitHub, Notion, SharePoint, OneDrive, and Slack
Grok can summarize inboxes, analyze repositories, draft documents, and prepare meeting briefings without manual uploads
Aimed for non-technical users (no-config)
In comparison:
OpenClaw offers broader multi-channel orchestration across 20-plus platforms and supports any AI model including Grok itself
Hermes is better for solo developers needing cron-driven, model-agnostic personal automation at near-zero cost
Claude Desktop is the closest parallel (a polished UI with tool connections), but requires manual MCP server setup and is locked to Anthropic's model stack
https://docs.x.ai/grok/connectors
OpenSwarm AI - open-source multi-agent system
Generates slide decks, reports, videos, ...  from prompt
Orchestrator agent coordinates eight (8) specialized agents covering research, data analysis, document formatting, and video generation
Integrates with 10K+ services via Composio, enabling complex workflows like investor pitches with citations and visualizations
Fully customizable (fork the repo for SEO, sales, or marketing swarms) and easy to install for Node.js
https://www.youtube.com/watch?v=QreoZTA4YEA
https://github.com/VRSEN/OpenSwarm

## Slide 8

Agentic AI Communication Chain

## Slide 9

AI
Perplexity Workflows
feature within Perplexity Computer
https://www.perplexity.ai/computer/workflows
Miscellaneous AI news
https://www.youtube.com/watch?v=qDI4odijz44
Nvidia Nemotron 3 Nano Omni - open-weight - vision, audio, and language - for local use
Poolside AI - Laguna XS2 open-weight, 33B params and Laguna M1 225B params
Alibaba Qwen Image 2.0 Pro - ranked 9th on the Arena leaderboard
xAI ThinkFast 1.0 - low-latency voice model
China Blocks Meta $2Bln Acquisition of Manus
Gemini can now generate and export PDFs, DOCX, XLSX files
Google Translate AI-powered pronunciation practice
11 Labs Music - discovering, creating, remixing AI-generated music
Spotify added green checkmarks for real human artists
Mayo Clinic developed an AI model that can detect pancreatic cancer on CT scans up to 3 years before a clinical diagnosis is typically possible
https://x.com/MayoClinic/status/2049536242929590709

## Slide 10

OpenClaw Updates
https://github.com/openclaw/openclaw  - 370K stars
https://github.com/openclaw/openclaw/releases
v2026.5.7 (May 7) — Plugin publish retry + version verification; Cron CLI JSON status output; Channels CLI overhaul with --all flag; native command owner enforcement; Active Memory admin scope; gateway session cache invalidation on reset; Discord channel routing fix; agent context compaction token clamping; Telegram/WhatsApp/Tavily/Codex approval reliability fixes.
v2026.5.6 (May 6) — Reverts 2026.5.5 doctor --fix that incorrectly rewrote valid openai-codex/* OAuth routes to openai/* ; plugin fetch header symbol metadata fix; debug proxy header normalization; guarded fetch cleanup on timeout.
v2026.5.5 (May 6) — Feishu/LINE/Telegram/Matrix/Discord messaging fixes; xAI Grok reasoning effort fixes; iOS LAN pairing improvements; TUI + gateway + Control UI reliability hardening.
v2026.5.4 (May 5) — Google Meet/Twilio realtime Gemini voice bridge; Slack Block Kit progress drafts; OpenRouter caching + attribution; Control UI improvements; plugin + gateway reliability fixes.
v2026.5.3 (May 3) — CalVer correction build; plugin API range + registry recovery fixes; update channel and install source handling fixes.
v2026.5.2 (May 2) — Plugin install/update/doctor repair (npm cutover, stale installs, beta fallback); leaner gateway + agent hot paths; WhatsApp Newsletter targets; Signal/Telegram/Slack/SearXNG fixes; dep refresh.
v2026.5.1 (May 1) — External plugin npm-first cutover with ClawHub metadata; plugin runtime scoping + hot-path caching; Grok 4.3 as default xAI model; Google Meet room controls; messaging + Control UI fixes.
After 100 days using OpenClaw and Hermes AI agents, the author is shifting away from building on unreliable foundations.
OpenClaw, despite offering powerful capabilities like machine control and autonomous scheduling, constantly breaks with updates, creating daily frustrations for users.
While it introduced revolutionary features that allowed AI to work independently, its instability stems from being built on broken architecture that should be rewritten from scratch.
https://www.youtube.com/watch?v=XZXRg18Ofi8

## Slide 11

AI Updates
Hermes Agent Curator
Instead of users picking agents, tools, and models themselves, Curator automatically selects the best agents for each job, and runs them in sequence
This open-source platform works with any AI model and dramatically reduces task completion time (30 min to 5 min) by picking the right agents immediately
The system has three main components:
a task reader, agent picker, and runner that learns from usage.
Curator works with Hermes' Kanban feature, breaking complex jobs into smaller cards and assigning appropriate agents automatically.
https://hermes-agent.nousresearch.com/docs/user-guide/features/curator
No AI Agent Orchestration Needed
https://arxiv.org/abs/2604.27891
"In-Context Prompting Obsoletes Agent Orchestration for Procedural Tasks"
Multi-agent frameworks like LangGraph and CrewAI may actually hurt performance rather than help.
The researchers compared orchestrated multi-agent systems against simple in-context learning approaches using Claude 4.5.
Findings: providing the entire procedural flowchart in a single system prompt consistently outperformed orchestrated approaches
Frontier AI models have become sophisticated enough to handle complex procedures holistically without external scaffolding, which can fragment reasoning and introduce failure modes
Hermes Agent
https://github.com/nousresearch/hermes-agent  - 139K stars
v0.13.0 - "The Tenacity Release" on May 7, 2026
(finishes what it starts)
v0.12.0 - "The Curator Release" on April 30
(self-maintaining skill management)

## Slide 12

AI Updates
Harness more important than the model
Stanford research reveals that the same model can show 6 (six)  times performance gaps depending on its harness.
A harness is the architecture that turns a model into an agent, giving it abilities to take actions and persist until problems are solved.
When agents underperform, audit the harness first rather than switching models.
The critical insight is the "subtraction principle" - as models improve, successful harness engineering involves removing unnecessary components rather than adding complexity.
https://arxiv.org/abs/2603.25723
https://arxiv.org/abs/2603.28052
InsForge - Backend for AI Coding Agents
https://github.com/InsForge/InsForge
https://x.com/akshay_pachaar/status/2051589749689962949
Claude Code used 3x fewer tokens with one change:
- Before: 10.4M tokens · 10 errors · $9.21
- After: 3.7M tokens · 0 errors · $2.81
Used Insforge Skills + CLI as the backend context engineering layer for Claude Code (open-source and local).

## Slide 13

AI Updates
Google Deepmind AI co-clinician
https://deepmind.google/blog/ai-co-clinician/
AI Co-Clinician is designed to work collaboratively alongside physicians assisting with tasks like patient history collection, diagnostic reasoning, and examination guidance
It is built on technologies like Gemini and Project Astra, and in testing it recorded zero critical errors in 97 out of 98 cases, matching or exceeding primary care doctors in nearly half of consultation areas assessed in a joint simulation study with Harvard Medical School and Stanford Medicine
TradingAgents - Open-source multi-agent LLM framework that simulates a Wall Street trading firm
Has specialized AI agents covering fundamental, sentiment, news, and technical analysis, plus debating Bull/Bear researchers, a trader agent, a risk management team, and a portfolio manager
Originally a UCLA/MIT research paper, it is built on LangGraph with full decision traceability, checkpoint resume, and support for major LLM providers
The project has surpassed 53,000 GitHub stars and serves as a clean reference architecture for multi-agent AI systems, though it is intended for research use only due to significant token costs
https://github.com/TauricResearch/TradingAgents

## Slide 14

Superpowers Agentic Framework
Superpowers is an agentic framework and software development methodology designed to transition AI coding from "vibe coding" to professional engineering
Developed by Jesse Vincent, it provides a suite of composable skills for tools like Claude Code and Codex, enforcing rigorous standards through a structured workflow
The process begins with Socratic brainstorming to define specs, followed by granular task planning and strict Test-Driven Development (TDD).
The framework utilizes sub-agent orchestration to isolate tasks, preventing context rot and ensuring code quality through independent reviews
Additionally, the superpowers-lab repository offers experimental features like interactive tmux control and headless Windows VMs
By prioritizing management, intent, and systematic verification, Superpowers enables developers to build complex, high-fidelity software with significantly reduced hallucinations and technical debt.
https://github.com/obra/superpowers
https://github.com/obra/superpowers-lab
https://www.youtube.com/watch?v=TX91PdBn_IA
https://www.youtube.com/watch?v=wtzzWyrEY_A
https://www.youtube.com/watch?v=7cOAayWzYDY
Jesse Vincent

## Slide 15

Andre Karpathy - talk at Sequoia
Andre Karpathy (co-founder of OpenAI and former Tesla Autopilot lead) talk at Sequoia's annual AI event
https://www.youtube.com/watch?v=96jN2OCOfLs
https://www.youtube.com/watch?v=pngC-TH8M0U - Matt Berman comments
Software 1.0 was explicit human-written code
Software 2.0 involved programming by arranging datasets for neural networks
Software 3.0 treats LLMs as a new computing platform; programming shifts to prompting and managing the context window (the "RAM" of this new system)
Vibe Coding - a term coined by Karpathy - just describe the intent - model will code
Verifiability: The Secret to AI "Smartness". Karpathy explains that AI automates domains faster when the output is verifiable. Code and Math are highly verifiable (you can run code to see if it works), which is why models excel there
Jaggedness: a model can refactor a million lines of code but fail to count letters in "strawberry". If a task isn't easily verifiable or wasn't a priority for Reinforcement Learning (RL), the model's performance "stagnates"
The "Bitter Lesson": human heuristics (rules) lose to end-to-end neural networks trained on data
Example: Tesla's transition from human-coded driving rules to a pure neural network approach significantly improved performance
Agentic Engineering vs. Vibe Coding
Vibe Coding "raises the floor," allowing anyone to build software without deep technical knowledge
Agentic Engineering "raises the ceiling," enabling professional engineers to orchestrate swarms of agents to maintain high quality and massive productivity
Karpathy suggests that while we can outsource "thinking" to AI, we cannot outsource understanding or taste.
Humans will move to a higher layer of abstraction, acting as "orchestrators" who provide oversight and aesthetic judgment
Internet needs to be rebuilt for agents

## Slide 16

Boris Cherny: Why Coding Is Solved
Boris Cherny: Why Coding Is Solved
https://www.youtube.com/watch?v=SlGRN8jh2RI
Boris Cherny is creator of Claude's coding assistant Claude Code at Anthropic
He accidentally created Claude Code in late 2024 as part of Anthropic Labs
Claude Code gained exponential growth starting with the Opus 4 model release in May 2025
Cherny now writes 100% of his code using AI agents, managing hundreds of concurrent agents from his phone and using automated "loops" that continuously maintain his codebase, fix CI issues, and process feedback
He predicts coding will become as democratized as literacy after the printing press, enabling anyone to build software regardless of technical background

## Slide 17

How Claude Code Works
How to build a coding agent like Claude Code
https://www.youtube.com/watch?v=VpetwCa7-eM
Core Agent Loop:
each agent "turn" takes a user request, inspects the repository context, selects relevant tools, runs the model, stores the transcript (including intermediate thinking), and either reports back or keeps looping
Key Components:
Repository mapper - scans the project, ignores .git, caches
Identifies entry points, test files, renders a short summary
Core tools: file ops (read, edit, write); run bash; describe
Search tools - glob (find files by name pattern), grep (search file
contents by regex), and read file window
Permission system (read-only, workspace write, full access)
Runtime guard that validates tool calls before execution
Plan mode - for risky or multi-file tasks; the agent drafts a plan
with steps, waits for user approval, then executes
Todo list tool - model breaks tasks into a structured to-do list
with pending/in-progress/completed states
Session & transcript - persistent conversation stored as JSON Lines, supporting append without rewriting the whole file
Context compaction /compact command; summarizes old messages and keeps recent ones intact to manage context length
Streaming with tool use and stop signals handled as separate event types
CLI entry point - parses arguments, creates or resumes sessions tied to a workspace fingerprint, builds the runtime, runs a turn, and prints the final answer
Design Philosophy:
The runtime coordinates 4 concerns - session memory, the LLM client, tool executor, and permission policy - without mixing their logic.
Model providers are kept interchangeable; the loop doesn't care which LLM is used. Tools are registered separately and routed by the executor.
Same model, different harness, 6x the performance.
Somewhere, a PM is adding 'Harness Engineer' to LinkedIn.

## Slide 18

Video & Audio
Higgsfield AI - Cinematic AI Videos
Higgsfield AI is a very fast growing startup. Founded in 2023 by Alex Mashrabov, the former Head of Generative AI at Snap, the San Francisco-based company officially became a unicorn in January 2026 after raising $80 million in a Series A extension, bringing its total Series A to $130 million and its valuation to over $1.3 billion
Produce short-form, cinematic AI videos and images from simple text prompts, product links, or visuals
Uses top AI models including Sora 2, Kling 3.0, Veo 3.1, and OpenAI's GPT-4.1/GPT-5
Generates 4 Mln videos per day
https://higgsfield.ai
https://openai.com/index/higgsfield/
Suno AI Music Generation
Startup founded in 2023 in Cambridge, Massachusetts
Use text prompts to generate songs - vocals, lyrics, instrumentation. Free credits cover ~ 10 songs/day
100 Mln users, generates 7+ Mln songs per day
Annualized revenue is more than $300 Mln, valuation $5 Bln
Suno faces ongoing lawsuits from major record labels
https://suno.com
https://en.wikipedia.org/wiki/Suno_(platform)

## Slide 19

AI
Microsoft Copilot Actions and Cowork
Require Microsoft 365 business/enterprise subscriptions
Schedule meetings, send emails, perform tasks using your work data; Co-work functions as an advanced agent that can handle complex assignments like event planning by researching information, scheduling meetings, creating documents, and managing multi-step workflows
https://www.youtube.com/watch?v=tl4cJO_itZ4
Hermes Agent "goals" system
Users can assign autonomous tasks that run independently in the background, with an AI judge verifying completion
The "swarm mode" allows multiple AI agents to work simultaneously
https://www.youtube.com/watch?v=9GxvfazA-Bg
Google Remy competes with OpenClaw
https://www.youtube.com/watch?v=nov9uoIQt6g
Cloud based, works with Gmail, Docs, Calendar, Drive, and Search
Operates continuously in the background
OpenAI GPT 5.5 Instant
Now ChatGPT's default model, 52% fewer hallucinations
Codex CLI's new "/goal" feature
add "goals = true" to Codex CLI config file

## Slide 20

AI
HyperFrames open-source HTML-to-video
By HeyGen, released in April 2026, Apache 2.0
Developers and AI agents can create videos by writing standard HTML, CSS, and JavaScript
Renders compositions into deterministic, frame-by-frame MP4 files using headless Chrome and FFmpeg
Works with Claude Code, since every LLM already knows how to write HTML
Has tools for TTS, transcription, and background removal
https://hyperframes.heygen.com
https://hyperframes.mintlify.app/introduction
https://hyperframes.mintlify.app/guides/prompting
Unity AI in open beta for Unity 6 developers
An agentic assistant with two modes - Ask and Agent
Can write C# scripts, generate 2D/3D assets, sprites, textures, animations, audio, and UI layouts directly inside the editor
Supports vision models, Git-integrated code diffing, and an MCP server for connecting external AI tools
https://discussions.unity.com/t/unity-ai-s-open-beta-now-live-for-unity-6/1718560

## Slide 21

Zed Editor vs VSCode
Zed Editor vs VS Code
VS Code is a mature, Electron-based editor with a massive extension ecosystem, excellent Python/debugging tools, and deep customization - but it is heavier on memory and CPU
Zed is built in Rust with GPU rendering, making it noticeably faster and more responsive, with lower memory usage
Zed has Claude AI built in natively, solid MCP support, and real-time collaboration out of the box
But Zed's extension library is smaller, its debugger is still maturing, and Markdown preview is less polished
For AI-first, speed-focused development, Zed is compelling
For full-featured Python debugging and rich extensions, VS Code still leads
https://zed.dev ; https://zed.dev/docs
https://github.com/zed-industries/zed
GitHub's Nathan Sobo began building Atom in 2011 as a "hackable" open-source editor
Atom launched publicly in 2014 and reached 1.3 million downloads by 2015
Along the way, the team inadvertently created the Electron framework and Tree-sitter parser
After Microsoft acquired GitHub in 2018, focus shifted to VS Code, and Atom was officially retired on December 15, 2022
Sobo and his Atom co-creators then founded Zed Industries, rebuilding editor from scratch in Rust with GPU-accelerated rendering
Zed was launched publicly in 2023, open-sourced in 2024, raised $32 Mln  in 2025, hit version 1.0 in April 2026
https://en.wikipedia.org/wiki/Atom_(text_editor)
https://en.wikipedia.org/wiki/Zed_(text_editor)

## Slide 22

Jujutsu Version Control
Jujutsu—a version control system - https://github.com/jj-vcs/jj
Jujutsu ("jj") is a version control system (VCS) created by Martin von Zweigbergk at Google, designed as a modern alternative to Git with full Git compatibility
Jujutsu separates the change ID (stable across rewrites) from the commit ID (changes with every rewrite)
This allows "jj" to automatically rebase all descendant commits whenever you amend any commit in history - https://tonyfinn.com/blog/jj/
The working copy is always a commit in "j" . There's no staging area or index to manage. Every time a `jj` command runs, it snapshots the working copy automatically, meaning you never need to explicitly `git add` changes before committing - https://news.ycombinator.com/item?id=42488112
Modifying any ancestor commit automatically rebases all descendants, with conflict propagation
Conflicts are stored as commit metadata, letting you commit and share a conflicted state and resolve it later
Every repo operation is recorded, so you can undo any action (not just the last one) or restore any previous state
No checkout/branch required: Use "jj new <revision>" to start working from any point; name it with "jj bookmark create" only when needed
Safe force-push by default - equivalent to Git's "--force-with-lease", preventing accidental overwrites
`jj` works as a frontend on top of a Git repo. Coworkers see a normal Git repo and don't need to use "jj" at all. You can use it on any existing Git project without disrupting your team's workflow
A VSCode extension "VisualJJ" - https://visualjj.com

## Slide 23

Weave and Mergiraf - Better Merge
Weave and Mergiraf are modern alternatives
to Git's default line-based merge strategy
Mergiraf parses the full syntax tree of your files and merges
at the AST (Abstract Syntax Tree) level rather than line-by-line
https://mergiraf.org
Weave goes further with entity-level merging — it understands functions, classes, and methods as discrete units. Powered by tree-sitter parsing, it merges per-entity rather than per-line or even per-tree node, so two agents editing different functions in the same file always merge cleanly
https://ataraxy-labs.github.io/weave/
https://github.com/Ataraxy-Labs/weave
Weave is specifically designed with AI coding agents in mind (Cursor, Claude Code, Codex). It ships with an MCP server with 15 tools, letting agents claim entities before editing, check what others are touching, and preview merges before they happen
brew install weave

## Slide 24

Jack Dorsey Lays off 4K workers
Julia McCoy discusses Jack Dorsey’s recent decision to lay off 4,000 employees, or 40% of his workforce, after a three-week experiment proved that AI models like Claude and Codex could perform their roles effectively http://www.youtube.com/watch?v=QGCKh_N6Ilo
Jack Dorsey is chairman (effectively CEO) of payments company Block, formerly known as Square.
~50% of tech layoffs in early 2026 are directly attributed to AI
To adapt, she advises business owners to:
audit operations for AI integration
shift from doing tasks to orchestrating AI agents
capitalize on the lowered costs of building new businesses
Jack Dorsey
Julia McCoy
Ex-Google Exec Mo Gawdat on How to Position Yourself
https://www.youtube.com/watch?v=E0Q96IKXx6Q
Warns of a 10-12 year period of economic and social upheaval
AI will eliminate many jobs within 2-3 years
AI startup took just 6 weeks to build versus the 4 years it would have required in 2022
Key survival skills: master AI as a tool, develop extreme agility for rapid pivoting, maintain strong ethics in AI development, and critically question all information to avoid manipulation.
He believes entrepreneurship will shift from long-term strategic planning to daily reactive agility.

## Slide 25

Jobs
https://layoffs.fyi
https://trueup.io/layoffs
Tech Layoffs by year (US only):
101.6K  in 2026 (as of May 8, 2026)
124K in 2025
153K in 2024
264K in 2023
165K in 2022                  https://layoffs.fyi
The Tech Layoff Tracker
In 2026: 128,270 people laid off (1,002 per day)
In 2025: 245,953 people laid off (674 per day)
In 2024: 238,461 people laid off (653 per day)
https://trueup.io/layoffs

## Slide 26

About the Speaker
Lev Selector, Ph.D.
40+ years of software engineering, data science, and building teams (hiring, training, and managing)
Ph.D. in mathematical modeling and computer simulations
Interests:
Generative AI, Using LLM with your data
Local AI for Local Private Data
Cloud architecture, fin-tech, application security
Find/connect: Linkedin, GitHub, YouTube, Google
https://eais.ai
Enterprise AI Systems

## Slide 27

Thank You!
