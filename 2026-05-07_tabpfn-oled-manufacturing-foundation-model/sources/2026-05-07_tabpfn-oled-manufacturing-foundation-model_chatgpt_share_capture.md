---
title: "ChatGPT share capture - TabPFN2.5 vs XGBoost"
date: 2026-05-07
source_url: "https://chatgpt.com/share/69fb811f-2764-83a2-9042-bd2e3c24642e"
capture_method: "Playwright snapshot and visible page text"
status: "partial-visible-capture"
---

# ChatGPT Share Capture

## Capture Result

Playwright로 공유 링크를 열었을 때 공개 화면에는 `TabPFN2.5 vs XGBoost`라는 제목의 초반 대화만 노출됐다. 사용자는 이 공유 링크 안에 두 개의 심층 리서치가 있다고 설명했지만, 현재 공개 렌더링에서는 해당 심층 리서치 본문을 확인할 수 없었다.

확인된 공개 대화의 핵심은 다음이다.

- 원문 seed는 Intellegens 쪽 실무형 표 데이터 비교 포스트로 보인다.
- 비교 대상은 `TabPFN2.5`, `TabICL`, `XGBoost`를 포함한 9개 표 데이터 모델이다.
- 데이터는 4개 데이터셋, 341개 예측 타깃이라고 설명되어 있다.
- 평균 정확도는 TabPFN/TabICL 같은 tabular foundation model이 가장 높았다고 요약되어 있다.
- 다만 예측 시간은 매우 느릴 수 있으며, 일부 경우 XGBoost가 초 단위로 끝내는 작업을 TabPFN 계열 모델이 시간 단위로 수행했다는 속도-정확도 trade-off가 강조되어 있다.

## How This Capture Was Used

이 capture는 최종 리뷰의 seed signal로만 사용했다. 공유 대화에 있다고 설명된 두 심층 리서치 본문은 직접 검증되지 않았으므로, 최종 결론에는 공식 문서, 논문, 기존 OLED 리서치 패키지, 공개된 TabPFN/TabICL 근거를 우선 적용했다.

## Visible Conversation Summary

공개 화면에서 보인 한국어 요약은 다음 주장으로 정리된다.

- TabPFN2.5는 표형 데이터용 파운데이션 모델로 주목받고 있다.
- 표형 데이터 분야는 오랫동안 XGBoost 같은 트리 기반 모델이 강했다.
- 실제 고객 데이터와 유사한 4개 데이터셋, 341개 예측 타깃에서 9가지 모델을 비교했다.
- TabPFN, TabICL 같은 tabular foundation model이 평균적으로 가장 높은 정확도를 보였다.
- 속도는 약점이다. 반복 실험과 interactive workflow에서는 XGBoost 계열의 빠른 응답성이 여전히 큰 실무 가치를 갖는다.
- 성능이 제품 안전성이나 성패를 좌우하는 고위험 설정에서는 몇 퍼센트의 정확도 향상이 느린 실행 시간을 정당화할 수 있다.

