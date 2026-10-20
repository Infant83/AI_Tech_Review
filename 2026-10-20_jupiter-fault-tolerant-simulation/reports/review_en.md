# Classical Simulation of a 104-Qubit Protocol: Testing Magic-State Cultivation on JUPITER

<p class="dek">Why building reliable quantum computation needs large classical calculations — magic states, coherent errors and leakage, and the meaning of a 45-bit state register</p>

<p class="kicker">TECH REVIEW · 20 October 2026 · Quantum error correction and high-performance computing</p>

<figure class="hero"><img src="hero.webp" alt="An abstract quantum lattice and blue and copper phase waves in front of supercomputer racks"><figcaption>A conceptual illustration of testing logical-state phase errors and leakage outside the computational subspace on a classical supercomputer. It depicts neither an actual quantum device or circuit nor computed data. AI-generated image.</figcaption></figure>

## 1. A classical supercomputer for designing quantum computers

Quantum error correction aims to build reliable logical qubits from imperfect physical qubits. Storing information for a long time, however, does not complete a useful computer. A machine must also perform logical gates, change its actions in response to measurements, and retry failed preparations. Testing this whole process under noise is part of its design.

On 19 October 2026, NVIDIA announced a simulation of a magic-state cultivation protocol using **104 physical qubit locations** on JUPITER at the Jülich Supercomputing Centre. The computation used 8,192 GH200 GPUs. This was a classical GPU calculation of a quantum protocol, rather than a 104-qubit experiment on a quantum processor. [1,2]

Two questions explain its significance. Why are magic states a bottleneck in fault-tolerant computation? And how could a circuit involving 104 locations be computed with a maximum encoded state register of 45 bits? The second answer involves reusing storage after measurement and packing three-level states together. It does not mean compressing an arbitrary 104-qubit state into a smaller state.

## 2. From logical memory to computation: the role of magic states

A Clifford gate maps Pauli operators to Pauli operators. Many error-correction operations fit this framework. With stabilizer-state inputs, Clifford gates, Pauli measurements and suitable Pauli noise, an efficient stabilizer simulator can avoid storing a huge state vector. [3]

Universal quantum computation requires resources beyond that restricted framework. One example is the T gate. We use the standard convention

$$
T=\operatorname{diag}(1,e^{i\pi/4}),\qquad
|T\rangle=T|+\rangle=
\frac{|0\rangle+e^{i\pi/4}|1\rangle}{\sqrt{2}}.
$$

An appropriately prepared nonstabilizer resource can be combined with Clifford operations, measurement and feedforward to implement a logical T operation. A magic state is consumed in that process. Not every non-Clifford circuit is hard to simulate, but the simple stabilizer shortcut no longer covers general computation. [3]

Conventional distillation processes several imperfect resource states together. **Cultivation** instead prepares a state in a small code, repeatedly checks it and transfers it into a larger code. A failed check can cause the attempt to be discarded and restarted. Gidney, Shutty and Jones analyzed the resource savings of this approach under specified circuit-level noise assumptions. [4]

Output fidelity alone therefore cannot characterize a factory. For independent, identical attempts with acceptance probability \(A\) and fixed cost \(C_{\rm trial}\) per attempt, a simple average gives

$$
\mathbb{E}[N_{\rm attempts}]=\frac1A,\qquad
C_{\rm accepted}=\frac{C_{\rm trial}}A.
$$

This is a teaching relation. Early termination, parallel preparation, resets and buffer waiting change a real cost model. Its lesson is that **low output error and adequate acceptance must be achieved together**.

## 3. The protocol being simulated

The technical account describes preparation in a distance-3 color code, additional flag measurements, growth into a distance-7 hybrid color/surface-code structure, and further error correction and readout. Flags are auxiliary measurements that expose particular error-propagation paths. The 104 locations include data and auxiliary physical positions used across the protocol sequence. [1]

<figure><img src="cultivation_flow_en.svg" alt="Stages from a distance-3 color code through flag checks to a distance-7 hybrid code, correction and readout"><figcaption>An original conceptual diagram based on the public technical account, rather than a gate-by-gate circuit reproduction. Postselection incurs discard and retry costs. Subsequent use of the resource in a logical T operation is general application context, not an application algorithm executed in this announcement. [1,4]</figcaption></figure>

Code distance is important for describing correctable or detectable error structure. Nevertheless, the effective suppression order of a complete noisy circuit does not automatically equal its static code distance. Error propagation, non-Clifford layers and measurements all matter. This motivates the additional flag research. [5]

## 4. Why coherent phase errors and leakage differ

Physical noise cannot always be replaced by independent Pauli errors. Small rotations repeated in the same direction can accumulate phase coherently. For stochastic Z errors, the statistics of even and odd error counts instead determine the outcome.

Consider a **single-qubit teaching example**: prepare \(|+\rangle\), apply \(R_z(\theta)=e^{-i\theta Z/2}\) a total of \(r\) times, then measure X. There is no intervening error correction. Match the one-step X-measurement error by choosing an independent stochastic Z error probability \(p=\sin^2(\theta/2)\). Then

$$
P_{-}^{\rm coherent}=\sin^2\!\left(\frac{r\theta}{2}\right),\qquad
P_{-}^{\rm stochastic}=\frac{1-(1-2p)^r}{2}.
$$

For \(\theta=0.01\) radians and \(r=20\), these are approximately **0.997% and 0.0500%**. Matching a one-step probability does not match repeated behavior. These values are independently calculated from the displayed formulas; they do not predict the JUPITER protocol's error rate.

Leakage presents a different problem. If a physical element occupies a third level outside the two computational levels, an additional component is needed. As a pure-state illustration,

$$
|\psi\rangle=a|0\rangle+b|1\rangle+c|2\rangle,
\qquad |a|^2+|b|^2+|c|^2=1.
$$

The probability of remaining in the computational subspace is \(1-|c|^2\). Unlike a Z error within that subspace, leakage can change how gates and measurements must be interpreted. The JUPITER technical account includes coherent phase errors and third-level leakage at selected physical locations, without publishing numerical noise strengths. [1]

<figure><img src="noise_channels_en.svg" alt="Phase evolution within two computational levels contrasted with leakage into a third level"><figcaption>An educational schematic distinguishing phase error from leakage. The arrows and level coupling are generic examples, not the campaign's actual noise channel, rates or measured data.</figcaption></figure>

## 5. From 104 locations to a 45-bit storage register

Direct storage of an arbitrary pure n-qubit state requires \(2^n\) complex amplitudes. An arbitrary entangled state with 104 simultaneously live qubits therefore cannot fit into a 45-bit state vector.

This calculation exploits the protocol's time structure. Once an auxiliary state is measured and no longer needs to remain quantum, its storage can be released and reused later. Classical dependencies and measurement probabilities must still be preserved. This is different from arbitrarily discarding entanglement that remains necessary. Reordering operations reduces the storage that must be simultaneously live. [1]

Qutrit packing provides another saving. Five three-level systems have \(3^5=243\) basis states. Assigning two binary bits separately to each qutrit would require ten bits. Packing the five together instead maps them exactly into 256 entries represented by eight bits:

$$
j=\sum_{k=0}^{4}3^k\ell_k,\quad \ell_k\in\{0,1,2\},
\qquad 0\le j\le242,\quad
\lceil\log_2 243\rceil=8.
$$

The remaining thirteen entries are encoding padding, not new physical levels. This mapping does not truncate valid amplitudes. It also cannot, by itself, explain the full 104-to-45 reduction. The public account reports a maximum 45-bit encoded register but does not specify the exact peak breakdown of two- and three-level degrees of freedom. [1]

<figure><img src="memory_register_en.svg" alt="104 physical locations connected through measurement and storage reuse to a 45-bit encoded register and 512 TiB memory"><figcaption>An original explanation of physical locations versus simultaneously stored register size. Memory values are calculated for a complex128 state vector; they are not measurements of total job memory or runtime. Five qutrits packed into eight bits is the published encoding example. [1]</figcaption></figure>

## 6. What 512 TiB tells us

With complex128 storage at sixteen bytes per amplitude, state-vector memory is \(M(n)=16\times2^n\) bytes. The following values are independently calculated from that expression. TiB and PiB mean \(2^{40}\) and \(2^{50}\) bytes.

| Encoded register | State-vector memory only | Interpretation |
|---|---:|---|
| 40 bits | 16 TiB | 1/32 of the 45-bit case |
| 45 bits | 512 TiB | Reported maximum register |
| 46 bits | 1 PiB | One additional bit doubles memory |
| 50 bits | 16 PiB | 32 times the 45-bit case |

At 45 bits there are \(2^{45}\), roughly 35.2 trillion amplitudes. Dividing 512 TiB evenly among 8,192 GPUs gives **64 GiB per GPU**. This is state storage alone, excluding communication buffers, workspaces and factorization analysis. Performance also depends on amplitude exchanges, operation placement and the network. Memory capacity alone cannot determine runtime or energy consumption.

The technical account also describes cuBLASMp/cuSOLVERMp-based factorization analyses of selected state partitions to investigate compact approximate representations. **The reference simulation continued from the original state.** An analysis of possible factorization is not evidence that the full reference computation proceeded with a truncated tensor representation. [1,6]

## 7. Improvements require matched conditions

Different kinds of improvement numbers appear in the surrounding literature. The original cultivation study compares **qubit-rounds**, a space-time resource, under specified noise and target-fidelity assumptions. NVIDIA's “90% fewer qubits” is a company summary claim. The announcement does not provide a matched comparison of target error, throughput and retry accounting, so it does not establish a universal 90% reduction in physical qubits for fault-tolerant computing. [2,4]

In a separate preprint, Chan and colleagues analyze error propagation through non-Clifford cultivation circuits and introduce additional flags. For distance-5 cultivation before escape, at circuit-level depolarizing noise probability \(p=10^{-3}\), one reported example reduces logical error by a factor of 4.9 while increasing attempts per accepted state by a factor of 1.36. Stronger checks can improve output quality and increase acceptance cost simultaneously. **Those are not measurements from JUPITER's coherent-error and leakage simulation.** [5]

There is also physical-hardware evidence. Google's Willow cultivation experiment reports a 40-fold error reduction relative to uncultivated states and fidelity 0.9999(1), together with postselection retaining 8% of attempts. That is a processor experiment; its metrics cannot be directly ranked against the classical JUPITER calculation. [7]

## 8. Verification and the information still needed

The approximately \(10^{-13}\) agreement in probabilities described in the technical article concerns **small packed-circuit cross-checks between state-vector and tensor-network methods at NVAQC**. It is neither the full 104-location protocol's logical error rate nor a guarantee for every output. The inspected public sources do not report full-run runtime, GPU-hours, shot or trajectory count, acceptance yield, output logical error or uncertainty intervals. [1]

We use 8,192 GPUs, consistent across the technical introduction and official release. One technical paragraph instead prints 8,912. This review checks the public explanation, formulas and memory arithmetic; it does not reproduce the JUPITER run. Existing cultivation research code and a reproducible package for this full campaign are also distinct resources.

The most useful next evidence would be output error and acceptance versus noise strength, cost per attempt and per accepted state, and the circuits, decoder, sampling procedure and statistical intervals. These would show which design decisions the large calculation changes beyond the implementation checks available on smaller circuits.

## 9. A route toward materials and chemistry applications

Resource estimates for fault-tolerant chemistry and materials simulation depend on non-Clifford resource demand and supply rate as well as logical-qubit count. A cheaper, reliable magic-state factory could change an algorithm's time and space budget. Establishing that connection requires matching the algorithm's T-resource demand and tolerated failure probability to the factory's acceptance, error and throughput.

This result does not demonstrate a more accurate molecular energy or quantum advantage. Its practical connection is the **ability to test resource preparation under more realistic noise before committing to hardware design**. Such calculations can investigate which checks reveal coherent errors or leakage, where additional measurements help, and how fidelity gains affect retries. Large classical calculations supply a reference. Comparing that reference with a device's calibration, measurement and leakage-removal behavior is the route toward fault-tolerant engineering.

The source DQB issue is available as the [20 October 2026 archived PDF](https://infant83.github.io/AI_Tech_Review/archive/files/2026-10-20-daily-quantum-brief.pdf); other issues remain in the [document archive](https://infant83.github.io/AI_Tech_Review/archive/).

## References

1. Holmes, Kloss, Pancotti and Svore. [Advancing Fault-Tolerant Quantum Computing with GPU-Accelerated Simulation](https://nvidia.github.io/cuda-quantum/blogs/blog/2026/10/19/jupiter-magic-state-simulation/). NVIDIA Quantum, 19 October 2026. Principal technical account of the protocol, noise, storage and small-circuit cross-checks.
2. NVIDIA. [NVIDIA Runs Record Simulation of Fault-Tolerant Quantum Computing at Jülich Supercomputing Centre](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Runs-Record-Simulation-of-Fault-Tolerant-Quantum-Computing-at-Jlich-Supercomputing-Centre/default.aspx), 19 October 2026. System context: JSC, [JUPITER](https://www.fz-juelich.de/en/jsc/systems/supercomputers/jupiter).
3. Bravyi and Kitaev. [Universal Quantum Computation with ideal Clifford gates and noisy ancillas](https://arxiv.org/abs/quant-ph/0403025). Physical Review A 71, 022316 (2005).
4. Gidney, Shutty and Jones. [Magic state cultivation: growing T states as cheap as CNOT gates](https://arxiv.org/abs/2409.17595), first released in 2024. [Original circuits, statistics and code](https://doi.org/10.5281/zenodo.13777072).
5. Chan, Strikis, Sun and Cai. [Diagnosing and Restoring the Degraded Fault Distance of Magic State Cultivation](https://arxiv.org/abs/2609.17706), v3, 30 September 2026. Preprint; a separate study from the JUPITER campaign.
6. NVIDIA. [cuStateVec](https://docs.nvidia.com/cuda/cuquantum/latest/custatevec/index.html), [cuBLASMp](https://docs.nvidia.com/cuda/cublasmp/index.html), [cuSOLVERMp](https://docs.nvidia.com/cuda/cusolvermp/). State-vector and distributed linear-algebra software documentation.
7. Rosenfeld et al. [Magic state cultivation on a superconducting quantum processor](https://arxiv.org/abs/2512.13908). Physical-hardware experiment; checked against Google Quantum AI's [15 October 2026 explanation](https://blog.google/innovation-and-ai/models-and-research/quantum-computing/magic-state-cultivation-quantum-computing/).
