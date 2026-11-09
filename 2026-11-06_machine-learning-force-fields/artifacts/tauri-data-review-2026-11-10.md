# Tauri 개정 원고 데이터와 판본 독립 검토

2026-11-10 · 검토: Codex `tauri_data_update`

## 판단

필수 수정 사항 없음. 한영 작성 원본 `article-ko.json`·`article-en.json`의 §6, §9 적용 기록, 참고문헌 31과 새 작성·검증 공개를 대조했다. 해당 문단과 참고 링크가 Markdown 내보내기에도 반영됐다. 학습 구조 수·전체 레코드 수·고유 배치 수를 구분하며, 한 DFT의 완전한 복제나 85개 원소의 균일 정확도를 주장하지 않는다.

## 사실과 한영 대응

- §6의 학습 147,894,100·validation 499,644·test 499,672·합계 148,893,416은 데이터 공개본 1.0.0의 README와 일치한다. 알려진 중성 물 풀의 694,467개 재사용과 전체 중복 제거 여부를 구분했다. 논문의 약 148M 학습 규모와 공개본 약 148.9M 전체 집계의 분모를 혼용하지 않는다.
- 초기 기준별 두 출력 head에서 후기 생산 head와 공유 표현을 함께 갱신하는 설명은 논문 II.2·SI S2.4에 맞는다. OMol25-0·OPoly26·재사용 물 풀은 힘만 학습하고 없는 레이블은 마스킹한다. 최종 모델을 단일 DFT 기준의 단순 복제로 설명하지 않는다.
- 자료 수와 샘플링 노출 빈도를 나누고, 85개 원소 포함을 균일한 원소·전하·스핀·배위 환경의 coverage로 확대하지 않는다. OMol/OPoly의 upstream 조성별 validation을 사용한 힘 평가와 새 온도·상·반응 경로·긴 궤적의 시험도 구분했다.
- §9의 고정 체크포인트·코드 commit·파일 해시 및 계산 설정을 남기자는 제안은 재현에 유용하다. 공식 저장소의 짧은 별칭은 이동할 수 있다. 현재 코드의 MIT 조건과 Tauri 가중치의 CC BY-NC 4.0 조건을 구분한 문장은 공식 NOTICES에 근거한다.
- 참고문헌 31은 조사한 코드 commit `ee62fa28860850d736845c3b91fba051d230f478`에 고정돼 있다. 새 공개 문단은 11월 6일 원 발행과 11월 10일 개정, 같은 arXiv v1·데이터 1.0.0의 재확인, 코드 정적 조사와 새 MD·학습·물성 재현의 부재를 구분한다. 사람의 문장별 최종 검토를 보증하지 않는다.

## 명료성 보완 권고

필수 정정은 아니지만, §6의 ‘지정한 PBE0 계열 자료’는 ‘지정한 PBE0+MBD-NL 자료’라고 좁히면 직접 분극률·분산 표적을 제공한 범위가 더 구체적이다. level-1 자료에 Hirshfeld 비율 필드가 있어도 학습에 사용하지 않았다는 공개본의 조건과도 맞는다. 양쪽 언어를 함께 고치는 선택이다.

기존 영어 공개 문단의 “the four body figures”는 개정 한국어의 ‘원판의 본문 네 도표’와 맞춰 “the original four body figures”로 쓰면 새 도식과 과거 제작 기록의 구분이 더 분명하다.

## 원출처와 확인 범위

- [SO3LR Tauri arXiv v1](https://arxiv.org/html/2611.06237v1): II.2, S2.1–S2.4, S3.
- [데이터 공개본 1.0.0 README](https://zenodo.org/api/records/22920714/files/README.md/content): 전체/학습 집계, 물 풀 재사용, 레이블과 분할.
- [공식 데이터 기록](https://zenodo.org/records/22920714): 버전 1.0.0, 최신 판본 표시를 API로 확인.
- [공식 코드의 고정 model registry](https://github.com/general-molecular-simulations/so3lr/blob/ee62fa28860850d736845c3b91fba051d230f478/so3lr/model_registry.py), [고정 NOTICES](https://github.com/general-molecular-simulations/so3lr/blob/ee62fa28860850d736845c3b91fba051d230f478/NOTICES.md).

검토는 문헌·작은 공개 메타데이터·설정과 레이블 관례의 대조다. 대형 원자료·가중치를 내려받거나 학습·추론·MD를 수행하지 않았다. 전체 데이터의 중복·오류·화학 coverage를 독립 실측한 검토와 구분한다. HTML/PDF 렌더링·실제 공개 배포 검수는 제작 담당의 별도 기록이다.
