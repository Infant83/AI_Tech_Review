# AI Tech Review Q/node icon

2026-10-22 · Asset version: `20261022-quantum-node`

AI·양자 기술 리뷰의 홈 화면·브라우저 아이콘. 독립적으로 설계한 기하학적 Q와
두 개의 연결 노드를 사용한다. 특정 양자 상태·얽힘·실험 장치의 도식이 아닌 브랜드 심볼이다.

검토한 세 발상:

1. Q 중심에서 바깥으로 이어지는 민트색 선: 단순하지만 탐색·레이더의 인상이 강함.
2. 아이보리 Q 안에 독립된 두 노드를 연결: 작은 크기의 Q 판독과 계산·연결의 상징이 함께 남음. **선택.**
3. Q 안에 세 갈래 노드를 배치: 작은 크기에서 가지와 Q 꼬리가 경쟁함.

잉크색 배경 `#10242C`, 아이보리 `#F4F4EC`, 민트 `#69DECA`의 평면 그래픽이다.
글자·그라데이션·광택·그림자를 넣지 않는다. 배경은 불투명하게 끝까지 채워 iOS가
모서리를 한 번만 마스킹하도록 한다. 마크에는 충분한 여백을 둔다.

## Regenerate

Pillow가 설치된 Python으로 저장소 루트에서 실행한다.

```sh
python3 .automation/assets/ai-tech-review-icon/build_favicon.py
```

`build_favicon.py`의 공통 `SHAPES` 기하가 SVG와 고해상도 래스터를 생성한다.
폰트·외부 이미지·생성형 이미지 모델에 의존하지 않는다.

- `ai-tech-review-icon.svg`: 확장 가능한 벡터
- `ai-tech-review-icon-512.png`: 512px 원본
- `apple-touch-icon.png`: 180px, 불투명 RGB
- `favicon-{16,32,64}x{16,32,64}.png`: 브라우저용 PNG
- `favicon.ico`: 16/32/48/64/128/256px 슬롯

`scripts/publish_public_site.py`가 최종 아이콘만 `site/`에 복사하며,
아이콘 URL의 버전으로 이전 깃털 아이콘 캐시를 갱신한다.
기존 Federlicht 원본은 이전 제작 기록으로만 보존한다.

## Verification

- 512px 원본, 180px 홈 화면, 64/32/16px 탭 아이콘을 시각 검토했다.
  16px에서 내부 연결은 작은 민트색 포인트로 축소되며 Q 윤곽은 남는다.
- 둥근 모서리 마스크와 흑백으로 확인했다. 실제 iOS 기기의 설치 검수는 하지 않았다.
- PNG 크기·불투명 RGB·빈 metadata, ICO의 여섯 크기, 공개본과 생성 원본의
  바이트 일치를 확인했다. SVG와 PNG는 같은 좌표·색·도형 목록을 사용한다.
- 별도 검토자가 후보의 소형 판독성과 공개 HTML의 아이콘 경로를 확인했다.

QA용 비교판과 화면 캡처는 공개 `site/`에 포함하지 않는다.
