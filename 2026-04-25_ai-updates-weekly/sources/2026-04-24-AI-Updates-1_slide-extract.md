# 2026-04-24-AI-Updates-1.pptx

## Slide 1

- Crowd-sourced "LM Arena" Leaderboard
GPT-5.5 Released
DeepSeek V4 Preview
Custor AI - Agent-first coding
- AI Updates - Apr 24, 2026
- SaaS with AI on Client Side
4-Steps Development
Matt Berman on Vibe Coding
Matt Berman on Opus 4.7
JourneyChat Agent-to-Agent
Anthropic Claude Design
OpenAI ChatGPT Images 2.0
State of the Claw - Peter Steinberger
Apple CEO Change
New world models
AI Agent Traps - DeepMind Cybersecurity
Kimi K2.6
Alibaba Qwen 3.6-Max-Preview
- "A week in AI is a year in any other field."
"The best model is whichever one shipped this morning."
"We stopped writing code. We started describing it."
"The IDE is dead. Long live the task list."
"One prompt, a thousand tool calls, four thousand lines — and a coffee break."
- Part 1

## Slide 2

- Starting Elo rating = 1000
https://en.wikipedia.org/wiki/Elo_rating_system
- "LM Arena" Leaderboard
- English - https://lmarena.ai/leaderboard/text
- Coding - https://lmarena.ai/leaderboard/text/coding
- https://lmarena.ai/leaderboard/text 
Design Arena -    https://www.designarena.ai 
https://openlm.ai/chatbot-arena/ 
https://beta.lmarena.ai 
Web Leaderboard -  1T paramshttps://web.lmarena.ai/leaderboard 
LLM Leaderboard - by @LlmStats - https://llmworld.net/llm_leaderboards/ 
LLM Leaderboard - by StackAI - https://www.stack-ai.com/llm-leaderboard 
LLM Leaderboard - by Artificial Analysis - https://artificialanalysis.ai/leaderboards/models 
Open LLM Leaderboard - by Hugging Face - https://huggingface.co/open-llm-leaderboard 
LLM Leaderboard - by Vellum - https://www.vellum.ai/llm-leaderboard 
AI Benchmarking Hub - https://epoch.ai/data/ai-benchmarking-dashboard
Grok 4 Benchmarks - https://artificialanalysis.ai/models/grok-4 
Image arena (alibaba) - http://aiarena.alibaba-inc.com/corpora/arena/leaderboard?arenaType=T2I 
image arena - https://lmarena.ai/leaderboard/text-to-image
- Data for April 23
- deepseek-v3.2  -  671B
deepseek-v4 - 1.6T
ernie-5.0 - 2.4T
glm-5.1 - 744B 
kimi-k2.6 - 1T
qwen3.5-397B
Xiaomi MiMo-V2-Pro - 1T+

## Slide 3

- GPT-5.5 Released
- GPT-5.5 Released
Improvements in coding speed, token efficiency, and complex problem-solving compared to GPT-5.4
GPT 5.5 is OpenAI's new frontier model, released in two forms: inside Codex and as GPT 5.5 Pro in ChatGPT. It's available to Plus, Pro, Business, and Enterprise users, with API access coming soon. The model features a 400K context window in Codex and a 1 million token context window overall, priced at $5 per million input tokens and $30 per million output tokens (roughly double GPT 5.4's cost).

Key improvements include stronger agentic coding, better computer use, and enhanced knowledge work capabilities. It matches GPT 5.4's token latency while delivering higher intelligence, and uses significantly fewer tokens for the same tasks, improving efficiency. It has a better, more concise personality, improved visual reasoning for iterating on UI layouts, and stronger performance on terminal bench, browse comp, and frontier math benchmarks. Fast mode runs 1.5x quicker for 2.5x the cost. It also offers multiple thinking settings (medium, high, extra high) and strengthened cybersecurity safeguards.
https://www.youtube.com/watch?v=s6H4QF5K9MM

## Slide 4

- DeepSeek V4 Preview 
Officially released and open-sourced
It comes in two MoE variants: V4-Pro, with 1.6 T params, 49B active paramsV4-Flash, with 284 B params, 13B active params 
Both models feature a 1 M token context window by default, powered by a novel Token-wise Compression and DeepSeek Sparse Attention (DSA) architecture
V4-Pro leads all open-source models in math, STEM, coding, and world knowledge, rivaling top closed-source models
V4-Flash offers near-Pro reasoning at faster speeds and lower cost
Both support Thinking and Non-Thinking modes, and are integrated with agents like Claude Code and OpenClaw.
https://api-docs.deepseek.com/news/news260424 
https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf
- DeepSeek V4 Preview
- ollama run deepseek-v4-flash:cloud
ollama launch claude --model deepseek-v4-flash:cloud
ollama launch openclaw --model deepseek-v4-flash:cloud 
ollama launch hermes --model deepseek-v4-flash:cloud

## Slide 5

- Custor AI - Agent-first coding
- Cursor 3 - has a new Rust-based Agents Window
Progress:
v.1. - AI tab completion and inline suggestions
v.2. - Agent-first, with Composer, up to 8 parallel agents
v.3. - Fleets of autonomous agents, with the developer acting as orchestrator/reviewer
Previous versions of Cursor were built on VS Code, with AI helping you write and edit code directly in the editor. The human was always in the loop, reviewing diffs and accepting suggestions line by line
Cursor 3 changes the primary interface from the code editor to an Agents Window, where you describe a task, spawn an agent, and let it handle the coding autonomously
Multiple agents can run in parallel across different repos, locally or in the cloud
You no longer need to look at the code unless you want to — agents can test their own fixes, generate demos, and submit pull requests
The traditional IDE editor is still accessible but is now treated as a secondary option.
- Cursor is working on a $2B Funding Round at $50B valuation
Revenue targets exceed $6B in 2026

## Slide 6

- We do these weekly videos every Friday
Stats: 6.64K subscribers, 281 videos

1. Subscribe to this channel https://www.youtube.com/@lev-selector 

2. Download slides from GitHub using links under the videos

3. Please pause the video - and answer the pinned question in comments under the video

## Slide 7

- SaaS with AI on Client Side
- AI on Server Side
provided by SaaS
- SaaS
- SaaS
- AI Agent on Client Side
- SaaS
- Will everyone have a personal Agent by the end of 2026 ?
Provide an Agent or a Plugin
- UI Communication
- UI or API Communication
- Skills, MCPs, Memory

## Slide 8

- 4-Steps Development
- Discuss Possible Architectures
or Frameworks
- Create Step by step implementation plan (task list)
- Use task list to do the job (build the system)
- Ask to Create Specific Architecture

## Slide 9

- AI
- Matthew Berman on dark side of vibe codinghttps://www.youtube.com/watch?v=XG3ksRWsUJ8 
Trend of shipping software using AI without reviewing the code
He highlights a personal $800 Vercel bill caused by unoptimized default settings and excessive automated builds as a primary cautionary tale
Berman argues that as AI assistants like Claude and Cursor prioritize chat interfaces over code visibility, developers are losing their understanding of system architecture and "platform risk." 
While AI enables unprecedented shipping speeds, it creates a dangerous disconnect between fuzzy natural language prompts and deterministic code
He warns that we may eventually reach a point where AI writes in languages humans cannot comprehend
He is stressing that fundamental coding knowledge remains essential to avoid costly, invisible errors
- What's Not Good - Opus 4.7 & Relatedhttps://www.youtube.com/watch?v=JyvKwKMS6SU 
Opus 4.7 had a broken system prompt in older Claude Code versions that caused it to falsely flag normal requests as prompt injections
Some users reported hallucinated conversation turns and tone misunderstandings
The new tokenizer increases token usage by up to ~30%, making it more expensive to run
One user noted incorrect MCP tool calls, which were rare in prior Claude models
The model also scores slightly lower on cybersecurity benchmarks than Opus 4.6, suggesting intentional capability restrictions
Claude Design's quota is stingy - one 14-page deck used 7% of the weekly allowance, and the chat input requires clicking a button to submit rather than pressing Enter
Anthropic is reducing subscription quotas due to compute constraints and likely cannot serve their best model (Mythos) at all
The host also regrets passing on an Anthropic investment SPV
and warned that agent-managed services (like Stripe Projects) can rack up surprise bills from third-party platforms like Vercel.
- JourneyChat
https://www.journeychat.ai
open-source, private messaging layer specifically designed for AI agent-to-agent communication

## Slide 10

- Anthropic Claude Design
- Anthropic Claude Design
Experimental product from Anthropic Labs
It lets users create polished visual work, including prototypes, slide decks, wireframes, marketing materials, and one-pagers, simply by describing what they want in plain text
The tool is powered by Claude Opus 4.7 and is currently available as a research preview for Claude Pro, Max, Team, and Enterprise subscribers
During onboarding, Claude Design reads your codebase and design files to automatically build a brand-consistent design system
Outputs can be exported as PDF, PPTX, HTML, or sent directly to Canva or Claude Code
It is aimed at non-designers who need to go quickly from idea to visual
https://www.anthropic.com/news/claude-design-anthropic-labs
- OpenAI ChatGPT Images 2.0 - image generation
Significantly improves instruction following, text rendering, and multilingual support; jumped 242+ ELO points on LMArena over the previous leader (Gemini 3.1 Flash/Nano Banana 2), from ~1270 to ~1512.
Can generate slides, infographics, maps, social media graphics, and product mockups; Up to 2K resolution, multiple aspect ratios, and can generate up to 8  related images at once with visual continuity
Advanced features powered by thinking models for Plus, Pro, Business, and Enterprise users; underlying API is open to developers

## Slide 11

- State of the Claw - Peter Steinberger
- 1. The "Stripper Pole" Growth (as opposed to "Hockey Stick". 30K commits and 2K contributors in just 5 months
2. Running "OpenClaw Foundation" is "Company Hard Mode". He cannot directly command, he focused on improving the "Bus Factor" - ensuring the project can survive if any single key contributor leaves
3. The Security Paradox: Feature vs. Exploit. There are many technical exploits that have zero practical impact on real users; Fearmongering - ignoring official security setup recommendations to create a better "story" about vulnerabilities 
4. New Paradigms of Software Development. The "Dreaming" Feature. Just as humans sleep to consolidate memories, "Dreaming" allows agents to reconcile session logs and convert local memories into long-term storage; Prompt Request vs. Pull Request: iterative approach where the "way to the mountain is never a straight line";  He often runs 5–10 agent sessions simultaneously to work on different parts of the code; The Importance of Taste: In an era where anyone can prompt code, Steinberger argues that "Taste" - the ability to identify "AI smell" and maintain a cohesive vision - is the ultimate moat for an engineer
5. Personal AI and Data Sovereignty, Data Ownership. Personal agents should allow users to own their data
6. The OpenAI supports OpenClaw. Peter is purposely bringing in engineers from Nvidia, Microsoft, and Tencent to ensure the project remains "Switzerland" - a neutral, open-source ecosystem
https://www.youtube.com/watch?v=zgNvts_2TUE
- Apple CEO Change
Tim Cook, 65, will step down as CEO on September 1, 2026
John Ternus, 50, Apple's current SVP of Hardware Engineering, will officially become CEO
Ternus, known for leading Apple Silicon development, inherits a $4 trillion company facing pressure to fix its lagging AI strategy

## Slide 12

- New world models
- New world models:
Tencent HY-World 2.0 - open-sourced on Hugging Face 
NVIDIA Lyra 2.0 14B on Hugging Face, "research-only" - turns image into a persistent, explorable 3D Gaussian scene
Alibaba Happy Oyster - generating scenes, can move around
Until this week, the best work was locked behind Google DeepMind's Genie paywall, Fei-Fei Li’s World Labs API, or NVIDIA's enterprise tooling. 
Now game studios, indie devs, and robotics researchers can pull commercial-use weights off Hugging Face for free
The cost of entry dropped by several orders of magnitude in 48 hours.

## Slide 13

- AI Agent Traps - DeepMind's Cybersecurity Paper
https://x.com/HowToAI_/status/2045749883773333717 
Google DeepMind's latest cybersecurity paper exposes a dangerous blind spot in AI agent security
Websites can already detect AI agent visits and serve them hidden malicious content - different from what humans see - a problem called "detection asymmetry." 
Attack vectors include hidden HTML instructions, commands encoded invisibly into image pixels, jailbreaks buried in PDFs, memory poisoning, data exfiltration, and multi-agent cascade infections where one compromised agent corrupts an entire pipeline
What makes this especially alarming is that defenses are largely ineffective. You can't sanitize a pixel, prompt-level safeguards are easily bypassed, and human oversight is impossible at agent operating speeds
When an agent browses dozens of sites, there's no practical way to verify it received the same content you would.
- AI Agent Traps

## Slide 14

- Kimi K2.6
- by Moonshot AI, open-source (MIT) coding
Supports long-running sessions 12+ hrs without losing context or derailing; example - from one prompt making 1,000+ tool calls, modifying 4,000+ lines of code, and achieving a 185% throughput
Long-session stability is maintained through sliding window context compression and checkpoint recovery, with a 256K token context window
Supports a swarm of up to 300 parallel agents each tackling a different part of a problem simultaneously, across up to 4,000 coordinated steps. K2.6 itself decides the orchestration, it dynamically determines which sub-agents to spin up and how to coordinate them
So you can give just one prompt, for example "optimize the throughput of this codebase" - and K2.6 acts as the orchestrator: it decomposes the task, spawns parallel sub-agents, manages their work, iterates, and runs until the task is done. You don't manually invoke the agents — the model handles that internally
94-95% cheaper than Opus 4.6
- Alibaba Qwen 3.6-Max-Preview 
It leads major benchmarks in agentic coding
Outperforms Claude in tool-use and instruction-following tests
256k token context window
a new preserve_thinking capability that carries reasoning across multi-step agent sessions
API compatibility with both OpenAI and Anthropic formats
Unlike earlier Qwen models, Max-Preview is proprietary with no open weights
Smaller options:Qwen3.6-27B - open source - very goodQwen3.6-35B-A3B - open sourceQwen3.6 Plus (1M context) - proprietary

## Slide 15

- About the Speaker
- Lev Selector, Ph.D.

40+ years of software engineering, data science, and building teams (hiring, training, and managing)
Ph.D. in mathematical modeling and computer simulations

Interests: 
Generative AI, Using LLM with your data
Local AI for Local Private Data
Cloud architecture, fin-tech, application security

Find/connect: Linkedin, GitHub, YouTube, Google
- https://eais.ai
- Enterprise AI Systems

## Slide 16

- Thank You!
