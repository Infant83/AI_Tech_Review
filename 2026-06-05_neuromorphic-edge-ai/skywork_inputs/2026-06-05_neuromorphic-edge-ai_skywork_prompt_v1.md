---
title: "뉴로모픽 Edge AI Skywork prompt v1"
type: skywork-prompt
author: "김현중"
date created: 2026-06-05
date modified: 2026-06-05
status: draft
tags:
  - ai-tech-review
  - skywork
  - neuromorphic-computing
---

# Skywork Prompt v1 - 뉴로모픽 Edge AI

## Deck Goal

Create a Korean technical review deck based on the AI Tech Review Letters report `2026-06-05_neuromorphic-edge-ai_final_review.md`.

The deck should explain why neuromorphic computing is becoming relevant again in 2026 as physical AI and edge AI move from model demos to real-world sensor systems. Avoid overclaiming that neuromorphic chips will replace LLMs. The core thesis is:

> Neuromorphic computing is not a direct replacement for LLMs. Its near-term role is a low-power, low-latency perception and reflex layer for physical AI, especially sensor-adjacent workloads.

## Audience

- AI/AX strategy reviewers
- semiconductor/display/sensor R&D readers
- engineers evaluating edge AI and physical AI technology directions

## Suggested Slide Structure

1. Title: `뉴로모픽, 물리적 AI의 반응 시간을 줄이는 기술`
2. Why this topic now: LLM/agentic AI meets physical AI latency/power limits
3. Source paper: Wang et al. 2026 Nature Communications
4. How the device works: MoS2 optoelectronic LIF neuron + HZO/MoS2 ferroelectric synapse
5. What the 91.7% / 93.5% numbers mean and do not mean
6. In-sensor computing and AI-native robotic vision
7. 2025-2026 review consensus: commercialization begins at edge/wearable/IoT
8. Workload fit matrix: strong / hybrid / not yet
9. Industry signals: Intel Hala Point, IBM NorthPole, Innatera Pulsar, SynSense Speck, BrainChip radar
10. Quantum AI comparison: nearer commercial path but narrower workload
11. Implications for display/sensor/materials and manufacturing teams
12. Recommended next questions and pilot ideas

## Visual Requirements

- Use clean white/light background with restrained accent colors.
- Use deterministic diagrams from `artifacts/final_review/figures/` as reference:
  - `neuromorphic_edge_stack.svg`
  - `in_sensor_neuromorphic_vision.svg`
  - `neuromorphic_workload_fit.svg`
  - `neuromorphic_maturity_timeline.svg`
- Do not use generic glowing brain/network imagery.
- Korean text must be readable and technically precise.

## Key Source Links

- ScienceTimes: https://www.sciencetimes.co.kr/nscvrg/view/menu/250?nscvrgSn=261508&searchCategory=222
- Nature Communications target paper: https://www.nature.com/articles/s41467-026-68905-3
- Nature scale review: https://www.nature.com/articles/s41586-024-08253-8
- Nature Communications commercialization perspective: https://www.nature.com/articles/s41467-025-57352-1
- NeuroBench: https://www.nature.com/articles/s41467-025-56739-4
- AI-native robotic vision review: https://www.nature.com/articles/s44335-025-00047-z

