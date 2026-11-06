# The Physics Behind Quantum Circuits

<p class="dek">From single-qubit rotations to interactions and answer probabilities</p>

<figure class="hero"><img src="hero.webp" alt="A colourful painted print connects parallel and opposite arrow pairs with offset circular bands and a central pattern of strong and weak interference."><figcaption>Parallel and opposite arrow pairs lead into offset arcs and contrasting interference patterns. This AI-generated conceptual illustration evokes phases assigned according to the relation between two qubit values, then used in interference to affect outcome probabilities. Angles and brightness are not computed data.</figcaption></figure>

When we draw a quantum circuit, small boxes line up along the wires: a gate that rotates one qubit, a CNOT connecting two qubits, then another rotation. A few lines of code run the circuit and return a result. Explaining why the boxes belong in that order can be harder. What has rotated? What relationship has formed between the qubits? Where does that change enter the problem we want to solve?

A short derivation shared by Daniel Buchta offers a useful way into these questions. Place a single-qubit Z rotation between two CNOT gates, and the combination implements a two-qubit ZZ interaction. His post connects this identity to Hamiltonian simulation and variational quantum algorithms. [1] An operation that changes the phase of one qubit becomes a coupling between two qubits.

The language of physics helps us follow what happens. Energy differences become phase differences as time passes. Those phase differences change how amplitudes add and cancel in later operations. At the final measurement, the difference appears in the probabilities of the outcomes. We will follow that connection through a complete calculation for the smallest two-qubit problem.

## What does a rotation change in a quantum state?

Write a qubit state as \(\alpha|0\rangle+\beta|1\rangle\). The complex numbers \(\alpha,\beta\) are the amplitudes of its two components. A measurement in the Z basis, which distinguishes 0 from 1, gives probabilities \(|\alpha|^2,|\beta|^2\), whose sum is 1. A complex amplitude's magnitude determines a probability; its direction, or phase, determines how it adds to other amplitudes.

Start by applying a Hadamard gate \(H_{\mathrm{Had}}\) to \(|0\rangle\):

$$|+\rangle=H_{\mathrm{Had}}|0\rangle=\frac{|0\rangle+|1\rangle}{\sqrt2}.$$

The two components have the same magnitude and phase, and each measurement outcome has probability 1/2. Now apply a Z rotation through an angle \(\phi\). Z is the Pauli operator with eigenvalue +1 on \(|0\rangle\) and −1 on \(|1\rangle\). [2]

$$R_z(\phi)=e^{-i\phi Z/2},\qquad
R_z(\phi)|+\rangle=\frac{e^{-i\phi/2}|0\rangle+e^{i\phi/2}|1\rangle}{\sqrt2}.$$

Both amplitudes still have magnitude \(1/\sqrt2\), so the Z-basis probabilities stay the same. What changes is the **relative phase \(\phi\) between the two components**. Multiplying the entire state by one common phase factor would turn all its amplitudes together. Here, the directions of the two components change relative to each other.

To read that difference, we need an operation that brings the components together again. Applying another Hadamard makes the amplitude leading to 0 depend on their sum, and the amplitude leading to 1 depend on their difference:

$$H_{\mathrm{Had}}R_z(\phi)H_{\mathrm{Had}}|0\rangle
=\cos\frac{\phi}{2}|0\rangle-i\sin\frac{\phi}{2}|1\rangle.$$

Thus \(P(0)=\cos^2(\phi/2)\) and \(P(1)=\sin^2(\phi/2)\). At \(\phi=0\), we always read 0; at \(\phi=\pi\), we always read 1. The probabilities that remained equal immediately after the middle rotation become different after the final Hadamard. **Interference is the addition or cancellation of amplitudes leading to an outcome, according to their phases.**

In Figure 1, follow the lengths of the arrows separately from their directions. After Rz, their lengths stay equal while their directions separate. After the last Hadamard, that difference in direction appears as a difference in the heights of the probability bars.

<figure><img src="phase_readout_en.svg" alt="Relative phase and measurement probabilities for a qubit passing through a Hadamard, a Z rotation, and another Hadamard. Probabilities that remain equal after the phase rotation change after the final operation."><figcaption>Figure 1. An ideal educational calculation of how a single-qubit phase affects measured probabilities. Immediately after Rz(φ), both Z-basis probabilities are 1/2. After the last Hadamard, P(0)=cos²(φ/2) and P(1)=sin²(φ/2). An amplitude arrow's length represents its magnitude, and its direction represents its phase. The Rz definition follows Ref. [2].</figcaption></figure>

On the Bloch sphere, this state is a point on the surface. The north and south poles represent \(|0\rangle,|1\rangle\), and the relative phase of the two components determines its position around the equator. A Z rotation turns that position around the axis. This geometry represents the relationship between two state components. In a physical device, the chosen pair of energy levels and the drive implement the rotation in state space. A Y rotation starting from \(|0\rangle\) produces \(\cos(\theta/2)|0\rangle+\sin(\theta/2)|1\rangle\), so in this case the Z measurement probabilities also change with the rotation angle.

## Giving equal and unequal bit pairs different phases

With two qubits, the state has four components: \(|00\rangle,|01\rangle,|10\rangle,|11\rangle\). Label the first bit \(a\) and the second \(b\), and choose a as the CNOT control and b as its target. CNOT flips b in the components where a is 1. In bit notation, \((a,b)\mapsto(a,a\oplus b)\), where \(\oplus\) is exclusive OR: 1 for unequal values and 0 for equal ones.

After the first CNOT, b holds the parity of the original pair. For original inputs `00` and `11`, b is now 0; for `01` and `10`, it is 1. Applying \(R_z(\theta)\) to b multiplies equal-bit components by \(e^{-i\theta/2}\) and unequal-bit components by \(e^{i\theta/2}\). The last CNOT restores the original bit arrangement. The phase given to each component remains.

| Original bits | After first CNOT | Phase factor from rotation | After last CNOT |
|---|---|---|---|
| 00 | 00 | \(e^{-i\theta/2}\) | 00 |
| 01 | 01 | \(e^{i\theta/2}\) | 01 |
| 10 | 11 | \(e^{i\theta/2}\) | 10 |
| 11 | 10 | \(e^{-i\theta/2}\) | 11 |

In a superposition, all four components follow this rule together, with no intermediate parity measurement. We can express the combined operation using the eigenvalues of ZZ. \(Z_aZ_b\) assigns +1 to `00` and `11`, and −1 to `01` and `10`. Therefore, [3]

$$\mathrm{CX}_{a\to b}(I\otimes R_z(\theta))\mathrm{CX}_{a\to b}
=e^{-i\theta Z_aZ_b/2}=R_{ZZ}(\theta).$$

The rightmost operator acts first. In the circuit, the execution order is the first CNOT, Rz on b, then the last CNOT. A phase operation on one qubit has become a **phase that depends on the relationship between two qubit values**. The CNOTs supply the two-qubit operations needed for this construction.

Follow the four paths in Figure 2 from top to bottom. Restoring the bit arrangement and reversing the phase are different operations. The relation can be condensed into the operator identity \(\mathrm{CX}(I\otimes Z)\mathrm{CX}=Z\otimes Z\). Conjugation turns a generator acting on one position into a generator acting jointly on two.

<figure><img src="parity_interaction_en.svg" alt="The four basis states pass through a first CNOT that puts parity in the target, an Rz that assigns parity-dependent phases, and a last CNOT that restores the bit arrangement."><figcaption>Figure 2. The action of CNOT–Rz–CNOT, with control a and target b. Equal-bit inputs 00 and 11 acquire a phase with the opposite sign to unequal-bit inputs 01 and 10. The final bit arrangement is restored. The basis order is 00, 01, 10, 11. The circuit and phases are reconstructed directly from the RZZ definition in Ref. [3].</figcaption></figure>

This operation can entangle two qubits in superposition. Applied to \(|++\rangle\), it leaves all four amplitude magnitudes at 1/2 but creates a relative phase between the equal-bit and unequal-bit components. At \(\theta=\pi/2\), the two qubits become maximally entangled. At \(\theta=\pi\), however, \(R_{ZZ}(\pi)=-iZ\otimes Z\), which separates into two local Z operations. Both the phase pattern and the input state determine entanglement.

## Why does an energy difference become a rotation?

Consider two spins coupled through an Ising interaction. Taking Pauli eigenvalues to be ±1, define the coupling as

$$\mathcal H_{\mathrm{Ising}}=JZ_aZ_b$$

The coupling constant \(J\) has units of energy. For \(J>0\), `00` and `11`, with equal Z values, have energy +J. The opposite configurations `01` and `10` have energy −J. This is an antiferromagnetic coupling: opposite configurations have lower energy.

In quantum mechanics, a component with energy E acquires a phase \(e^{-iEt/\hbar}\) over time t. The four components of the two-spin state accumulate phases in different directions according to their energies. Comparing this time evolution with the gate above gives

$$U(t)=e^{-i\mathcal H_{\mathrm{Ising}}t/\hbar}
=R_{ZZ}\!\left(\frac{2Jt}{\hbar}\right).$$

The rotation angle \(\theta=2Jt/\hbar\) is dimensionless. The factor of 2 follows from using Pauli operators and the convention \(R_{ZZ}(\theta)=e^{-i\theta ZZ/2}\). Writing the Hamiltonian in terms of physical spin operators \(S_z=\hbar Z/2\) would put those factors into the definition of the coupling constant as well.

**The rotation angle contains the coupling strength and how long it acts.** This is why a circuit can represent a physical system's time evolution. Once we choose the time t to simulate, the required angle is fixed. The device implements that transformation using its available native gates. Decomposition into two CNOTs is one way to do so. The device's actual drive duration and the simulated system's time t are related through their respective Hamiltonians and the control method.

A transverse term \(h(X_a+X_b)\) would also require X rotations. The ZZ term distinguishes equal from unequal spin values; the X terms mix Z states. These operators generally do not commute, so their order affects the result. Our [review of observable-aware quantum dynamics](https://infant83.io/AI_Tech_Review/reviews/2026-10-26_observable-aware-quantum-dynamics/) takes up the construction of time evolution from short steps involving several terms.

## Putting a problem into a circuit

Now connect two vertices with one edge. Assign 0 or 1 to each vertex. Different assignments earn 1 point; equal assignments earn 0. This is the smallest instance of MaxCut, which divides a graph into two groups to maximize the number of edges crossing between them. The good answers are `01` and `10`.

We already know the answers. Working at this size lets us examine every intermediate state and see how a problem's condition becomes a formula and then a gate. The score for two classical bits is

$$c(a,b)=a+b-2ab$$

A bit value of 0 corresponds to Z eigenvalue +1, and a bit value of 1 to −1. Replace \(a\) by \((I-Z_a)/2\) and \(b\) by \((I-Z_b)/2\). Substitution and simplification give the score operator: [4]

$$C=\frac{I-Z_aZ_b}{2}.$$

Acting on the four bit strings, this operator returns their scores as eigenvalues: 0 for `00` and `11`, and 1 for `01` and `10`. To express score maximization as energy minimization, we could define \(\mathcal H_C=-C\). Here we keep the score-maximization convention of the original quantum approximate optimization algorithm, QAOA. [4]

Start in \(|++\rangle=(|00\rangle+|01\rangle+|10\rangle+|11\rangle)/2\). Each candidate has probability 1/4, so the chance of earning 1 point is 1/2. First apply the score-dependent phase operation \(U_C(\gamma)=e^{-i\gamma C}\), where \(\gamma\) is dimensionless. Zero-score components stay unchanged, and the components scoring 1 are multiplied by \(e^{-i\gamma}\):

$$U_C(\gamma)|++\rangle
=\frac{|00\rangle+e^{-i\gamma}|01\rangle+e^{-i\gamma}|10\rangle+|11\rangle}{2}.$$

The problem's condition is now encoded in the relative phases of the four amplitudes. We can also read off the gate to implement:

$$U_C(\gamma)=e^{-i\gamma/2}e^{i\gamma Z_aZ_b/2}
=e^{-i\gamma/2}R_{ZZ}(-\gamma).$$

Apart from the common factor \(e^{-i\gamma/2}\), this is the CNOT–Rz–CNOT circuit, with Rz angle −γ on b. The short circuit that started our discussion corresponds to the score term of the problem we chose.

All four probabilities are still 1/4. The probability of scoring 1 is still 1/2. Having written the score into phase, we now need to mix the components so that phase can affect the outcomes.

## Turning phase differences into answer probabilities

In this QAOA example, we apply an X rotation to each qubit. Using the mixing operator \(B=X_a+X_b\) and parameter \(\beta\), [4,5]

$$U_B(\beta)=e^{-i\beta B}
=R_x(2\beta)\otimes R_x(2\beta).$$

An X rotation brings each component together with other components of the Z basis. Since \(R_x(2\beta)|0\rangle=\cos\beta|0\rangle-i\sin\beta|1\rangle\), several initial bit strings contribute amplitudes to any one final two-qubit bit string. The phases they acquired in the problem phase layer change the magnitude of their sum.

Working through the small example, the probability of a good answer after both layers is

$$P(01)+P(10)=\frac{1+\sin(4\beta)\sin\gamma}{2}.$$

The two parameters set the phase difference we use and how strongly we mix the components. Choose \(\gamma=\pi/2\) and \(\beta=\pi/8\), and the product of the two sine factors is 1. The final state is

$$|\psi\rangle=-i\frac{|01\rangle+|10\rangle}{\sqrt2}.$$

We can watch one cancellation directly. After the problem phase layer at γ=π/2, write \(c=\cos\beta\) and \(s=\sin\beta\). The final amplitude of `00` receives a combined contribution \((c^2-s^2)/2\) from the original `00` and `11`, and a contribution \(-cs\) from the original `01` and `10`. Its amplitude is therefore \((\cos2\beta-\sin2\beta)/2\). At β=π/8, the two terms have equal magnitude and cancel exactly. The −i acquired in the problem phase layer and the −i from an X rotation multiply to produce the minus sign used in this cancellation.

In the ideal statevector calculation, amplitudes leading to `00` and `11` cancel, leaving `01` and `10` with probability 1/2 each. Their sum is 1, so measurement returns one of the two good answers. The success probability starts at 50%, stays at 50% immediately after the problem phase layer, and reaches 100% after mixing.

Read the phase arrows and probability bars together in Figure 3. The middle stage records phase; the final stage changes how often the answers appear. Following both makes the purpose of each layer visible. Reversing the phase and mixing layers leaves the probability of a good answer at 1/2 for this initial state. Because \(|++\rangle\) is an eigenstate of B, a mixing layer applied first only gives the entire state a common phase.

<figure><img src="problem_to_probability_en.svg" alt="The initial state, problem phase layer, and mixing layer for a problem that gives one point to unequal bits. The combined probability of good answers 01 and 10 changes from 50 percent to 50 percent to 100 percent."><figcaption>Figure 3. This review's educational calculation for single-edge MaxCut. The initial state is |++⟩, with exp(−iγC) followed by exp(−iβB), at γ=π/2 and β=π/8. After the phase layer, each of the four probabilities is 1/4. After mixing, P(01)=P(10)=1/2. The formulas and circuit conventions follow Refs. [3–5]; the numbers are calculated directly from ideal statevectors for this review.</figcaption></figure>

<!-- PHASE_WIDGET -->

In the calculation tool, start with the two-vertex example and vary γ and β. At the “After cost phases” stage, the arrows move while the probabilities stay fixed. At “After X mixers,” the same angle changes appear in the probability bars. You can also compare γ=0 or β=0. The reset button restores the angles used in the calculation above.

How do we find useful angles for a larger problem? One measurement gives one bit string. We prepare and measure the same circuit repeatedly to estimate its mean score, and a classical optimizer uses that estimate to update the angles. QAOA repeats this process with circuits built from alternating problem phase and mixing layers. We chose good angles analytically for the small example. For larger graphs, that search becomes an important part of the algorithm's cost. [4]

## More couplings call for a new choice of angles

Choose the triangle in the calculation tool, and three bits are joined by three edges. The score sums the contribution of each edge: \(C_\triangle=\sum_{(i,j)}(I-Z_iZ_j)/2\). Once two spins point oppositely, the remaining spin cannot satisfy both its neighbors. This is the familiar frustration of an antiferromagnetic triangle. The maximum score is 2, reached by all six bit strings other than `000` and `111`.

Applying the same RZZ building block to each edge makes the problem phase layer. The angles must now be chosen for this coupling structure. Reusing \(\gamma=\pi/2,\beta=\pi/8\) lowers the ideal calculation's mean score from an initial 1.5 to 0.75. Choosing angles suited to the triangle,

$$\gamma=\arctan(1/\sqrt2),\qquad \beta=\gamma/2$$

instead reaches a mean score of 2 with the same single layer. Each of the six optimal answers has probability 1/6. Comparing the two sets of example angles in the tool shows why a change in coupling structure calls for a new design of phases and interference.

The ZZ terms on different edges commute, so this example's problem phase layer factors exactly into a product of edgewise RZZ gates. Whether two gates sharing a qubit can run at the same time depends on the device's controls. When the problem graph differs from the device's connectivity, additional operations to move qubits may also be needed. Mathematical decomposition and physical circuit depth both enter the design.

## What a researcher should read in a circuit

Even for the same rotation gate, the way we set its angle depends on the algorithm's purpose. Hamiltonian simulation matches angles to given coupling constants and the time to simulate. QAOA searches for angles that increase the mean score. A variational quantum eigensolver, VQE, searches the angles of a circuit-prepared state \(|\psi(\boldsymbol\theta)\rangle\) to lower its energy \(\langle\psi|\mathcal H|\psi\rangle\). Its variational principle makes the energy of a normalized trial state an upper bound on the ground-state energy. [6]

We can read the family of states a circuit can prepare as its ansatz: the assumed form of the states to explore. The positions of Rz and Rx gates, and the choice of qubits to connect, determine which states are accessible. Preserving a physical system's particle number or symmetries in the circuit can reduce the search space. If operations needed to create the correlations of interest are missing, even successful optimization may struggle to reach the desired state. The judgment used to choose wavefunction forms and variational degrees of freedom in computational condensed-matter physics carries over to circuit design.

A universality theorem states that arbitrary single-qubit operations combined with CNOT can construct arbitrary unitary transformations on several qubits. [7] Turning that possibility into an algorithm requires using problem structure to implement the needed transformation with few resources. We must choose an error tolerance and circuit depth, count angle-search iterations and measurement shots, and compare time and cost against classical computation at the same target accuracy. In our small two-qubit calculation, we evaluated every amplitude directly. Evaluating performance for a larger problem requires specifying its scale and comparison method.

Several calculations can help us check a circuit before tuning its angles. Compare the classical scores with the score operator's eigenvalues on small inputs. Compute intermediate states to see where phases and probabilities change. Set parameters to zero, reverse operation order, and check that intended symmetries hold. Two-qubit Z measurement distributions can match those of a mixture whose coherence has been lost; checking entanglement therefore requires correlations in other bases or an appropriate witness as well. In an educational calculation with a known statevector, we can check factorization directly.

The same questions help us read circuits proposed or generated by AI. Which terms do they implement? Which symmetries do they preserve? What does the measured quantity mean in the original problem? This is also the connection between candidate generation and checking discussed in our [review of automated circuit design](https://infant83.io/AI_Tech_Review/reviews/2026-10-19_generative-ai-quantum-circuit-design/). Interpreting a short piece of circuit code calls for expertise that considers the problem, state, and observables together.

Return to CNOT–Rz–CNOT, and the small boxes have acquired meaning. The first CNOT puts the relationship between two values in the target. The rotation assigns a phase to that relationship. The final CNOT restores the original bit arrangement. When subsequent operations suited to the problem use that phase in interference, answer probabilities change. **Choosing which differences to record as phase, and in which observable to read them**, gives a concrete place to begin designing a quantum circuit.

<p class="computation-note">Calculations and reproducibility: The probabilities and intermediate states in this article are ideal statevector educational calculations using NumPy 2.0.2. [8] The <a href="https://github.com/Infant83/AI_Tech_Review/blob/main/2026-11-04_quantum-gates-phase-and-interaction/artifacts/check_examples.py">checking code</a> and <a href="https://github.com/Infant83/AI_Tech_Review/blob/main/2026-11-04_quantum-gates-phase-and-interaction/artifacts/example-checks.json">calculation record</a> are provided. Figures use the same gate conventions, and the tool updates states directly in the browser. For single-qubit foundations, see the <a href="https://infant83.io/AI_Tech_Review/lectures/quantum-machine-learning/">quantum machine-learning lecture notes</a>.</p>

## References

1. D. Buchta, [A small identity in quantum computing can tell a surprisingly big story](https://www.linkedin.com/posts/daniel-buchta-4355b1b6_quantumcomputing-qiskit-vqe-activity-7523623075221757952-uFeg), LinkedIn (4 November 2026) (accessed 5 November 2026).

2. IBM Quantum, [RZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZGate) (accessed 5 November 2026).

3. IBM Quantum, [RZZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZZGate) (accessed 5 November 2026).

4. E. Farhi, J. Goldstone, and S. Gutmann, A quantum approximate optimization algorithm, [arXiv:1411.4028v1](https://arxiv.org/abs/1411.4028v1) (2014).

5. IBM Quantum, [RXGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RXGate) (accessed 5 November 2026).

6. A. Peruzzo, J. McClean, P. Shadbolt, M.-H. Yung, X.-Q. Zhou, P. J. Love, A. Aspuru-Guzik, and J. L. O’Brien, A variational eigenvalue solver on a photonic quantum processor, [Nat. Commun. **5**, 4213 (2014)](https://doi.org/10.1038/ncomms5213).

7. A. Barenco, C. H. Bennett, R. Cleve, D. P. DiVincenzo, N. Margolus, P. Shor, T. Sleator, J. A. Smolin, and H. Weinfurter, Elementary gates for quantum computation, [Phys. Rev. A **52**, 3457 (1995)](https://doi.org/10.1103/PhysRevA.52.3457).

8. C. R. Harris *et al.*, Array programming with NumPy, [Nature **585**, 357 (2020)](https://doi.org/10.1038/s41586-020-2649-2).
