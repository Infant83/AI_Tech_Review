# AI 처리장치 스택 소스 노트

- 작성일: 2026-06-17
- 범위: CPU, GPU, TPU, NPU, LPU, DPU/IPU, QPU와 추가 전략(FPGA/adaptive compute, ASIC, wafer-scale, compute-in-memory, photonic interconnect, analog/near-memory)
- 리뷰 초점: 이름별 제품 비교가 아니라 병렬성, 데이터 이동, 정밀도, 지연시간, 전력, 소프트웨어 스택이 어떻게 역할 분화를 만드는지 정리

## 핵심 판단

1. 처리장치의 분화는 “연산량 증가”만으로 설명되지 않는다. 더 큰 병목은 메모리 이동, 통신, 낮은 정밀도 활용, tail latency, 소프트웨어 스케줄링이다.
2. CPU, GPU, TPU, NPU, LPU는 선형 계층이 아니라 병목별 도구다. CPU는 제어와 오케스트레이션, GPU는 높은 범용 병렬 처리, TPU는 행렬 데이터플로와 클라우드 ML 스택, NPU는 엣지 전력 효율, LPU는 언어모델 추론 지연시간 최적화라는 식으로 나뉜다.
3. DPU/IPU는 모델 연산기가 아니라 AI 데이터센터의 네트워크·스토리지·보안 병목을 다루는 인프라 가속기다.
4. QPU는 현재 일반 AI 가속기가 아니다. 양자 오류정정, 샘플링, 물질/최적화 연구 영역에서 의미가 있지만, 실무 AI 추론·학습 스택과는 성숙도가 다르다.

## 원리·아키텍처 근거

- Hennessy & Patterson, "A New Golden Age for Computer Architecture": Moore/Dennard 이후 범용 성능 향상 둔화와 도메인 특화 아키텍처의 부상 논의.  
  https://www.doc.ic.ac.uk/~wl/teachlocal/arch/papers/cacm19golden-age.pdf
- Jouppi et al., "In-Datacenter Performance Analysis of a Tensor Processing Unit": TPU를 데이터센터 추론용 도메인 특화 아키텍처로 분석한 초기 핵심 논문.  
  https://arxiv.org/abs/1704.04760
- Google Cloud TPU architecture 문서: TPU의 matrix processing, systolic array, MXU, vector/scalar unit 구조 설명.  
  https://docs.cloud.google.com/tpu/docs/system-architecture-tpu-vm
- Intel AMX 설명: CPU 내부에 행렬 연산 가속 블록을 붙여 BF16/INT8 기반 AI workload를 CPU에서 처리하는 접근.  
  https://www.intel.com/content/www/us/en/products/docs/accelerator-engines/what-is-intel-amx.html
- Arm SME/SME2: Arm CPU ISA에 matrix-heavy AI/ML workload 가속 기능을 넣는 전략.  
  https://newsroom.arm.com/blog/scalable-matrix-extension  
  https://www.arm.com/technologies/sme2

## 2025-2026 주요 동향

- Google TPU 8t/8i: 2026-04-23 Google Cloud 발표. TPU 8t는 대규모 pre-training, TPU 8i는 sampling/serving/reasoning에 맞춘 분화가 핵심. FP4, SparseCore, CAE, Boardfly topology, Arm Axion host 병목 완화가 강조됨.  
  https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive
- NVIDIA Blackwell/NVL72: fifth-generation NVLink로 72-GPU domain과 대규모 모델 통신 병목을 줄이는 방향. Blackwell Transformer Engine은 FP4를 포함한 낮은 정밀도 활용을 강조.  
  https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/  
  https://docs.nvidia.com/multi-node-nvlink-systems/multi-node-tuning-guide/overview.html
- AMD Instinct MI350: 최신 GPU/accelerator 경쟁 축.  
  https://www.amd.com/en/products/accelerators/instinct/mi350.html
- AWS Trainium3: NeuronCore, HBM3e, W4A8 quantization, collective cores, Neuron SDK를 전면에 둔 클라우드 AI ASIC 전략.  
  https://aws.amazon.com/ai/machine-learning/trainium/
- Qualcomm AI200/AI250: 2025-10-28 발표. 데이터센터 inference 전용 rack-scale accelerator, LPDDR memory capacity, near-memory compute, disaggregated serving을 강조.  
  https://www.qualcomm.com/news/releases/2025/10/qualcomm-unveils-ai200-and-ai250-redefining-rack-scale-data-cent

## 엣지·NPU 근거

- Microsoft Copilot+ PCs developer guide: 여러 Windows AI 기능이 40+ TOPS NPU를 요구하고, Windows가 CPU/GPU/NPU에 작업을 배정한다는 설명.  
  https://learn.microsoft.com/en-us/windows/ai/npu-devices/
- Microsoft Copilot+ PCs business page: Copilot+ PC의 40+ TOPS NPU 요구와 CPU/GPU 대비 AI-specific workload 효율 강조.  
  https://www.microsoft.com/en-us/windows/business/devices/copilot-plus-pcs
- Apple M4 발표: Neural Engine 38 TOPS를 명시한 온디바이스 NPU 사례.  
  https://www.apple.com/newsroom/2024/05/apple-introduces-m4-chip/

## LPU·추론 전용 근거

- Groq LPU explanation: deterministic execution, resource contention 제거, software-controlled scheduling을 강조.  
  https://groq.com/blog/the-groq-lpu-explained
- Groq LPU architecture: SRAM을 primary weight storage로 두고, static scheduling, direct chip-to-chip connectivity를 강조.  
  https://groq.com/lpu-architecture
- 주의: LPU는 CPU/GPU처럼 표준화된 범용 범주라기보다 Groq가 강하게 밀고 있는 벤더 정의에 가깝다. 본문에서는 “언어 추론 전용 데이터플로 설계의 대표 사례”로 다룬다.

## DPU/IPU·인프라 근거

- NVIDIA BlueField: BlueField-3 DPU는 software-defined networking, storage, cybersecurity의 line-rate processing을 담당하고, BlueField-4는 800Gb/s infrastructure platform으로 설명됨.  
  https://www.nvidia.com/en-us/networking/products/data-processing-unit/
- AMD Pensando: DPU/SmartNIC 계열 인프라 오프로드 전략의 비교 대상으로 언급 가능.  
  https://www.amd.com/en/products/accelerators/pensando.html

## QPU·양자 근거

- Google Willow: 105 qubits, quantum error correction 진전, useful beyond-classical computation이 다음 과제라고 명시.  
  https://blog.google/innovation-and-ai/technology/research/google-willow-quantum-chip/
- IBM Quantum roadmap: fault-tolerant quantum computing으로 가는 장기 로드맵 참고.  
  https://www.ibm.com/quantum/blog/quantum-roadmap-2033
- D-Wave systems: annealing quantum computer 계열의 상용 특수목적 접근.  
  https://www.dwavequantum.com/solutions-and-products/systems/

## 추가 전략

- Cerebras WSE-3: wafer-scale로 온칩 메모리와 대규모 AI cores를 묶어 memory bandwidth 병목을 다르게 푸는 전략.  
  https://www.cerebras.ai/chip
- AMD Versal AI Engine: FPGA/adaptive SoC 안의 VLIW/SIMD tile, DSP와 ML inference를 동시에 겨냥하는 재구성 가능 전략.  
  https://www.amd.com/en/products/adaptive-socs-and-fpgas/technologies/ai-engine.html
- Lightmatter Passage/photonic interconnect: AI supercomputer scale에서 전기적 interconnect 한계를 optical interconnect로 줄이려는 전략.  
  https://lightmatter.co/
- Intel Loihi 2 / neuromorphic computing: sparse event-driven computation, spiking neural networks, integrated memory and computing을 활용하는 연구 축. 주류 LLM 학습/추론 대체재라기보다는 센서·로보틱스·저전력 이벤트 처리의 장기 옵션으로 분류.  
  https://www.intel.com/content/www/us/en/research/neuromorphic-computing.html

## 시각 자료 계획

- Figure 1: imagegen hero, 다른 AI Tech Review 시리즈와 같은 흰 배경·회색 라인·LG red accent 톤.
- Figure 2: SVG workload map, 이름보다 병목으로 구분하는 역할 지도.
- Figure 3: imagegen memory wall, 데이터 이동 병목.
- Figure 4: Remotion still PNG, CPU가 각 가속기로 작업을 라우팅하는 정적 페이지 삽입 가능 산출물.
- Figure 5: imagegen edge NPU, 엣지/온디바이스 추론.
- Figure 6: imagegen LPU dataflow, 언어 추론 전용 저지연 데이터플로.
- Figure 8: SVG specialization curve, 전문화의 원리와 비용.
