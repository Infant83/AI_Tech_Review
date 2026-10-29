# Original explanatory figures

The four figure families were drawn for this review from source-defined data and independent geometry. No publisher figure, anatomy scan, patient image or external artwork was copied, traced or adapted. Each family has Korean and English desktop and mobile layouts. SVG text is outlined for consistent display; reading descriptions and captions remain in the article HTML.

## Evidence questions

`evidence_steps` uses four parallel cards: birth timing, proliferating lineage, molecular state, and circuit/functional contribution. The layout is not a hierarchy of assays and does not claim to record a cell lineage. `figure_data.json` preserves the source questions and method boundaries.

Source facts: Eriksson et al. (1998), DOI [10.1038/3305](https://doi.org/10.1038/3305); Spalding et al. (2013), DOI [10.1016/j.cell.2013.05.002](https://doi.org/10.1016/j.cell.2013.05.002); Dumitru et al. (2025), DOI [10.1126/science.adu9575](https://doi.org/10.1126/science.adu9575); Disouky et al. (2026), DOI [10.1038/s41586-026-10169-4](https://doi.org/10.1038/s41586-026-10169-4). A marker, molecular ordering or inferred expression direction is not treated as direct cell-birth dating, observed lineage or clinical recovery.

## Recovery mechanisms

`recovery_mechanisms` distinguishes new-neuron birth/integration, existing-circuit adjustment/relearning, and task/environmental compensation. These can operate together; neurogenesis is itself part of structural neuroplasticity. Nested location boxes indicate medial temporal lobe, hippocampal formation and dentate gyrus only. They are not an anatomical section, MRI or relative-size estimate. Circuit line thickness is a conceptual cue, not measured connectivity. The figure does not generalize dentate-gyrus findings to repair throughout an injured brain.

Source framework: human hippocampal studies above and the INCOG 2.0 memory guideline, DOI [10.1097/HTR.0000000000000837](https://doi.org/10.1097/HTR.0000000000000837).

## STEMTRA reported results

`stemtra_results` reads the attributed `stemtra_reported.json`. The bars show reported 24-week/6-month least-squares mean FMMS changes, not raw individual observations. A separate panel shows the reported between-group estimate and its 95% confidence interval; group standard errors are not drawn as confidence intervals. The sample flow, three pooled cell-dose groups, FMMS range/direction, secondary-outcome limit and serious-adverse-event reporting window are explicit.

Source: Kawabori et al., Neurology (2021), DOI [10.1212/WNL.0000000000011450](https://doi.org/10.1212/WNL.0000000000011450). Geometry is newly drawn from numerical facts. The 48-week post hoc follow-up is contextualized separately in the manuscript and data file; it is not plotted as the six-month result. No participant-level data were reanalysed.

## AI and quantum research roles

`research_roles` places four roles in parallel panels, with separate species, populations and validation targets. It does not depict one combined experiment or a causal treatment pipeline. The final bar is a question for future clinical testing under matched rehabilitation conditions, not an observed outcome. No numerical efficacy axis, model-performance comparison or cross-panel arrow is drawn.

- Molecular AI: expression/projection classification for grafted human neurons in mouse ischemic cortex, and the design of injury-responsive expression switches in separate mouse injury models. Wang et al. (2026), DOI [10.1016/j.stem.2025.12.008](https://doi.org/10.1016/j.stem.2025.12.008); Zamboni et al. (2026), DOI [10.1038/s41593-025-02131-w](https://doi.org/10.1038/s41593-025-02131-w). Wang's final abstract and institutional report were read along with detailed public preprint methods, rather than the blocked final full text. Zamboni's final full text was checked. Reporter targeting, graft projection and human functional recovery remain distinct endpoints; no code was rerun.
- Network AI and individual brain models: observed stroke prognosis and individualized circuit dynamics. Bonkhoff et al. (2021), DOI [10.1093/braincomms/fcab227](https://doi.org/10.1093/braincomms/fcab227); Falcon et al. (2016), DOI [10.1523/ENEURO.0158-15.2016](https://doi.org/10.1523/ENEURO.0158-15.2016). TVB's biophysical modelling is not relabeled as machine learning. Neither selected study establishes efficacy of a model-chosen treatment.
- Quantum sensing: atomic-spin OPM sensing of magnetic fields associated with brain activity, with a healthy-participant stepping study. Spedden et al. (2025), DOI [10.3390/s25134160](https://doi.org/10.3390/s25134160); device mechanism supported by Borna et al. (2023), DOI [10.3389/fnins.2023.1190310](https://doi.org/10.3389/fnins.2023.1190310). This is sensing during controlled steps, not a QPU calculation, cell-birth assay or patient rehabilitation trial.
- QPU computing: proposed hybrid molecular calculations in the official [CLARA programme](https://www.clara-center.eu/research/research-programs/RP1) and [quantum-testbed task](https://www.clara-center.eu/infrastructure/CLARA-testbed/leveraging-quantum-computing-acceleration). These plans concern molecular research, not a demonstrated clinical regeneration endpoint or a measured quantum advantage.

The four new SVGs are `research_roles_ko.svg`, `research_roles_en.svg`, `research_roles_mobile_ko.svg` and `research_roles_mobile_en.svg`. Their original geometry follows the existing review palette and typography. Source-defined labels and scientific boundaries are stored in `figure_data.json`. No licensed source diagram or institutional logo was reused.

## Reproducibility and rights

Run `build_figures.py` with `--font` and `--bold`; add `--figure research_roles` to render only the four new variants while preserving earlier SVG files. Matplotlib uses a fixed SVG identifier salt, no date metadata, original coordinates and outlined glyphs. The builder checks the 63-to-61 sample flow, 46+15 analysis denominator, mean difference and interval values before rendering. PNG previews and publication QA remain under ignored `tmp/`.

Nanum Gothic is used under SIL Open Font License 1.1. The complete font license is retained in `font-OFL.txt`; article font subsets are renamed Review Sans Subset. The article also embeds a renamed Noto Sans JP fallback subset for accented names, Japanese references and the minus sign, with the complete OFL in `fallback-font-OFL.txt`. Source: [Google Fonts Noto Sans JP](https://github.com/google/fonts/tree/main/ofl/notosansjp). A minimal Noto Sans Latin fallback preserves additional reference-name characters such as ş; its complete OFL is retained in `latin-font-OFL.txt` and the derivative is renamed Review Sans Latin Fallback. Source: [Google Fonts Noto Sans](https://github.com/google/fonts/tree/main/ofl/notosans). The outlined figures do not require an installed source font. Source articles retain their own rights; the Neurology source's CC BY-NC-ND terms are not used as permission to adapt its artwork. This record does not add a blanket license to repository content. The site's rights and AI-use notice governs review-authored outputs.

The original twelve layouts were independently checked for scientific scope and labels, and inspected in original-size previews plus the article's desktop/mobile layouts. The four new research-role layouts passed original-size and 390px Chrome preview checks; root independently checked their scientific relationships, species/population boundaries and labels. A scratch rebuild produced byte-identical SVGs while the original twelve SVGs and cover stayed unchanged. Expanded article and complete PDF output are checked after manuscript typesetting.
