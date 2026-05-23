---
title: Nature alert AI digest source note
date: 2026-05-01
source_type: gmail+nature-alert
tags:
  - ai-tech-review
  - nature
  - ai-digest
  - gmail-intake
---

# Nature Alert AI Digest Source Note

## Gmail 확인

- Gmail query: `subject:"Fwd: Nature alert for 30th April 2026" in:anywhere`
- Gmail message id: `19de02c57ce1e1f5`
- Gmail thread id: `19de02c57ce1e1f5`
- 전달 메일 수신 시각: 2026-05-01 05:54 KST
- 원 Nature alert:
  - sender: Nature `<alerts@nature.com>`
  - title: `Nature alert for 30th April 2026`
  - Nature Volume 652 Issue 8112

## 기준 범위

메일 본문과 Nature Volume 652 Issue 8112 페이지, 그리고 해당 메일에 포함된 `New Online` Nature 항목을 기준으로 AI 관련 항목을 선별했다. 일부 Nature news/commentary 본문은 구독 접근이 필요한 상태였으므로, 공개 preview, Nature issue page, abstract, DOI metadata, 메일 본문 설명을 함께 사용했다.

## AI 관련으로 선별한 항목

### Core AI / AI governance

- [Training language models to be warm can reduce accuracy and increase sycophancy](https://www.nature.com/articles/s41586-026-10410-0)
  - Nature Article, 2026-04-29
  - 직접 연구 논문. Persona/warmth training이 정확도와 sycophancy에 미치는 영향.
- [Friendlier LLMs tell users what they want to hear — even when it is wrong](https://www.nature.com/articles/d41586-026-01153-z)
  - News & Views, 2026-04-29
  - 위 논문에 대한 해설.
- [Could agentic AI topple grant-funding systems?](https://www.nature.com/articles/d41586-026-01297-y)
  - Comment, 2026-04-27
  - Agentic AI가 grant proposal과 peer review 시스템을 어떻게 흔들 수 있는지 논의.
- [No humans allowed: scientific AI agents get their own social network](https://www.nature.com/articles/d41586-026-01278-1)
  - News, 2026-04-20
  - Agent4Science와 AI-generated paper/discussion loop.

### AI-for-science / domain foundation model

- [Merlin: a computed tomography vision-language foundation model and dataset](https://www.nature.com/articles/s41586-026-10181-8)
  - Nature Article, 2026-03-04, issue date 2026-04-30
  - 3D CT VLM, clinical dataset, diagnostic/prognostic task.
- [Genome modelling and design across all domains of life with Evo 2](https://www.nature.com/articles/s41586-026-10176-5)
  - Nature Article, 2026-03-04, issue date 2026-04-30
  - Biological foundation model, genome-scale prediction/design.

### Embodied AI / AI infrastructure

- [World models are AI's latest sensation: what are they and what can they do?](https://www.nature.com/articles/d41586-026-00820-5)
  - News Explainer, 2026-04-28
  - Physical-environment world model과 robotics/simulation.
- [AI data hubs in space: when will they take flight?](https://www.nature.com/articles/d41586-026-01370-6)
  - News Explainer, 2026-04-28
  - AI data centre pressure와 orbital data centre 구상.

### AI-adjacent / follow-up watch

- [Vectorized instructive signals in cortical dendrites](https://www.nature.com/articles/s41586-026-10190-7)
  - Nature Article, 2026-02-25, issue date 2026-04-30
  - Biological credit assignment과 vectorized teaching signal.
- [Improving access to essential medicines via decision-aware machine learning](https://www.nature.com/articles/s41586-026-10433-7)
  - Nature Article, 2026-04-29
  - Decision-aware ML deployment in Sierra Leone medicine allocation.
- [A chemistry lab that runs itself to find the perfect reaction](https://www.nature.com/articles/d41586-026-01283-4)
  - Research Highlight, 2026-04-27
  - Low-cost self-driving chemistry lab.

## 메일 본문에서 제외한 항목

다음 항목들은 과학정책, 생명과학, 재료/디스플레이, 에너지, 고생물학, 연구윤리 등으로 중요하지만 AI 중심 digest에서는 제외했다.

- Big G 측정, vaccine misinformation survey, NSF advisory board, science panels, octopus intelligence, quantum computing health-care contest, smell maps, Roman Empire genetic history, journal ranking closure, paper-mill authorship fraud.
- Perovskite QD LEDs, 2D-3D metasurface display, visible metalens roll-to-roll manufacturing, OPV triplet exciton recycling, anode-free pouch cells, metallic glass, tropical rainforest biodiversity, sorghum pangenome 등.

## 작성 원칙

- 확인 가능한 Nature source에 근거한 사실과 해석을 구분한다.
- 구독 장벽 때문에 전문을 확인하지 못한 news/commentary는 `preview + alert summary 기반`으로 표시한다.
- AI hype로 과잉 일반화하지 않고, 연구소/기술조직 관점의 실무적 의미를 정리한다.

## 2026-05-01 심층 확인 업데이트

사용자 요청에 따라 Nature 기사 수준의 digest에서 논문/프리프린트 확인 중심의 deep digest로 확장했다.

### 추가 확보한 원문/PDF

- Nature PDF 확보:
  - `sources/papers/warm_llm_nature.pdf`
  - `sources/papers/evo2_nature.pdf`
  - `sources/papers/dendritic_credit_assignment_nature.pdf`
  - `sources/papers/robochem_flex_nature_synthesis.pdf`
- arXiv PDF 확보:
  - `sources/papers/warm_llm_arxiv_2507_21919.pdf`
  - `sources/papers/llm_funding_arxiv_2601_15485.pdf`
  - `sources/papers/tao_ai_math_arxiv_2603_26524.pdf`
  - `sources/papers/merlin_arxiv_2406_06512.pdf`
  - `sources/papers/essential_medicines_arxiv_2211_08507.pdf`
- 기타 공개 PDF 확보:
  - `sources/papers/essential_medicines_author_pdf.pdf`

### 접근 제한 또는 PDF 미확보

- Nature News/Comment 계열 일부는 `.pdf` URL 요청 시 PDF가 아니라 HTML 응답이 내려왔다.
- Evo 2 bioRxiv, dendritic credit assignment bioRxiv, RoboChem-Flex ChemRxiv PDF는 직접 PDF 요청에서 403이 발생했다.
- 해당 경우에는 Nature 본문/PDF, arXiv 대체본, 저자 공개 PDF, DOI/metadata, 공개 preview를 조합해 분석했다.

### 생성된 보조 자료

- PDF 텍스트 추출:
  - `sources/metadata/text/*.txt`
- PDF 다운로드 상태:
  - `sources/metadata/2026-05-01_pdf_download_status.json`
  - `sources/metadata/2026-05-01_additional_preprint_download_status.json`
- OpenAlex/arXiv DOI metadata:
  - `sources/metadata/2026-05-01_openalex_arxiv_metadata.json`

### 심층 보고서

- `reports/2026-05-01_nature-alert-ai-digest_deepresearch.md`
- `reports/2026-05-01_nature-alert-ai-digest_deepresearch.html`
