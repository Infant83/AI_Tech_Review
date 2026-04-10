# Skywork LGD Deck Quality Review

- Review target:
  - `skywork_exports/2026-04-10_encrypted-llm-ai-data-protection_skywork_lgd_v1.pptx`
- Review date:
  - `2026-04-10`
- Method:
  - PPT object-model inspection via `python-pptx`
  - slide image export via PowerPoint COM
  - comparison against `reports/2026-04-10_encrypted-llm-ai-data-protection_deepresearch.md`

## Findings

### 1. High: template placeholder leakage remains in final slides
- Slides `4`, `7`, `11`, `14` still contain template placeholder or spec text.
- Examples:
  - Slide 4: `기술 핵심 및 비교 / Noto Sans KR SemiBold / ~16px`, `컬처명을 입력해 주세요`
  - Slide 7: `헤드라인 / Headline`, `컬러명을 입력해 주세요`
  - Slide 11: `페이지 제목 / Page title`
  - Slide 14: `페이지 제목 / Go No-Go 체크리스트 및 최종 Closing Insight`, `헤드라인 / Headline / ...`
- Impact:
  - final deck reads as unfinished template customization rather than executive-ready output.

### 2. High: mandatory comparison content is not present as real editable slide text on key pages
- Slide 4 was supposed to be the core `HE vs TEE vs MPC vs conventional encryption` comparison page.
- In the PPT object model, slide 4 contains only the title, brand footer, and placeholder/spec text. No editable comparison matrix body is present.
- Slide 10 shows the same pattern: title/subtitle exist, but no editable industry matrix body is present in the text layer.
- Impact:
  - critical decision-support content is either missing or flattened into non-editable image assets, which weakens reuse, review, and downstream editing.

### 3. Medium: slide 12 conflates bootstrapping cost with end-to-end inference latency
- Slide 12 row `③ 지연 시간 수 초 이내 처리 (Bootstrapping)` says:
  - `Bootstrapping 비용으로 실제 지연은 수십 초~수분 수준`
- The deep research report explicitly separates:
  - per-bootstrapping acceleration results
  - end-to-end encrypted inference latency such as Cerium `BERT-Base 8.8s`, `Llama3-8B first token 134s`
- Impact:
  - this phrasing risks mis-teaching the audience that a single bootstrapping step itself takes tens of seconds to minutes, which is not the same claim as end-to-end model latency.

### 4. Medium: language quality drops below professional briefing standard on several slides
- Detected text defects:
  - Slide 5: `최전 연산`
  - Slide 7: `암호화 BERT금 추론`, `제한적 테스코 파일럿 운용 가능`
  - Slide 8: `자연 시간 과제 전존`
  - Slide 12: `현재는 현재는 파일럿·PoC 단계`
- Impact:
  - these are visible enough to reduce trust in a technical strategy deck for CTO/CISO audiences.

### 5. Medium: several technically important slides are image-heavy enough to reduce searchability and editability
- Slides `2`, `3`, `6`, `8`, `12` contain large numbers of `PICTURE` objects relative to typed text objects.
- Example:
  - Slide 2: `16` picture objects, `5` text shapes
  - Slide 12: `45` picture objects, `34` text shapes
- Impact:
  - the deck may look acceptable visually, but evidence blocks and comparison content become harder to edit, localize, search, and audit later.

## Open Questions
- Slide 4 and slide 10 may have visually rendered tables inside images, but in the editable PPT layer they are not available as structured text.
- If LGD wants this deck to be maintained internally, the current raster-heavy construction is likely to become a maintenance cost.

## Recommendation
- First fix:
  - remove all template placeholder/spec strings
  - rebuild slide 4 and slide 10 as true editable comparison tables
  - rewrite slide 12 latency wording to separate `bootstrapping cost` from `end-to-end inference latency`
  - run a Korean copy-edit pass across slides 5, 7, 8, 12, 14
- Second fix:
  - convert key evidence and matrix slides from image-heavy blocks into editable tables/shapes wherever possible
