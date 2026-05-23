---
title: "Research Runlog - TabPFN OLED Manufacturing Foundation Model Review"
date: 2026-05-07
slug: tabpfn-oled-manufacturing-foundation-model
status: "webzine-revision-complete"
---

# Research Runlog

## Execution Notes

- Working directory: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
- Topic folder: `2026-05-07_tabpfn-oled-manufacturing-foundation-model`
- Browser path:
  - Opened `https://chatgpt.com/share/69fb811f-2764-83a2-9042-bd2e3c24642e` through Playwright.
  - Captured visible page state with Playwright snapshot.
  - The public page exposed only the early `TabPFN2.5 vs XGBoost` summary conversation, not the two deep-research bodies described by the user.
- Research path:
  - Used official TabPFN/Prior Labs documentation, Nature TabPFN paper, TabPFN-2.5 arXiv report, Hugging Face model card, TabPFN GitHub, TabICL documentation/arXiv, OLED inverse-design literature, OLED host screening literature, and prior local OLED review packages.
- Writing path:
  - Applied the user correction to remove execution-roadmap framing.
  - Applied `beautiful-prose` style constraints as Korean report-editing principles: remove filler, avoid generic transitions, keep paragraphs specific, do not end with a procedural roadmap.

## Outputs

- Source capture:
  - `sources/2026-05-07_tabpfn-oled-manufacturing-foundation-model_chatgpt_share_capture.md`
- Source note:
  - `notes/2026-05-07_tabpfn-oled-manufacturing-foundation-model_sources.md`
- Final review:
  - `reports/2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`
- HTML companion:
  - `reports/2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.html`
- Obsidian mirror:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-07_tabpfn-oled-manufacturing-foundation-model\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-07_tabpfn-oled-manufacturing-foundation-model\artifacts\final_review\`

## 2026-05-10 Webzine Revision

- Rewrote the report as `AI Tech Review Letters` rather than a checklist-style technical report.
- Applied the AI_Tech_Review Korean editorial harness:
  - removed report-like 판정 요약 structure
  - rebuilt the opening around the OLED data problem
  - reduced AI-like contrast phrasing and slogan endings
  - kept source links visible in the body
- Added article visuals:
  - OpenAI imagegen hero: `artifacts/final_review/figures/tabpfn_oled_hero_imagegen.png`
  - OpenAI imagegen data-junction illustration: `artifacts/final_review/figures/tabpfn_oled_data_junction_imagegen.png`
  - SVG data-layer diagram: `artifacts/final_review/figures/tabpfn_oled_data_layers.svg`
  - SVG inverse-design filter diagram: `artifacts/final_review/figures/tabpfn_inverse_design_filter.svg`
  - SVG adoption-boundary diagram: `artifacts/final_review/figures/tabpfn_adoption_boundary.svg`
- Added visual audit records:
  - `artifacts/final_review/figure_manifest.md`
  - `artifacts/final_review/figure_audit/tabpfn_final_review_desktop_1440.png`
  - `artifacts/final_review/figure_audit/tabpfn_final_review_mobile_390.png`
  - `artifacts/final_review/figure_audit/tabpfn_final_review_snapshot_1440.yml`
- Added Skywork Image generation packet:
  - `skywork_inputs/2026-05-07_tabpfn-oled-manufacturing-foundation-model_skywork_image_prompt_pack.md`
  - Actual Skywork Image export was not embedded because this session did not expose a callable Skywork Image tool and no project/artifact URL or PNG export was created. The prompt pack is ready for manual or future Playwright execution, and the report follows the rule that Skywork-generated figures are used only after the export is archived.
- Verification:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - Required forbidden-phrase search returned no reader-facing hits.
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - Browser verification at `1440x1200` and `390x1000` confirmed all five images loaded and no horizontal overflow was detected.
  - Obsidian mirror was refreshed with the report, HTML, figure manifest, figures, audit screenshots, and Skywork Image prompt pack.

## 2026-05-11 Editorial Revision

- Applied user feedback from 2026-05-11:
  - removed reader-facing `Image generated with OpenAI image model...` metadata lines from the article body
  - converted images to the same `<figure>` / `<figcaption>` style used in `2026-05-09_ai-updates-weekly_final_review.md`
  - added `작성정보`
  - kept `작성정보`, `References`, `직접 검증 참고자료`, `처음 참고한 자료`, `문체와 시각자료 참고` visible in the section map
  - kept `처음 참고한 자료` and `문체/시각자료 참고` links visible in the generated HTML evidence-link rail
  - rewrote title, opening, section headings, and closing so the article explains TabPFN itself, why it is useful for tabular/manufacturing data, and how it can apply to OLED candidate screening rather than explaining the agent's organization of the topic
  - added a term table for TabPFN/OLED usage vocabulary
- Additional terminology/unit audit on 2026-05-11:
  - normalized OLED property notation in the final review: `T<sub>1</sub>`, `ΔE<sub>ST</sub>`, `η<sub>EQE</sub>`, `LT<sub>95</sub>`, `L<sub>0</sub>`, `L<sub>90</sub>`, `cd m<sup>-2</sup>`, `eV`, and `h`
  - expanded the term table with reliable external definitions from Stanford HAI, IBM, Springer Nature, NIST, IUPAC Gold Book, RSC, scikit-learn, and DeepChem
  - replaced the previous Figure 2 structure with a TabPFN in-context prediction diagram and adjusted SVG text sizing/readability
  - rechecked the JACS 2026 OLED exciplex host numbers and unit notation against the Seoul National University Pure metadata page
- Live source re-checks:
  - Prior Labs model documentation was rechecked on 2026-05-11 for TabPFN-2.6, TabPFN-2.5, TabPFN-2.5-Plus, max row/feature guidance, and license notes.
  - Prior Labs industrial page, TabPFN product page, JACS 2026 OLED exciplex host metadata, and the 2026 steel property prediction arXiv page were rechecked for current wording and facts.
  - Terminology and notation checks used Stanford HAI foundation model guidance, IBM in-context learning and knowledge-distillation explanations, Springer Nature surrogate-modeling survey, NIST DFT page, IUPAC frontier-orbital/triplet-state/BDE entries, RSC OLED EQE review, scikit-learn data-leakage guidance, and DeepChem scaffold-split documentation.
- Verification:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0` after the terminology/unit audit.
  - Forbidden phrase search confirmed no reader-facing `Image generated...` or `Prompt and review notes...` lines remain.
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - Browser verification at `1440x1200` and `390x1000` confirmed all five images loaded and no horizontal overflow was detected. Updated screenshots are in `artifacts/final_review/figure_audit/`.
  - HTML check confirmed Figure 2 now points to `tabpfn_in_context_prediction.svg`; the old `tabpfn_oled_data_layers.svg` no longer appears in the rendered report.
  - Obsidian mirror was refreshed after the terminology/unit pass, and root mirror image links all resolve.

## 2026-05-17 TabPFN-3 And License Update

- Rechecked current Prior Labs and package sources after the user asked to revisit the recent TabPFN review with licensing and company-use considerations.
- Confirmed that the prior 2026-05-11 text was stale on the default model point:
  - `docs.priorlabs.ai/models` now describes TabPFN-3 as the open-source package default model and TabPFN-3-Plus as the API/enterprise model.
  - PyPI shows the 8.x package line started with `tabpfn 8.0.0` on 2026-05-12 and reached `8.0.3` on 2026-05-16.
- Added a dedicated source note:
  - `notes/2026-05-17_tabpfn-3-license-update_sources.md`
- Updated the final review:
  - added TabPFN-3 model/version update paragraphs
  - updated the `활용 전에 확인할 조건` section with version pinning and API/local deployment distinctions
  - added `회사에서 사용할 때는 PoC와 업무 의사결정을 분리해야 합니다`
  - added a company-use table separating preliminary assessment from production, procurement, vendor comparison, product integration, hosted service, customer deliverable, and distillation use cases
  - refreshed `작성정보` and `References`
- Verification:
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - Playwright browser verification through a temporary local HTTP server confirmed at `1440x1200` and `390x1000`: five images loaded, no unloaded images, no horizontal overflow, two tables present, and the new TabPFN-3/license section visible.
  - Obsidian mirror was refreshed with the updated final review markdown, HTML companion, root mirror markdown, and the new source note.

## 2026-05-17 Data Provenance And Use-Case Reframing

- Reframed the article after the user clarified that DFT should be treated as one example rather than the main theme.
- Added the message that TabPFN adoption depends on preparing tables where calculation, experiment, process, inspection, SCM, and design context are explicit enough for the model to learn from them.
- Added a dedicated source note:
  - `notes/2026-05-17_tabpfn-data-provenance-usecases_sources.md`
- Updated the final review:
  - changed the title/subtitle toward industrial tabular data and provenance
  - added `계산값과 실험값은 조건까지 같이 학습해야 합니다`
  - added `TabPFN은 암묵지를 feature로 바꾸는 작업을 빠르게 시험하게 해줍니다`
  - expanded the use-case map to DFT inverse design, device/product design, process optimization, inspection/quality, SCM/raw-material risk, and equipment/predictive maintenance
  - added guidance around row meaning, when the predicted value is finalized, provenance columns, leakage, and decision unit
  - strengthened references with Materials Project methodology, HT-DFT uncertainty comparison, FAIR principles, AiiDA provenance, Materials Experiment Knowledge Graph, Material Data Hub schema, and active learning/multi-fidelity materials references
- Verification:
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - Playwright browser verification through a temporary local HTTP server confirmed at `1440x1200` and `390x1000`: five images loaded, no unloaded images, no horizontal overflow, three tables present, and the new provenance/SCM sections visible.

## 2026-05-17 OLED Quantum-Chemistry And Figure Audit Revision

- Applied user feedback that the previous DFT discussion still felt too broad and too close to inorganic high-throughput DFT language.
- Added a dedicated source note:
  - `notes/2026-05-17_tabpfn-qchem-figure-audit_sources.md`
- Rechecked and added firmer OLED/computational-chemistry references:
  - SCM OLED/AMS/ADF page for charge transport, exciton coupling, phosphorescence, SOC-TDDFT, TADF, and Bumblebee OLED stack modeling.
  - Schrödinger organic electronics page for physics-based modeling, OLED device ML, and organic electronic material discovery workflows.
  - Annual Reviews TD-DFT review for charge-transfer and double-excitation limitations.
  - Onida/Reining/Rubio RMP review and the RSC BSE chemistry review for GW/BSE context.
- Updated the final review:
  - changed the subtitle from DFT-first wording to OLED molecular-calculation case wording.
  - moved GGA/GGA+U from a leading OLED framing example to a supplementary solid-state provenance example.
  - added terminology rows for DFT/molecular quantum-chemistry protocol, TD-DFT/SOC-TDDFT, GW/BSE, and CT state/exciplex.
  - rewrote the calculation-provenance section around software workflow, functional/basis set, conformer, spin state, environment, excited-state method, state character, and expert review status.
  - added a humble caution that TabPFN can rank candidates from flawed calculation assumptions unless expert review gates the table first.
  - replaced DFT-centric use-case wording with molecular quantum-chemistry based inverse-design wording.
- Added and registered a new figure:
  - `artifacts/final_review/figures/tabpfn_qchem_provenance_gate.svg`
  - Updated `artifacts/final_review/figure_manifest.md`.
  - Renumbered captions so the article now contains Figures 1-6 in order.
- Verification:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - SVG XML parse check returned `svg_xml_ok`.
  - `python ..\scripts\markdown_to_html.py --mode final-review .\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion with exit code 0.
  - Playwright browser verification through a temporary local HTTP server confirmed at `1440x1200`: six images loaded, no unloaded images, three tables present, Figure 3 SVG loaded at natural size `1200x760`, captions `그림 1.` through `그림 6.` appeared in order, Schrödinger/SCM/GW/BSE terms were present, and no horizontal overflow was detected.
  - Playwright browser verification at `390x1000` confirmed six images loaded, no unloaded images, Figure 3 was present, and no horizontal overflow was detected.

## 2026-05-17 Context-Learning Figure And Concision Revision

- Applied user feedback from screenshots:
  - the term table was too long and made non-essential specialist terms feel mandatory.
  - the calculation-provenance paragraph looked like a long feature dump.
  - Figure 3 had label/arrow overlap and was carrying too much information.
  - the article needed a better visual explanation of how TabPFN differs from XGBoost-style tabular modeling.
- Rechecked TabPFN technical basis:
  - Nature 2025 TabPFN paper for in-context learning on tabular data, pretrained learning-algorithm framing, and remaining need for feature engineering/problem framing.
  - Prior Labs Models documentation for TabPFN-3/TabPFN-3-Plus distinction and local/API capability boundary.
  - Prior Labs Regression documentation for prediction distribution/quantile support.
- Added a dedicated source note:
  - `notes/2026-05-17_tabpfn-context-learning-figure_sources.md`
- Generated a new imagegen base illustration:
  - `artifacts/final_review/figures/tabpfn_context_learning_bridge_base.png`
  - `artifacts/final_review/figures/tabpfn_context_learning_bridge_base-web.png`
  - Prompt type: `infographic-diagram`, no readable text, no logos, no neural-network cloud, designed for exact Korean labels added afterward.
- Updated the final review:
  - reduced the terminology table to five necessary terms: TabPFN, in-context learning, feature, provenance, uncertainty.
  - removed the old `tabpfn_in_context_prediction.svg` body figure.
  - removed the `tabpfn_qchem_provenance_gate.svg` body figure and kept it only as an archived artifact.
  - replaced Figure 2 with an imagegen base plus inline SVG overlay showing LLM sentence-context prediction, TabPFN table-context label prediction, and the XGBoost-vs-TabPFN distinction.
  - compressed the long feature list into three context groups: calculation lineage, physical/measurement context, and validation status.
  - shortened the use-case table's context column.
- Verification:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - `python ..\scripts\markdown_to_html.py --mode final-review .\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - Playwright browser verification through a temporary local HTTP server confirmed at `1440x1200`: five images loaded, no unloaded images, four tables present, captions `그림 1.` through `그림 5.` appeared in order, the new context-learning base image loaded, old qchem/in-context SVGs were absent from the body, inline overlay text was present, and no horizontal overflow was detected.
  - Playwright browser verification at `390x1000` confirmed five images loaded, no unloaded images, the new context-learning base image and inline overlay were present, and no horizontal overflow was detected.
  - A viewport screenshot of Figure 2 confirmed the base image and exact Korean overlay labels are visible together, and was archived at `artifacts/final_review/figure_audit/tabpfn_context_learning_bridge_desktop.png`.

## 2026-05-17 Human Writing Audit Revision

- Applied user feedback to re-audit the article for human, Hyun-Jung Kim-style Korean prose.
- Added a dedicated writing-audit note:
  - `notes/2026-05-17_tabpfn-human-writing-audit.md`
- Updated the final review:
  - changed the title to `TabPFN과 산업 표 데이터: 값의 의미를 정하는 기록 조건`.
  - rewrote the opening from a generic model-summary frame to a research-team model comparison scene.
  - reduced AI-style contrast cadence such as repeated `A가 아니라 B`, slogan-like headings, and generic closing phrases.
  - revised the TabPFN, provenance, tacit-knowledge, license, and use-case sections so the article reads from row meaning and business decision context rather than from a feature checklist.
  - adjusted captions for Figures 1 and 2 so the visual argument connects more directly to candidate validation and checklist usage.
  - linked the new writing-audit note in the `작성정보` section.
- Verification:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - Playwright browser verification through a temporary local HTTP server confirmed at `1440x1200` and `390x1000`: five images loaded, no unloaded images, no horizontal overflow, the new title was visible, and the new writing-audit note link appeared in the rendered article.

## 2026-05-18 Figure 2 Pretraining/Context Generalization Revision

- Applied user feedback/question:
  - If pretraining saw tasks like `features [a,b,c] -> target d` and `features [a,b] -> target e`, does that mean a later user can bring `a,e` and get a target prediction?
- Rechecked source basis:
  - Nature 2025 TabPFN paper: pretraining predicts masked targets across synthetic datasets; real-world prediction uses labeled training samples as context for unseen datasets.
  - Prior Labs overview: TabPFN applies learned inductive biases and optimization strategies through in-context learning rather than re-optimizing weights per dataset.
- Technical clarification:
  - TabPFN does not memorize semantic feature names such as `a,b,c,d,e`.
  - A new `a,e -> y` task is possible when the user supplies labeled rows defining `y`, and when `a,e` actually contain signal for `y`.
  - Without `y` labels, or when `a,e` are irrelevant, TabPFN cannot infer the target from pretraining memory alone.
- Follow-up clarification:
  - In Figure 2, `pretraining` means model-level pretraining before release on synthetic tabular tasks.
  - User data passed during use, such as `fit(X_train, y_train)` in the sklearn-style API, is the context provided to the already pretrained model, not the model pretraining step itself.
  - Added a short body paragraph after Figure 2 to state the surprising but bounded implication: even if company-specific columns such as `a,e` were not present in model pretraining, TabPFN can try to infer `a,e -> y` from the new table's labeled rows; what generalizes is the procedure for reading examples and query rows, not the business meaning of the column names.
- Updated artifacts:
  - Added `artifacts/final_review/figures/tabpfn_pretraining_context_generalization.svg`.
  - Replaced the old Figure 2 body block with the new deterministic SVG and caption.
  - Updated `artifacts/final_review/figure_manifest.md`.
  - Updated `notes/2026-05-17_tabpfn-context-learning-figure_sources.md` with the 2026-05-18 clarification.
- Verification:
  - SVG XML parse returned `svg_xml_ok`.
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - Playwright browser verification confirmed at `1440x1200` and `390x1000`: five images loaded, no unloaded images, no horizontal overflow, Figure 2 used `tabpfn_pretraining_context_generalization.svg`, and the new caption text was present.
  - A desktop Figure 2 screenshot was archived at `artifacts/final_review/figure_audit/tabpfn_pretraining_context_generalization_desktop.png`.

## 2026-05-18 Section Heading Concision Revision

- Applied user feedback that section headings should not read as full `~합니다/~입니다` sentences.
- Updated H2 headings from sentence-style claims to concise scan-friendly labels:
  - `TabPFN 빠른 기준 모델`
  - `필수 용어 5개`
  - `계산값의 출처와 조건`
  - `암묵지의 기록 방식`
  - `공정·SCM·검사·설계의 행 단위`
  - `DFT/양자화학 역설계`
  - `분자 물성과 소자 성능 간극`
  - `소자·공정 조합 문제`
  - `라벨·검증·라이선스 체크`
  - `회사 PoC와 업무 판단 경계`
  - `활용 사례별 데이터 설계 기준`
- Verification:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - `rg` confirmed no H2 headings ended with sentence-style Korean endings such as `합니다`, `됩니다`, `입니다`, or `습니다`.

## 2026-05-18 AI-Like Jargon Removal Revision

- Applied user feedback that the previous governance-style wording sounded too AI-like and should be removed.
- Updated the final review:
  - changed the title to `값의 의미를 정하는 기록 조건`.
  - changed the final use-case heading to `활용 사례별 데이터 설계 기준`.
  - replaced the abstract final paragraph with concrete questions about what one row represents, when the predicted value is finalized, and whether the input includes information unavailable at prediction time.
  - trimmed several soft AI-like phrases around Figure 1, the TabPFN overview, supplier-claim wording, and PoC guidance.
- Verification:
  - `rg` confirmed the removed wording no longer appears in the reader-facing final review markdown.

## 2026-05-21 Evidence Note Wording Revision

- Applied user feedback on the first Evidence Note body under the TabPFN update section.
- Rewrote the note from a broad warning against treating TabPFN as a “no-tuning universal model” into a more practical adoption check:
  - TabPFN should be read as a fast baseline model with low training and tuning burden.
  - Company review should check data scale, local/API feature differences, processing time, version migration effects, and license scope.
  - OLED use should judge dataset split timing, label meaning, reduction of calculation/experiment candidates, and allowed internal use of outputs, not average accuracy alone.
- Verification:
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
- Follow-up wording update:
  - Replaced the note with the user's preferred phrasing: TabPFN as a fast foundation model with low training and tuning burden, with adoption checks covering performance, data scale, local/API differences, latency, version migration effects, license scope, and OLED-specific label/context validity.
  - Regenerated the HTML companion and reran the writing audit; the audit returned `finding_count: 0`.

## 2026-05-21 Figure 2 Pretraining / User Context Clarification

- Applied user feedback that Figure 2 must make TabPFN's pretraining and actual use stage unambiguous.
- Updated Figure 2 SVG:
  - Changed the main message to `사용자는 TabPFN을 다시 사전학습하지 않습니다`.
  - Renamed the left stage to `모델 제작: pretraining`.
  - Renamed the right stage to `사용자 적용: fit/predict`.
  - Changed the center block to `배포된 TabPFN foundation model` and stated that the weights are already learned.
  - Clarified that valid use is labeled rows defining target meaning, then predicting query rows.
- Updated the Figure 2 caption and following paragraph:
  - `pretraining` now explicitly means the model-development step before release.
  - User PoC work is described as providing labeled rows as context through `fit(X_train, y_train)` or API fit.
  - The LLM analogy is limited to providing examples/context in a prompt-like input; it is not described as RAG-style external document retrieval.
- Verification:
  - Opened the Nature 2025 TabPFN article and Prior Labs model/changelog documentation to confirm the distinction between once-only model pretraining, in-context real-world prediction, and the current fit/API language.
  - SVG XML parse returned `svg_xml_ok`.
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`.
  - Playwright browser verification over local HTTP confirmed Figure 2 loaded, caption was updated, and the page had no horizontal overflow at `1440x1200`.

## 2026-05-21 PoC Boundary Section Removal

- Applied user feedback that the standalone `회사 PoC와 업무 판단 경계` section felt unnecessary and too prescriptive.
- Removed the full section, including:
  - the detailed company PoC/license table.
  - the prescriptive staged adoption paragraph.
  - Figure 5 `tabpfn_adoption_boundary.svg` from the report body.
- Kept only a short license caution in the preceding `라벨·검증·라이선스 체크` section:
  - small evaluation experiments and actual candidate selection, process decisions, or client-facing outputs are not the same use case.
  - license scope and data-transfer conditions should be checked before connecting outputs to business decisions.
- Updated `artifacts/final_review/figure_manifest.md` to archive the removed Figure 5.
- Verification:
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`, `h2_count: 12`, and `figure_count: 4`.
  - `rg` confirmed the removed section title, removed Operator note wording, `그림 5`, `tabpfn_adoption_boundary`, and the unused GitHub reference no longer appear in the reader-facing markdown or HTML.

## 2026-05-21 Foundation Terminology / API / Best-Practice Revision

- Applied user feedback to reduce generic `회사` phrasing and use context-appropriate subjects such as `연구자`, `개발자`, `연구팀`, and `우리`.
- Updated terminology:
  - Changed the section heading from a baseline-like framing to `TabPFN Foundation 모델`.
  - Kept `Foundation 모델` rather than translating it as `기준 모델`.
  - Added a `용어 메모` footnote explaining why `Foundation 모델` and `빠른 비교 기준` are different terms.
  - Added `Foundation 모델` to the essential terminology table and expanded the table from 5 to 6 terms.
- Added a new section, `사용 방식과 성능 기준`:
  - included a short scikit-learn-style `TabPFNRegressor` code block.
  - explained API as using a hosted model service through network requests rather than installing the model locally.
  - added a best-practice table covering raw input/preprocessing, domain features, feature selection, validation split, comparison models, metrics, fine-tuning, and local/API choice.
  - added a performance interpretation table based on Nature 2025 TabPFNv2, TabPFN-2.5 technical report, TabArena 2025, and Prior Labs TabPFN-3 docs.
- Strengthened the provenance rationale:
  - clarified that provenance is not a TabPFN-only decoration.
  - stated that because TabPFN reads target relationships from labeled rows, label-changing conditions must appear in the table as context features.
- Source refresh:
  - checked Prior Labs Quickstart, Benchmarking TabPFN, Improving Performance, Feature Engineering, Feature Selection, Fine-Tuning, Regression, Models, and TabPFN-3 docs.
  - checked Nature 2025 TabPFN, TabPFN-2.5 technical report, TabArena 2025, and Stanford HAI Foundation Models explanation.
- Verification:
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` regenerated the HTML companion.
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-07_tabpfn-oled-manufacturing-foundation-model\reports\2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md` returned `finding_count: 0`, `h2_count: 14`, and `figure_count: 4`.
  - `rg` confirmed `회사`, `업무`, removed PoC boundary wording, and removed Figure 5 references do not appear in the reader-facing markdown/HTML, except for deliberate terminology notes.
  - Playwright browser verification over local HTTP confirmed no horizontal overflow at `1440x1200`, the new section exists, the `TabPFNRegressor` code block rendered, the Foundation model footnote rendered, and the removed company-use section remained absent.

## 2026-05-21 Terminology Table Heading Revision

- Applied user feedback on the terminology table wording:
  - Changed `필수 용어 6개` to `용어 정리`.
  - Changed table headers from `말`, `이 글에서 쓰는 뜻`, `왜 필요한가` to `용어`, `의미`, `활용 포인트`.
  - Softened the lead sentence so it does not sound like a mandatory study list.
- Verification:
  - Regenerated the HTML companion.
  - Writing audit returned `finding_count: 0`.
  - `rg` confirmed the old heading and old table headers no longer appear in the reader-facing markdown or HTML, and the HTML TOC now points to `용어 정리`.

## 2026-05-21 Checkpoint Wording Revision

- Applied user feedback that `checkpoint` is unclear for mixed readers.
- Rewrote the TabPFN-3 changelog sentence:
  - from `단순한 checkpoint 교체보다 넓게 설명합니다`
  - to a clearer explanation that the update changes usable data range, API usage style, advanced features, and migration conditions beyond simply distributing a new model file.
- Replaced the later version-recording item `checkpoint` with `사용한 모델 버전`.
- Verification:
  - Regenerated the HTML companion.
  - Writing audit returned `finding_count: 0`.
  - `rg` confirmed `checkpoint` no longer appears in reader-facing markdown or HTML.

## 2026-05-21 Update Sentence / Tacit Knowledge Context Revision

- Applied user feedback on the TabPFN-3 update paragraph:
  - rewrote the changelog sentence so the paragraph begins directly with the actual changes: larger in-context data range, `/tabpfn/*` JSON endpoint usage, API-only advanced features, and migration conditions.
  - avoided the previous contrastive framing around `모델 파일 하나` and `checkpoint`.
- Strengthened the `암묵지의 기록 방식` section:
  - defined 암묵지 before using it as an argument.
  - added OLED/manufacturing examples such as post-maintenance runs, rate stabilization, visual haze judgment, and supplier lot storage age.
  - added a compact table that converts field expressions into model-readable columns and verification questions.
  - added recent context from Communications Materials 2020, JST CRDS Process Informatics, autonomous experimental systems review, Faraday Discussions 2024, and the 2026 pinax provenance paper.
  - removed the remaining `operator` callout so the section does not read as a prescriptive PoC note.
- Verification:
  - Regenerated the HTML companion with `python scripts\markdown_to_html.py --mode final-review`.
  - Korean writing audit returned `finding_count: 0`, `h2_count: 14`, and `figure_count: 4`.
  - `rg` confirmed stale phrases such as `모델 파일 하나`, `checkpoint`, `embedding하고`, `Operator note`, `왜 중요한가`, `핵심은`, and `보여줍니다` are absent from reader-facing markdown and HTML.

## 2026-05-21 Cover Title / Subtitle Revision

- Applied user feedback that the cover wording was too abstract and did not clearly answer why readers should review TabPFN.
- Revised the reader-facing title:
  - from `TabPFN과 산업 표 데이터: 값의 의미를 정하는 기록 조건`
  - to `TabPFN 활용 검토: 빠른 후보 선별을 위한 표 데이터 준비`.
- Revised the cover subtitle so it explains:
  - TabPFN is a Foundation model pretrained for tabular data.
  - The review focuses on what calculation/measurement conditions and field records must be prepared before applying TabPFN to OLED molecular calculation, process, SCM, inspection, and design data.
- Updated `date modified` to `2026-05-21`.
- Verification:
  - Regenerated the HTML companion with `python scripts\markdown_to_html.py --mode final-review`.
  - Korean writing audit returned `finding_count: 0`, `h2_count: 14`, and `figure_count: 4`.
  - Confirmed the HTML cover now renders the new title and subtitle without the previous subtitle quotation marks.
  - Confirmed the old abstract title/subtitle no longer appears in markdown or HTML.

## 2026-05-21 Cover Title / Subtitle Final Wording

- Applied the user's preferred cover wording:
  - title: `TabPFN: Foundation model for Tabular inference`
  - subtitle: `TabPFN은 표 데이터를 미리 학습한 Foundation 모델로, 작은 데이터에서도 빠른 비교 기준을 세우는 데 강점이 있어 새로운 표준으로 자리잡아 가고 있습니다. 이 리뷰는 OLED 분자 계산부터 공정, SCM, 검사, 설계 데이터까지 TabPFN을 효과적으로 적용하기 위한 고려사항을 논의합니다.`
- Verification:
  - Regenerated the HTML companion with `python scripts\markdown_to_html.py --mode final-review`.
  - Korean writing audit returned `finding_count: 0`, `h2_count: 14`, and `figure_count: 4`.
  - Confirmed the HTML cover renders the requested English title and revised Korean subtitle.
  - Confirmed the old Korean title and prior subtitle no longer appear in markdown or HTML.

## 2026-05-21 Calculation Metadata Table Revision

- Applied user feedback on the `계산값의 출처와 조건` section:
  - removed the Materials Project GGA/GGA+U and HT-DFT comparison paragraph from the body.
  - removed the related Materials Project and HT-DFT reference entries because the revised body no longer uses them.
  - replaced the broad three-bucket guidance table with a concrete OLED calculation metadata table showing how `calculation_protocol`, `geometry_source`, `conformer_policy`, `environment_model`, `state_interpretation`, and `review_status` appear as data values.
  - added a short discussion of how having or omitting those metadata/tacit-knowledge fields changes TabPFN-style tabular inference.
- Verification:
  - Regenerated the HTML companion with `python scripts\markdown_to_html.py --mode final-review`.
  - Korean writing audit returned `finding_count: 0`, `h2_count: 14`, and `figure_count: 4`.
  - Confirmed `Materials Project`, `GGA/GGA+U`, `HT-DFT`, and the removed inorganic-database comparison paragraph no longer appear in reader-facing markdown or HTML.
  - Confirmed the revised section contains the concrete OLED calculation metadata example rows and the ML inference impact discussion.

## 2026-05-21 ChemFM / MACE Foundation Model Context Addition

- Applied user feedback to connect the metadata/provenance discussion with broader foundation-model work in chemistry and atomistic modeling.
- Checked and added:
  - Communications Chemistry ChemFM paper: chemical foundation model, UniChem dataset selection, data diversity/informativeness, preprocessing from InChI to canonical SMILES and SMILES enumeration.
  - ACEsuit/mace-foundations GitHub repository: MACE pre-trained foundation models with training dataset, level of theory, target system, model size, and license listed in the model table.
- Added a concise paragraph explaining that these sources do not make TabPFN the same kind of model as ChemFM or MACE, but they show the broader move toward gathering, curating, documenting, and expanding data together with model capabilities.
- Added both sources to the direct references and the writing metadata.
- Verification:
  - Regenerated the HTML companion with `python scripts\markdown_to_html.py --mode final-review`.
  - Korean writing audit returned `finding_count: 0`, `h2_count: 14`, and `figure_count: 4`.
  - Confirmed ChemFM and MACE links render in markdown/HTML body and references.
  - Confirmed the removed Materials Project/GGA/HT-DFT references remain absent from reader-facing markdown and HTML.

## 2026-05-21 Final Structure / Humanize Pass

- Applied user feedback to remove the standalone `DFT/양자화학 역설계` section from the current review.
- Preserved the removed section in a follow-up note:
  - `notes/2026-05-21_tabpfn-qchem-inverse-design_followup.md`
  - includes the removed OLED inverse-design draft, reuse note for `tabpfn_inverse_design_filter.svg`, and follow-up review directions.
- Updated the main review:
  - removed the DFT/quantum-chemistry inverse-design body section and the corresponding SVG figure from the article body.
  - renumbered the remaining data-junction figure from Figure 4 to Figure 3.
  - revised the use-case table row from `분자 양자화학 기반 역설계` to `분자·계산 후보 선별`.
  - removed the now-unused `Deep-learning-based inverse design model...` reference from the main review.
  - updated `작성정보` with `최종 수정: 2026-05-21` and the DFT follow-up note link.
  - updated `figure_manifest.md` date and archived `tabpfn_inverse_design_filter.svg` for follow-up reuse.
- Humanized several remaining AI-cadence sentences:
  - replaced generic `분명합니다`, `이 차이는`, `이 흐름은`, `직접적인 힌트`, and repeated contrast-style phrasing with more concrete actor/action wording.
- Verification:
  - Regenerated the HTML companion with `python scripts\markdown_to_html.py --mode final-review`.
  - Korean writing audit returned `finding_count: 0`, `h2_count: 13`, and `figure_count: 3`.
  - The audit reported `figure_density: review-needed` because the article now has 3 figures after the DFT/OLED inverse-design figure was intentionally removed. This was accepted for the current scope because the remaining figures cover the article opening, TabPFN pretraining/context distinction, and the data-junction message.
  - Verified the removed DFT section heading, old Figure 4 numbering, inverse-design SVG reference, and unused inverse-design paper reference no longer appear in the reader-facing markdown/HTML.

## 2026-05-21 Figure 2 Redesign

- Applied user feedback that Figure 2 looked crowded and structurally weak.
- Rebuilt `artifacts/final_review/figures/tabpfn_pretraining_context_generalization.svg` as a new deterministic SVG:
  - expanded canvas to `1400x780`.
  - changed the layout to three clear stages: model development, released model, user-time inference.
  - kept the main correction that model pretraining belongs to the model-development stage.
  - simplified the user table and summarized the bottom area as model characteristics rather than `하는 일` / `하지 않는 일`.
  - removed the overly boxy old bottom layout and gave arrows more spacing.
- Revised the Figure 2 caption to be shorter and less repetitive.
- Updated `figure_manifest.md` with the redesign rationale.
- Verification:
  - Parsed the redesigned SVG as XML successfully.
  - Regenerated the HTML companion with `python scripts\markdown_to_html.py --mode final-review`.
  - Korean writing audit returned `finding_count: 0`, `h2_count: 13`, and `figure_count: 3`.
  - The audit still reports `figure_density: review-needed` because the article intentionally keeps 3 figures after the DFT/OLED inverse-design figure was moved to a follow-up note.
  - Fixed the audit's SVG readability warnings by increasing the smallest text size from 13px to 14px and splitting the long subtitle into two lines.
  - Render-checked the SVG with Playwright and saved `artifacts/final_review/figures/tabpfn_pretraining_context_generalization_preview.png`.
  - Visual check confirmed the redesigned Figure 2 has stable three-column spacing, no broken frame, and no extra empty table column.

## 2026-05-21 Figure 2 Positive Title / Characteristics Revision

- Applied user feedback on Figure 2 wording and structure:
  - changed the SVG title from a negative sentence to `TabPFN은 배포된 Foundation 모델로 새 행의 라벨을 예측합니다`;
  - removed the bottom `하는 일` / `하지 않는 일` split;
  - replaced it with `작동 특징`: `사전학습 prior`, `사용 시 context`, and `예측 출력`.
- Updated the Figure 2 caption so it explains fixed released weights and user-provided labeled rows as context without making the caption feel like a warning label.
- Verification:
  - Parsed the edited SVG as XML successfully.
  - Render-checked the SVG with Playwright and refreshed `artifacts/final_review/figures/tabpfn_pretraining_context_generalization_preview.png`.
  - Visual check confirmed the new positive title and characteristics row fit within the 1400x780 canvas.

## 2026-05-21 Metadata Feature / Intro Revision

- Checked the current Prior Labs documentation for TabPFN feature engineering, model capabilities, and quickstart usage.
- Revised the opening paragraph so the review starts from a research-team model comparison question:
  - organize data by candidate, condition, and label;
  - compare XGBoost, LightGBM, CatBoost, and TabPFN under the same split and metric.
- Clarified the metadata/protocol point in `계산값의 출처와 조건`:
  - TabPFN does not expose a separate metadata channel;
  - protocol, review status, lot, recipe, and inspection fields can be used when represented as feature columns in `X`;
  - low-cardinality strings can be passed as categorical features;
  - long free-text notes should be normalized into tags, summary features, vectorized features, or handled through API-native text features when appropriate.
  - included the prediction-time availability caution so protocol fields are not accidentally used as leakage.

## Unverified Items

- The two deep-research bodies said to be inside the ChatGPT share link were not visible in the public page state.
- No live Skywork deck generation was run in the original pass because the user requested report writing and specifically removed the prescriptive execution roadmap.
- No live Skywork Image generation was run in the 2026-05-10 revision because a callable Skywork Image tool was not available in this session; a ready-to-submit prompt pack was prepared instead.
- No OpenProject update was performed in this pass because no target work package was specified and the current instruction was scoped to report generation.
