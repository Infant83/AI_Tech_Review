# Skywork Prompt Packet

## Deck Goal

Create a technically credible Korean AI Tech Review deck about why AI processors have diversified into CPU, GPU, TPU, NPU, LPU, DPU/IPU, QPU and adjacent strategies. The deck should help engineering, product, and strategy readers distinguish these processors by workload bottleneck rather than by hype.

## Audience

- AI/ML engineers
- product and platform teams evaluating AI hardware
- technical leadership reviewing AI infrastructure or on-device AI strategy

## Source Files

- `reports/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_final_review.md`
- `notes/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_sources.md`
- `artifacts/final_review/figure_manifest.md`

## Visual Assets To Use

- `artifacts/final_review/figures/imagegen/fig01_processor_stack_hero_v2-web.png`
- `artifacts/final_review/figures/svg/fig02_processor_workload_map.svg`
- `artifacts/final_review/figures/imagegen/fig03_memory_wall_imagegen-web.png`
- `artifacts/final_review/figures/remotion/fig04_processor_routing_remotion.png`
- `artifacts/final_review/figures/imagegen/fig05_edge_npu_imagegen-web.png`
- `artifacts/final_review/figures/imagegen/fig06_lpu_dataflow_imagegen-web.png`
- `artifacts/final_review/figures/svg/fig07_specialization_curve.svg`

## Suggested Structure

1. Title: AI 처리장치 스택: 왜 CPU, GPU, TPU, NPU, LPU가 나뉘는가
2. One-line thesis: 이름보다 병목으로 보라
3. Workload map: CPU/GPU/TPU/NPU/LPU/DPU/QPU role split
4. Why specialization happens: memory wall, precision, scheduling, interconnect
5. CPU/GPU/TPU comparison
6. NPU and on-device AI
7. LPU and inference-specific design
8. DPU/IPU and AI infrastructure offload
9. QPU and long-horizon research
10. Additional strategies: FPGA, cloud ASIC, wafer-scale, near-memory, photonic, neuromorphic
11. Limits: TOPS illusion, utilization, software lock-in, supply chain
12. Practical checklist and outlook

## Style

- Korean, friendly expert tone.
- White background, dark gray text, LG red accent.
- Use visuals as evidence aids, not decoration.
- Avoid hype claims and avoid treating LPU/QPU as equivalent maturity to GPU/TPU.
- Preserve source links in speaker notes or appendix.
