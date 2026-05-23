# 2026-04-24-AI-Updates-2.pptx

## Slide 1

- AI Updates - Apr 24, 2026
- AI-attributed layoffs x9 in 2026
consensus.app
Claude CoWork Built 1.4 Mln Audience
MLOps model lifecycle management
AI Pretends to be a Scientist
AI on How To Live Longer
Jobs & Layoffs
- Open Mythos
Neuro-symbolic AI Cuts Energy Use 100 times
Yann LeCun LeWorldModel
OpenClaw Updates
Hermes Updates
5 open-source tools for Claude Code
OpenAI GPT Rosalind & GPT-5.4 Cyber
Engineers are steering agents - not writing code
Google Simula - Generate Training Data for AI
Anthropic - Not Enough Compute
SpaceX partnered with Cursor
Jensen Huang about Nvidia
Abacus AI’s "Agent Swarms"
- "End every session by telling the model to update the skill." 
                -  Sabrina Rammanov
- Part 2

## Slide 2

- Open Mythos
- Open Mythos - built by a 22-year-old Kai Gomez 
Attempting to reverse-engineer Anthropic's secretive Claude Mythos architecture using only public research and speculation
open-source https://github.com/kyegomez/OpenMythos 
A 770M parameter Recurrent-Depth Transformer (RDT)reuses a small set of layers up to 16 times instead of stacking more parameters
This re-use enables deeper reasoning at inference
Combined with a Mixture of Experts setup, the model activates only a small subset of 384 specialists per pass, making it highly efficient
Research suggests a 770M parameter version can match a 1.3B standard transformer

## Slide 3

- Neuro-symbolic AI Cuts Energy Use 100 times
- Neuro-symbolic AI Cuts Energy Use 100 times
AI now consumes over 10% of U.S. electricity, with tech giants spending $650 billion on data centers this year alone. 
Researchers just announced a neuro-symbolic AI system that cuts energy use by 100 times while actually improving accuracy — combining neural networks with step-by-step symbolic reasoning instead of brute-force pattern matching. Additional efficiency breakthroughs include Google's TurboQuant algorithm and the ASUS Eugen 300, a USB device delivering 40 TOPS of AI processing at just 2.5 watts. For businesses, this means AI tools once limited to enterprise budgets will become affordable for everyone, enabling fully personalized customer interactions and automated workflows at a fraction of today's cost.
https://www.youtube.com/watch?v=HkEcPUQ4Ng8

## Slide 4

- Yann LeCun LeWorldModel
- Yann LeCun LeWorldModel 
Yann LeCun long argued that generative AI wastes compute memorizing patterns instead of understanding reality
His alternative, JEPA, predicts abstract concepts rather than raw pixels or words - but suffered from "representation collapse," where the AI oversimplified everything
A new paper called LeWorldModel (LeWM) fixes this with a single mathematical regularizer, forcing the model to internalize physical structure
The result: a 15-million-parameter model that trains on one GPU in hours, plans 48x faster than massive foundation models, and genuinely understands physics - potentially making trillion-parameter LLMs look like an expensive wrong turn.
https://x.com/HowToAI_/status/2046254937559237012

## Slide 5

- OpenClaw Updates
- OpenClaw Updateshttps://github.com/openclaw/openclaw - 363K starshttps://github.com/openclaw/openclaw/releases 
v2026.4.23 - Apr 24 — Image gen via Codex/OpenRouter, per-call timeouts, forked subagent context; fixes Codex routing, WhatsApp onboarding, duplicate reply suppression, Slack/Telegram regressions. 
v2026.4.22 - Apr 23 — xAI image/TTS/STT, realtime Voice Call transcription, local TUI mode, `/models add` CLI, WhatsApp reply quoting, Tencent Cloud provider, Claude Opus 4.7 via Bedrock. 
v2026.4.21 - Apr 22 — Defaults image gen to `gpt-image-2`; fixes owner-command auth bypass, Slack thread aliases, browser invalid ref handling. 
v2026.4.20 - Apr 21 — Onboarding wizard rework, tiered model pricing, session entry-cap, cron state split, Mattermost streaming; fixes exec YOLO rejection, Codex transport, SSRF guards.

## Slide 6

- Hermes Updates
- How to setup Hermes Agenthttps://github.com/nousresearch/hermes-agent - 115K stars
v0.11.0 (v2026.4.23) - Apr 23 — 1,556 commits, 761 merged PRs since v0.9.0 - "The Interface Release": beta TUI v2, unlimited subagent recursion depth/width, 5 new LLM providers, expanded image gen, QQBot gateway, dashboard themes & plugins, GPT-5.5 support.https://github.com/NousResearch/hermes-agent/blob/main/RELEASE_v0.11.0.md 
v0.10.0 (v2026.4.16) - Apr 16 — The "Tool Gateway" release; paid Nous Portal subscribers can now use web search and other gateway toolshttps://github.com/NousResearch/hermes-agent/blob/main/RELEASE_v0.10.0.md

## Slide 7

- 5 advanced open-source tools for Claude Code
- 5 advanced open-source tools for Claude Codehttps://www.youtube.com/watch?v=QK0B1mbJ-VU 
1. CLI Anything - builds  CLI form any tool or repo
2. Compound Engineering (Every Inc Plugin) - follows a six-step cycle: Brainstorming, Planning, Doing, Reviewing, Compounding, and Repeating. It uses an adversarial agent to filter through dozens of potential project improvements to find the most effective one
3. Product Management Skills Plugin - a suite of eight plugins - product strategy, market research, and "Growth Loops." Generate marketing ideas and growth strategies
4. Planning with Files (Manus-style Pattern) - addresses "goal drift" and context loss in AI agents by using a persistent three-file memory pattern (Progress Log, Findings/Research, Session Log). The agent is instructed to save its findings every two operations, preventing it from repeating failures
5. Oh My Claude Code - Agent Teams - allows multiple agents to communicate and share information in real-time; Autopilot Mode:  Enables fully autonomous execution where specialized agents (e.g., one for back-end, one for front-end) coordinate on a single feature
- Anthropic News:
Released Live Artifacts in Cowork for auto-updating dashboards
Added new connectors (AllTrails, Instacart, Audible, TripAdvisor, TurboTax, etc.)
Claude is now available inside Microsoft Word for Pro/Max users

## Slide 8

- AI Updates
- Anthropic News:
Released Live Artifacts in Cowork for auto-updating dashboards
Added new connectors (AllTrails, Instacart, Audible, TripAdvisor, TurboTax, etc.)
Claude is now available inside Microsoft Word for Pro/Max users
- Google DeepMind's Deep Research Max
Autonomous research agent built on Gemini 3.1 Pro
Asynchronous, background workflows, it runs around 160 search queries per task, iteratively reasoning and refining before delivering a fully cited report
supports MCP and web search
Multimodal inputs - text, PDFs, CSVs, images, audio, and video
Natively generates charts and infographics inline
- Warp added universal agent support (Claude Code, Codex, OpenCode in one terminal)
Microsoft Copilot gained agentic capabilities in Word, Excel, and PowerPoint
X rolled out Custom Timelines powered by Grok
HeyGen launched HyperFrames for AI-generated animations via Claude Code
Ideogram added custom model training on your own images
Four robots finished a half marathon in China in under an hour
xAI Grok Text-to-Speech: API at 5% error rate vs 11 Labs' 12%, priced at $0.10/hour supporting 25 languages, targeting the voice AI market.

## Slide 9

- OpenAI GPT Rosalind & GPT-5.4 Cyber
- OpenAI GPT Rosalind & GPT-5.4 Cyber 
OpenAI GPT Rosalind is a new life sciences model built for biology, drug discovery, genomics, and protein engineering
It connects to over 50 scientific databases, outperforms GPT-5.4 on bioinformatics tasks, and is currently available only to select organizations like Moderna and Amgen
OpenAI GPT-5.4 Cyber focuses on defensive security, featuring binary code analysis for vulnerability detection without needing source code, with relaxed restrictions for verified security professionals
OpenAI also updated its Agents SDK with a model-native harness, secure sandbox, and memory management to simplify building autonomous agents
https://www.youtube.com/watch?v=CFBIg4_z99w

## Slide 10

- Engineers are steering agents - not writing code
- Engineers are steering agents - not writing code
Ryan Laapo, a member of technical staff at OpenAI, argues that software engineering has fundamentally shifted
Code is now free and abundant, generated by AI agents rather than written by hand
The scarce resources today are human time, attention, and model context
Engineers should act as staff-level orchestrators, steering agents rather than writing code themselves
 The key to making this work is "harness engineering" - structuring codebases, documentation, guardrails, lint rules, and review agents so AI can do the full job reliably
Success depends on documenting non-functional requirements, eliminating slop systematically, and progressively removing humans from the loop
The goal is a fully autonomous pipeline driven by a token budget and clear priorities
https://www.youtube.com/watch?v=am_oeAoUhew

## Slide 11

- Google Simula - Generate Training Data for AI
- Google Simula - Generate Training Data for AI
Simula builds datasets from first principles using reasoning and mechanism design
It controls four key properties independently: 
coverage (what topics to include), 
diversity (variety of examples), 
complexity (difficulty level), 
quality (via a dual-critic verification step)
The approach consistently outperforms simpler methods and requires fewer data samples to achieve better results
Simula already powers Gemini safety classifiers, ShieldGemma, MedGemma, Android scam call detection, and Google Messages spam filtering
https://research.google/blog/designing-synthetic-datasets-for-the-real-world-mechanism-design-and-reasoning-from-first-principle
https://research.google/pubs/orchestrating-synthetic-datasets-with-reasoning/
https://www.marktechpost.com/2026/04/21/google-introduces-simula-a-reasoning-first-framework-for-generating-controllable-scalable-synthetic-datasets-across-specialized-ai-domains/

## Slide 12

- AI Updates
- Anthropic - Not Enough Compute
xAI - compute-rich, demand-poor - just partnered with Cursor
Google - rich in both, selling TPUs while serving Gemini
OpenAI - high demand, adequate compute
Anthropic - demand-rich, compute-starved
The economics for Anthropic: Anthropic can't raise prices (users would flee to Codex) and can't serve demand, so they're using quota manipulation as a stealth price hike.
- SpaceX partnered with Cursor
Elon Musk's rocket and space company announced a partnership with Cursor AI coding tool made by startup Anysphere
The deal gives SpaceX the option to either acquire Cursor later in 2026 for $60 Bln, or pay $10 Bln for the collaborative work if no acquisition takes place
Cursor gains access to SpaceX's massive Colossus supercomputer

## Slide 13

- AI Updates
- Jensen Huang about Nvidia
Nvidia's moat isn't easily commoditized because transforming electrons into valuable tokens requires deep, ongoing engineering across a five-layer AI stack
He frames Nvidia's role as doing "as much as necessary, as little as possible," partnering broadly while owning the hardest parts
Its advantages stem from scale, supply chain commitments, a rich CUDA ecosystem, massive installed base, and cross-cloud availability, giving it the best performance-per-dollar and performance-per-watt.
On competition, Huang dismisses TPUs as narrower, noting Nvidia's programmability enables new algorithms like MoE and attention variants
He admits missing early opportunities to invest in Anthropic but won't repeat that mistake with OpenAI. Bottlenecks like CoWoS, HBM, and EUV are solvable within two to three years given demand signals; energy and labor shortages worry him more.
Huang pushes back hard against export controls on China, arguing China already has abundant energy, chips, and researchers
Conceding that market, he contends, hands the second-largest ecosystem to Huawei and fractures the American tech stack globally
He prefers dialogue and competition over isolation, rejecting absolutist framings of AI as equivalent to nuclear weapons.
- Abacus AI’s "Agent Swarms,"
A hierarchical multi-agent architecture
A "master agent" decomposes complex prompts into subtasks, mapping dependencies and deploying specialized "worker agents" to execute them in parallel or sequence
"intelligence emerging through coordination" rather than just larger single models"
Swarms build sophisticated products, including a supermarket management system, a Notion-like workspace, and a comprehensive HR platform
Beyond coding, the system excels at complex research, replacing traditional consulting by coordinating parallel investigations into board-ready presentations

## Slide 14

- consensus.app - Academic Search
- https://consensus.app - is an AI-powered academic search engine that searches over 220 Mln peer-reviewed research papers to help users quickly find and understand scientific evidence
Unlike general AI tools, every answer it provides is grounded in real studies with verifiable citations
Users can ask natural language or yes/no questions, and Consensus synthesizes findings across multiple papers into a clear summary
A unique feature called the Consensus Meter visually shows how much the literature agrees or disagrees on a topic
It is used by over 5 Mln researchers, students, and professionals worldwide
Consensus offers a free tier with limited searches and a paid Pro plan with deeper research capabilities
- AI-attributed layoffs are projected to increase ninefold in 2026, hitting white-collar roles hardest
Companies are suppressing hiring. Entry-level postings dropped 15%, while AI-focused roles surged 340%
Atlassian exemplifies the trend: laying off 10% while hiring 800 AI specialists
New models now outperform humans on desktop productivity tasks, accelerating the shift
The takeaway for founders and professionals: integrate AI into your workflows now or risk being left behind
https://www.youtube.com/watch?v=xsWaPdvCmy4
- AI-attributed layoffs x9 in 2026

## Slide 15

- Claude CoWork Built 1.4 Mln Audience
- Claude CoWork Built my 1.4 Mln Audiencehttps://www.youtube.com/watch?v=oYlA8dtC9WI 
Sabrina Rammanov uses Claude Co-work and Blotato to manage 250 pieces of content per week without a team
Blotato was founded by Sabrina, it is all-in-one AI content enginehttps://www.blotato.com 
Sabrina uses a prompt to have Claude interview her about content pillars, target audience, and preferred tone. She provides writing samples until Claude is "95% confident" it can replicate her "voice"
She created skills for writing content
She uses Claude’s ability to use local files
Generating Visuals and Infographics using a custom connector for her tool Blotato - generating whiteboard-style infographics and other visuals
Sabrina shows how to schedule posts to multiple platforms (LinkedIn, Facebook, X) entirely through Claude
She still manually reviews every post to ensure brand integrity 
She recommends ending every session by telling Claude to "update the skill" based on the feedback given during that conversation to refine the AI's performance over time

## Slide 16

- MLOps model lifecycle management
- MLflow is an open-source AI engineering platform used by thousands of enterprises to manage the full ML lifecycle
It provides experiment tracking - logging parameters, metrics, and model artifacts across training runs so teams can compare results and reproduce any past experiment
Its Model Registry acts as a governed, version-controlled store where models move through staging, production, and archived states with full audit trails
MLflow supports automated deployment to REST APIs, cloud platforms like AWS SageMaker, Azure ML, and Google Vertex AI, and edge devices
It integrates with frameworks including PyTorch, HuggingFace, and LangChain, and supports LLM and agent tracing
Being framework-agnostic, self-hostable, and cloud-neutral makes it ideal for regulated, multi-cloud enterprise environments
https://mlflow.org/docs/latest/ml/
- Weights & Biases (W&B) is an AI developer platform trusted by thousands of companies including OpenAI and NVIDIA for building, training, evaluating, and monitoring ML models
Its core product tracks experiments in real time with rich, interactive dashboards, making it easy for distributed teams to collaborate and compare results
W&B Weave provides deep observability for LLM applications and autonomous agents -  tracing every call, token, and tool invocation.
The Model Registry governs versioning, lineage, and handoff across teams
For enterprise use, W&B supports SaaS, on-premise, and hybrid deployments with SOC 2 compliance, SSO, customer-managed encryption, custom roles, audit logs, and HIPAA-compliant options
It integrates with all major frameworks, clouds, and CI/CD pipelines. 
https://wandb.ai/site/for-enterprise/

## Slide 17

- AI Pretends to be a Scientist
- A major study from Friedrich Schiller University Jena and IIT Delhi tested three frontier AI models across eight scientific domains in over 25,000 experimental runs
The results are damning. 
In 68% of cases, AI agents gathered evidence and ignored it
In 71%, they never updated their beliefs at all
Only 7% of traces showed the kind of multi-evidence reasoning that defines real science
The researchers call it "evidence non-uptake": the AI performs science without actually doing it
Worse, better prompting and scaffolding barely helps - scaffolding explains just 1.5% of performance variance, while the base model accounts for 41.4%
Until scientific reasoning becomes a core training objective, AI scientist outputs cannot be trusted the way genuine scientific findings can.
https://x.com/MillieMarconnni/status/2046892074541474195 
https://arxiv.org/abs/2604.18805

## Slide 18

- AI on How to Live Longer
- I asked AI to make a list of things to do to live longer. Then to sort it putting the most important factors on top.Here is the list:
Manage chronic stress — one of the strongest predictors of early death and accelerated cellular aging
Maintain strong social relationships and avoid isolation — people with close bonds have a 50% greater survival rate; loneliness rivals smoking in its health impact
Don't smoke — one of the most well-established life-shortening behaviors
Eat a mostly plant-based, whole-food diet and limit ultra-processed foods and added sugar — consistently linked to longevity across all Blue Zone populations
Stay physically active through natural daily movement — walking, gardening, stairs; no gym required
Maintain a healthy body weight
Drink alcohol minimally or not at all
Have a sense of purpose (ikigai) — associated with significantly lower mortality risk
Sleep enough and consistently
Get regular medical checkups and preventive screenings

## Slide 19

- Jobs
- https://layoffs.fyi
https://trueup.io/layoffs
- Tech Layoffs by year (US only):
92.3K  in 2026 (as of April 24, 2026)
124K in 2025 
153K in 2024
264K in 2023
165K in 2022                  https://layoffs.fyi
- The Tech Layoff Tracker
In 2026: 104,093 people laid off (913 per day)
In 2025: 245,953 people laid off (674 per day)
In 2024: 238,461 people laid off (653 per day)
https://trueup.io/layoffs

## Slide 20

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

## Slide 21

- Thank You!
