# Research Runlog

작성일: 2026-04-29  
주제: Cline과 온프레미스 Qwen으로 구축하는 일상 업무용 Agentic Workflow 강연안

## 1. 실행 요약

- 사용자 요청을 기반으로 90분 기술 강의용 Skywork 입력 패키지 작성에 착수.
- ChatGPT 대화 링크는 공개 접근에서 본문 확인 불가.
- Cline 공식 문서, Cline GitHub repo, OpenAI Agents SDK 발표, Alibaba Qwen 관련 공식/논문 출처를 확인해 외부 근거 anchor를 구성.
- 이미지 생성 스킬을 사용해 강연용 spot illustration 4개 생성을 시도했으나, 로컬 `OPENAI_API_KEY`가 401 invalid key로 거절되어 실제 PNG 생성은 중단.
- 대신 Skywork 또는 나노바나나2에 바로 사용할 수 있는 visual asset prompt set을 작성.
- 2026-04-29 추가 요청에 따라 opening hook을 보강:
  - 대통령-하사비스 YouTube Shorts metadata와 auto-caption을 저장.
  - Eric Vyacheslav LinkedIn post의 Claude Code 98.4% infrastructure framing과 arXiv/GitHub source를 확인.
  - Erdős Problem #1196 AI-assisted discovery 사례를 Erdős Problems thread, Scientific American, cautionary summary로 확인.
  - intro slides 2-4를 `specific enough -> harness infrastructure -> AI-assisted discovery` 흐름으로 개정.

## 2. 확인한 자료

| 구분 | URL | 사용 목적 |
|---|---|---|
| Cline customization overview | https://docs.cline.bot/customization/overview | Rules, Skills, Workflows, Hooks, `.clineignore`의 역할 구분 |
| Cline workflows | https://docs.cline.bot/customization/workflows | Markdown workflow, slash command, global/workspace 위치, tool 사용 방식 |
| Cline rules | https://www.mintlify.com/cline/cline/customization/cline-rules | `.clinerules`, `AGENTS.md`, global/local rules, conditional rules |
| Cline GitHub | https://github.com/cline/cline | VS Code 안의 파일/terminal/browser/MCP 기반 agent 기능 설명 |
| OpenAI Agents SDK | https://openai.com/index/the-next-evolution-of-the-agents-sdk/ | harness, tools, sandbox, memory, skills, `AGENTS.md` 트렌드 anchor |
| Alibaba Qwen3-Coder-Next | https://www.alibabacloud.com/blog/602864 | agentic coding model, local development, tool use, failure recovery |
| Qwen3-Coder-Next technical report | https://arxiv.org/abs/2603.00729 | 80B total / 3B active 수치의 정확한 적용 범위 확인 |
| YouTube Shorts 69HKqLFis0Y | https://youtube.com/shorts/69HKqLFis0Y | 대통령-하사비스 대화 opening hook |
| Dive into Claude Code | https://arxiv.org/abs/2604.14228 | Claude Code architecture, simple loop + surrounding systems |
| VILA-Lab GitHub | https://github.com/VILA-Lab/Dive-into-Claude-Code | `98.4% infrastructure, 1.6% AI` 요약과 design-space 자료 |
| Eric Vyacheslav LinkedIn | https://www.linkedin.com/posts/eric-vyacheslav-156273169_researchers-reverse-engineered-claude-code-share-7452612489550258176-53w1 | 대중적으로 확산된 Claude Code infrastructure framing 확인 |
| Erdős #1196 thread | https://www.erdosproblems.com/forum/thread/1196 | Liam Price, GPT-5.4 Pro chat link, Terence Tao/Jared Lichtman discussion |
| Scientific American | https://www.scientificamerican.com/article/amateur-armed-with-chatgpt-vibe-maths-a-60-year-old-problem/ | Liam Price / ChatGPT Pro / 60-year-old problem 보도와 expert comments |
| FutureGenNews | https://futuregennews.com/gpt-5-4-pro-credited-with-solving-erdos-primitive-sets-problem-after-prompt-by-liam-price | viral framing caution 정리 |

## 3. 이미지 생성 시도

명령 목적:

- `agentic-workflow-desk.png`
- `rules-skillset-hierarchy.png`
- `onprem-governance-bridge.png`
- `human-loop-feedback-cycle.png`

결과:

- 실행 실패.
- 원인: OpenAI Images API 호출 시 401 invalid key.
- 후속 처리:
  - 임시 JSONL은 삭제.
  - 동일한 prompt는 `skywork_inputs/..._visual_asset_prompts.md`에 정리.
  - 실제 이미지가 필요하면 유효한 API key로 재실행하거나, Skywork/나노바나나2 이미지 생성 단계에서 prompt를 사용한다.

## 4. 현재 blocker

- ChatGPT 링크의 심층 리서치 본문을 아직 확보하지 못함.
- 내부 Qwen 모델명, endpoint, deployment 형태, 파라미터 수, context length 등은 자료 확인 전까지 placeholder로 유지해야 함.
- Skywork live 실행과 PPTX/PDF export는 아직 수행하지 않음.

## 5. 다음 단계

1. 사용자가 심층 리서치 결과를 붙여넣으면 `source_pack`의 `심층 리서치 원문 삽입 영역`에 반영한다.
2. Qwen 모델명과 운영 환경 관련 claim을 `confirmed / caution / unconfirmed`로 재분류한다.
3. Skywork에 `LGD_Template.pptx`, source pack, master prompt, visual asset prompts를 업로드한다.
4. 1차 생성 후 deck drift를 확인하고, 필요한 경우 correction packet을 작성한다.
5. 최종 PPTX/PDF를 `skywork_exports/`에 저장한다.

## 6. Skywork 실행 시도 - 2026-04-29

### 시도 1: v1 full prompt

- mode: `submit_wait_download`
- upload:
  - `LGD_Template.pptx`
  - source pack, visual prompts, blueprint, source note, runlog
- 결과:
  - Google 2FA 인증 이후 Skywork 로그인 상태 감지.
  - 템플릿과 source file 업로드, prompt 입력까지 진행.
  - `PPTX 파일 업로드` 모달이 닫히지 않아 submit click이 프로젝트 URL로 전환되지 않음.
- 조치:
  - `.automation/skywork-playwright/skywork_sxs_retry.cjs`에 PPTX upload dialog close 로직 추가.

### 시도 2: dialog close 보정 후 재시도

- 결과:
  - `SkyClaw 설정` 또는 Claw upgrade 문구를 모달로 오인하는 false positive가 발생.
  - PowerPoint skill readiness 감지 실패.
- 조치:
  - `Claw` 단어만으로 overlay를 닫지 않도록 자동화 조건 축소.

### 시도 3: v2 compact prompt

- `skywork_inputs/..._skywork_prompt_v2_compact.md` 작성.
- 목적:
  - Skywork prompt input 안정성을 위해 긴 v1 prompt 대신 source pack 첨부 + 짧은 실행 지시로 전환.
- 결과:
  - Skywork 세션이 다시 로그아웃 상태로 돌아감.
  - manual wait에서 로그인 모달이 유지되어 제출 불가.

### 시도 4: OAuth provider 자동 클릭

- mode: `submit`
- 결과:
  - Google provider coordinate click까지 진행.
  - OAuth 전환 중 Playwright browser context가 닫히며 실패.

### 현재 상태

- Live Skywork 프로젝트 URL은 확보하지 못함.
- 최종 PPTX/PDF export pair는 확보하지 못함.
- 다운로드 폴더에서 기존 Skywork PDF를 발견:
  - `C:\Users\angpa\Downloads\From_Prompt_to_Workflow__VS_Code_+_Cline_+_On-premise_LLM을_활용한_일상_업무_자동화.pdf`
  - `pdfinfo` 기준 30 pages, 16:9 PDF.
  - 제목과 주제는 관련 있으나, 생성 시간이 2026-04-29 02:03 KST로 이번 `specific enough / Claude Code / Erdős` intro 보강 전 산출물일 가능성이 높다.
- 해당 PDF는 `skywork_exports/..._skywork_prior_prompt_pdf_only.pdf`로 보관하되 최종본으로 간주하지 않는다.
- 다음 재시도에는 사용자가 visible Skywork window에서 로그인과 Google 2FA를 완료한 상태를 유지해야 한다.

## 7. Skywork 재시도 결과 정정 - 2026-04-29 06:20 KST

### 확보된 항목

- Skywork project:
  - `https://skywork.ai/project/2049206039079092224?from=home_query&is_new_project=false`
- 템플릿:
  - `skywork_inputs/LGD_Template.pptx`
- v1 output:
  - output id: `2049206851514249216`
  - slide count: 35
  - export: `skywork_exports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_v1.pptx`
  - PPTX ZIP structure 기준 `ppt/slides/slide*.xml` 35개 확인.
- v2 output:
  - output id: `2049236012020600832`
  - slide count: 35
  - Skywork API에서 생성 상태는 확인됨.
  - 현재 세션에서는 export endpoint가 `401 Unauthorized`를 반환하여 PPTX/PDF export를 확보하지 못함.

### PDF export 상태

- `skywork_exports/..._skywork_v1.pdf`로 저장된 파일은 실제 PDF가 아니었음.
- 파일 header가 `%PDF`가 아니라 `PK`로 시작했고, `skywork_v1.pptx`와 동일한 크기였음.
- 해당 payload는 다음 위치로 이동:
  - `artifacts/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_v1_pdf_click_returned_pptx_payload.pptx`
- PPTX URL에서 직접 유추한 `.pdf` URL은 HTTP 404를 반환.
- `/tool/generate/export` 및 `/tool/generate/artifact/export`에 대한 `pptx/pdf` 직접 호출은 현재 browser session에서 모두 `401 Unauthorized`를 반환.
- 따라서 이번 재시도 상태는 `valid PPTX available / valid current PDF blocked`로 기록한다.

### 주의

- `skywork_exports/..._skywork_prior_prompt_pdf_only.pdf`는 30 pages의 유효한 PDF이나, 이번 `specific enough / Claude Code / Erdős` intro 보강 전 산출물로 보관한다.
- 최종 공유용 PDF로 간주하지 않는다.

### Speaker notes 보정

- Skywork 원본 PPTX에는 `ppt/notesSlides/notesSlide*.xml`이 35개 존재했지만, 실제 note text는 slide number만 포함되어 있었음.
- `reports/..._blueprint.md`의 slide-by-slide `Speaker note`를 사용해 notes XML만 주입한 별도 PPTX를 생성:
  - `skywork_exports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_v1_with_speaker_notes.pptx`
- 이 파일은 Skywork 시각 결과를 유지하고 speaker notes만 보강한 post-processed copy다.
- 검증:
  - slide XML: 35개
  - notesSlide XML: 35개
  - slide 2 note text에 opening hook speaker note가 삽입된 것 확인.

## 8. Skywork V2 export 복구 - 2026-04-29 06:38 KST

### 확보된 항목

- Skywork project:
  - `https://skywork.ai/project/2049206039079092224?from=home_query&is_new_project=false`
- v2 output:
  - output id: `2049236012020600832`
  - slide count: 35
  - Skywork UI에서 `From Prompt to Workflow VS Code + Cline + On-premise LLM을 활용한 일상 업무 자동화 V2` artifact로 확인.
- v2 export task:
  - PPTX task id: `2049239964370411520`
  - PDF task id: `2049241049183944704`

### 다운로드 결과

- PPTX:
  - `skywork_exports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_v2.pptx`
  - size: 41,015,130 bytes
  - ZIP/PPTX structure 기준 `ppt/slides/slide*.xml` 35개, `ppt/notesSlides/notesSlide*.xml` 35개 확인.
- PDF:
  - `skywork_exports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_v2.pdf`
  - size: 20,759,215 bytes
  - header: `%PDF-1.4`
  - `/Type /Page` marker 기준 35 pages 확인.

### Speaker notes 보정

- Skywork V2 원본 PPTX 역시 notes slide는 존재했지만 실제 note text는 slide number만 포함하고 있었음.
- `reports/..._blueprint.md`의 35개 slide block을 기준으로 notes XML을 주입한 별도 PPTX를 생성:
  - `skywork_exports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_v2_with_speaker_notes.pptx`
- 검증:
  - slide XML: 35개
  - notesSlide XML: 35개
  - speaker notes 삽입: 35개
  - slide 2 note text에 대통령-하사비스 opening hook 설명이 삽입된 것 확인.

### 상태 정정

- 이전 `valid PPTX available / valid current PDF blocked` 상태는 더 이상 최신 상태가 아님.
- 현재 상태는 `valid V2 PPTX / valid V2 PDF / V2 speaker-notes PPTX available`이다.

### 용어 drift 보정

- V2 본문 slide 13, slide 24에서 Skywork가 `Qwen 2.5`와 `1M 컨텍스트`를 임의로 넣은 것을 확인.
- 입력 자료 기준으로 단정할 수 없는 모델명/스펙이므로, Skywork 시각 결과는 유지하고 PPTX XML의 해당 표현만 보수적으로 수정한 발표용 사본을 생성:
  - `skywork_exports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_v2_corrected_with_speaker_notes.pptx`
- 수정 내용:
  - `Qwen 2.5` → `내부 LLM`
  - `Qwen 2.5 사례` → `내부 LLM 사례`
  - `1M 컨텍스트를 지원하는 Qwen 2.5 ...` → `검증된 내부 On-premise LLM ...`
- 검증:
  - 수정된 XML: `ppt/slides/slide13.xml`, `ppt/slides/slide24.xml`
  - slide XML: 35개
  - notesSlide XML: 35개
  - `client`, `BS code`, `weird code`, `QN 3.5`, `Qwen 2.5`, `Qwen-2.5` 잔존 없음.
- 주의:
  - Skywork 원본 PDF는 export 원본 보관용이다. 실제 발표에는 위 corrected PPTX를 우선 사용한다.
