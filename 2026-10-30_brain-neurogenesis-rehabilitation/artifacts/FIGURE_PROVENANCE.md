# Original explanatory figures

The three figure families were drawn for this review from source-defined data and independent geometry. No publisher figure, anatomy scan, patient image or external artwork was copied, traced or adapted. Each family has Korean and English desktop and mobile layouts. SVG text is outlined for consistent display; reading descriptions and captions remain in the article HTML.

## Evidence questions

`evidence_steps` uses four parallel cards: birth timing, proliferating lineage, molecular state, and circuit/functional contribution. The layout is not a hierarchy of assays and does not claim to record a cell lineage. `figure_data.json` preserves the source questions and method boundaries.

Source facts: Eriksson et al. (1998), DOI [10.1038/3305](https://doi.org/10.1038/3305); Spalding et al. (2013), DOI [10.1016/j.cell.2013.05.002](https://doi.org/10.1016/j.cell.2013.05.002); Dumitru et al. (2025), DOI [10.1126/science.adu9575](https://doi.org/10.1126/science.adu9575); Disouky et al. (2026), DOI [10.1038/s41586-026-10169-4](https://doi.org/10.1038/s41586-026-10169-4). A marker, molecular ordering or inferred expression direction is not treated as direct cell-birth dating, observed lineage or clinical recovery.

## Recovery mechanisms

`recovery_mechanisms` distinguishes new-neuron birth/integration, existing-circuit adjustment/relearning, and task/environmental compensation. These can operate together; neurogenesis is itself part of structural neuroplasticity. Nested location boxes indicate medial temporal lobe, hippocampal formation and dentate gyrus only. They are not an anatomical section, MRI or relative-size estimate. Circuit line thickness is a conceptual cue, not measured connectivity. The figure does not generalize dentate-gyrus findings to repair throughout an injured brain.

Source framework: human hippocampal studies above and the INCOG 2.0 memory guideline, DOI [10.1097/HTR.0000000000000837](https://doi.org/10.1097/HTR.0000000000000837).

## STEMTRA reported results

`stemtra_results` reads the attributed `stemtra_reported.json`. The bars show reported 24-week/6-month least-squares mean FMMS changes, not raw individual observations. A separate panel shows the reported between-group estimate and its 95% confidence interval; group standard errors are not drawn as confidence intervals. The sample flow, three pooled cell-dose groups, FMMS range/direction, secondary-outcome limit and serious-adverse-event reporting window are explicit.

Source: Kawabori et al., Neurology (2021), DOI [10.1212/WNL.0000000000011450](https://doi.org/10.1212/WNL.0000000000011450). Geometry is newly drawn from numerical facts. The 48-week post hoc follow-up is contextualized separately in the manuscript and data file; it is not plotted as the six-month result. No participant-level data were reanalysed.

## Reproducibility and rights

Run `build_figures.py` with `--font` and `--bold`. Matplotlib uses a fixed SVG identifier salt, no date metadata, original coordinates and outlined glyphs. The builder checks the 63-to-61 sample flow, 46+15 analysis denominator, mean difference and interval values before rendering. PNG previews and publication QA remain under ignored `tmp/`.

Nanum Gothic is used under SIL Open Font License 1.1. The complete font license is retained in `font-OFL.txt`; article font subsets are renamed Review Sans Subset. The article also embeds a renamed Noto Sans JP fallback subset for accented names, Japanese references and the minus sign, with the complete OFL in `fallback-font-OFL.txt`. Source: [Google Fonts Noto Sans JP](https://github.com/google/fonts/tree/main/ofl/notosansjp). The outlined figures do not require an installed source font. Source articles retain their own rights; the Neurology source's CC BY-NC-ND terms are not used as permission to adapt its artwork. This record does not add a blanket license to repository content. The site's rights and AI-use notice governs review-authored outputs.

The final twelve layouts were independently checked for scientific scope and labels, and inspected in original-size previews plus the article's desktop/mobile layouts. PDF pages are checked separately after final typesetting.
