# AI 처리장치 스택 메모

- 작성일: 2026-06-17
- 대상: CPU, GPU, TPU, NPU, LPU, DPU/IPU, QPU와 추가 전략
- 본문 리뷰: `reports/2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu_final_review.md`

## 핵심 요약

AI 처리장치의 분화는 workload가 갈라진 결과입니다. CPU는 제어와 오케스트레이션, GPU는 대량 병렬 연산, TPU는 행렬 데이터플로와 클라우드 ML 스택, NPU는 엣지·온디바이스 저전력 추론, LPU는 언어모델 추론의 낮은 지연시간, DPU/IPU는 네트워크·스토리지·보안 오프로드, QPU는 양자 샘플링과 오류정정 연구 축을 맡습니다.

도입 판단에서는 먼저 우리 workload가 어디에서 멈추는지 봐야 합니다. compute, memory bandwidth, network fabric, tail latency, 전력, software stack 중 어느 항목이 비용을 만드는지에 따라 답이 달라집니다.

## 최근 동향

- Google TPU 8t/8i는 같은 TPU 세대 안에서도 pre-training용 8t와 serving/reasoning용 8i를 나눴습니다. 이는 학습과 추론의 병목이 달라졌다는 신호입니다.
- NVIDIA Blackwell은 GPU 자체와 함께 NVLink, NVLink Switch, FP4 Transformer Engine을 강조합니다. 대형 모델에서는 interconnect와 낮은 정밀도 활용이 핵심입니다.
- AWS Trainium3, Qualcomm AI200/AI250은 hyperscaler·inference 경제성을 겨냥한 custom ASIC/near-memory 전략을 보여줍니다.
- Microsoft Copilot+ PC와 Apple M4 Neural Engine은 NPU가 클라우드 대체재라기보다 로컬 추론, 개인정보, 배터리, 지연시간 문제를 다루는 장치임을 보여줍니다.
- Groq LPU는 벤더 정의가 강한 명칭입니다. 그래도 deterministic scheduling과 token latency가 새로운 추론 병목으로 부상했다는 점을 잘 드러냅니다.

## 도입 체크리스트

1. 모델 유형: training, fine-tuning, batch inference, real-time serving, edge inference 중 무엇인가.
2. 병목: compute, memory bandwidth, network, storage, tail latency, power 중 어디에서 막히는가.
3. 정밀도: FP16/BF16/FP8/FP4/INT8/W4A8 quantization을 허용할 수 있는가.
4. 소프트웨어: CUDA, XLA/JAX, Neuron SDK, ONNX Runtime, vendor NPU SDK 같은 실제 배포 경로가 있는가.
5. 운영: cooling, rack power, HBM supply, observability, security isolation, driver/runtime version을 감당할 수 있는가.

## 시각 자료

- Figure 1: imagegen hero, 전체 처리장치 생태계.
- Figure 2: SVG workload map, 이름이 아니라 병목으로 보는 역할 구분.
- Figure 3: imagegen memory wall, 데이터 이동 병목.
- Figure 4: Remotion still PNG, 정적 HTML에 삽입 가능한 라우팅 도식.
- Figure 5: imagegen edge NPU, 온디바이스 추론.
- Figure 6: imagegen LPU dataflow, token streaming.
- Figure 7: SVG specialization curve, 전문화의 장점과 비용.

## 결론

미래의 AI 컴퓨팅은 하나의 승자 칩으로 정리되기 힘듭니다. 모델과 서비스가 다양해질수록 CPU, GPU, TPU, NPU, LPU, DPU/IPU, QPU와 추가 전략이 서로 다른 시간 스케일과 데이터 경로를 맡게 됩니다. AI stack을 평가할 때는 약어의 수보다 데이터가 어디에서 멈추는지, 그 작업을 어느 처리장치로 보내야 하는지 먼저 봐야 합니다.
