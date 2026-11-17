# Classiq: 같은 진폭 곱셈 회로를 Qmod로 표현하기

이 예제는 Classiq SDK **1.35.0**에서 실수·복소수 입력과 균등·중요도 입력의 네 Qmod 모델을 실제 생성하고 JSON·클라이언트 모델 스키마 검사를 통과했다. **Classiq 클라우드 합성·상태벡터 시뮬레이션·QPU 실행은 수행하지 않았다.** `validation.json`은 확인한 범위를 구분한다. Qmod 생성은 회로 실행 결과를 뜻하지 않는다.

## 로컬 모델 생성

Python 3.12의 별도 환경에서 실행한다.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python ntca_classiq.py --output classiq-models
```

`--output` 기본값은 `classiq-models`다. 기본 실행은 로그인이나 클라우드 호출 없이 모델 네 개와 `classiq-validation.json`을 만든다. 공유용 모델을 쓸 때에는 SDK의 소스·디버그 메타데이터를 제거한 뒤 클라이언트 스키마를 다시 검사한다. 이번 공개 산출물에는 원시 모델 JSON이나 기기별 디버그 경로를 포함하지 않는다.

`prepare_amplitudes`는 **실수** 진폭을 받는다. 실수 예제는 부호를 포함한 진폭을 그대로 전달한다. 복소수 예제 `(1,i,-1,0)/sqrt(3)`는 양의 실수 진폭 `(1,1,1,0)/sqrt(3)`를 준비한 뒤 `S(out[0])`, `Z(out[1])`로 위상을 붙인다. Qmod의 비트 인덱스 0은 수치의 가중치 1에 해당한다. 이 예에서 사용한 상태 준비의 `bound=0`은 정확한 준비를 요청하는 모델 조건이며, 실제 합성 결과를 측정한 정확도는 아니다. [공식 상태 준비 문서](https://docs.classiq.io/qmod-reference/library-reference/core-library-functions/prepare_state_and_amplitudes/prepare_state_and_amplitudes), [양자 자료형과 비트 가중치 예제](https://docs.classiq.io/qmod-reference/language-reference/quantum-types).

각 필터는 새 두 큐비트 작업 레지스터를 입력 상태로 준비하고 주소의 두 비트에서 대응 작업 비트로 CNOT을 적용한다. 모든 작업 레지스터가 0인 가지를 남기면 주소 j의 진폭에 입력 진폭 x[j]가 곱해진다. 균등 입력은 작업 레지스터 세 개, 중요도 입력은 주소의 입력 상태 준비와 작업 레지스터 두 개를 사용한다. 명시한 주소·작업 레지스터는 각각 8·6큐비트이고 전체 순방향 상태 준비 호출은 두 방식 모두 세 번이다. 실제 Classiq 합성 폭·깊이·실행 시간은 이번에 측정하지 않았다.

## 기존 연결에서만 선택하는 클라우드 확인

Classiq SDK에 이미 허가된 로그인이 있는 환경에서는 다음 명령으로 클라우드 합성과 **Classiq 고전 시뮬레이터**의 상태벡터를 요청할 수 있다.

```sh
.venv/bin/python ntca_classiq.py --output classiq-models --cloud
```

`--cloud`를 명시해야 `synthesize(model)`와 `calculate_state_vector(program, backend="simulator", amplitude_threshold=0.0, verbose=False)`가 호출된다. QPU 백엔드는 선택하지 않는다. 새 인증이 필요한 독자의 환경에서는 [공식 SDK 인증 절차](https://docs.classiq.io/user-guide/authentication/sdk-authentication)를 따르며 자격 정보를 코드에 넣지 않는다. 이번 작업에서는 새 로그인이나 클라우드 작업을 수행하지 않았다.

상태벡터의 DataFrame에서는 `work0=work1[=work2]=0`인 행을 고른다. 주소와 작업 출력은 `QNum[2]`로 이름을 붙였으므로 물리 큐비트 배치 순서 대신 각 열의 정수 값을 사용한다. 남은 가지의 노름 제곱을 성공 확률로 계산하고 복소 진폭의 조건부 충실도를 검사한다. 전역 위상은 충실도에 영향을 주지 않는다. 인위적으로 만든 시험용 DataFrame으로 검사한 후처리 함수 테스트는 실제 Classiq 상태벡터 실행과 구별한다. [공식 상태벡터 문서](https://docs.classiq.io/user-guide/execution/calculate-state-vector).

## QSVT로 확장할 때

현재 코드는 순방향 U와 XOR로 세제곱의 진폭 곱을 만드는 회로다. 밀집 행렬을 유니터리로 넣은 기준 계산이나 실제 QSVT 실행으로 표시하지 않는다.

SDK 1.35.0에는 `qsvt`와 `qsvt_lcu`가 있으며 위상 생성은 `classiq.applications.qsp.qsvt_phases`로 제공된다. `qsvt_synthesis`는 이 버전의 최상위 SDK나 `classiq.applications.qsp`에서 내보내는 함수가 아니다. Classiq의 위상 생성은 reflection signal·Hadamard 측정 기저 관례를 사용한다. 일반 다항식으로 확장할 때에는 다항식의 경계·짝홀성·스케일, 블록 인코딩의 projector와 위상 관례, 원하는 실수·복소 성분의 추출을 별도로 구현하고 끝까지 검사해야 한다. 다른 프레임워크의 위상 벡터를 그대로 이식하지 않는다. [QSVT API](https://docs.classiq.io/sdk-reference/qmod/functions/open_library/qsvt), [위상 생성 API](https://docs.classiq.io/sdk-reference/applications/QSP).

공식 문서와 실제 설치한 SDK 인터페이스의 확인일은 2026-11-17이다.
