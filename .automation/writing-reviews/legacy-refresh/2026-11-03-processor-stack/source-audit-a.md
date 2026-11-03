# 처리장치 스택: 독립 근거·서지 감수 A

대상은 2026-06-17 발행 원고 한 편이며, 당시 근거 범위와 2026-11-03 재확인 날짜를 구별한다. 본문과 원 작성 기록을 읽었고 새 모델·제품 동향으로 범위를 확장하지 않았다. 공개 원문·현재 공식 문서의 열람 판본과 정식 APS 문자열은 reference-a.json에 기록했다. 하드웨어 실험이나 제품 벤치마크는 재현하지 않았다.

## 읽은 범위

Jouppi 등의 arXiv:1704.04760v1 17쪽과 Hennessy–Patterson의 출판 PDF 13쪽을 전체 읽었다. TPU 데이터 재사용 도식과 도메인 특화 구조의 실제 렌더를 확인했다. ACM 발행 메타데이터는 Crossref와 출판사 검색 기록으로 대조했으며, Jouppi의 출판 PDF 12쪽을 직접 읽었다고 표시하지 않는다. Google TPU 구조·8t/8i 발표, NVIDIA 구조·GB200 튜닝 가이드, AWS Trainium 제품·출시 발표의 본문을 확인했다.

## 유지할 근거와 필요한 조정

- TPU의 systolic array는 정해진 흐름으로 데이터를 연산기 사이에서 재사용한다. 이 설명은 현재 제품 문서와 TPUv1의 실제 구조·명령·메모리 분석이 뒷받침한다. 2017년 성능 비율을 현재 모든 CPU/GPU의 우열로 옮기지 않는다.
- TPU 8t/8i 발표의 원제는 Inside the eighth-generation TPU: An architecture deep dive이며, 저자는 Diwakar Gupta와 Sabastian Mugazambi다. 공식 날짜는 2026-04-22이다. 두 시스템 모두 AI lifecycle을 지원하면서 8t는 학습·embedding, 8i는 post-training·sampling·serving의 병목을 우선한다. Native PyTorch는 이 자료에서 preview다.
- Blackwell FP4의 micro-tensor scaling과 GB200의 72-GPU NVLink domain은 2025-04-21 튜닝 가이드에 있다. 현재 제품 페이지의 Ultra·576-GPU 표현을 과거 글에 새로 넣지 않는다. 정밀도를 낮춰 얻는 효율은 모델·연산·정확도 조건과 함께 설명한다.
- Trainium3는 2025-12-02 공식 출시 발표로 원 발행일 이전 제공을 확인했다. 원고의 engine·HBM3e·W4A8·통신·Neuron SDK 설명은 현재 공식 제품 설명과 맞는다. 당시 HTML 사본이 없어 현재 페이지의 전체 상태를 6월 상태라고 보증하지 않는다.
- 그림7의 CPU→GPU→TPU/NPU→LPU/ASIC→QPU 상승 곡선에는 공통 workload·측정값이 없다. 도메인 특화 문헌도 이 제품들을 단일 효율 축으로 순위화하지 않는다. 전문화의 선택·제약을 설명하는 개념도로 정정하는 것이 필요하다.

## APS·원저자 크레딧

Jouppi 논문은 ISCA 2017, 1–12쪽, DOI10.1145/3079856.3080246의 정식 출판 서지에 연결한다. 확인한 PDF와 Crossref는 Daniel Killebrew를 포함한 76저자이며, 20명 초과인 APS 규정에 따라 N. P. Jouppi et al.로 표기한다. Hennessy–Patterson은 Commun. ACM 62, 48 (2019), DOI10.1145/3282307로 정리한다. 웹 문서는 실제 기관·원제·확인일을 기록하고, 날짜 있는 발표와 수시 갱신 문서를 나눈다. 임의 번역이나 검증 설명을 서지 문자열에 붙이지 않는다.

본문·캡션의 최종 인용순과 실제 배포물·렌더 검수는 총괄 단계에서 합친다. 이 감수 기록만으로 게시 완료를 표시하지 않는다.
