# 카이랄 증폭 표지 재설계 v5

- 작성일: 2026-11-06 · 기준: 표지 원칙 1.2
- 상태: 재제작·독립 과학/시각 검토·한영 PDF 전 페이지 검수 완료; 출판 반영 검증 중
- 원고: 거울상 분자의 작은 불균형을 키우는 화학
- 기획·제작: weekly_cover_chiral_brain; 최종 과학·게재 검토: 총괄 편집

## 전달할 사건과 구체성

거울상으로 서로 포개지지 않는 두 형태가 있고, 생성물이 다음 생성을 돕는 반응에서 작은 초기 조성 차이가 커질 수 있다. 비선형 효과의 조립·활성과 비대칭 자가촉매는 본문의 구분을 유지한다. 표지는 후자의 자기촉진과 집단의 비대칭을 정성적으로 표현한다. 실제 Soai 분자나 반응 구조, 관측 비율은 그리지 않는다.

알아볼 대상은 한 바퀴 나선형 분자 모형 단위와 그 정확한 거울형이다. `artifacts/cover-geometry/module-pair.png` 및 source.mjs는 이전에 만든 자체 기하 참조다. reference의 x반사·면적·강체변환 검증을 보존한다. 새 생성 그림의 정확한 개수·곡면 합동은 별도 검토하며 원래 참조의 정량 검증을 새 래스터에 자동 승계하지 않는다. 생성 이미지에 화학 CIP의 R/S 표기를 붙이지 않는다.

| 요소 | 과학적 대응 | 보존할 관계 | 허용할 추상화 |
|---|---|---|---|
| 전경의 큰 두 나선 | 거울상 쌍 | 색뿐 아니라 반대 감김 | 크기·재질·시점 |
| 반복되는 나선 집단 | 두 형태의 정성적 조성 | 진행에 따라 한 형태의 상대적 우세 | 실제 개수·비율·시간 간격은 부여하지 않음 |
| 같은 감김의 완성형과 형성 중인 단위 | 생성물이 다음 생성을 돕는 자가촉매 | 같은 형태의 생성에 참여 | 실제 촉매-기질 구조 대신 만드는 접점 |

## 예술적 접근과 실제 참고작

Sophie Taeuber-Arp, *Composition of Circles and Semicircles* (1935), gouache on paper, National Museum of Women in the Arts. [공식 작품 페이지](https://nmwa.org/art/collection/composition-circles-and-semicircles/)와 실제 작품 이미지를 2026-11-06 확인했다. 짙은 바탕 위 원과 반원의 간격·묶음·색의 강약이 시선을 움직이는 것을 관찰했다. 이 작업에서는 반복 단위 사이 간격과 비대칭 강약이라는 원리만 취한다. 원작의 도상·배치·색 묶음을 재현하거나 원작 파일을 생성 입력·배포 자산으로 사용하지 않는다.

새 장면은 밝은 종이 위의 반대 감김 나선과 깊이 방향의 집단 변화다. 전경의 거울쌍, 중간의 만드는 접점, 뒤쪽 반복의 밀도를 하나의 대각선 흐름으로 연결한다. 과슈의 불투명색과 잉크·스텐실 경계는 분자 단위의 반복을 손으로 관찰하는 감각으로 발전시킨다. 미세 표면만이 아니라 반대 감김·다른 조성·자기촉진의 단서를 볼 수 있도록 한다.

## 세 발상과 선택

| 안 | 장면·매체·예술적 원리 | 장점·오독 위험 |
|---|---|---|
| A, 반복 단위의 비대칭 흐름 | 검증된 거울형 나선의 과슈·스텐실 집단; 간격·반복의 변주 | 거울형·집단 차이·형성 접점을 같은 장면에서 읽을 수 있다. 실제 분자·정량 동역학으로 오해하지 않도록 범위를 밝힌다. |
| B, 두 작업대의 생성 | 서로 거울형 틀을 쓰는 잉크 판화 작업대 | 자기촉진의 행위는 직접적이나 도구의 비유가 실제 화학을 가릴 수 있다. |
| C, 분자 거울의 정물 | 정밀한 두 분자 모형과 거울의 유화 | 형태 차이는 분명하나 비대칭 증폭과 시간의 흐름이 약하다. |

선택 A. 기존 v4 점토 손의 색을 바꾸는 방식에서 벗어나, 본문에서 다루는 형태와 집단을 구체적으로 제시한다. 지난주 다른 표지와 매체·구도·밀도를 비교하며, 뇌 표지의 가지형 청사진 및 다른 주제의 연속운동·분광적 장면과 구별한다.

## 제작과 검토 계획

- 프롬프트: `artifacts/hero-redesign-2026-11-06-prompt.txt`
- 도구: 내장 image_gen; 자체 기하 참조만 입력. 외부 작품 입력 없음.
- 새 자산: `artifacts/hero-redesign-2026-11-06.png` 및 인코딩본은 최종 생성 후 기록한다.
- 검수: 전경 두 형태의 반대 감김, 반복 단위의 감김 일관성, 같은 감김의 생성 접점, 정성적 우세; 원본·320×180·흑백·실제 모바일; 제목/캡션을 가린 판독과 독립 과학 검토.
- 실제 생성·자체 검토 결과는 아래에 기록한다. 기존 표지·PDF·게재 자산의 교체는 독립 감수와 출판 단계에서 확인한다.

## 실제 제작·자체 검토 결과

- 최종 원본 PNG: `artifacts/hero-redesign-2026-11-06.png`, 1672×941; 생성 원본을 그대로 보존했다.
- 한영 캡션·alt, SHA256, 참조·프롬프트와 검토 기록: `artifacts/hero-redesign-2026-11-06.json`.
- Actual new PNG and own geometric pair inspected. The foreground pair has opposed winding; the edited formative contact shows matching orange winding.
- Qualitative population change is visible; no numerical population, CIP assignment or actual Soai molecular structure is asserted.
- At320x180 the foreground pair and growing orange population remain readable; at full size pigment/contact and repeated units add discovery.
- Grayscale preserves opposed foreground silhouettes and the larger/smaller forming contact.
- Publication/mobile/PDF and independent scientific checks remain with the publication workflow.
- 초기 결과에서 작은 형성 단위의 감김이 반대로 읽힐 위험을 발견해 한 단위만 편집했다. 최종 프롬프트 전문은 `artifacts/hero-redesign-2026-11-06-edit-prompt.txt`에 보존했다.
- 새 그림에는 외부 참고작 파일을 입력하거나 원작을 재배포하지 않았다. 최종 사이트·PDF·아카이브의 실제 교체는 별도 출판 단계에서 확인한다.
- 두 번째 국소 편집에서 근거 없는 주변 ball-and-stick 모형만 안료·스텐실 흔적으로 정리했다. 전경 반대 감김 쌍과 같은 감김의 형성 접점을 다시 확인했다. 편집 프롬프트: `artifacts/hero-redesign-2026-11-06-cleanup-prompt.txt`.

## 독립 표지 검토 · 2026-11-06

총괄 root가 최종 PNG와 한영 캡션·alt JSON을 직접 대조해 채택했다. 전경 쌍의 반대 감김, 큰 주황 단위와 작은 형성 단위의 같은 감김, 배경의 정성적 우세와 미검증 분자 장식 제거를 확인했다. 이는 표지의 질적 과학·디자인 판독이며 독자 이해도 실험이나 실제 배포 확인은 아니다.

## 최종 독립 출력 검수

2026-11-06 weekly_cover_chiral_brain가 최종 한국어9쪽·영어10쪽의 모든 페이지를 렌더 이미지로 실제 확인했다. 새 표지·한영 캡션과 수식·도표·참고문헌·작성검증·쪽번호를 대조했으며 글자 누락·겹침·중요한 내용의 잘림·빈 페이지를 발견하지 못했다. 최종 PDF 해시는 검수 뒤 다시 확인했다. 표지 밖의 한영 원문은 보존했다. 실제 HTTPS 배포와 아카이브 다운로드 일치 확인은 출판 검증에서 별도로 수행한다.
