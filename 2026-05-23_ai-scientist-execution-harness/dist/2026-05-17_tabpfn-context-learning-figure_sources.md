---
title: "TabPFN context-learning 설명 및 Figure 2 교체 메모"
date: 2026-05-17
slug: tabpfn-context-learning-figure
status: source-note
language: ko
tags:
  - ai-tech-review
  - tabpfn
  - imagegen
  - in-context-learning
  - figure-audit
---

# TabPFN context-learning 설명 및 Figure 2 교체 메모

이 메모는 TabPFN을 XGBoost식 tabular ML과 구분해 설명하기 위해 TabPFN 논문과 공식 문서를 다시 확인하고, 본문 Figure 2를 imagegen+SVG hybrid figure로 교체한 기록입니다.

## 기술 판단

- 사용자의 LLM 비유는 큰 방향에서 적절합니다. [Nature 2025 TabPFN 논문](https://www.nature.com/articles/s41586-024-08328-6)은 TabPFN이 LLM에서 알려진 in-context learning을 표 데이터에 적용한다고 설명합니다.
- 다만 “암묵지를 자동으로 알아낸다”는 표현은 피해야 합니다. 논문은 TabPFN이 합성 표 과제에서 사전학습된 learning algorithm을 새 표에 적용한다고 설명하지만, domain expertise, feature engineering, data cleaning, problem framing은 여전히 필요하다고 명시합니다.
- XGBoost/CatBoost/LightGBM 같은 tree-based method와의 차이는 “표를 쓴다/안 쓴다”가 아니라 “데이터셋마다 fit하는 모델”과 “사전학습된 모델이 train row와 query row를 같은 context로 읽는 방식”의 차이로 설명하는 것이 정확합니다.
- [Prior Labs Models 문서](https://docs.priorlabs.ai/models)는 TabPFN-3가 OSS package의 default model이고, TabPFN-3-Plus는 API/enterprise에서 thinking mode와 native text feature를 제공한다고 설명합니다. 따라서 text note나 자유서술형 암묵지를 그대로 local TabPFN-3에 넣을 수 있다는 식의 표현은 제한했습니다.
- [Prior Labs regression 문서](https://docs.priorlabs.ai/capabilities/regression)는 TabPFNRegressor가 mean, median, mode, quantiles, full distribution을 반환할 수 있다고 설명하므로, uncertainty를 다음 실험 후보 선정 관점에서 간단히 남겼습니다.

## Figure 2 교체

| 항목 | 내용 |
|---|---|
| 생성 방식 | OpenAI imagegen base illustration + deterministic SVG labels |
| Base file | `artifacts/final_review/figures/tabpfn_context_learning_bridge_base.png` |
| Web copy | `artifacts/final_review/figures/tabpfn_context_learning_bridge_base-web.png` |
| Body file | `tabpfn_context_learning_bridge_base.png`를 직접 로드하고 본문 inline SVG로 라벨을 얹음 |
| 목적 | LLM의 문장 문맥 예측과 TabPFN의 표 문맥 라벨 예측을 나란히 보여주고, XGBoost식 fit-per-dataset 접근과 TabPFN의 pretrained in-context 접근 차이를 직관적으로 전달합니다. |
| 채택 판단 | 생성 이미지는 텍스트 없이 문장 카드, transformer-like bridge, 빈 label이 있는 표, 산업 context card가 구분됩니다. 정확한 한국어 문구는 inline SVG로 얹었습니다. 외부 SVG의 `<image href>` 방식은 브라우저에서 base PNG가 보이지 않아 본문 방식에서 제외했습니다. |

## Imagegen prompt 요약

- Use case: `infographic-diagram`
- Asset type: article figure base illustration
- Primary request: compare language-model sentence-context prediction and TabPFN table-context missing-label prediction
- Constraints: no readable text, no fake labels, no logos, no neural-network cloud, no crowded dashboard
- Output: `1536x1024`, quality `high`

## 2026-05-18 Figure 2 개념 보정

사용자 질문: 사전학습 때 `features [a,b,c] -> target d`, `features [a,b] -> target e` 같은 task를 보았다면, 실제 사용자가 `a,e`를 feature로 들고 와서 새 target을 예측할 수 있다는 뜻인가?

정리한 답은 다음과 같습니다.

- 가능하다는 말은 `a`와 `e`라는 feature 이름의 의미를 모델이 외웠다는 뜻이 아닙니다.
- [Nature 2025 TabPFN 논문](https://www.nature.com/articles/s41586-024-08328-6)은 TabPFN이 synthetic dataset에서 feature와 target의 관계가 다양한 task를 만들고, masked target을 예측하도록 사전학습된다고 설명합니다.
- 같은 논문은 실제 사용 단계에서 unseen dataset의 labeled training samples를 context로 제공하고, unlabelled samples의 label을 in-context learning으로 예측한다고 설명합니다.
- [Prior Labs overview](https://docs.priorlabs.ai/overview)는 TabPFN이 새 데이터셋마다 weight를 재최적화하는 대신, pretraining으로 얻은 inductive bias와 optimization strategy를 in-context learning으로 적용한다고 설명합니다.
- 따라서 `a,e -> y` 예측은 새 업무 표 안에 `y`가 정의된 labeled rows가 있을 때 성립합니다. `y` 라벨이 없거나 `a,e`가 `y`와 무관하면, 사전학습이 `d`나 `e`의 의미를 기억해서 답을 만들어주는 것은 아닙니다.
- 여기서 사전학습은 사용자가 `fit(X_train, y_train)`으로 데이터를 넣는 단계를 뜻하지 않습니다. 모델 weight가 배포되기 전에 synthetic tabular task들로 학습되는 단계를 뜻합니다. 사용자의 labeled rows는 사전학습 데이터가 아니라, 배포된 모델이 예측할 때 읽는 context입니다.

### Figure 2 반영

- 기존 `tabpfn_context_learning_bridge_base.png` + inline SVG overlay는 LLM next-token 비유를 설명하는 데는 유용했지만, feature/target 조합 일반화에 대한 오해를 줄이기에는 부족했습니다.
- 새 figure로 `artifacts/final_review/figures/tabpfn_pretraining_context_generalization.svg`를 만들었습니다.
- 그림은 `사전학습: 많은 synthetic task -> 학습된 prior -> 실제 사용: 새 업무 표`의 세 단계를 보입니다.
- 하단 callout에는 가능한 사용과 아닌 사용을 나눴습니다.
  - 가능한 사용: `a,e`로 `y`를 예측할 labeled rows가 있고 그 column에 실제 신호가 있을 때
  - 아닌 사용: `y` 라벨 없이 사전학습 기억만으로 `d`나 `e`의 의미를 맞히는 것
