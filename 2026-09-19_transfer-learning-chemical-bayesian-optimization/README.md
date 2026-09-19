# Chemical Bayesian optimization and transfer learning

Review date: 2026-09-19. Korean canonical with an English translation.

This is a methods explainer and public-code review prompted by Thijs Stuyver's announcement of *Robust Transfer Learning for Bayesian Optimization of Chemical Reactions* in Digital Discovery, DOI [10.1039/D6DD00527F](https://doi.org/10.1039/D6DD00527F).

## Evidence and limits

| Claim | Checked source | Scope |
|---|---|---|
| Publication and authors | Author's LinkedIn post; Crossref publisher DOI record | Journal article exists. Precise online date not inferred from DOI creation time. |
| Positive and negative transfer, two-phase protocol | Complete abstract registered for preprint v2, DOI 10.26434/chemrxiv.15006440/v2 | Qualitative author claims; journal full-text changes unverified. |
| Dimension-aware GP prior and earlier study | ACS publisher-hosted Figshare abstract; Crossref DOI 10.1021/acs.jctc.6c00251 | Earlier paper published online 2026-05-15, JCTC 22(11), 5594–5608. |
| Prior formulas and implementation settings | TL-ChemBO commit a35276cdbf8b8c6dde4d71c224b918e04ddf52c2 | Read-only code inspection and limited construction probes. |
| A+B task labels at start of C | `transfer_loop.py`, same commit | Probe confirms both historical A and initial target B are assigned training. No assertion about final journal intent. |
| Thirty iterations, batch one, P 5/10/15 | `transfer_loop.py` and `run.sh`, same commit | Settings, not reported gains or universal choices. |
| Existing experimental table lookup | `base/benchmarking.py`, `base/transfer_utils.py` | Retrospective simulation; no full campaign independently run. |
| OLED application and future switching rules | Review analysis | Proposals; no OLED results claimed. |

The final journal full text and supplement could not be inspected because of access restrictions. Figure-level gains, uncertainty intervals, precise stress-test outcomes and changes from the preprint remain unverified. Performance plots and gain percentages are deliberately absent. The transfer tutorial repository was empty at inspection and was not used as evidence.

## Rebuild

Run `python build.py` from this directory. It uses standard Python and the checked-in web illustration to assemble `dist/` and deterministic explanatory SVGs. Publish from the repository root with:

```sh
python scripts/publish_public_site.py --review 2026-09-19_transfer-learning-chemical-bayesian-optimization
```

`verify_source.py` accepts the path to a checkout of the pinned TL-ChemBO commit. It requires pandas. It extracts the inspected functions using Python's AST, substitutes minimal dependencies, checks task labels and prior construction, and fits no GP. It does not reproduce benchmark performance.

## Public assets

Only the final bilingual HTML, WebP hero and language-specific SVGs are referenced by the pages and copied to the public review directory. No downloaded paper, private conversation, raw browsing capture or source API response is distributed.

Responsible editor: Hyun-Jung Kim. AI assistance: one Codex agent. Exact model identifier not retained. Human publication authorization is not represented as a line-by-line review. Editorial Harness 2026.08 and scientific-stop-slop-ko publication copyediting applied.

Copyediting audit: repetitive emphasis and unsupported performance language removed; prior formulas, task labels, iteration counts and scope retained; final journal performance and supplementary details remain unverified.
