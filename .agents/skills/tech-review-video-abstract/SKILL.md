---
name: tech-review-video-abstract
description: Create or revise optional, source-grounded scientific video abstracts, focused video reviews and moving illustrations for AI Tech Review using deterministic local rendering. Use for an explicit video request, a publication requirement, or a scientific review whose process or comparison benefits from motion. Lecture notes and ordinary reviews do not acquire a video by default. Excludes generative video API production and unrelated promotional videos.
---

# Tech Review Video Abstract

Work in the intended Tech Review checkout. Locate its `EDITORIAL_POLICY.md`, `EDITORIAL_METHOD.md`, `SCIENTIFIC_EXPLANATION_DIRECTION.md`, `COVER_ART_DIRECTION.md`, `VIDEO_ABSTRACT_DIRECTION.md` and `templates/video-abstract-brief.md`; read them before production. If the current directory is another project, locate the intended checkout from available context instead of creating Tech Review policy files there.

## Make the scientific scope explicit

Honor an explicit request or publication requirement. Otherwise decide whether a changing quantity, ordered process or staged comparison improves understanding and record the reason. Lecture notes, lists and short news normally omit video. A section-level explainer must not be presented as an abstract of the entire article.

For an article abstract, read the article and preserve its central argument, evidence and significance. A representative example can carry the explanation, but say how it supports the article's message. Do not solve narrative problems by silently replacing the requested abstract with a narrow tutorial. Not every article section needs screen time.

Create `video-abstract-brief.md` in the topic folder. Map each scene to a claim, source location or validated data, units and conditions, execution level, meaningful motion and a likely misreading. Keep paper-reported results, review calculations and conceptual analogies distinct. Preserve caveats in the video itself, not only in the article.

Reuse scientific code or data already checked for the article when available. Verify equations, numbers, denominators, directions, counts, connections and intermediate states before polishing transitions. Explain screen time versus physical time or calculation steps. Morphing between endpoints must not invent a physical path or intermediate scientific structure.

## Select a small rendering stack

Use deterministic code-driven frames and local encoding. Do not use generative video APIs in this workflow unless the user separately explicitly requests that production method. Start with the repository's existing renderer or a focused Pillow/SVG/Canvas + FFmpeg implementation. Use Remotion for repeated timeline/layout/caption work when its installation and license fit; consult current official docs and skills before introducing it. Choose Manim for mathematical scenes or PyVista/Blender/Three.js for needed scientific 3D rather than adding every engine.

The reference implementation is `2026-10-21_video-abstract-pilot/v4/`. Inspect its actual README and render scripts before reuse. Its oscillator content is an example, not a universal storyline. Reuse shared mechanics only when they fit the next scientific topic. Supply runtime/font paths through arguments or environment variables; keep downloaded dependencies and temporary frames outside public assets.

## Produce a reviewable package

Write the continuous explanation before dividing it into timed scenes. Follow the writing guidance in the repository's `EDITORIAL_METHOD.md` §3: define what the viewer should understand, make each transition necessary to that argument, and introduce terms or equations after their physical meaning. Depth does not require adding more applications. Keep one model and comparison legible; separate branches that need their own argument. Have a separate reader summarize the script's claim, reasoning, evidence and limits without the planning notes. Revise actual gaps before rendering. A technical QA pass does not establish narrative clarity. For a writing-only revision, deliver the revised script and plan without implying an older MP4 contains the new text.

Map each scientifically important visual to the words that explain what it shows, what the result means, and how it connects to the article's argument. Describe and interpret key curves, comparisons and quantities in the spoken script, or in the on-screen explanation for a silent video. Do not rely on a visual to explain itself while the explanation moves elsewhere. Decorative details need not be read aloud. After rendering, compare actual frames with speech or silent explanation as well as reading the script alone. Keep interpretations within the evidence's scope.

Plan the order of attention, not just which figures share a scene. Anchor meaningful reveal, change, emphasis and hold events to actual spoken phrases with stable semantic identifiers; recalculate language-specific times after synthesis. For silent videos, anchor events to the corresponding on-screen explanation and reading phases instead; narration remains optional. Preserve the result through its interpretation and carry a relevant object, result or question into the next scene. Avoid showing every new diagram at full strength from the start, while keeping simultaneous changes when they explain a relationship. Do not assume a scheduler exists: implement the plan in the chosen renderer and verify it after edits.

Use disciplinary names, symbols and units, connecting each essential first-use term to a concrete object or operation. Show how a physical state maps to a plotted point or normalized quantity; distinguish canonical momentum from velocity and computational steps from physical paths. Read the shared explanation guide for the article-prose equivalent. Check first appearance, change, result hold and actual scene transition in the output; distinguish still-frame inspection from continuous playback and listening. A guidance-only update must not be reported as a new MP4.

For a full abstract, aim for a short question, the central mechanism, one supported result and its limit, usually 45–75 seconds. Adapt length and sequence to the subject. Prioritize meaningful changing diagrams over moving text. Give each language its own readable labels and captions, allowing timing changes for translation.

When the user asks for scientific depth, a focused 2–3 minute visual review can give the central reasoning room. Select the assumptions, mechanisms, examples or counterexamples that the argument needs; do not force every module into the script. Stage equations in response to the viewer's current question. Write natural Korean first when it is canonical; preserve claims and conditions in idiomatic English without requiring sentence-by-sentence translation.

Image generation may create original conceptual still artwork, materials, lighting and settings. Read the available imagegen skill and record prompts, captions and scope. Composite these assets with deterministic scientific overlays; exact trajectories, geometry, forces, equations and measurements remain code-generated. A camera move over a still does not replace the scientific explanation. Never continue an old model's motion after changing its parameters unless the new dynamics have actually been computed.

Narration can carry context while short on-screen phrases direct attention. Local synthesis is an option; disclose synthetic speech and record engine, weights/preset and output-use terms. Local availability does not imply public redistribution rights: the v2 pilot replaced macOS system voices with licensed Supertonic 2 output after checking the applicable terms. For narrated videos, derive scene timing from actual speech, provide speech captions, and verify actual audio duration and clipping. Record exactly what was listened to, rather than calling automated checks a full listening review. Silent videos use on-screen explanation and reading time instead. Allow Korean/English durations to differ and provide a transcript describing the important visuals in either format.

Deliver an MP4, poster, timed captions, a transcript that describes essential visual information, source/production manifest and reproducible render source. Narration is optional; silent videos still need a transcript. A short GIF is an optional preview, not the master. Preserve static covers unless a cover change is actually needed and authorized.

Verify numerical invariants independently from animation code, decode the actual MP4, inspect representative and transition frames, and check readability at desktop and mobile sizes. Check axes, logarithmic/normalized scales, labels, captions, seek/play/pause/replay and a reduced-motion static fallback. Record checks actually performed and human review actually received.

For mathematical typography, check the actual rendered exponents, indices, signs and derivatives. A Korean-capable font may omit mathematical glyphs, and a math font may omit some Unicode script characters. Use suitable math typesetting or verified font fallback rather than allowing missing glyphs or silently dropping scientific notation. If a scientific condition changes during a narrated scene, align that change with the corresponding spoken cue.

## Integrate within the user's scope

For a planning/prototype request, deliver the local player and proposal without registering or deploying it. For authorized publication, implement the publisher's explicit named asset allowlist and `poster`/caption handling as needed, sanitize VTT as text, and inspect binary metadata and licenses. Copy only approved final assets, never the entire topic folder.

Web players have controls, inline playback, a poster and restrained preloading; avoid default autoplay or looping. Include transcript and download links. PDF uses a still, explanation and stable web link. Check Korean/English pages, metadata, thumbnail, PDF and archive copies when applicable. Do not claim a local prototype is live or production integration is complete.

Report the useful artifact first, with its scope, rendering method, verified results, remaining limitations and whether it was published. Distinguish zero additional video-generation API calls from agent usage, local compute, software licensing and hosting costs.
