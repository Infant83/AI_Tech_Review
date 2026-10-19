# The Quasi-Riemann Hypothesis and AI Mathematics: Prime Distributions and Proof Verification

<p class="dek">From the link between zeta zeros and prime-counting errors to the 7/8 and 11/12 manuscripts, metaplectic forms, Lean verification, and the limits of algorithmic applications</p>

<p class="kicker">TECH REVIEW · October 20, 2026 · Analytic number theory and AI-assisted research</p>

<figure class="hero"><img src="hero.webp" alt="Mathematical concept illustration of a transparent vertical passage emerging within a dark space of points and curves"><figcaption>An AI-generated conceptual image of discovering hidden mathematical structure and making an argument intelligible. It does not plot actual zeta zeros or proof data.</figcaption></figure>

## 1. How precisely can we describe the locations of primes?

Primes such as 2, 3, 5, 7, and 11 are easy to define, yet difficult to describe precisely in terms of where and how often they occur. Their average tendency to become less frequent among larger numbers is known. The questions become deeper when we ask how far their distribution can depart from that average, or how evenly primes occur with a particular remainder.

The Riemann zeta function turns these questions into a problem about the zeros of a complex function. Restricting where its zeros can lie in the complex plane also constrains errors in the distribution of primes. The Riemann hypothesis states that every nontrivial zero lies on the line with real part 1/2. The quasi-Riemann hypothesis sets a weaker but still powerful goal: establish a fixed gap, independent of height, that prevents zeros from approaching the line with real part 1. [2,5,6]

On October 19, 2026, Konstantin Kakaes reported in Quanta Magazine on OpenAI’s quasi-Riemann manuscripts and the responses of mathematicians reading them. That article is the source behind the shared link. The public materials include a long manuscript claiming a boundary at real part 7/8, a human-edited alternative manuscript at 11/12, and associated Lean formalizations. Experts are primarily interpreting the shorter alternative argument, with positive assessments accompanied by calls for detailed scrutiny. [1–4]

**The central result concerns a fixed zero-free region. The 1/2 boundary of the Riemann hypothesis itself remains unresolved.** Understanding this distinction is essential to evaluating both the number-theoretic implications and AI’s role. This review separates the mathematics claimed by the manuscripts, what can be established by inspecting public code, and the additional conditions required for applications.

## 2. Where the zeta function meets the primes

For a complex number \(s=\sigma+it\), \(\sigma\) is the real part and \(t\) the imaginary part. In the region where the real part exceeds 1, the zeta function can be expressed both as an infinite series and as an infinite product over primes.

$$
\zeta(s)=\sum_{n=1}^{\infty}\frac{1}{n^s}
=\prod_{p\,\mathrm{prime}}\left(1-p^{-s}\right)^{-1},
\qquad \operatorname{Re}s>1.
$$

Expanding the Euler product produces every positive integer through combinations of prime powers. The uniqueness of prime factorization underlies this identity. The zeta function therefore encodes information about all the primes together. The ordinary convergent series–product identity above must, however, include the condition \(\operatorname{Re}s>1\). The remaining region is handled by analytic continuation, with a simple pole at \(s=1\). Transferring the source article’s intuitive account without this condition would be inaccurate. [5,6]

The zeros at the negative even integers −2, −4, … are called trivial zeros. The nontrivial zeros of central interest lie in the critical strip \(0<\operatorname{Re}s<1\). The Riemann hypothesis narrows their location to the strip’s central line. The quasi-Riemann hypothesis instead seeks some fixed \(\theta<1\) that excludes zeros from the right half-plane.

$$
\zeta(s)\ne0\quad\text{for}\quad
\operatorname{Re}s>\theta,\ s\ne1.
$$

The word “fixed” matters. Unlike classical zero-free regions whose boundaries approach real part 1 as the imaginary part increases, the same \(\theta\) must apply at every height. Combining this with the reflection symmetry supplied by the zeta function’s functional equation confines the real parts of nontrivial zeros between \(1-\theta\) and \(\theta\). [2,5]

| Statement | Range for the real parts of nontrivial zeta zeros | Status in this review |
|---|---|---|
| Critical strip | Between 0 and 1 | Classical background |
| Alternative 11/12 manuscript | [1/12, 11/12] | Claim of a separate, human-edited argument |
| 7/8 manuscript | [1/8, 7/8] | Claim of the stronger manuscript and a target of the public formalization |
| Riemann hypothesis | Exactly 1/2 | A hypothesis not resolved by these results |

Since 7/8 is smaller than 11/12, it moves the right boundary farther left and gives the stronger result. The zero-free assertion concerns the open half-plane strictly to the right of the boundary. It should not be read as excluding zeros on the boundary itself.

<figure><img src="zero_regions_en.svg" alt="Diagram comparing candidate zero regions in the 11/12 and 7/8 manuscripts with the real-part-1/2 line of the Riemann hypothesis"><figcaption>An explanatory comparison of the regions in which nontrivial zeta zeros may remain. It does not show measured zeros or points obtained through a numerical search. The strip boundaries obtained using symmetry are included; the RH line remains hypothetical. [2,3,5]</figcaption></figure>

## 3. Why a boundary in the complex plane controls prime-counting error

Let \(\pi(x)\) count the primes not exceeding \(x\). The prime number theorem states that \(\pi(x)\) is asymptotic to \(x/\log x\). A more precise average approximation uses \(\operatorname{Li}_2(x)=\int_2^x dt/\log t\). Logarithms here are natural logarithms.

Chebyshev’s \(\psi(x)\) makes the relationship easier to express. It assigns weights to prime powers as well as to primes.

$$
\psi(x)=\sum_{p^k\le x}\log p.
$$

The zeta function’s explicit formula connects this sum to a main term \(x\) and oscillatory contributions from the zeros. For example, using \(\psi_0(x)\), which averages the values on the two sides of a jump, gives the following structure for \(x>1\). The sum counts nontrivial zeros with multiplicity and is interpreted as a limit taken symmetrically in imaginary height. [5,6]

$$
\psi_0(x)=x-\sum_{\rho}\frac{x^{\rho}}{\rho}
-\log(2\pi)-\frac12\log(1-x^{-2}).
$$

Writing a zero as \(\rho=\beta+i\gamma\) gives \(x^\rho=x^\beta e^{i\gamma\log x}\). Its real part \(\beta\) determines the growth rate of the oscillation’s amplitude. After dividing by the main term \(x\), the magnitude of this contribution is \(x^{\beta-1}/|\rho|\). Keeping \(\beta\) a fixed distance from 1 restricts that growth rate to be smaller than the main term’s.

Obtaining the full error requires controlling the sum over all zeros, truncation errors, and other terms. The observation about one contribution is therefore not itself a complete prime-number-theorem error estimate. For a fixed \(1/2\le\theta<1\), if every nontrivial zero satisfies \(\operatorname{Re}\rho\le\theta\), then the following holds for every \(\varepsilon>0\). [6]

$$
\pi(x)=\operatorname{Li}_2(x)
+O_{\theta,\varepsilon}\!\left(x^{\theta+\varepsilon}\right).
$$

The notation \(O_{\theta,\varepsilon}\) allows the bounding constant to depend on the fixed \(\theta\) and on \(\varepsilon\). It does not permit simply substituting \(\varepsilon=0\). This must also be distinguished from the stronger classical error \(O(\sqrt{x}\log x)\) implied by RH. Choosing a fixed small positive \(\varepsilon<1-\theta\) makes the error exponent smaller than 1—a substantial change delivered by a quasi-Riemann result.

<figure><img src="prime_error_en.svg" alt="Logarithmic plot comparing pure power factors corresponding to real-part exponents 11/12, 7/8, and 1/2"><figcaption>A comparison of the pure power factor \(x^{\beta-1}\), computed for this review. The plot omits zero-height factors, constants, logarithms, \(\varepsilon\), and sums over multiple zeros. It is therefore neither a bound on the actual error in \(\pi\) or \(\psi\) nor measured error data.</figcaption></figure>

## 4. Placing the zeta function within a larger family

The new manuscripts’ statements extend beyond the zeta function alone. The 7/8 manuscript claims the same boundary for every Dirichlet \(L\)-function and every finite-order Hecke \(L\)-function over \(K=\mathbb Q(\sqrt{-3})\), allowing the pole at \(s=1\) associated with the principal character. The 11/12 manuscript proposes a weaker boundary for the same families. This does not prove the generalized Riemann hypothesis for all number fields or all automorphic \(L\)-functions. [2,3]

A Dirichlet character \(\chi\) is a periodic function that represents the multiplicative structure of residue classes through complex values. Introducing these weights initially gives the following series in its region of convergence.

$$
L(s,\chi)=\sum_{n=1}^{\infty}\frac{\chi(n)}{n^s},
\qquad \operatorname{Re}s>1.
$$

Combining these weights can isolate primes with remainder \(a\) modulo \(q\). This addresses the frequency of primes in sequences with a specified remainder, such as 1, 5, 9, …. The standard residue-class condition for prime-distribution questions is \(\gcd(a,q)=1\). Because functions that separate residue classes connect to zeros of their \(L\)-functions, a uniform boundary for an entire family broadens the range of applications.

Here \(\mathbb Q(\sqrt{-3})\) is the number field obtained by adjoining \(\sqrt{-3}\) to the rationals. Its Eisenstein integers and cubic and sextic residue characters provide an important setting for the proof. Hecke \(L\)-functions form a more general framework encoding arithmetic over number fields of this kind. Readers need not master every definition first, but the strategy is worth retaining: **use related families and averages rather than track the zeros of one function directly**.

## 5. How were existing tools connected?

This section explains the argumentative structure in §2 of the human-edited 11/12 manuscript, rather than reproducing the full proof. The central task is to obtain sufficient cancellation in sums with Möbius coefficients and transfer it into a zero-free statement for \(L\)-functions. The Möbius function \(\mu(n)\) is zero on integers with a square factor and equals \((-1)^r\) on a squarefree integer with \(r\) distinct prime factors. It appears in the Dirichlet series for the reciprocal of the zeta function, providing a connection to the zero problem. [3,6]

The argument first constructs a family of Möbius sums twisted by sextic characters over the Eisenstein integers. A “twist” attaches an arithmetic phase weight to each term. Instead of adding the absolute values of individual sums, the method seeks cancellation in the mean square over the whole family. Poisson summation and Gauss–Jacobi relations connect these expressions to cubic Gauss sums. [3]

Their coefficients can be interpreted as Fourier coefficients of Kubota’s cubic metaplectic theta function. Here metaplectic forms supply transformation laws connecting different summation representations. A Voronoi-type transformation for the theta function produces quadratic characters, the cubes of sextic characters, allowing the use of a quadratic large sieve to bound sums over multiple quadratic characters together. Möbius inversion removes the cubic factors needed for the transformation, while further Poisson transformations and recursion control the remainder. This recursion and the remainder estimates are among the difficult parts of the argument. [3,7]

The final calculation producing the exponent 11/12 can be presented more briefly. Here \(\mu_K\) extends the integer Möbius function through prime-ideal factorization. For a fixed finite-order Hecke character \(\nu\), a smooth, compactly supported weight function \(W\), and \(u\in\mathcal O_K\), consider the following sum. [3]

$$
A_u(D)=\sum_{\mathfrak n}
\mu_K(\mathfrak n)\nu(\mathfrak n)\chi_{\mathfrak n}(u)
W\!\left(\frac{N\mathfrak n}{D}\right).
$$

The sum runs over nonzero integral ideals coprime to 2, 3, and the conductor of \(\nu\), with \(\chi_{\mathfrak n}(u)\) denoting a sextic residue character. Here \(N\) is the algebraic norm and \(H\) limits the size of the family. For \(D\ge2\), \(0<\vartheta\le1/10\), and \(\varepsilon>0\), the manuscript gives the following mean-square bound. The implied constant in \(\ll\) may depend on \(\nu,W,\vartheta,\varepsilon\).

$$
\sum_{0<N(u)\le H}|A_u(D)|^2
\ll D^{1+\varepsilon}H,
\qquad H=D^{1+\vartheta}.
$$

For rows with \(u=p^6\), the sextic character is mostly 1, enabling comparison with \(A_1(D)\). Using primes \(p\) whose norms have size \(H^{1/6}\) gives the following bound.

$$
|A_1(D)|^2
\ll D^{1+\varepsilon}H^{5/6}+D^2H^{-1/3}.
$$

Choosing \(\vartheta>0\) sufficiently small makes the exponent in the first term 11/6 plus an arbitrarily small amount. Taking the square root gives a bound of the form \(D^{11/12+\varepsilon}\), with \(\varepsilon\) relabeled to absorb the small losses. The brevity of this calculation does not make the mean-square estimate itself easy. The 7/8 manuscript uses a longer argument involving moments and compensating factors; it should not be described as obtaining 7/8 through a minor adjustment of these two lines.

The role of prior work also requires precision. Dunn and Radziwiłł’s *Bias in cubic Gauss sums: Patterson’s conjecture* appeared as a preprint in 2021 and as an Annals paper in 2024. The year 2022 is when Quanta reported on the related research. That work’s asymptotic formula over primes is conditional on GRH, but the theta expansions and summation formulas imported by the new manuscripts are unconditional tools. Describing the argument as circular because it assumes a conditional final conclusion in order to prove quasi-RH would misrepresent the manuscripts’ logic. [2,7]

## 6. What changes for research on prime distributions?

The first practical change is a quantitative error estimate. Subsequent work by Fiori and Jaskari combines the condition that all nontrivial zeros have real part at most 7/8 with their methods to give the following explicit bound. Here \(\psi\) is the weighted prime sum defined above, and logarithms are natural. [8]

$$
|\psi(x)-x|
<0.04934\,x^{3/4}(\log x)^2
+0.02636425\,x^{7/8},\qquad x\ge21.
$$

This goes beyond saying that some constant exists: it supplies coefficients and a domain that can be used in calculations. Dividing the right-hand side by \(x\), this review computes approximately 0.03850 at \(x=10^{12}\) and 0.0001770 at \(x=10^{24}\). These are relative-error bounds of approximately 3.85% and 0.0177%, respectively, not measurements of the actual error. The subsequent paper presents the estimate as a consequence assuming the 7/8 result; this does not constitute an independent verification of the entire original proof. Nor can a bound for \(\psi(x)\) be treated as the same formula for \(\pi(x)\).

A second change concerns primes in arithmetic progressions. Corollary 1.2 of the 11/12 manuscript claims a uniform absolute-error bound of order \(x^{11/12}\log x\) for the difference between \(\pi(x;q,a)\) and \(\operatorname{Li}_2(x)/\varphi(q)\). Here \(\varphi(q)\) counts residue classes coprime to \(q\). Since the main term contains \(1/\varphi(q)\), it may become smaller as \(q\) grows. This does not imply a small relative error for every \(q\le x\). [3]

A third change concerns exceptional Landau–Siegel zeros. The possible presence of real zeros extremely close to real part 1 in \(L\)-functions of real Dirichlet characters has complicated the effectivity of many number-theoretic estimates. The public formalization scope also includes a statement giving a single constant \(c>0\) such that \(1-\beta\ge c/\log q\) for a primitive, nonprincipal real Dirichlet character \(\chi\) of conductor \(q\ge3\) and real zeros \(0<\beta<1\) of its \(L\)-function. This does not exclude all real zeros, and the scope document does not give an explicit value of \(c\). [9]

An application paper should therefore be read with attention to the function family and boundary it uses, whether constants are explicit and effective, and the applicable variable ranges. A consequence about primes in short intervals does not by itself improve the best existing record for interval length: other methods may already give stronger results in a particular setting.

## 7. What Lean checks, and what people must check

A formal proof expresses mathematical statements and logical inferences in code, and a small trusted component—the kernel—checks the validity of proof terms. This provides stronger verification than a model’s natural-language assertion that it has proved something, but the proposition and definitions being checked must also be examined. [10,15]

The public scope document for family 003 distinguishes the 7/8 boundaries for zeta, all Dirichlet characters, and the specified Hecke family from the exceptional-real-zero gap. It does not claim to formalize every later application in the manuscript. Comparator configurations in the repository are set up to compare a public challenge statement with a theorem in a separate solution module and check conditions including the permitted axioms. [9,15]

The roles of two files are easily confused here. The challenge file named `QuasiRiemannHypothesis.lean` contains a `sorry`. This is a placeholder in the statement to be compared; the actual proof is linked through a separate solution module. That file alone does not establish that the proof is missing. Conversely, the existence of a separate module does not establish that independent re-verification is complete.

The inspected Comparator configuration lists `propext`, `Quot.sound`, and `Classical.choice` as permitted axioms, with `enable_nanoda` set to false. The last value configures an additional kernel option; it does not mean that ordinary Lean checking is absent. The repository’s `review.status: unchecked` is likewise review metadata and cannot by itself be interpreted as a failed kernel check. This review inspected the public statements, definitions, and links between modules; it did not rebuild the entire library in a clean environment or independently run Comparator. [9,10,15]

<figure><img src="proof_path_en.svg" alt="Workflow from a natural-language theorem through auditing formal statements and definitions, checking a separate proof with a kernel, and assessing mathematical understanding and applications"><figcaption>A reconstruction of the public repository’s organization and the roles of formal verification. It is neither a record of a full Lean rebuild performed for this review nor an execution log of the proof-discovery process. [9,10,15]</figcaption></figure>

### Why a function can have a value at the pole at 1

Consider a concrete example. The mathematical zeta function has a pole at \(s=1\), but Mathlib’s `riemannZeta : ℂ → ℂ` is a total function assigning a value to every complex input. The library version used assigns the following special value at that point, where \(\gamma\) is the Euler–Mascheroni constant. [11]

$$
\texttt{riemannZeta}(1)
=\frac{\gamma-\log(4\pi)}{2}\ne0.
$$

This does not remove the divergence of the analytic zeta function. It is a convention for defining the coded function on every input. The actual solution path handles \(s=1\) in a separate branch and applies the nonvanishing theorem for Dirichlet \(L\)-functions in the remaining cases. The absence of an \(s\ne1\) hypothesis in the challenge therefore does not, on its own, make the theorem incorrect. [11]

This example shows why semantic inspection matters. The kernel checks the relationship between propositions and proofs within the code. Establishing that the intended mathematical objects, hypotheses, and exceptions match that code requires reading the definitions. Matching function or theorem names alone is insufficient.

## 8. How much does the public record reveal about AI’s work?

The release comes from research evaluations using an unreleased internal model. The repository describes presenting the model with approximately 4,000 problems, and expresses the average computation under its general fixed procedure as the equivalent of about three hours of ChatGPT Pro thinking with that model. However, **work on the zeta zero-free region is explicitly listed as an exception to that procedure.** There is no basis for presenting the quasi-Riemann result as a proof that an ordinary user can reproduce in three hours. The public record also does not establish this result’s model version, total computation, or complete search process. [4]

The reported counts require distinctions of units as well. Quanta describes the October 6 announcement in terms of 377 results and 722 manuscripts. The repository catalogue at the October 12 commit pinned for this review contains 372 families and 719 manuscripts. The report’s “results” and the repository’s “families” must not be assumed to be identical counting units. One family may contain a principal result, alternative proofs, and manuscripts deriving consequences. The history records the withdrawal of three Hodge-related manuscripts and revisions to other papers. The initial reported count must therefore not be relabeled as the current number of fully verified theorems. [1,4]

Other AI-mathematics examples help distinguish types of work. The AlphaProof IMO demonstration released in 2024 describes receiving human-formalized problems and searching and verifying within a formal language. Those conditions differ from an unreleased model’s exploration of research problems. Success rates or computation times from either setting cannot be transferred into reproducibility claims about the other. [14]

An interesting feature of the new result is the capacity to search broadly for connections among existing mathematical tools. Turning such a connection into knowledge that other researchers can reuse requires clear hypotheses and citations, isolated key lemmas, and explanations that humans can read. The number of discovered results must be assessed together with the cost of understanding, verifying, and extending them.

## 9. What further conditions do primality testing and cryptographic applications require?

Prime distribution, primality testing, and factorization are different problems. Asking how many primes occur near \(x\) concerns distribution. Deciding whether a given integer is prime concerns testing. Producing the prime factors of a given composite integer concerns factorization. A theorem giving better control over distribution does not by itself supply an algorithm for the last problem.

Connections between Riemann-type hypotheses and algorithms have a long history. Miller’s 1976 work studies primality testing under the Extended Riemann Hypothesis. The quasi-Riemann result and the ERH required by that algorithm must not be treated as the same assumption. Moreover, unconditional deterministic polynomial-time primality testing is already known through AKS’s *PRIMES is in P*. The new result cannot be described as making fast primality testing possible for the first time. [12,13]

A substantive cryptographic claim would need to specify the problem’s inputs and outputs, the improvement in running time, and what was measured at which integer sizes. The materials examined here do not provide evidence that the quasi-Riemann result demonstrates practical RSA factorization or cryptanalytic performance. A natural research direction is to revisit which parts of conditional algorithm analyses require only the zero boundaries for these particular function families, rather than to announce immediate security-performance figures.

## 10. A practical order for evaluating AI mathematics

| What to examine first | Question to ask | Example in this case |
|---|---|---|
| Precise scope of the theorem | Which functions, variables, boundaries, and exceptions are covered? | 7/8 and 11/12, the principal-character pole, and the specified Hecke family |
| Logic of the manuscript | Which lemmas are new, and which earlier results are used? | Möbius mean squares, theta transformations, and conditional conclusions versus unconditional tools |
| Formal statements and definitions | Do the paper and the code concern the same objects? | The total-function convention for `riemannZeta` and the branch at 1 |
| Actual verification runs | What was rechecked, with which versions, axioms, and dependencies? | Comparator’s target theorem and the separate solution module |
| Transfer to applications | Are constants, effectivity, variable ranges, and algorithmic costs established? | An explicit \(\psi\) bound and absolute errors in arithmetic progressions |

This order is the review’s proposal for research and development practice. Preserving the paper PDF, a pinned repository commit, target theorems and library versions, verification commands, and actual results together makes later scrutiny easier. If only some theorems have been formalized, that scope should be stated. Numerical illustrations must also be distinguished from proofs covering infinitely many cases.

The implications of the quasi-Riemann result are more concrete than an impression that primes look slightly more regular. It places a fixed restriction on zero locations and transfers that restriction into quantitative errors for prime distributions and questions about related \(L\)-functions. From the perspective of AI research, an important part of the task is turning an argument found through broad exploration into **mathematics that others can verify and reuse**. Examining these two processes together is an appropriate starting point for assessing the result as of October 20, 2026.

## References and source material

1. Kakaes, K. *AI Proved the Quasi-Riemann Hypothesis. What Happens Now?* Quanta Magazine, 2026-10-19. [Article](https://www.quantamagazine.org/ai-proved-the-quasi-riemann-hypothesis-what-happens-now-20261019/). Reporting on expert responses and the state of human understanding and scrutiny; it does not substitute for independent verification of the entire original proof.
2. OpenAI. *The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane Re(s)>7/8*. Manuscript dated 2026-09-30, 199 pages. [Pinned-version PDF](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf). Theorem 1.1 and the introduction’s function families and conditions on prior results.
3. OpenAI. *The Quasi-Riemann Hypothesis*, alternate 11/12 proof, 2026-10-05, 49 pages. [Pinned-version PDF](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/paper2.pdf) · [Manuscript notes](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/README.md). Theorem 1.1, Corollary 1.2, §2, and equations (2.2)–(2.5). A separate, human-edited argument.
4. OpenAI. *Sharing AI progress in mathematics*, announced 2026-10-06, updated 10-15. [Official announcement](https://openai.com/index/sharing-ai-progress-in-mathematics/) · [Repository README](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/README.md) · [Revision history](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/history.md). Repository evidence is pinned to commit `1581d4c`.
5. Bombieri, E. *The Riemann Hypothesis*. Clay Mathematics Institute problem description. [Official PDF](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf). Foundations of the zeta function, its zeros, RH, and prime distributions.
6. Sutherland, A. V. MIT 18.785, *Number Theory I*, Fall 2019. [Problem Set 8](https://math.mit.edu/classes/18.785/2019fa/ProblemSet8.pdf), Problem 1 for the explicit formula and part (f) for errors implied by zero boundaries. [Lecture 17](https://math.mit.edu/classes/18.785/2019fa/LectureNotes17.pdf) supplies background on the functional equation and critical strip.
7. Dunn, A.; Radziwiłł, M. *Bias in cubic Gauss sums: Patterson’s conjecture*. Annals of Mathematics **200**(3), 967–1057 (2024). [Published paper](https://annals.math.princeton.edu/2024/200-3/p03) · [DOI](https://doi.org/10.4007/annals.2024.200.3.3) · [arXiv:2109.07463](https://arxiv.org/abs/2109.07463). The 2021 preprint is distinguished from the 2024 publication.
8. Fiori, A.; Jaskari, M. *Explicit bounds for the prime number theorem*. [arXiv:2609.23222v2, 2026-10-08](https://arxiv.org/html/2609.23222v2). Theorem 1.4 and the explicit \(\psi\) bound obtained by substituting the 7/8 assumption.
9. OpenAI. Family 003 formalization scope and configurations. [Scope document](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/docs/003.md) · [Challenge statement](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/QuasiRiemannHypothesis.lean) · [Comparator configuration](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/QuasiRiemannHypothesis.json) · [Formalization catalogue](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/formalization.yaml). This review’s examination is a static inspection of code and statements.
10. Lean. *Theorem Proving in Lean 4*, Axioms and Computation. [Official documentation](https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/). Background on axioms, proofs, computation, and verification.
11. Mathlib. *NumberTheory/Harmonic/ZetaAsymp.lean*, `riemannZeta_one` and `riemannZeta_one_ne_zero`. [Pinned library version](https://github.com/leanprover-community/mathlib4/blob/d13f23b723b8a846827a245b89c10fc7d3f11612/Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean#L419). [OpenAI’s actual branch at 1](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/OAI/NumberTheory/DirichletL/Hecke/Dirichlet.lean#L171).
12. Agrawal, M.; Kayal, N.; Saxena, N. *PRIMES is in P*. Annals of Mathematics **160**, 781–793 (2004). [Published paper](https://annals.math.princeton.edu/2004/160-2/p12) · [DOI](https://doi.org/10.4007/annals.2004.160.781). Unconditional deterministic polynomial-time primality testing.
13. Miller, G. L. *Riemann’s Hypothesis and Tests for Primality*. Journal of Computer and System Sciences **13**(3), 300–317 (1976). [Author’s public PDF](https://www.cs.cmu.edu/~glmiller/Publications/Papers/Mi76.pdf). The ERH assumption and its connection to primality testing.
14. Google DeepMind. *AI achieves silver-medal standard solving International Mathematical Olympiad problems*, 2024-07-25. [Official explanation](https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/). Problem formalization and computational conditions in the AlphaProof and AlphaGeometry 2 demonstration.
15. Leanprover. *Comparator*. [Official repository](https://github.com/leanprover/comparator) · [OpenAI’s execution instructions](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/README.md). The challenge–solution comparison and permitted-axiom checking configuration were inspected; the full verification was not rerun for this review.

<p class="downloads"><a href="review_en.pdf">English PDF</a> · <a href="../index.html">Korean review</a> · <a href="../review_ko.pdf">Korean PDF</a></p>
