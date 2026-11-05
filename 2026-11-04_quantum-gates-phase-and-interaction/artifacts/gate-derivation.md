# CNOT 회로와 ZZ 회전의 행렬 유도

본문의 보충 유도. 기저는 \((|00\rangle,|01\rangle,|10\rangle,|11\rangle)\), 첫 큐비트가 제어이고 둘째가 표적이다. 행렬곱은 오른쪽부터 작용한다. \(u=e^{-i\theta/2}\), \(v=e^{i\theta/2}\)로 쓰면

$$\mathrm{CX}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&1\\0&0&1&0\end{pmatrix},\qquad I\otimes R_z(\theta)=\begin{pmatrix}u&0&0&0\\0&v&0&0\\0&0&u&0\\0&0&0&v\end{pmatrix}.$$

먼저 오른쪽 CNOT을 곱하면, 마지막 두 열이 바뀐다.

$$(I\otimes R_z)\mathrm{CX}=\begin{pmatrix}u&0&0&0\\0&v&0&0\\0&0&0&u\\0&0&v&0\end{pmatrix}.$$

왼쪽 CNOT은 마지막 두 행을 바꾼다.

$$\mathrm{CX}(I\otimes R_z)\mathrm{CX}=\begin{pmatrix}u&0&0&0\\0&v&0&0\\0&0&v&0\\0&0&0&u\end{pmatrix}.$$

ZZ의 고유값은 +1, −1, −1, +1이다. 따라서 위 행렬은 \(\exp(-i\theta Z\otimes Z/2)=R_{ZZ}(\theta)\)다. 대각 원소는 중간 패리티가 같거나 다른 성분에 남는 위상 인자다. 이 정의는 [IBM Quantum RZZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZZGate)와 같다.

## 한 간선의 확률식

점수 \(C=(I-Z_aZ_b)/2\)와 초기 상태 \(|++\rangle\)를 사용한다. 문제 위상층 뒤 진폭은 \((1,e^{-i\gamma},e^{-i\gamma},1)/2\)다. 혼합층을 \(R_x(2\beta)\otimes R_x(2\beta)\)로 두고 \(c=\cos\beta,s=\sin\beta\)로 쓰면 최종 진폭은

$$A_{00}=A_{11}=\frac{\cos2\beta}{2}-\frac{i\sin2\beta}{2}e^{-i\gamma},\qquad A_{01}=A_{10}=\frac{\cos2\beta}{2}e^{-i\gamma}-\frac{i\sin2\beta}{2}.$$

각 진폭의 절댓값 제곱을 계산하면

$$P(01)+P(10)=2|A_{01}|^2=\frac{1+\sin4\beta\sin\gamma}{2}.$$

γ=π/2이면 \(A_{00}=(\cos2\beta-\sin2\beta)/2\), \(A_{01}=-i(\cos2\beta+\sin2\beta)/2\)다. β=π/8에서 전자는 0, 후자는 −i/√2가 된다. 규약과 층 순서는 [Farhi–Goldstone–Gutmann 원전](https://arxiv.org/abs/1411.4028v1)의 식 (2)–(6), (12)를 사용했다. 유도한 식은 리뷰의 교육 계산이며 [검산 코드](check_examples.py)와 [계산 기록](example-checks.json)에 수치 대조를 남겼다.
