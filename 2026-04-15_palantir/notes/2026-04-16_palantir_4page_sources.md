# Palantir 4-Page Deck Source Note

## Review Context
- Topic: Palantir 심층 조사 및 자사 도입 검토용 4-page 경영진 토론 deck
- Package folder: `2026-04-15_palantir`
- Update date: `2026-04-16`
- Immediate use case: `2026-04-27` Palantir 경영진 미팅 전 사전 판단 및 질의 포인트 정리
- Output target:
  - 4-page discussion deck aligned to the newly added template
  - supporting Korean briefing document
  - Skywork regeneration packet

## New Template
- Location: `sources/ppt_template/Template_4pages_new.pptx`
- Local note:
  - this file is the corrected 4-page template provided by the user on `2026-04-16`
  - this pass uses the template directly as a final `4 content-page` deck base

## Meeting-Note Inputs

### 1. 2026-04-14 kickoff note
- Subject: `Meeting Notes: Palantir 도입 검토 및 부회장님 보고자료 준비 회의`
- Sender: `team@genspark.ai`
- Timestamp: `2026-04-14 23:54:59`
- Gmail URL: `https://mail.google.com/mail/#all/19d8e6b745b43956`
- Key directives:
  - 보안 우려는 `on-prem` 설명으로 풀되, cloud / on-prem 비교 구조를 같이 가져갈 것
  - LG Energy Solution, LG Innotek, LG Electronics의 진행 단계를 process-flow처럼 정리할 것
  - 자사 제안은 전사 rollout이 아니라 좁은 영역의 POC부터 시작할 것

### 2. 2026-04-15 strategy structure note
- Subject: `Meeting Notes: 팔란티어 경영진 미팅 대비 전략회의: 보고자료 구조 및 내용 논의`
- Sender: `team@genspark.ai`
- Timestamp: `2026-04-15 01:23:45`
- Gmail URL: `https://mail.google.com/mail/#all/19d8ebcbbaf890d0`
- Key directives:
  - 보고자료는 `보안 / 삼성 / 계열사 / 자사 도입방안` 4개 축으로 고정
  - 삼성은 `2nm 수율`, `도입 이후 확장`, `실제 효과`를 끝까지 추적하되 과장 없이 정리할 것
  - 계열사 파트에는 stage map과 cost frame을 둘 것
  - 자사 파트는 `effectiveness / proof window / scalability / cost` 기준으로 후보영역을 평가할 것

### 3. 2026-04-15 Samsung + safety-analysis follow-up
- Subject: `Meeting Notes: 팔란티어(Palantir) 적용 사례 발표 준비 및 안전사고 데이터 분석 결과 검토`
- Sender: `team@genspark.ai`
- Timestamp: `2026-04-15 08:42:22`
- Gmail URL: `https://mail.google.com/mail/#all/19d904e496ea1e8c`
- Key directives:
  - 삼성은 `작년 기사 이후 실제로 어떤 흐름이 이어졌는지`를 더 깊게 볼 것
  - Samsung AI Center ontology / knowledge graph hiring signal을 활용할 것
  - 현대 및 기타 국내 제조 사례를 보강할 것
  - 자사 PoC 후보는 품질 외에도 `안전사고 leading indicator` 같은 영역을 다시 볼 것

## Public Verification Sources by Theme

### A. Security, deployment, and governance
- Palantir Apollo docs:
  - `https://www.palantir.com/docs/apollo/core/introduction`
  - confirms deployment across `cloud`, `on-premises`, and `disconnected (air-gapped)` environments
- Palantir documentation index:
  - `https://www.palantir.com/docs/foundry/data-lineage/explore-artifacts/index.html`
  - confirms support for `AWS Private Link`, `Azure Private Link`, and `GCP Private Service Connect`
- Palantir Privacy and Governance Whitepaper:
  - `https://www.palantir.com/assets/xrfr7uokpv1b/4lXOhv4ycKr5IEMMFybaBj/2d7011ad45d11d189970d13e474f62bd/Palantir_Privacy_and_Governance_Whitepaper__1_.pdf`
  - usable for ontology, lineage, checkpoints, purpose limitation, auditability
- Microsoft Azure Foundry / Azure OpenAI privacy:
  - `https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy`
  - usable for private data handling, non-training statement, geography, logging caveat
- Microsoft `On Your Data` network hardening:
  - `https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/on-your-data-configuration`
- Google Vertex AI VPC Service Controls:
  - `https://docs.cloud.google.com/vertex-ai/docs/general/vpc-service-controls`
- Korea legal anchor:
  - `https://www.law.go.kr/LSW/lsPdfPrint.do?ancYnChk=0&bylChaChk=N&efGubun=Y&efYd=20220804&joAllCheck=Y&joEfOutPutYn=on&lsiSeq=240053&mokChaChk=N`

### B. Samsung, peers, and 2025-2026 public signals
- ETNews `2024-08-05`: Samsung DX Rubicon 3-vendor PoC
  - `https://www.etnews.com/20240805000275`
- ETNews `2024-09-02`: Samsung DX rollout selected Microsoft
  - `https://www.etnews.com/20240902000267`
- Samsung Semiconductor AI Forum 2025
  - `https://semiconductor.samsung.com/kr/news-events/tech-blog/future-of-semiconductor-industry-with-ai-samsung-ai-forum-2025/`
- Samsung Semiconductor GTC 2026
  - `https://semiconductor.samsung.com/kr/news-events/tech-blog/samsung-showcases-agentic-ai-driven-semiconductor-engineering-innovation-at-nvidia-gtc-2026/`
- ETNews `2026-03-18` / Yonhap `2026-03-18` on Samsung and SK manufacturing AI signals
  - `https://www.etnews.com/20260318000242`
  - `https://www.yna.co.kr/amp/view/AKR20260318004300091`
- Hankyung `2026-03-31` on Samsung 2nm yield signal
  - `https://www.hankyung.com/article/2026033177201`
- TechPowerUp `2025-03-18` secondary Samsung-Palantir rumor
  - `https://www.techpowerup.com/334276/samsung-reportedly-partnered-up-with-palantir-to-improve-chip-production-yields`

### C. LG and Korean manufacturing references
- LG CNS official partnership release
  - `https://www.lgcns.com/kr/newsroom/press/detail.enterpriseai-2603-4`
- Palantir / LG CNS release via Nasdaq
  - `https://www.nasdaq.com/press-release/lg-cns-and-palantir-announce-strategic-partnership-accelerate-ai-transformation-2026`
- Dailian `2026-04-07` on LG Chairman meeting Palantir leadership
  - `https://www.dailian.co.kr/news/view/1630338/%EA%B5%AC%EA%B4%91%EB%AA%A8-%EC%8B%A4%EB%A6%AC%EC%BD%98%EB%B0%B8%EB%A6%AC%EC%84%9C-AX-%EA%B0%80%EC%86%8DLG-A-2026`
- Reuters / Yahoo Finance `2026-01-20` on HD Hyundai expansion
  - `https://finance.yahoo.com/news/exclusive-palantir-signs-hd-hyundai-141518689.html`

### D. Cost structure
- Palantir `2025 FY 10-K`
  - `https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf`
- Palantir `Q3 2024 Business Update`
  - `https://investors.palantir.com/files/Palantir%20Q3%202024%20Business%20Update.pdf`
- GSA federal pricelist
  - `https://www.gsaadvantage.gov/ref_text/47QTCA24D004L/103TVU.3VU6QI_47QTCA24D004L_PALANTIR47QTCA24D004L.PDF`

## Fact Classification Rules For The Deck

### Use as confirmed public fact
- Palantir supports cloud / on-prem / disconnected deployment patterns
- Palantir provides governance tooling around lineage, checkpoints, permissions, and auditability
- Samsung DX tested Palantir in 2024, but Microsoft won that public-facing rollout
- LG CNS has an official 2026 Palantir partnership and an unnamed LG affiliate quality PoC -> full contract signal
- HD Hyundai is a strong 2026 Korean manufacturing reference

### Use only as internal signal
- Samsung DS AI Center `Knowledge Graph` JD including `Palantir ontology`
- LG affiliate stage details discussed internally but not publicly attributed by name
- `LG Innotek POC 8억` cost mention from the meetings

### Use only as weak / secondary signal
- March 2025 Samsung semiconductor Palantir-yield story
- any statement directly attributing Samsung 2nm yield improvement to Palantir
- any public SK manufacturing deployment claim unless a stronger source is found later

## Deck Design Constraints Derived From The Notes
- This is not a company-intro deck.
- This is not a broad AI strategy deck.
- It must be a `4 content-page` executive discussion deck.
- Page 1 must de-risk security and data sovereignty without sounding naive.
- Page 2 must separate `signal` from `proof`.
- Page 3 must remain editable because affiliate readiness and cost status are partly estimate-based.
- Page 4 must end in a discussable PoC selection frame, not a vague recommendation.

## Practical Interpretation For This Pass
- The strongest public 2026 argument is not `Samsung already deployed Palantir`.
- The strongest public 2026 argument is:
  - Palantir is demonstrably capable of high-governance deployment,
  - Korean conglomerates are actively using or scaling it in manufacturing-adjacent operations,
  - Samsung is moving toward the same ontology / agentic / manufacturing-AI problem space,
  - therefore the correct question for us is `where to test`, `how to govern`, and `what not to expose`.
