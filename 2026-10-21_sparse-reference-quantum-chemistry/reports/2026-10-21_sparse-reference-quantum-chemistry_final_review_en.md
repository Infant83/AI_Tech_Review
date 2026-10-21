# Reading Energy Differences in Quantum Chemistry: Sparse References and Mixed Estimators

<p class="dek">How sparse references reduce energy-measurement costs — from projection geometry to the interpretation of Helios experiments</p>

<p class="kicker">TECH REVIEW · October 21, 2026 · Quantum chemistry · Quantum measurement · Scientific computing</p>

<figure class="hero"><img src="hero.webp" alt="A printmaking-inspired conceptual scene with a sparse reference plate and a finely textured residual plate placed against one larger target impression."><figcaption>A sparse reference plate and a separate residual plate are compared with one target impression, symbolizing energy estimation from the target state's overlaps with reference and residual states. This AI-generated conceptual illustration depicts no molecule, measurement apparatus or quantitative data; it does not imply that two shots suffice.</figcaption></figure>

## We prepared a good state, so why is the calculation not finished?

Suppose we want to know which of two molecular geometries is more stable. A quantum processor has successfully prepared their two electronic states. Can we simply read each energy once and subtract?

An energy eigenstate has a definite energy. Why, then, might an experiment to determine that energy require thousands, or even millions, of repetitions? **The energy uncertainty of a state and the statistical cost of our chosen measurement procedure are different things.** Once we understand that distinction, the idea behind this study comes into view.

Lenihan and colleagues study how to read energies by combining a sparse classical reference state with a quantum-prepared target state, using a model of a photoactive Ru molecule. The key move is to replace measurements of many Hamiltonian terms with overlap measurements involving the reference and its residual. The study includes execution on the Quantinuum Helios device, but ideal shot estimates, statistical precision on hardware, and remaining bias must be distinguished. The paper is **preprint v1**, released on October 19, 2026. [1]

Deriving the estimator from the relation between the reference and its residual reveals when two probabilities can recover an energy, and where that argument fails. The two-level model, calculations, and exercises below are educational material developed for this review, distinct from the paper's experimental data.

## 1. Chemistry asks for small differences between large energies

The paper's H₂DBB–Ru system is a molecular model extracted from a Ru-functionalized Hf metal–organic framework. A triplet state with metal-to-ligand charge-transfer character, MLCT, competes with metal-centered, MC, character. As the nuclear coordinates change, so do the important electronic configurations. The difficulty is **multireference character**: a single Slater determinant cannot readily describe the electrons. [1, §2.2]

An active space \((n_e,n_o)\) means that \(n_e\) electrons are correlated within \(n_o\) selected spatial orbitals. Thus \((10,10)\) means ten electrons in ten orbitals. In the representation used here, with two spin orbitals per spatial orbital, this corresponds to 20 data qubits. The paper's 50-qubit circuit does not result from enlarging that active space to 50 orbitals.

CASCI is a reference calculation that diagonalizes the Hamiltonian using all allowed electronic configurations within specified orbitals and an active space. It provides a rigorous comparison within that space, but is not the exact energy of the real molecule including correlation outside the active space, basis-set effects, the environment, and nuclear motion. This study uses \((6,6),(8,8),(10,10)\) active spaces to evaluate the method. [1]

Indeed, the paper's CASCI energy difference between the two geometries changes to approximately −6.3, −6.3, and +0.1 mHa as the active space is enlarged. Its sign changes between the last two spaces. Agreement between a device and CASCI within one active space is a separate question from convergence of the chemical energy difference with active-space size. [1, Table S6]

Let us also establish the energy scale. One mHa is \(10^{-3}E_h\), or approximately 27.2114 meV. The paper's target of 1.6 mHa is approximately 43.54 meV. As an educational example, consider a simple Arrhenius relation \(k\propto e^{-E_a/(k_BT)}\) with identical prefactors. At 300 K, changing the barrier by 1.6 mHa changes the rate by a factor of approximately 5.39. This is a **sensitivity example** calculated using NIST constants, not an actual reaction-rate model or therapeutic-efficacy calculation for the Ru system. [3]

> **First question.** If one absolute energy has an error of 5 mHa, must the energy difference between two geometries also be wrong by 5 mHa? We first need to know whether the two errors move together. We will return to this question when reading the hardware results.

## 2. Why repeatedly measure a state with a definite energy?

Write the electronic Hamiltonian, mapped onto qubits, as a sum of Pauli strings.

$$
H=\sum_j c_jP_j,\qquad E=\sum_jc_j\langle P_j\rangle.
$$

Here \(P_j\) is a tensor product of I, X, Y, and Z, and \(c_j\) is a coefficient with units of energy. Strings that cannot share a measurement basis require separate circuits and shots. A shot is one execution from state preparation through measurement. If fixed compatible groups \(H_g\) are sampled independently of one another,

$$
\operatorname{Var}(\widehat E)=\sum_g\frac{\operatorname{Var}_{\Psi}(H_g)}{N_g}.
$$

Covariances within each group are included in \(\operatorname{Var}(H_g)\). This expression does not instruct us to treat every Pauli measurement as an independent, single-string measurement.

For an exact energy eigenstate, \(\operatorname{Var}_{\Psi}(H)=0\). Yet the variance of each chosen measurement group need not vanish. Efficiently implementing a measurement in the Hamiltonian's eigenbasis is a different task from combining averages measured in several readily accessible Pauli bases. Quantum phase estimation is another way to read an energy, but requires longer coherent evolution and additional resources.

The method does not attempt to reconstruct the entire state. **First calculate what can be known classically, then measure only the quantities needed for the remaining energy correction.** This shift is the starting point of the mixed estimator.

## 3. Where does the Hamiltonian send the reference?

Let the normalized target state be \(\lvert\Psi\rangle\), and let \(\lvert\Phi\rangle\) be a sparse reference state that can be constructed classically. Sparse means that its set of selected electronic determinants, \(S_\Phi\), is small.

$$
\lvert\Phi\rangle=\sum_{x\in S_\Phi}a_x\lvert x\rangle,
\qquad \sum_x|a_x|^2=1.
$$

First calculate the reference energy. Then subtract from \(H\lvert\Phi\rangle\) the component parallel to the reference.

$$
E_\Phi=\langle\Phi|H|\Phi\rangle,\qquad
Q_\Phi=I-\lvert\Phi\rangle\langle\Phi\rvert,
$$

$$
\lvert R\rangle=Q_\Phi H\lvert\Phi\rangle,
\qquad r_\Phi=\sqrt{\langle R|R\rangle},
\qquad \lvert\Lambda\rangle=\frac{\lvert R\rangle}{r_\Phi}.
$$

The last definition applies only when \(r_\Phi>0\). Since \(\langle\Phi|\Lambda\rangle=0\), \(\Lambda\) is a normalized residual state orthogonal to the reference. The following is therefore an identity, not an approximation:

$$
\boxed{H\lvert\Phi\rangle
=E_\Phi\lvert\Phi\rangle+r_\Phi\lvert\Lambda\rangle.}
$$

The quantity \(r_\Phi\) is a magnitude with units of energy, not a probability. For Hermitian \(H\) and a normalized reference,

$$
r_\Phi^2=\langle\Phi|H^2|\Phi\rangle-E_\Phi^2.
$$

This is the energy variance in the reference state. If the reference is an eigenstate, the residual is zero. Its energy is already \(E_\Phi\), and there is no reason to define a separate \(\Lambda\). Conversely, a small residual alone does not establish proximity to the desired eigenstate: another, undesired eigenstate also has zero residual.

<figure><img src="projection_residual_en.svg" alt="The Hamiltonian acting on the reference is decomposed into a parallel reference component and an orthogonal residual, and both are compared with the target state."><figcaption>An educational diagram reconstructed directly from the relationships in equations (1)–(4) of the original paper. Orthogonality refers to the Hilbert-space inner product, not to molecular orientations or device wiring. The diagram is a conceptual cross-section showing the relationships for a real eigenstate; phases of complex states are addressed in the equations in the text. [1]</figcaption></figure>

Now multiply this identity on the left by \(\langle\Psi|\). Writing \(s=\langle\Psi|\Phi\rangle\ne0\) and \(h=\langle\Psi|\Lambda\rangle\), we obtain

$$
\boxed{E_{\rm ME}
=\frac{\langle\Psi|H|\Phi\rangle}{\langle\Psi|\Phi\rangle}
=E_\Phi+r_\Phi\frac hs.}
$$

If the target is an exact eigenstate, \(\langle\Psi|H=E\langle\Psi|\), so the numerator is \(E s\), and the ratio gives the exact eigenvalue. This algebraic exactness holds even when the reference is approximate. It requires a nonzero overlap, an exact target eigenstate, and exact classical constants and residual. We will examine an approximate target separately below. [1, §2.1]

> **Mixed estimator versus expectation value.** This expression differs from \(\langle\Psi|H|\Psi\rangle\). It is a “mixed” estimator because the numerator contains both the target and the reference. Replacing the mixed functional with the ordinary expectation value changes the later discussion of variational bounds.

### A sparse reference does not automatically make the residual cheap

The number of determinants in \(H\Phi\) can exceed that in the reference. If we truncate the residual to a smaller \(\widetilde\Lambda\) for preparation, the exact identity above also becomes approximate. For the signed estimator with \(E_\Phi,r_\Phi,s\) held fixed, the Cauchy–Schwarz inequality gives

$$
|\widetilde E_{\rm ME}-E_{\rm ME}|
\le\frac{r_\Phi}{|s|}\,\|\widetilde\Lambda-\Lambda\|
$$

This is a worst-case alignment bound of the same form as equation (5) in the paper. Residual-truncation error, approximate-target error, device noise, and chemical errors from outside the active space are distinct contributions. A small denominator overlap also amplifies truncation error. The experiment selects determinants using classically obtained CASCI information, so it should not be read as independently discovering a molecular solution inaccessible to classical calculation. [1, §2.3; S2]

## 4. When can we avoid measuring the full phase?

In general, \(h,s\) are complex. Knowing two absolute values does not determine the phase of their complex ratio. For an exact eigenstate, however, \(E-E_\Phi\) is real. Moreover, if the target is **the lowest eigenstate in the same invariant symmetry subspace as the reference**, the variational principle fixes the sign:

$$
E-E_\Phi=r_\Phi h/s\le0.
$$

Under this condition, the measured probabilities

$$
p=|h|^2=p_\Lambda,\qquad q=|s|^2=p_\Phi
$$

suffice to select the negative branch.

$$
\boxed{E_{\rm ME}=E_\Phi-r_\Phi\sqrt{p/q},\qquad q>0.}
$$

The point is not that complex phases always disappear. Exactness of the eigenstate makes the ratio real; being the lowest state in the relevant subspace determines its sign as well. For an arbitrary approximate state the ratio can be complex, and for an arbitrary excited eigenstate a positive correction may be required.

The paper's treatment of a chemically excited triplet does not contradict this condition. The calculations target the **lowest triplet state** within the selected active space. This is a symmetry-sector problem, distinct from the molecule's overall singlet ground state. Choosing electron numbers \((N_\alpha,N_\beta)=(4,2),(5,3),(6,4)\) fixes \(M_S=1\), but fixing \(M_S\) alone does not guarantee total spin \(S=1\). State construction, spin checks, and symmetry conditions must be considered together. The negative branch cannot simply be applied to any higher MLCT or MC root. [1, §2.2]

### The probability read by a compute–uncompute circuit

Here we consider two independent CU circuits. If \(U_\Psi\lvert0\rangle=\lvert\Psi\rangle\) and \(U_\Phi\lvert0\rangle=\lvert\Phi\rangle\), prepare the target, apply the inverse reference-preparation circuit, and measure whether all bits are zero.

$$
\Pr(0^n)=|\langle0|U_\Phi^\dagger U_\Psi|0\rangle|^2
=|\langle\Phi|\Psi\rangle|^2=q.
$$

Replacing the inverse reference circuit with the inverse residual circuit gives \(p\). Having two circuit types does not mean that two shots suffice. Each must be repeated to estimate its probability to the required precision. A complicated reference or residual also makes its inverse circuit expensive. The original paper additionally compares signed-overlap measurements, classical shadows, and flagged CU. Methods that handle both probabilities in a single circuit require their own covariance and circuit-cost calculations. [1, §2.4; S3–S4]

## 5. A two-level example to work out by hand

Let us set aside the real molecule for a moment. The following is **a verifiable educational model developed for this review**, not data from the original paper. Choose an energy gap \(\Delta=100\,{\rm mHa}\) and a reference angle \(\theta=30^\circ\).

$$
H=\begin{pmatrix}0&0\\0&\Delta\end{pmatrix},\quad
\lvert\Psi_0\rangle=\begin{pmatrix}1\\0\end{pmatrix},\quad
\lvert\Phi\rangle=\begin{pmatrix}\cos\theta\\\sin\theta\end{pmatrix}.
$$

Direct multiplication and subtraction of the parallel component give

$$
E_\Phi=\Delta\sin^2\theta,\quad
r_\Phi=\Delta\sin\theta\cos\theta,\quad
\lvert\Lambda\rangle=\begin{pmatrix}-\sin\theta\\\cos\theta\end{pmatrix}
$$

for \(0<\theta<\pi/2\) and \(\Delta>0\). Thus \(q=\cos^2\theta\) and \(p=\sin^2\theta\), so

$$
E_{\rm ME}=\Delta\sin^2\theta
-\Delta\sin\theta\cos\theta\sqrt{\frac{\sin^2\theta}{\cos^2\theta}}=0.
$$

| Quantity | Value in the educational example | Meaning |
|---|---:|---|
| Reference energy \(E_\Phi\) | 25 mHa | Energy obtained from the reference alone |
| Residual magnitude \(r_\Phi\) | 43.301270 mHa | Residual norm with units of energy |
| Reference probability \(q\) | 0.75 | Squared target–reference overlap |
| Residual probability \(p\) | 0.25 | Squared target–residual overlap |
| Correction \(-r_\Phi\sqrt{p/q}\) | −25 mHa | Correction using the sign condition |
| Mixed estimator | 0 mHa | Exact target eigenvalue |

<figure><img src="two_level_model_en.svg" alt="A reference at 30 degrees is projected in a two-level system with energies 0 and 100 mHa, yielding a 25 mHa reference energy and a negative correction."><figcaption>A two-level educational model developed for this review. Δ=100 mHa and θ=30° are illustrative choices, not parameters or observations for the Ru molecule or Helios. The matrix products, probabilities, and variance in the text were checked against independent numerical calculations.</figcaption></figure>

<!-- TWO_LEVEL_EXPLORER -->

In this example, \(p+q=1\). In a general Hilbert space, the target can have components outside the plane spanned by \(\Phi,\Lambda\), giving \(p+q\le1\); equality cannot be assumed. If equality is already known in this restricted model, one probability could be inferred from the other. We assume separate measurements here to practice the statistics of two independent CU circuits; the model establishes neither an optimal measurement protocol nor quantum acceleration. Also, at \(\theta=0\) the residual vanishes, so no residual state is defined. At \(\theta=90^\circ\), \(q=0\), and the mixed estimator itself cannot be used.

### Counterexample 1: even an exact target gives the wrong answer if the sign is wrong

Change the target to the excited state \(\lvert\Psi_1\rangle=(0,1)^T\). With the same reference, \(s=1/2\) and \(h=\sqrt3/2\). The signed ratio gives the correct result, \(25+75=100\,{\rm mHa}\). Forcing the negative branch instead gives \(25-75=-50\,{\rm mHa}\). The probability measurement is not at fault: **the sign assumption used to interpret those probabilities is wrong.**

### Counterexample 2: an approximate target can give an energy below the ground state

Tilt the target slightly to \(\lvert\Psi_\eta\rangle=(\cos\eta,\sin\eta)^T\), with \(\eta=-5^\circ\). Then

$$
E_{\rm ME}(\eta)=\frac{\Delta\sin\theta\sin\eta}{\cos(\theta-\eta)}
\simeq-5.319876\,{\rm mHa}.
$$

The ordinary expectation value in that state is \(\Delta\sin^2\eta\simeq0.759612\,{\rm mHa}\), above the ground-state energy. The mixed estimator, by contrast, lies below zero. Thus a mixed estimator for an approximate target is generally not a variational upper bound. A lower number is not evidence of a better wavefunction. This counterexample is an educational calculation isolating a mathematical property, not a reproduction of an error in the paper's experiments.

### Why use this method with an approximate target, then?

Let the exact target eigenstate be \(\Psi_0\), with energy \(E_0\). Align the phases and write \(\Psi=\Psi_0+\delta\Psi\) and \(\Phi=\Psi_0+\delta\Phi\). Subtracting \(E_0s\) from the numerator gives the identity

$$
E_{\rm ME}-E_0
=\frac{\langle\delta\Psi|(H-E_0)|\delta\Phi\rangle}
{\langle\Psi|\Phi\rangle}.
$$

The cross terms containing the exact eigenvector vanish. If both the reference and target are good and the denominator is sufficiently large, the error depends on the product of the two state errors. This explains why a good classical reference can ease the demands on target preparation. If either state is poor or the denominator is small, however, there is no guarantee of a benefit. This identity was expanded directly for the review as an explanation; it is not a theorem guaranteeing improved performance for every molecule.

## 6. Statistics of the two probabilities: where should we spend more shots?

Suppose independent Bernoulli measurements estimate the residual probability \(p\) with \(N_p\) shots and the reference probability \(q\) with \(N_q\) shots. Treat \(E_\Phi,r_\Phi\) as exactly known constants. Differentiating \(f(p,q)=E_\Phi-r_\Phi\sqrt{p/q}\) gives

$$
\frac{\partial f}{\partial p}=-\frac{r_\Phi}{2\sqrt{pq}},\qquad
\frac{\partial f}{\partial q}=\frac{r_\Phi\sqrt p}{2q^{3/2}}.
$$

First-order error propagation for large samples yields

$$
\sigma_E^2\simeq\frac{r_\Phi^2}{4}
\left[\frac{1-p}{qN_p}+\frac{p(1-q)}{q^2N_q}\right]
=\frac A{N_p}+\frac B{N_q}.
$$

Here \(A=r_\Phi^2(1-p)/(4q)\) and \(B=r_\Phi^2p(1-q)/(4q^2)\) have units of energy squared. We derived this expression directly using the same assumptions as the CU variance in S4 of the original paper. A small \(q\) destabilizes the denominator statistics. If the denominator event is never observed in any shot, this approximation cannot even be evaluated. Boundary probabilities and small samples require attention to the bias of the nonlinear ratio, bootstrap methods or confidence intervals, and the treatment of zero counts. [1, S4.4; S4.8–S4.9]

With a fixed total of accepted shots \(N=N_p+N_q\) and equal cost for the two types, the Cauchy–Schwarz inequality or Lagrange multipliers give

$$
N_p:N_q=\sqrt A:\sqrt B,\qquad
\sigma_{E,\min}^2=\frac{(\sqrt A+\sqrt B)^2}{N}
$$

Simply splitting the budget equally between the two circuits is not generally optimal.

In the baseline two-level example, \(A=468.75\) and \(B=52.083333\) mHa². Allocating 10,000 accepted shots as 7,500 residual shots and 2,500 reference shots predicts a standard error of **0.288675 mHa**, compared with **0.322749 mHa** for an equal split. These are independent educational calculations, not a reoptimization of the paper's 2,000:8,000 allocation.

Different time costs change the answer. If the average costs per accepted shot are \(c_p,c_q\), the allocation minimizing time at a fixed precision satisfies

$$
\frac{N_p}{N_q}=\sqrt{\frac{Ac_q}{Bc_p}}.
$$

In a simple model with a fixed cost per attempt, acceptance rate \(\alpha_j\), and time \(\tau_j\) per submitted shot, \(c_j\simeq\tau_j/\alpha_j\). In practice, preparation, inverse circuits, measurement, and reset take different times; early termination, calibration, and waiting can add further costs. **Minimizing shots and minimizing time are different optimization problems.**

## 7. Reading the experiment: 400 and 10,000 are different comparisons

The approximately 400 CU shots in Fig. 6(d) are an **estimate from ideal variances** for reaching 1.6 mHa at a specific \((6,6)\) geometry and sparse-reference setting. The same figure gives approximately 40,000 shots for a single-determinant, classical-shadow method and 694,194 shots for grouped Pauli measurements. Because both the reference state and measurement protocol change, this is not a single-factor ablation showing “a hundredfold improvement from changing only the sparse reference.” The CASCI variances used for the Pauli baseline must also be distinguished from the selected approximate-target conditions for CU. [1, §2.4; Fig. 6; Table S7]

The actual \((10,10)\) Helios experiment used 2,000 reference-circuit shots plus 8,000 residual-circuit shots per geometry: **10,000 submitted shots in total**. It reported standard errors of 1.66–1.73 mHa for individual energies. The conditions differ in active-space size, device noise, postselection, and preparation circuits. Consequently, the statement “performance became 25 times worse, going from 400 to 10,000” is also unsupported. [1, Table 1; Fig. 8]

Constructing the energy difference between two geometries requires this budget twice, for 20,000 submitted shots in total. The precision target for each individual energy must also be distinguished from the precision target for the difference itself.

<figure><img src="evidence_conditions_en.svg" alt="Panels distinguish an ideal 400-shot estimate for the 6,6 active space from a physical experiment with 10,000 submitted shots in the 10,10 active space, separating standard error from central-value deviation."><figcaption>Conditions reconstructed separately from Fig. 6, Table 1, and Fig. 8 of the original paper. The numbers 400 and 10,000 do not form a speed ratio for the same workload. Standard error describes finite-sample precision; deviation from CASCI describes central-value agreement. These are not results from an independent rerun of the original experiment. [1]</figcaption></figure>

Another large number is 50 qubits. The \((10,10)\) data register contains 20 qubits. Leakage detection alone uses 20 qubits in total; coherent parity checks (CPC) use 22; and measurement-based parity checks (MBPC) use 20 data qubits plus 30 auxiliary qubits, or 50 in total. Additional auxiliary checks do not imply a larger electronic active space, and stronger checks did not always improve the final energy difference. [1, §4.5; Table 1]

## 8. Postselection changes numerator and denominator together

Consider part of the Helios-1 \(R_x\), \((10,10)\) results in Table 1 of the paper. The probabilities below are all-zero probabilities conditioned on shots passing the checks. The \(s\) circuit measures the reference overlap; the \(h\) circuit measures the residual overlap.

| Checks | Total qubits | Reference/residual acceptance | \(q=p_\Phi\) | \(p=p_\Lambda\) | \(\sqrt{p/q}\) |
|---|---:|---|---:|---:|---:|
| Leakage | 20 | 92.4% / 85.7% | 0.7829 ± 0.0096 | 0.0733 ± 0.0031 | 0.3059 ± 0.0068 |
| Leakage + CPC | 22 | 86.5% / 78.8% | 0.8242 ± 0.0092 | 0.0782 ± 0.0034 | 0.3080 ± 0.0069 |
| Leakage + MBPC | 50 | 85.2% / 78.8% | 0.8256 ± 0.0092 | 0.0773 ± 0.0034 | 0.3059 ± 0.0069 |

The uncertainties are one standard error as reported in the paper. For example, the leakage-only accepted counts are approximately \(2000\times0.924=1848\) and \(8000\times0.857=6856\). Because the published rates are rounded, these are approximations calculated from reported acceptance rates, not newly obtained raw integer counts. When calculating standard errors for conditional probabilities, 2,000 and 8,000 must not simply be used as the accepted denominators.

Suppose noise changes the two probabilities to \(p(1+\epsilon_p),q(1+\epsilon_q)\). A first-order expansion in small relative errors gives

$$
\sqrt{\frac{p(1+\epsilon_p)}{q(1+\epsilon_q)}}
\simeq\sqrt{p/q}\left[1+\frac{\epsilon_p-\epsilon_q}{2}\right]
$$

Common relative errors can partly cancel in the ratio, but a check that improves only one probability more strongly can move the ratio farther from its ideal value. Improving quantum measurement probabilities and improving the final energy constructed from those probabilities are distinct claims.

The same distinction applies to the difference between two geometries, \(\Delta E=E_x-E_0\). If the central-value biases are \(b_x,b_0\), the bias of the difference is \(b_x-b_0\). The sampling variance, by contrast, is

$$
\operatorname{Var}(\widehat{\Delta E})
=\sigma_x^2+\sigma_0^2-2\operatorname{Cov}(\widehat E_x,\widehat E_0)
$$

Even if the statistical covariance is zero for independent shot experiments, common device errors can partly cancel in the central-value biases. These two kinds of “cancellation” must not be confused.

The original paper reports deviations from CASCI of approximately 0.5–13 mHa for individual emulator and hardware energies, and approximately 0.2–9 mHa for energy differences. These ranges collect results across several conditions; they are not error bars for one specific setting. Parity checks on Helios-1 did not consistently improve the final energy difference. **Obtaining a standard error of approximately 1.7 mHa does not guarantee that the value lies within 1.7 mHa of CASCI.** [1, Fig. 8]

Let us calculate one actual pair of values. Subtracting the Helios-1 leakage-only central estimates in Table S8 gives \(\Delta E=-3.676\,{\rm mHa}\); propagating independent standard errors gives approximately 2.392 mHa. The corresponding CASCI difference in Table S6 is approximately +0.119 mHa, so the central-value discrepancy is −3.795 mHa. This is **an arithmetic comparison made for the review** using rounded values from the published tables, not a new hardware measurement. This discrepancy alone also cannot establish a particular physical noise mechanism or support a claim of statistical significance. [1, Tables S6; S8]

## 9. After reducing readout cost: the different question asked by SVD-THC

So far, we have read the energy of a prepared state at one geometry. Reaction paths and conformational landscapes require Hamiltonians for thousands of geometries. The SVD-THC method of Cortes and colleagues finds a common low-rank representation of geometry-dependent electronic integrals and packages the ensemble into a single multiplexed block encoding. This is **input and resource design** for future fault-tolerant quantum circuits. It addresses a different execution stage from measurement reduction in the present Helios experiment. [2]

| Comparison for 5,184 alanine geometries | Circuit qubits | Toffoli reduction relative to sliced-THC |
|---|---:|---:|
| sliced-THC baseline | 1,191 | 1× |
| SVD-THC, Toffoli-optimal | 8,498 | Approximately 201× |
| SVD-THC, qubit-comparable | 1,330 | 108× |

The 8,498-qubit setting gives an active-volume improvement of 22.1×. Toffoli counts alone do not capture Clifford operations, data movement, and other costs. This is a proof of concept in the minimal STO-3G basis. The reported accuracy below 0.6 mHa is a compression and truncation error measured against the CCSD correlation energy of the uncompressed Hamiltonian. It does not guarantee the true molecular energy or physical-device performance. [2, Tables VI–VII]

This comparison does not justify multiplying the two papers' reduction factors. It establishes that **the cost of supplying geometries, the cost of preparing states, and the cost of reading the desired quantity all remain**. For small ensembles, fixed compression costs may erase the benefit. Total costs must be recalculated at the same chemical accuracy and under the same execution model.

<figure><img src="cost_chain_en.svg" alt="A workflow connects electronic structure and reference construction, circuit synthesis, quantum preparation and overlap measurement, postselection, and energy-difference calculation to assess total cost."><figcaption>A workflow constructed for this review by connecting the two papers. Time, memory, and acceptance rates must be measured separately at each stage. This is not a pipeline that has validated OLED or catalyst performance, or a speedup from combining the two methods. [1,2]</figcaption></figure>

## 10. What should the next study show?

The achievement is that jointly designing a sparse reference and direct overlap measurements can reduce measurement variance, and that the authors tested the approach on a physical trapped-ion device. The study does not establish converged molecular reaction rates, improved OLED emitter performance, or a total-time advantage over strong classical methods.

Follow-up experiments should jointly report reference size, target-preparation depth, submitted and accepted shots, circuit time, classical preprocessing, and bias at the same geometry, basis, active space, and target error. Classical comparisons, such as CASSCF/NEVPT2 and selected CI, should also address the same physical problem at matched accuracy. The paper's AI-assisted steps are classical optimization components that select sparse support and circuits; their costs remain part of the calculation.

Application to OLEDs and photoactive transition-metal molecules is **a follow-up proposal from this review**. Initial tests could ask whether the reference maintains good overlap along a torsional path, whether the same sign and symmetry assumptions hold as electronic-state character changes, and whether the comparison survives inclusion of dynamic correlation and environmental effects. The paper should not be described as validating OLED devices or therapeutic efficacy.

These results leave three questions for further work.

1. What does a “better reference” optimize: lower variational energy, a smaller residual, larger target overlap, or a shorter preparation circuit? Can you construct an example in which these goals conflict?
2. If an accurate energy difference results from fortuitous cancellation of device biases, what tests would establish whether it remains reliable at other geometries?
3. Could comparing total time at equal precision change the ranking of CU, classical shadows, and Pauli measurements? What changes when several references can be reused?

## 11. Exercises with worked solutions

### Exercise 1 — Derive the residual norm

For normalized \(\Phi\), set \(R=(H-E_\Phi)\Phi\) and derive \(r_\Phi^2=\langle H^2\rangle_\Phi-E_\Phi^2\). Explain what \(r_\Phi=0\) means and whether it guarantees the desired ground state.

**Solution.** Since \(\langle(H-E_\Phi)^2\rangle=\langle H^2\rangle-2E_\Phi\langle H\rangle+E_\Phi^2\) and \(\langle H\rangle=E_\Phi\), the result follows. Zero variance means \((H-E_\Phi)\Phi=0\): the reference is an eigenstate. It does not guarantee that it is the lowest eigenstate in the desired symmetry sector. When the residual vanishes, \(\Lambda=R/r_\Phi\) is not defined.

### Exercise 2 — Find the sign for an exact excited state

In the two-level model, choose the target \(\Psi_1=(0,1)^T\) and calculate \(s,h,E_{\rm ME}\). Why does applying the negative-square-root formula give −50 mHa?

**Solution.** We have \(s=\sin30^\circ=1/2\) and \(h=\cos30^\circ=\sqrt3/2\), so the signed ratio is \(\sqrt3\). The energy is \(25+43.301270\sqrt3=100\) mHa. Measuring only the probabilities and forcing the negative sign instead subtracts the same correction magnitude, 75, giving −50. The assumption that the target is the lowest state in the relevant space has failed.

### Exercise 3 — Allocate a fixed shot budget optimally

Allocate 10,000 accepted shots in the baseline two-level model. If an accepted shot of the residual circuit costs four times as much as one of the reference circuit, how does the time-minimizing allocation ratio change?

**Solution.** Since \(A/B=9\), equal costs give \(N_p/N_q=3\), or 7,500:2,500, with a standard error of 0.288675 mHa. If \(c_p=4c_q\), then \(N_p/N_q=\sqrt{9/4}=1.5\). This ratio minimizes time at the target precision; it must be distinguished from the ratio that minimizes variance at a fixed total of 10,000 shots.

### Exercise 4 — Separate acceptance rates from uncertainty in an energy difference

Submit 2,000 reference shots and 8,000 residual shots, accepting 90% and 80%, respectively. Find the expected accepted counts. If the independent statistical standard errors of two geometries are both 1.7 mHa, what is the standard error of their difference? If their central-value biases are +8 and +6 mHa, what is the bias of the difference?

**Solution.** The expected accepted counts are 1,800 and 6,400. The statistical standard error is \(\sqrt{1.7^2+1.7^2}=2.404163\) mHa. The bias of the difference is +2 mHa. A small bias and a small sampling error bar are separate properties. This example does not reproduce the paper's raw counts.

### Exercise 5 — Evaluate the claim of a 201-fold improvement

Correct a sentence that describes the 201-fold SVD-THC improvement as a physical runtime improvement. Include the setting with a comparable number of qubits and another cost metric.

**Solution.** “For the specified energy-thresholding circuit on 5,184 alanine geometries, Toffoli-optimal SVD-THC requires approximately 201 times fewer Toffoli gates than sliced-THC, but increases the circuit-qubit count from 1,191 to 8,498. The 1,330-qubit setting reduces Toffoli count by 108×, while the 8,498-qubit setting improves active volume by 22.1×. This is not a measurement of total physical runtime including error correction, factories, and waiting.” A combined speedup for the two papers cannot be calculated from these figures either.

## 12. Return to the opening question

Even an exact energy eigenstate leaves a statistical cost when we use a readily implementable measurement procedure. By separating the part already known through a sparse reference, we can read an energy correction from the target's relationships with the reference and residual. We must still check the eigenstate, symmetry, sign, and nonzero-denominator assumptions, the costs of actual preparation circuits and shots, and device bias.

**A good quantum-chemical energy estimator needs an algebraically correct formula, an executable measurement, and a trustworthy account of uncertainty together.** This study offers a concrete case in which all three can be examined within the same experiment.

## References and further reading

1. Lenihan et al. [Measurement-efficient energy estimator for quantum chemistry of photodynamic materials](https://arxiv.org/abs/2610.26689v1), arXiv:2610.26689v1, October 19, 2026. [Full HTML and supplementary information](https://arxiv.org/html/2610.26689v1). Key locations: §2.1, equations (1)–(4); §2.2, symmetry and active spaces; §2.4, Fig. 6; §2.5, Table 1 and Fig. 8; Methods §4.5–4.6; S4, variance, allocation, and time; S5, hardware results. These are author-reported results; the original experiments were not independently reproduced.
2. Cortes et al. [Efficient Block Encodings for Ensembles of Molecular Hamiltonians](https://arxiv.org/abs/2610.25968v1), arXiv:2610.25968v1, October 19, 2026. [Full HTML](https://arxiv.org/html/2610.25968v1). §V–VI, Tables VI–VII, and Appendix C. These are logical-circuit resource estimates, separate from the Helios experiments.
3. NIST/CODATA. [2022 recommended fundamental constants](https://physics.nist.gov/cuu/pdf/all.pdf). The thermal-sensitivity example in the text was calculated directly for this review using the Hartree–eV conversion and Boltzmann constant.
4. [Public archive of the October 21 DQB](https://infant83.github.io/AI_Tech_Review/archive/files/2026-10-21-daily-quantum-brief.pdf). This was the starting point for identifying this review's topic. For further foundational study, see the [independent study notes on quantum machine learning](https://infant83.github.io/AI_Tech_Review/lectures/quantum-machine-learning/).

The equations, two-level examples, and numerical calculations of optimal shot allocation were checked with code developed for this review. These checks verify the educational mathematics; they do not constitute independent reruns of the Ru molecule's electronic structure, the paper's optimization and device circuits, or its QPU shots. The generated cover is a conceptual illustration. The exact structures and numerical values in the explanatory figures and exercises were produced deterministically.
