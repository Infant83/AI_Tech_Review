# 비디오 abstract v4

노터 게시물의 대칭·보존량·모형 설계와 계산 검증이라는 논지를 대표 용수철 계산과 HNN 구성으로 설명한다. 앞서 작성한 장면별 시각 개편 계획을 실제 새 영상에 적용했다. v3 출력은 보존했다.

최종 게시 주소는 다음과 같다. 제작 원본은 이 폴더의 `dist/`에 생성하고, 게시자는 검증된 파일만 기사의 명명 규칙으로 복사한다. Git에는 원본 MP4를 중복 보관하지 않는다.

- [게시물의 영상 모듈](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/#video-abstract)
- [한국어 MP4](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/noether-abstract-ko.mp4): 236.75초, 약 3분 57초.
- [English MP4](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/en/noether-abstract-en.mp4): 228초, 3분 48초.
- [한국어 자막](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/noether-abstract-ko.vtt) · [English captions](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/en/noether-abstract-en.vtt)
- [한국어 시각 transcript](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/noether-abstract-transcript-ko.txt) · [English visual transcript](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/en/noether-abstract-transcript-en.txt)
- [한국어 poster](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/noether-abstract-poster-ko.webp) · [English poster](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/en/noether-abstract-poster-en.webp)
- [주제별 제작 기획](../../2026-10-17_noether-symmetry-conservation/video-abstract-brief.md) · [근거](source-map.md) · [기사에 설치한 manifest](../../2026-10-17_noether-symmetry-conservation/artifacts/video-abstract-manifest.json) · [제작 원본 프로버넌스](production-manifest.json)

에너지 막대를 읽는 동안 두 시간축은 나오지 않는다. 실제 용수철의 한 상태에서 정규화한 좌표·위상 평면의 점·같은 에너지 원으로 이어지고, 첫 Euler 한 걸음과 실제 25배 확대를 설명한다. 로그 비율 → 벨레 선 → 선형 %오차를 차례로 읽으며 결과를 유지한다. HNN에서는 학습 함수 → 기호의 뜻 → 해밀턴 방정식 → 수치 적분을 따로 소개한다. 결론은 앞의 두 결과와 축을 회수하며 새 수식을 넣지 않는다.

웹용 MP4는 1600×900, 24fps, H.264/AAC이며 faststart를 사용한다. 발화 자막은 MP4에 굽지 않고 별도 VTT로 제공한다. MP4만 내려받으면 자막이 포함되지 않으므로 VTT도 함께 받는다. 소스·TTS·중간 음성·QA·런타임은 공개 `dist/` 밖에 둔다. 기사 통합은 언어별 MP4·poster·VTT·TXT만 이름을 명시한 allowlist로 복사한다. 제작 manifest의 검증 상태와 실제 게시 상태를 구별한다.

음성은 로컬 Supertonic 2 기본 F1 합성이다. 이번 제작에서는 기존 v3 음성 49개를 재사용하고 새 정의·수정 발화 26개만 합성했다. 새 이미지나 생성형 비디오·외부 유료 TTS API를 호출하지 않았다. v2의 기존 생성 hero 하나를 배경으로 재사용하며 정확한 과학적 정보는 코드로 구성했다. 추가 API 호출 0은 에이전트 사용·과거 이미지 생성·로컬 연산·저장·호스팅 비용이 없다는 뜻이 아니다.

재현은 저장소 루트에서 실행한다. 기존 v2 로컬 런타임을 재사용하거나 아래처럼 Python 3.12 환경을 만든다. 의존성은 `v2/artifacts/requirements.txt`의 NumPy 2.3.5, Pillow 12.3.0, imageio-ffmpeg 0.6.0과 `requirements-tts.txt`의 onnxruntime 1.20.1, soundfile 0.14.0이다. 로컬 가상환경과 모델은 Git에 포함하지 않는다.

```sh
python3.12 -m venv 2026-10-21_video-abstract-pilot/v2/.runtime/tts-venv
2026-10-21_video-abstract-pilot/v2/.runtime/tts-venv/bin/python -m pip install -r 2026-10-21_video-abstract-pilot/v2/artifacts/requirements.txt -r 2026-10-21_video-abstract-pilot/v2/artifacts/requirements-tts.txt
2026-10-21_video-abstract-pilot/v2/.runtime/tts-venv/bin/python 2026-10-21_video-abstract-pilot/v2/artifacts/setup_local_tts.py --download
```

최초 모델 설치·고정 SHA 검증은 [로컬 음성 안내](../v2/artifacts/local-tts-notes.md)와 [설치 소스](../v2/artifacts/setup_local_tts.py)를 따른다. 모델과 helper의 고정 revision·URL·SHA는 lock에, MIT/OpenRAIL-M 원문과 출력 고지 조건은 v2의 `licenses/`와 `local-tts-notes.md`에 보존한다.

```sh
2026-10-21_video-abstract-pilot/v2/.runtime/tts-venv/bin/python 2026-10-21_video-abstract-pilot/v4/artifacts/render_review.py --lang both
2026-10-21_video-abstract-pilot/v2/.runtime/tts-venv/bin/python 2026-10-21_video-abstract-pilot/v4/artifacts/verify_review.py
2026-10-21_video-abstract-pilot/v2/.runtime/tts-venv/bin/python 2026-10-21_video-abstract-pilot/v4/artifacts/build_manifest.py
```

기존 v3 음성 캐시는 선택 사항이다. 해당 private 폴더가 없으면 renderer가 75개 발화를 모두 로컬에서 새로 합성한다. 새 실행의 재사용·합성 개수는 manifest가 다시 계산한다. `VIDEO_FONT`와 `VIDEO_MATH_FONT`에는 사용권한이 있는 한글·수학 폰트를, `VIDEO_FFMPEG`에는 로컬 encoder를, `VIDEO_TTS_PYTHON`에는 합성 의존성이 설치된 Python을 지정한다. 이번 출력은 Apple SD Gothic Neo와 STIX Two Math를 rasterize했으며 폰트 파일을 배포하지 않는다. 원작성자의 private 절대경로를 재현 설정으로 요구하지 않는다.

각 의미 cue는 한영의 실제 발화 구절에 연결되며, 음성 unit의 시작·끝 시간은 private timeline에 남는다. 대본·시각 설명을 바꿀 때는 발화도 달라졌는지 확인한다. `--text-only`는 변하지 않은 발화와 시각 설명을 동기화하는 용도이며 영상 재제작을 대신하지 않는다.

고정 대본·코드·모델을 사용하더라도 폰트 버전·CPU·라이브러리의 부동소수점 연산·FFmpeg build에 따라 재합성 음성과 영상의 binary hash가 달라질 수 있다. 배포한 최종본의 동일성은 최종 manifest의 hash로 확인한다. 재제작 후에는 수치·자막·디코드·실제 전환 검수를 다시 수행한다.

Git에 포함하지 않는 private QA를 예전 hash의 검토 기록으로 대체하지 않는다. 독립 검토자가 새 master의 hash를 기록하지 않으면 `build_manifest.py`의 `independent_encoded_visual_review`는 false이며 공개 installer가 이를 차단한다. 실제 출력의 기술 검사와 별도 과학 검토는 사람의 평가가 아니다. 사람이 청취·발음·이해도를 평가하지 않았다는 점을 계속 명시한다.

최종 기술 검사는 두 MP4 전체 디코드·faststart·음량과 clipping·75개 발화의 출처·VTT 내용과 시각·이미지 metadata 검사를 통과했다. 별도 에이전트가 각 언어 83개 실제 인코딩 프레임, 총 24개 시간순 contact sheet와 8개 전체 해상도 프레임을 확인했다. 수치·전환 프레임 심사와 기사 native player의 재생·자막 검사는 별도 단계다.
