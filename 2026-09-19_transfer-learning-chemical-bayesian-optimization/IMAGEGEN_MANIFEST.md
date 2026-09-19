# Illustration and figure provenance

## Hero

- File: `artifacts/transfer_hero.webp`
- Tool: OpenAI built-in imagegen; exact image model identifier not retained.
- Generation date: 2026-09-19.
- Dimensions: 1672 × 941, approximately 16:9.
- Concept: information from historical chemistry experiments guiding exploration of new chemical options.
- Prompt: “16:9 editorial hero illustration for a scientific review about transfer learning in Bayesian optimization of chemical reactions, using past experimental campaigns to guide new chemical options while allowing new data to correct misleading prior experience. Sophisticated scientific magazine illustration, tactile translucent glass chemistry micro-well plates on a warm ivory laboratory tabletop, an older teal plate softly in the background and a fresh amber-and-teal plate prominent in foreground, a few fine flowing threads of light connecting selected wells across the plates, some threads gently separating as the new plate establishes its own pattern. Restrained graphite, deep teal, warm amber palette, quiet side lighting, subtle paper-like texture, clear composition at thumbnail size. Visual metaphor only; not an actual apparatus or measured results. No text, numbers, logos, labels, axes, equations, graphs, brains, robots, generic circuit boards, or arrows.”
- Processing: RGB WebP encoding at quality 88; no compositional editing. EXIF empty in source; no EXIF or private metadata passed to output.
- Inspection: original generated image visually inspected; no text, numerical claims or purported experimental apparatus identification.
- Public caption states conceptual origin and absence of measured results.

## Explanatory SVGs

- `prior_scale_ko.svg` and `prior_scale_en.svg`: original computation of μℓ = 0.4√d + 4 for illustrative d = 32, 128, 512, 2048. Values approximately 6.263, 8.525, 13.051, 22.102. Not dataset dimensions or performance data.
- `two_phase_ko.svg` and `two_phase_en.svg`: original code-flow reconstruction, including A+B training labels at the start of C. No benchmark result or automatic switching claim.
- Source: TL-ChemBO commit a35276cdbf8b8c6dde4d71c224b918e04ddf52c2, `base/kernels.py` and `transfer_loop.py`.
- The source paper's figures are not reproduced. `build.py` regenerates both sets of SVGs.
