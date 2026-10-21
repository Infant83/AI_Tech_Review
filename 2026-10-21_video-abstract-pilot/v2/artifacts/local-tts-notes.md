# 로컬 내레이션: Supertonic 2

이 영상의 공개용 내레이션은 Supertonic 2의 기본 F1 음성으로 로컬 CPU에서 합성한다. 사람이 녹음한 음성 또는 특정인의 복제 음성이 아니다. 추론 시 외부 TTS 서비스·API 키·인터넷 접속을 사용하지 않는다.

## 확인한 라이선스와 조건

- 추론 예제 코드: [공식 보존 저장소 MIT](https://github.com/supertone-oss-archive/supertonic/blob/1e9799e964ea4c0dad7cde993b65c3c813a7b373/LICENSE). 사용한 `py/helper.py`를 해당 commit의 내용과 해시로 대조했다. 예제 코드의 원 라이선스는 `licenses/supertonic-code-MIT.txt`에 보존한다.
- 모델: [Supertonic 2의 고정 revision](https://huggingface.co/Supertone/supertonic-2/tree/75e6727618a02f323c720cba9478152d4bc16ca4). [Open RAIL-M 원문](https://huggingface.co/Supertone/supertonic-2/blob/75e6727618a02f323c720cba9478152d4bc16ca4/LICENSE)은 `licenses/supertonic-2-OpenRAIL-M.txt`에 보존한다.
- §6은 명시한 조건을 제외하고 제공자가 출력물의 권리를 주장하지 않는다고 정한다. 출력 이용은 라이선스의 사용 제한을 지켜야 하며, Attachment A(e)에 따라 합성 콘텐츠임을 명확하고 이해할 수 있게 표시해야 한다. 이 제작물은 교육용 과학 해설이다.
- 공개 플레이어·transcript와 독립 MP4에서 **“AI 합성 음성 · Supertonic 2 / F1”**, 영어에서는 **“AI-generated narration · Supertonic 2 / F1”**라고 표시한다. 기본 음성을 특정 연구자나 제3자의 실제 목소리처럼 소개하지 않는다.

라이선스 확인일 2026-10-21. 모델 weight·의존 runtime은 `.runtime/`에만 두며 공개 배포 자산에 포함하지 않는다. 생성 WAV·MP4는 각자 이름으로 명시한 공개 allowlist와 검사를 거쳐 제공한다.

## 재실행 인터페이스

프로젝트의 v2 폴더에서 다음과 같이 호출한다. 가상환경은 Python 3.12, ONNX Runtime 1.20.1의 macOS Intel CPU wheel과 SoundFile 0.14.0을 사용한다. 전역 Python에는 설치하지 않았다.

```sh
.runtime/tts-venv/bin/python artifacts/local_tts.py \
  --lang ko --text-file narration-ko.txt --output narration-ko.wav \
  --voice F1 --speed 1.0 --steps 8
```

영어는 `--lang en`으로 지정한다. `--text`로 직접 입력하거나 `--text-file`로 UTF-8 문장을 읽는다. 출력은 44.1kHz·모노·16bit PCM WAV이며, 같은 이름의 JSON에 입력문·모델 revision·voice preset·설정·runtime·음성 및 voice style 해시·실측 소요 시간·합성 음성 고지를 기록한다. 영상 편집기에서 필요하면 24kHz 등으로 별도 변환한다. 문장 단위 합성 후 실제 WAV 길이로 자막·장면 시간을 다시 계산해야 한다.

## 실제 수행한 실행 확인

같은 F1·8 steps·speed 1.0·seed 42로 짧은 한국어와 영어 문장을 각각 합성했다.

| 언어 | 출력 길이 | 모형 로드 | 추론 | 추론/출력 길이 |
|---|---:|---:|---:|---:|
| 한국어 | 4.462초 | 0.730초 | 0.308초 | 0.069 |
| 영어 | 4.280초 | 0.732초 | 0.285초 | 0.066 |

한 번의 짧은 실행에서 측정한 값이며 일반 성능 벤치마크가 아니다. `qa/supertonic-ko-proof.wav`와 `qa/supertonic-en-proof.wav` 및 JSON에 시험 결과를 보존했다. 실행·WAV 생성은 확인했으나 직접 청취에 의한 발음·억양·호흡 품질 검토를 수행했다고 주장하지 않는다. 최종 영상의 음성·자막 동기와 수학 용어 발음은 별도 검수 대상이다.
