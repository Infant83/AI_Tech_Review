# 표지 일러스트 브리프

- 리뷰 제목: 머신러닝 포스필드: 원자 사이의 힘에서 물질의 성질까지
- 작성일: 2026-11-06
- 상태: 제작·과학·축소 검토 완료 · 한영 출판 패키지 반영
- 기획: root, mlff_cover_brief / 제작: root / 과학 검토: 별도 감수

## 전달할 사건

원자 주변의 배치를 배운 상호작용 모형이 에너지와 힘의 계산을 거쳐 원자들의 시간 변화를 예측하게 한다.

분야: 원자·분자 시뮬레이션 / 표현 유형: 배치와 에너지의 대응, 시간 변화 / 매체: 무광 광물·도자기 부조

결과의 실행 수준: 계산 방법의 개념 일러스트. 실제 계산 데이터·궤적이 아니다.

| 시각 요소 | 과학적 지시 대상 | 보존할 관계 | 허용할 추상화 | 피할 해석 |
|---|---|---|---|---|
| 분리된 구슬 무리 | 원자와 그 주변 배치 | 배치가 상호작용 모형의 입력임 | 특정 분자 아닌 추상 원자 이웃 | 허구의 화학 결합·구조 |
| 접힌 넓은 면 | 배치 공간의 퍼텐셜 에너지 | 실제 위치 공간과 구분 | 고차원 함수의 개념적 저차원 투영 | 원자가 지형을 굴러 내려감 |
| 달라진 이웃 배치 | 시간에 따른 좌표 변화 | 힘 평가와 적분의 결과 | 짧은 움직임 흔적 | 측정 궤적·항상 에너지 최소화 |

## 후보와 선택

| 안 | 장면·매체 | 관계와 오독 위험 |
|---|---|---|
| A 배치가 만드는 에너지 지형, 이어지는 움직임 | Matte mineral / ceramic relief with painterly edges and soft daylight; pale cool-grey ground, muted slate-violet, chalk white and one restrained coral accent. | Atomic configuration informs the learned interaction model; energy and force evaluation enables motion. A generated landscape can be mistaken for actual data or physical-space topography. Avoid axes, contour values, particles travelling on the surface and downhill arrows; disclose the conceptual mapping in the caption. |
| B 작은 환경들의 합창 | Dry-brush monotype and granular pigment on a light blue-grey ground; warm vermilion accents and deep charcoal. | Many local environments contribute to a system-level interaction description and collective motion. May imply all models use a strict sum of independent local energies, or confuse neighboring environments with fixed molecular bonds. The energy/force relation is less immediately visible than in A. |
| C 정지한 배치에서 시간의 띠로 | Translucent resin and softly brushed pigment, pale dawn-grey background, muted rust and aubergine. | A state evolves into the next under an interaction model; a trajectory is a sequence of configurations. Can imply an observed or calculated trajectory, equal time steps, or a particular film of atoms. Panel transparency and atom identity may become visually confusing. |

선택: A. A directly introduces the review's configuration–energy/force–motion relationship and reads as one sculptural event. It differs from the latest covers through broad mineral folds, cool light ground, an asymmetric continuous composition and unbonded atomic neighborhoods; it avoids the recently repeated cream paper, branching, glass twin-plate and loom metaphors.

최근 네 표지와의 실제 비교(2026-11-06 공개 목록 기준):
- 2026-11-04_quantum-gates-phase-and-interaction (발행 11월 5일): 짙은 남색·금색 종이 구조가 모이는 구성.
- 2026-11-02_chiral-amplification-nobel-chemistry: 청록 바탕과 테라코타 손의 만드는 동작.
- 2026-11-01_ai-science-automation-and-expertise: 어두운 바탕의 프리즘과 분산된 스펙트럼.
- 2026-10-30_brain-neurogenesis-rehabilitation: 크림색 바탕과 조밀한 청록 신경 부조.

새 표지는 밝고 차가운 회색 바탕, 보라색 광물 부조와 낮고 넓은 윤곽, 양쪽 산호색 원자 무리를 사용한다. 촉감 있는3D라는 매체는 일부 반복되지만 구도·색·비유는 구별된다. 큰 봉우리와 골이 첫 초점을 만들고, 양쪽 원자 무리와 오른쪽 움직임 흔적이 배치 변화의 관계를 보완한다. 이는 실제 시안을 본 편집 판단이며 독자 실험 결과가 아니다.

정확한 의미는 본문에서 검산한 LJ 에너지·힘 그림과 두 입자의 MD 에너지 그림으로 설명한다. 표지의 지형에는 수치·힘 벡터·실제 궤적을 넣지 않는다.

## 제작과 검토 기록

- 생성 도구: 내장 image_gen, imagegen 스킬. 정확한 이미지 모델 ID는 반환 시 확인 가능 범위만 기록한다.
- 프롬프트 전문: `artifacts/hero-prompt.txt`
- 최종 자산: `artifacts/hero.webp`, 1600×900 · PNG 원본의 최종 WebP 변환본
- 과학 검토: 원자 무리는 지형 위를 굴러가지 않고 특정 분자의 결합으로 표시되지 않았다. 320×180과 흑백에서 두 무리·지형이 식별된다. 실제 1:1·4:3 크롭은 양쪽 원자 무리를 자르므로 사용하지 않는다. PDF·모바일에서 원본 16:9 비율을 보존한다. 이전 네 기사 제목보다 원자 상호작용 주제와 직접 연결된다. 기존 Chrome 390 px 검토에서 348×195.75 px로, 이번 한영 출판 레이아웃에서는 390 px 화면에서 390×219 px로 전체 비율과 가로 넘침 없음을 확인했다.
- 공개 배포 상태: 한영 HTML·PDF 출판 패키지; 배포는 사이트 게시 절차에서 확인

## 공개 문구

- 한국어 캡션: 원자 주변의 배치, 굽이진 에너지 지형, 달라지는 배치를 이어 놓아 학습한 상호작용 모형이 원자의 운동 계산으로 이어지는 관계를 나타냈다. 지형은 배치에 따른 퍼텐셜 에너지의 비유이며 실제 공간·분자 구조·계산 궤적이 아니다. AI 생성 개념 일러스트.
- English caption: Atomic neighborhoods, a sculpted energy landscape and changing arrangements evoke how a learned interaction model enables calculations of atomic motion. The landscape is a metaphor for potential energy over configurations, not physical topography, a molecular structure or a calculated trajectory. AI-generated conceptual illustration.
- 한국어 대체 텍스트: 밝은 회색 바탕에서 작은 원자 모형 무리와 굽이진 보라색 지형이 이어지고, 오른쪽의 조금 달라진 원자 배치에 짧은 움직임 흔적이 보인다.
- English alt text: Small atom-like groups flank a folded violet-grey landscape on a light grey ground; the slightly changed group at the right has a few short motion marks.
