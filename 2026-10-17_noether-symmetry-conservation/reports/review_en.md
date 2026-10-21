# From Symmetry to Conservation: Noether’s Theorems in Scientific Computing

<p class="dek">Why continuous symmetries of the action lead to momentum and energy conservation—and what it takes to carry that structure into simulation, scientific AI, and quantum computing</p>

<p class="kicker">TECH REVIEW · October 17, 2026 · Physical principles and computational applications</p>

<figure class="hero"><img src="hero.webp" alt="Conceptual illustration of translational and rotational symmetry using repeated rings and a continuous blue ribbon"><figcaption>An AI-generated conceptual illustration of structure preserved under symmetry transformations. It does not depict an experimental apparatus, particle trajectories, or measured data.</figcaption></figure>

## 1. A plausible prediction can still be physically wrong

Release a mass attached to an ideal spring on a frictionless horizontal surface. The mass moves fastest as it passes through equilibrium and briefly stops at maximum extension or compression. For the linear spring considered here, the restoring force is proportional to displacement. Kinetic energy and elastic energy exchange throughout the motion, but their sum stays constant when stiffness is fixed and no external work is done. A computer calculation of the same motion can nevertheless produce a growing amplitude and increasing energy. In the forward Euler example below, this artificial heating comes from the numerical approximation, not from an actual supply of work or heat.

A molecular simulation can encounter the same problem: the first few oscillations look right, yet total energy drifts upward over a longer run. Once the conditions for constant energy have been specified, accurate atomic positions over a short interval are not enough to establish the reliability of long-time dynamics. An AI model with low training error can fail in a similar way. We need to ask both what should be conserved and what the calculation actually conserves.

Symmetry makes these questions concrete. Should a molecule’s internal energy change merely because every atom has been moved by the same displacement? If the entire configuration is rotated, should its energy stay fixed while its forces rotate with it? If energy increases in a closed model whose external conditions do not change with time, where did the discrepancy enter?

Noether’s first theorem relates these questions to the action, a quantity assigned to an entire candidate trajectory. **A suitable continuous symmetry of the action yields a quantity conserved along solutions of the equations of motion.** This relationship helps us design models consistent with the intended physics and detect errors in their computed predictions. We first identify the symmetries appropriate to the system boundary and external conditions. We then ask whether the physical model and learning architecture respect them, and whether the numerical result retains the corresponding relations. Choosing a model with an exact conservation law, learning that model accurately, and integrating it accurately are separate achievements. [2–4]

The starting point is Shalma Wegsman’s Quanta Magazine article, “How Noether’s Theorem Revolutionized Physics.” Published on February 7, 2025, it connects the problem of energy in general relativity to Emmy Noether’s work of 1918. The shared LinkedIn post introduces the same article. The mathematics and computational applications developed below extend that account with original sources and related research. [1]

## 2. What exactly remains unchanged?

A symmetry statement must specify what is transformed and what remains unchanged. Rotating a circle leaves its shape unchanged; translating an entire experiment can leave its governing laws unchanged. These are related ideas, but they concern different objects. A translation moves every position by the same displacement. In physics, we examine how the laws and action transform, rather than asking whether one image or instantaneous configuration looks the same.

A free particle moves in a particular direction, so its trajectory is not unchanged under every rotation. Its governing laws nevertheless have no preferred spatial direction. **The symmetry of a law differs from the symmetry of a particular solution.** A mass attached to a spring fixed to a support illustrates the other side of this distinction. Moving only the mass changes the spring’s extension; the model for that mass does not have translational symmetry in that direction. Which parts of the apparatus and environment belong to the system matters. [2,3]

Noether’s first theorem concerns continuous symmetries, such as displacements and rotations that can be varied by arbitrarily small amounts. Time translation means that the governing laws do not depend on when the experiment begins. Resetting the stopwatch’s zero does not change the law of a spring whose external conditions remain fixed. This differs from time reversal, which reverses the direction of temporal evolution. Discrete transformations, such as a triangle’s rotation through 120 degrees or a reflection, do not admit the same argument starting from an arbitrarily small transformation. [2,3]

| Transformation and conditions | Corresponding conserved quantity | An example that changes the conditions |
|---|---|---|
| Continuous spatial translation of an entire closed system | Total linear momentum | Momentum exchange with a fixed external potential |
| Continuous spatial rotation of an entire closed system | Total angular momentum | An external torque or a field with a fixed direction |
| Time translation of the action | Energy corresponding to the Hamiltonian | External driving that changes with time |
| Adding the same angle to the complex phase throughout a matter field: a global phase rotation | The charge associated with that theory | The particular phase symmetry and its interactions must be specified |

The table should be read by asking which objects are transformed together. “Entire” is essential. With no external force and an interaction potential depending only on the two particles’ relative position, either particle’s momentum can change while their total momentum stays constant. A changing quantity in a subsystem does not, by itself, signal a failure of conservation. To see why a symmetry gives a constant quantity, we now turn to the action.

## 3. A short derivation from action to conserved quantity

Let \(q_i\) denote generalized coordinates describing the configuration, such as positions or rotation angles, and let \(\dot q_i\) denote their time derivatives. The Lagrangian \(L(q,\dot q,t)\) determines the motion; for familiar particle systems it is the difference \(T-V\) between kinetic and potential energy. The action \(S\) is the integral of \(L\) along a candidate trajectory. Paths with the same endpoints can have different actions because their intermediate positions and velocities differ. The units of \(L\) are energy, and the SI units of \(S\) are J·s.

$$
S[q]=\int_{t_1}^{t_2}L(q,\dot q,t)\,dt.
$$

The actual motion makes the first-order change in the action vanish under admissible small variations with fixed endpoints. This is the condition of stationary action; it need not be a minimum. It gives the Euler–Lagrange equations. The canonical momentum \(p_i\) corresponding to \(q_i\) is defined by differentiating \(L\) with respect to \(\dot q_i\). For the simple spring mass, \(p=m\dot x\), but canonical momentum cannot generally be replaced by velocity. A position coordinate has a conjugate momentum with units of kg·m/s; an angular coordinate has a conjugate angular momentum. [2,3]

$$
\frac{d}{dt}\frac{\partial L}{\partial\dot q_i}-\frac{\partial L}{\partial q_i}=0,
\qquad p_i=\frac{\partial L}{\partial\dot q_i}.
$$

First keep time fixed and change \(q_i\) by \(\epsilon\eta_i\). The small parameter \(\epsilon\) sets the size of the transformation, while \(\eta_i\) describes how each coordinate changes; \(\epsilon\eta_i\) has the units of the coordinate. We allow a symmetry for which the first-order change in the Lagrangian is \(\epsilon\,dB/dt\). Its integral is only \(\epsilon[B(t_2)-B(t_1)]\), so the action may change by an endpoint term. Substituting the equations of motion gives

$$
\frac{\delta L}{\epsilon}
=\sum_i\left(\frac{\partial L}{\partial q_i}\eta_i+p_i\dot\eta_i\right)
=\frac{d}{dt}\sum_i p_i\eta_i
=\frac{dB}{dt}.
$$

Thus \(Q=\sum_i p_i\eta_i-B\) has zero time derivative along a solution. The symmetry supplies the boundary term, and the equations of motion turn the Lagrangian variation into a total derivative. Their combination produces a conserved quantity. The Lagrangian need not remain literally unchanged under the transformation. [2,3]

When time also transforms, another term appears. Define \(t'=t+\epsilon\tau\) and \(q_i'(t')=q_i(t)+\epsilon\eta_i\), and suppose the first-order change in the transformed \(L\,dt\) is \(\epsilon\,dB\). Here \(\tau\) specifies the infinitesimal change of time. The parameter’s units depend on the transformation: \(\epsilon\tau\) has units of time, \(\epsilon\eta_i\) of the coordinate, and \(\epsilon B\) of action. Defining the Hamiltonian by \(H=\sum_i p_i\dot q_i-L\), the conserved quantity is

$$
Q=\sum_i p_i\eta_i-H\tau-B,\qquad \frac{dQ}{dt}=0.
$$

For a spatial translation, \(\tau=0\), and constant \(\eta_i\) selects the corresponding momentum component. For a rotation, \(\boldsymbol\eta=\boldsymbol\omega\times\mathbf r\) gives the connection to \(\mathbf r\times\mathbf p\). A time translation with \(\tau=1,\eta_i=0,B=0\) gives \(Q=-H\). The overall sign follows the convention for the direction of transformation; the conserved energy can be written as \(H\). Whether this Hamiltonian equals the familiar \(T+V\) must be checked for the particular Lagrangian. [3]

A driven spring shows why the conditions matter. If an external mechanism varies the stiffness \(k(t)\), the Lagrangian is \(L=m\dot x^2/2-k(t)x^2/2\). Along a solution of the equations of motion,

$$
\frac{dH}{dt}=-\frac{\partial L}{\partial t}
=\frac{1}{2}\dot k(t)x^2.
$$

With \(k\) measured in N/m, the right-hand side is power in W. The energy change accounts for the external driving. Including the stiffness-control mechanism requires describing energy exchange within a larger system. Calling the subsystem’s change a violation of energy conservation would overlook that boundary.

## 4. How do Noether’s two theorems differ?

The spring example tracks the energy of one mechanical system. For charge or a fluid distributed through space, matter and energy can also cross a region’s boundary. We then express conservation using a density and a flux. Let \(\rho_Q\) denote charge density and \(\mathbf j\) current density. The local conservation equation and charge \(Q_V\) within a finite region \(V\) obey the relations below, where \(\partial V\) is the boundary and \(d\mathbf A\) points outward.

$$
\frac{\partial\rho_Q}{\partial t}+\nabla\cdot\mathbf j=0,
\qquad \frac{dQ_V}{dt}=-\oint_{\partial V}\mathbf j\cdot d\mathbf A.
$$

For electric charge, \(\rho_Q\) has units of C/m³, \(\mathbf j\) has units of A/m², and the surface integral has units of A. Charge can decrease within the region while conservation holds exactly, provided the decrease equals the outward flow. In field theory, Noether’s first theorem also gives **local continuity equations** of this kind. A spatial integral remains constant only with the appropriate flux and boundary conditions. [4]

The difference between the two theorems is not whether they describe all of space or a small region. The first concerns continuous symmetries with constant transformation parameters, such as a displacement or rotation angle. The second allows the parameters to be arbitrary functions of spacetime and gives differential identities among the equations of motion. These identities hold without requiring the equations of motion to be satisfied first. [2]

In electromagnetism, different potentials can describe the same electric and magnetic fields. Transformations between those descriptions are gauge transformations. The freedom to describe the same spacetime using different coordinates provides a related setting in general relativity. Multiple descriptions of one physical state imply that the equations are not all independent. For electric charge, we must distinguish the current associated with a matter field’s global phase symmetry, the constraints from local gauge invariance, and charges defined at a boundary. Each local gauge freedom does not supply a new independent conserved quantity. [2,4,5]

Read boxes 1–3 from top to bottom to follow the first theorem through to conservation within a region. A symmetry of the action yields a conservation relation along motion satisfying the equations; the total inside a chosen region also requires zero net boundary flux to stay constant. The separate box below explains the identities among equations supplied by the second theorem. “Local” in a continuity equation and “local” in a gauge symmetry refer to different properties.

<figure><img src="symmetry_en.svg" alt="Top-to-bottom diagram tracing action symmetry, solutions of the equations of motion, and net boundary flux, followed by a separate bottom box for the second theorem’s role"><figcaption>An explanatory reconstruction of Noether’s theorems and continuity equations. A local continuity equation can hold while the total quantity inside a region changes through net outward flux. The second theorem is shown separately from the three stages. This is not a measurement from a particular experiment. [2–4]</figcaption></figure>

## 5. Why does light lose energy in an expanding universe?

The distinction between symmetry and boundary conditions also matters for energy in general relativity, a central theme of the source article. The energy–momentum tensor \(T^{\mu\nu}\) describes local energy and momentum densities, their fluxes, and stresses such as pressure. Together with the equations of motion it satisfies the covariant conservation relation \(\nabla_\mu T^{\mu\nu}=0\). Here \(\nabla_\mu\) is a derivative that accounts for spacetime geometry when comparing changes and flows. This local relation does not imply that a simple sum of energy over the entire universe stays constant. [6]

The standard construction of a globally conserved energy requires suitable time symmetry and boundary conditions. A timelike Killing vector identifies a direction along which translating time leaves the spacetime geometry unchanged. A generic expanding universe need not have this global time-translation symmetry. Other energy definitions use the asymptotic conditions of isolated systems or other geometric properties, however, so curvature does not make every definition of energy impossible. [6]

For a homogeneous, isotropic universe, the local conservation equation explains how expansion relates to photon redshift. Work in units with the speed of light equal to 1, and write \(\rho\) for energy density, \(P\) for pressure, and \(a(t)\) for the scale factor. Distances between points moving with the expansion scale with \(a(t)\). For a component that exchanges no energy with other components,

$$
\dot\rho+3\frac{\dot a}{a}(\rho+P)=0,
\qquad d(\rho a^3)=-P\,d(a^3).
$$

A fixed comoving volume follows the same coordinate locations as the universe expands; its physical volume grows as \(a^3\). The quantity \(\rho a^3\) is proportional to the component’s energy within that volume. The second equation relates its change to pressure and changing volume. Radiation that exchanges no energy with other components has \(P=\rho/3\), giving \(\rho\propto a^{-4}\). The factor \(a^{-3}\) describes dilution by the increasing volume. The remaining \(a^{-1}\) describes the decreasing energy of freely propagating photons as measured by comoving observers, who move with the expansion. This is compatible with local covariant conservation and does not require accelerated expansion. A local energy-flow equation and the existence of a conserved energy for the entire universe are different questions. Neither supports a claim that arbitrary energy can be created in a closed laboratory system. [6]

## 6. How can a numerical simulation retain symmetry?

So far, the question has been which conservation laws apply to the physical model. We now ask whether a computer calculation retains them. A numerical method updates a state over finite time steps, introducing approximation error even when the continuous-time law is exact. Return to the spring from the opening example to see where that error enters.

Take a harmonic oscillator with mass \(m\), fixed stiffness \(k\), and natural angular frequency \(\omega=\sqrt{k/m}\). Use its initial amplitude \(A\) as a fixed length scale. Normalize position as \(q=x/A\) and canonical momentum as \(p=p_{\rm phys}/(mA\omega)\). For this mass, \(p_{\rm phys}=m\dot x\), so \(p=\dot x/(A\omega)\); that identification between scaled momentum and velocity does not extend to every model. In this section, \(\tau=\omega t\) denotes dimensionless time. It has a different role from the time-transformation function \(\tau\) in Section 3. The time step \(h=\omega\Delta t=0.1\) is also dimensionless; it does not mean 0.1 seconds.

With physical energy \(E_{\rm phys}\), the dimensionless Hamiltonian is \(H=E_{\rm phys}/(mA^2\omega^2)=(p^2+q^2)/2\). Starting from \((q_0,p_0)=(1,0)\), the exact motion keeps \(H_0=0.5\) constant. This value is not an energy of 0.5 J. The figure below labels this dimensionless \(H\) as energy \(E\), so \(E/E_0=H/H_0\); the ratio also equals the physical-energy ratio \(E_{\rm phys}/E_{{\rm phys},0}\). Plotting each position–momentum pair as a point gives a phase plane. Equal-energy states lie on the circle \(q^2+p^2=1\). This is a contour of constant energy, not the mass’s path through physical space.

Forward Euler approximates the next state by applying the current rate of change over one time step. For \(dq/d\tau=p\) and \(dp/d\tau=-q\), its updates are

$$
q_{n+1}=q_n+h p_n,\qquad p_{n+1}=p_n-h q_n.
$$

Both right-hand sides use the old state. The first step moves \((1,0)\) to \((1,-0.1)\), outside the unit circle, raising the computed energy from 0.5 to 0.505: a 1% increase. Although the instantaneous direction is tangent to the circle, a finite straight step ends outside that equal-energy contour. The segment represents a numerical update, not the path actually traveled by the mass. Substituting the two updates into the energy cancels the cross terms and gives the exact growth factor:

$$
H_{n+1}=\frac{(q_n+h p_n)^2+(p_n-h q_n)^2}{2}
=(1+h^2)H_n.
$$

The same 1% increase repeats at every update. After 2,000 steps, \(E_{2000}/E_0=H_{2000}/H_0=1.01^{2000}\approx4.39\times10^8\). The update rule itself explains how the calculation keeps adding energy without an external supply.

Variational integrators offer one way to address such problems. They discretize the action, rather than directly discretizing the equations of motion, and derive the updates from that discrete action. If the discrete Lagrangian retains the relevant symmetry, the discrete Noether theorem gives conservation of the corresponding momentum. Under suitable regularity conditions, the method also preserves a symplectic structure. For this one-degree-of-freedom system, that means a small region of neighboring states in the phase plane keeps its area after a step. With more degrees of freedom, symplecticity preserves the geometric relations among canonical coordinate–momentum pairs, a stronger requirement than preserving total phase-space volume alone. Marsden and West connect molecular-dynamics methods such as Verlet through this framework. [7]

Preserving this geometry does not make the original energy exactly constant at each state. With fixed-step symplectic methods, energy can oscillate slightly; under suitable regularity and stability conditions, the error remains controlled over long times. Conserved momentum, preserved geometry, and the behavior of physical-energy error must therefore be checked separately. [7]

For this oscillator, symplectic Euler first updates momentum and then uses that new momentum to update position. Velocity Verlet changes momentum by half a step using the current force, advances position by a full step, and completes the momentum update using the force at the new position. Unlike forward Euler, these rules use newly updated values within the step. Their different update sequences are reflected in the energy-error behavior below.

The figure compares three methods using the same initial state, \(h=0.1\), and 2,000 steps. Start with the upper panel: \(E/E_0=1\) means energy equal to its initial value. Equal vertical intervals on the logarithmic scale represent equal factors, not equal differences, allowing Euler’s large growth to share a plot with the other methods. The lower panel expands the scale linearly to show how far symplectic Euler and velocity Verlet depart from 1. It still plots \(E/E_0\), not relative error in percent. The horizontal axis is \(\tau=\omega t\), time measured in units of the inverse natural angular frequency.

<figure><img src="integrator_en.svg" alt="Upper logarithmic energy-ratio plot showing forward Euler’s growth; lower linear enlargement comparing symplectic Euler and velocity Verlet around a ratio of 1"><figcaption>Calculations performed for this review. Energy \(E\) in both panels denotes the dimensionless \(H\) defined in the text, and the plotted quantity is \(E/E_0\). This ratio is unchanged when physical units are restored. The upper scale is logarithmic; the lower scale is linear and magnifies the small variations of the two structure-preserving methods. This is an educational comparison at an identical time step, not a benchmark matched for computational cost or accuracy, or a reproduction of a published paper. The accompanying script generates the data and update rules.</figcaption></figure>

Reading each curve’s departure from 1 as a fraction of the initial energy gives maximum absolute relative energy errors of approximately 5.26% for symplectic Euler and 0.25% for velocity Verlet over this run. Their energies oscillate within a limited range instead of growing continually as forward Euler’s does. The comparison shows that the numerical method changes how error accumulates even for the same equation. These values apply to this oscillator and time step. Small energy error does not establish correct oscillation timing, nor do these results make every symplectic method superior to every alternative.

The same design question arises when particles and fields are computed together. Particle-in-cell methods couple particle motion to electromagnetic fields on a grid to simulate plasma. Xiao and colleagues’ Vlasov–Maxwell study designs a discrete Lagrangian, gauge invariance, and a noncanonical symplectic structure for the combined particle–field system. The authors construct charge-conserving algorithms and test them on nonlinear Landau damping and electron Bernstein waves, which probe plasma-wave damping and propagation. This is a concrete method for long-time plasma computation, not evidence of a fusion device’s control performance. [8]

## 7. Should scientific AI learn conservation laws or embody them?

The previous example started with a known equation and compared ways of computing its motion. What changes when the function determining that motion must itself be learned from data? A general neural network predicting the next position and velocity does not acquire an exact built-in conservation law merely because its data contain conservative trajectories. A Hamiltonian Neural Network (HNN) learns an energy-like scalar function \(H_\theta(q,p)\) and determines motion through its derivatives. The parameters \(\theta\) belong to the neural network. Here \(q,p\) denote general canonical coordinates and momenta; they are not assumed to have the numerical values of the oscillator’s dimensionless variables. Hamilton’s equations, also called the canonical equations of motion, turn the learned function into rates of change of position and momentum. [9]

$$
\dot q=\frac{\partial H_\theta}{\partial p},\qquad
\dot p=-\frac{\partial H_\theta}{\partial q}.
$$

For a smooth \(H_\theta\) with no explicit time dependence, substituting these rates into \(dH_\theta/dt\) makes the two terms cancel in continuous time. What is conserved is **the learned function**. To understand an actual prediction, we must distinguish learning the function, the continuous motion defined by Hamilton’s equations, and its finite-step numerical integration. The continuous dynamics conserve \(H_\theta\) even if it gives the wrong physical energy. Finite-step integration can then introduce conservation error, as in the previous section. Using the correct canonical coordinate–momentum pairs is a further condition. The original study includes springs, pendulums, two-body motion, and image-based examples, and explicitly notes that friction requires additional modeling. [9]

A Lagrangian Neural Network (LNN) learns \(L_\theta(q,\dot q)\) from coordinates and velocities, then obtains motion through the Euler–Lagrange equations. This is useful when canonical momenta are difficult to obtain directly. Solving uniquely for accelerations requires a nonsingular Hessian, the matrix of second derivatives with respect to velocities. Time dependence, constraints, and dissipation also need appropriate treatment. The original paper is a 2020 workshop study presenting a double pendulum, a relativistic particle, and a one-dimensional wave equation. Those examples alone do not establish the reliability of an industrial digital twin. [10]

The practical benefit is to constrain the relationship between the learned function and motion according to physics. If the observed degrees of freedom exchange energy through friction, reactions, coupling to an environment, or external driving, a conservative model that omits those exchanges can produce the wrong motion. Chemical reactions do not themselves abolish energy conservation in a closed system taken as a whole. The model must specify which contributions to energy it includes and account for the work, heat transfer, dissipation, and control inputs needed to explain the observed changes.

## 8. Equivariant neural networks and interatomic potentials

Learning an energy function does not settle whether its dependence on spatial orientation is correct. Consider the molecular rotation raised in the introduction. In the absence of an externally preferred direction, rotating the entire molecule should leave its energy unchanged and rotate its force vectors with it. An unchanged value is invariant; a vector output that follows the input’s rotation is equivariant. With atomic positions \(\mathbf r\) and rotation matrix \(R\), the target relations are \(E(R\mathbf r)=E(\mathbf r)\) and \(\mathbf F(R\mathbf r)=R\mathbf F(\mathbf r)\). An external field or substrate with a preferred direction must also be transformed, or the symmetry conditions adjusted.

NequIP is an interatomic-potential model with representations that respect these spatial symmetries. Its authors test data efficiency and predictive performance on water, amorphous materials, interfaces, and ionic conductors. Forces that transform in the right direction and forces that derive from a potential energy satisfy different requirements. NequIP first predicts the configuration’s total potential energy \(E_\theta\), then computes the force on atom \(i\) as its negative gradient with respect to that atom’s position. [11]

$$
\mathbf F_i=-\nabla_{\mathbf r_i}E_\theta.
$$

Forces derived from a single differentiable energy function form a conservative field: the net work around a closed path is zero. If that energy is invariant under common translations and rotations of an isolated system, the net force and net torque must also vanish. **Equivariant transformation of a vector field does not, by itself, establish that the field is the gradient of an energy.** Energy invariance, force equivariance, and the derivative linking energy to force are distinct conditions. Even when they hold, total-energy behavior in molecular dynamics depends on the time step, the integrator, and the thermostat settings that govern heat exchange with an environment. [11]

For OLED and molecular-materials research, a natural first application would be evaluating structures and thermal motion on an electronic ground-state potential. Excited states, charge transfer, spin–orbit coupling, nonadiabatic transitions, and emission lifetimes require additional physics and validation. This is an application proposed by the review; the original NequIP paper did not validate OLED device efficiency or lifetime.

## 9. In quantum computing, symmetry can identify errors

The preceding examples use symmetry to design models and computations. It can also identify components of an already computed result that violate the required conditions. In a closed quantum system, an observable is conserved during evolution when its operator commutes with the Hamiltonian and has no explicit time dependence. Commutation means that applying the two operators in either order gives the same result. This relation can identify a particle number or symmetry subspace that the calculation should retain. Restricting the allowed states and making the entire computation faster remain separate outcomes to evaluate. [4,12]

In 2019, Sagastizabal and colleagues tested parity symmetry while estimating the hydrogen molecule’s ground state with two qubits in a superconducting circuit quantum electrodynamics (circuit-QED) processor. Here parity distinguishes an even from an odd number of qubit excitations, labeled \(+1\) and \(-1\). The target state lies in the odd-parity subspace; qubit relaxation and residual excitation introduce components outside it. The researchers estimated states and energies from measured Pauli expectation values and reduced errors by post-processing those values for the target subspace. This was a real, small-scale quantum-device experiment. Its procedure differs from directly rejecting individual shots using an additional parity measurement on every execution. [12]

Projection expresses what that selection means. A projector \(\Pi\) selects the component in the target subspace, while the density matrix \(\rho\) describes the quantum state, including noise. The ideal state conditioned on successful projection and the success probability are

$$
\rho_{\rm kept}=\frac{\Pi\rho\Pi}{\mathrm{Tr}(\Pi\rho)},
\qquad p_{\rm keep}=\mathrm{Tr}(\Pi\rho).
$$

The numerator \(\Pi\rho\Pi\) is the selected component; dividing by \(p_{\rm keep}\) restores total probability to 1. In an ideal procedure that actually selects independent samples with success probability \(p_{\rm keep}\), retaining the same sample count requires about \(1/p_{\rm keep}\) times as many attempts on average. This is an educational relation for direct selection, not a formula for the measurement cost of the experiment above. That study post-processes the required Pauli expectation values. For the hydrogen Hamiltonian’s \(ZZ\) parity check, no measurement terms beyond those already needed for energy estimation were required. Equal numbers of measurement terms do not imply equal statistical error or estimator variance. Errors remaining inside the target subspace also escape this check. [12]

Parity is discrete rather than continuously variable, so this is not a direct application of Noether’s first theorem. The connection is that symmetry constrains models and algorithms and supplies conditions against which results can be tested. The demonstration on this small device neither replaces error correction nor establishes quantum advantage.

## 10. Three different meanings of broken symmetry

What does it mean when a calculation changes an expected conserved quantity or fails a symmetry check? To distinguish changed modeling assumptions from numerical or device errors, we first need to separate three physical meanings of symmetry breaking.

**Explicit symmetry breaking** occurs when a term in the Lagrangian, such as a directed external field or a time-dependent drive, removes the corresponding symmetry. Changes in the associated quantity then reflect the force, torque, or power supplied by that term. The spring with externally varied stiffness is one example.

In **spontaneous symmetry breaking**, the action and laws retain an exact symmetry, but the selected ground state does not share it. This does not itself imply nonconservation of the Noether current. A potential can treat every direction about the origin equally while having equivalent minima away from the origin. Choosing one minimum then selects a direction. The distinction between the law and the state matters again. [13]

A **quantum anomaly** occurs when a symmetry of the classical action does not survive in the full quantum theory. This requires examining the measure used to sum over paths and the regularization used to handle divergent expressions. Fujikawa’s original work explains the axial anomaly through transformation of the path-integral measure. This axial-current anomaly does not mean that electromagnetic charge arbitrarily ceases to be conserved. The anomaly cancellation required for consistent dynamical gauge theories is a separate issue. [14]

These distinctions matter in technical validation. When an expected conserved quantity changes, first examine external driving, flux out of a subsystem, an approximate model, and discretization. Numerical error alone is not evidence for new physics or a quantum anomaly.

## 11. What to check in research and development

Answering the opening question requires more than choosing a symmetry by name. The required relation must enter the model, and its predictions must then be compared with that relation and with physical observables. The table pairs design choices with quantities that can test their consequences.

| Intended application | Useful design choices | Observables for evaluating the result |
|---|---|---|
| Long-time integration of molecular dynamics or mechanical systems | Variational or symplectic integrators suited to the system’s symmetries | Energy error over time, total momentum, phase error |
| Learning dynamics from data | HNNs or LNNs with suitable external-force and dissipation terms | Unseen trajectories, true energy, errors at multiple time steps |
| Learning interatomic potentials | Energy invariance, force equivariance, and energy derivatives | Rotation and translation checks, force errors, work around closed paths, NVE stability |
| Particle–electromagnetic-field computation | Preservation of discrete gauge structure and charge continuity | Charge residuals, field constraints, long-time physical observables |
| Quantum-state and energy estimation | Symmetry subspaces and verification measurements | Energy bias, retained fraction, total measurement count, undetectable errors |

Read each design choice together with the observables used to test it. For an interatomic model, compare energies and forces before and after moving or rotating the entire configuration; in an isolated system without external forces, also check total force and torque. For a force-only model without an energy function, work around a closed path provides one test of conservativity. NVE denotes isolated-system conditions with fixed particle number (N), volume (V), and energy (E). Inspecting energy error and oscillation-timing error in an NVE calculation without a thermostat helps distinguish properties of the integrator. A stable trajectory alone still does not establish that the potential is accurate.

In the opening spring example, energy growth arose from a numerical approximation to known conservative motion. For the HNN, we also had to ask whether the learned function represented the true energy. For NequIP, we distinguished the energy’s spatial symmetry from the relation generating forces. Quantum symmetry verification rejected some components outside the target conditions but could not detect errors within the allowed subspace. Small learning error can therefore coexist with incorrect integrated motion, while exact conservation can describe motion on the wrong potential. Data fit, symmetry and conservation relations, numerical integration, and experimental observables must be assessed together.

Noether’s theorems **restrict admissible models and motions through the system’s symmetries and boundary conditions, and give us a way to ask whether a computation retains those relations.** If a conserved quantity changes, distinguish omitted exchanges with the environment, an incorrectly learned function, integration error, and device error. The same questions connect classical mechanics and field theory to numerical analysis, scientific AI, and quantum verification, provided each application stays within the scope its evidence supports.

## References and source material

1. Wegsman, S. *How Noether’s Theorem Revolutionized Physics*. Quanta Magazine, 2025-02-07. [Article](https://www.quantamagazine.org/how-noethers-theorem-revolutionized-physics-20250207/). The starting point for the historical context and motivating questions.
2. Noether, E. *Invariante Variationsprobleme* (1918), 235–257. English translation by M. A. Tavel, *Transport Theory and Statistical Physics* **1**(3), 186–207 (1971). [DOI](https://doi.org/10.1080/00411457108231446) · [English text, arXiv:physics/0503066v3, 2018-05-30](https://arxiv.org/html/physics/0503066v3). The first and second theorems appear in §§1–2.
3. Harvey Mudd College Physics 111 materials. *Symmetries and Conservation Laws*, Chapter 6, §§6.4–6.5. [Original PDF](https://www.physics.hmc.edu/~saeta/courses/p111/uploads/Y2012/Ch06.pdf). A textbook chapter hosted on Professor Saeta’s course website; no author is assigned here because the PDF does not identify one. Mechanics including time transformations and boundary terms.
4. Tong, D. *Quantum Field Theory*, §1.3, Symmetries and Noether’s theorem. [Official lecture notes](https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S1.html). Currents, charges, boundary conditions, and the background to quantum theory.
5. Avery, S. G.; Schwab, B. U. W. *Noether’s Second Theorem and Ward Identities for Gauge Symmetries*. *Journal of High Energy Physics* **2016**, 31. [arXiv:1510.07038](https://arxiv.org/abs/1510.07038) · [DOI](https://doi.org/10.1007/JHEP02(2016)031). Local symmetries, identities, and the role of boundaries.
6. Tong, D. *General Relativity*, Chapter 4, especially §4.3 and §§4.5–4.6. [Official lecture notes](https://www.damtp.cam.ac.uk/user/tong/gr/grhtml/S4.html). Covariant conservation, Killing symmetries, energy, and cosmology.
7. Marsden, J. E.; West, M. *Discrete mechanics and variational integrators*. *Acta Numerica* **10**, 357–514 (2001). [DOI](https://doi.org/10.1017/S096249290100006X) · [Author’s exposition](https://lagrangeweb.web.engr.illinois.edu/var_int/). Discrete action, momentum, and symplectic structure.
8. Xiao, J. et al. *Explicit high-order non-canonical symplectic particle-in-cell algorithms for Vlasov-Maxwell systems*. *Physics of Plasmas* **22**, 112504 (2015). [DOI](https://doi.org/10.1063/1.4935904) · [arXiv:1510.06972v2, 2016-03-12](https://arxiv.org/abs/1510.06972v2). An application in numerical plasma computation.
9. Greydanus, S.; Dzamba, M.; Yosinski, J. *Hamiltonian Neural Networks*. NeurIPS 2019. [Paper](https://arxiv.org/html/1906.01563) · [Conference](https://papers.neurips.cc/paper_files/paper/2019/hash/26cd8ecadce0d4efd6cc8a8725cbd1f8-Abstract.html). The structure in §2 and interpretation of the conserved quantity in §3.2.
10. Cranmer, M. et al. *Lagrangian Neural Networks*. ICLR 2020 Deep Differential Equations Workshop. [arXiv:2003.04630v2, 2020-07-30](https://arxiv.org/abs/2003.04630v2) · [Author code](https://github.com/MilesCranmer/lagrangian_nns). A workshop study, distinguished here from a main-conference paper.
11. Batzner, S. et al. *E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials*. *Nature Communications* **13**, 2453 (2022). [DOI](https://doi.org/10.1038/s41467-022-29939-5) · [Public manuscript](https://arxiv.org/html/2101.03164). Construction of energy and forces in Methods.
12. Sagastizabal, R. et al. *Experimental error mitigation via symmetry verification in a variational quantum eigensolver*. *Physical Review A* **100**, 010302(R) (2019). [DOI](https://doi.org/10.1103/PhysRevA.100.010302) · [Public manuscript](https://arxiv.org/html/1902.11258). The public manuscript is titled *Error Mitigation by Symmetry Verification on a Variational Quantum Eigensolver*.
13. Kaplunovsky, V. *Spontaneous Symmetry Breaking*, University of Texas lecture notes (2020). [Original PDF](https://web2.ph.utexas.edu/~vadim/Classes/2020f/SSB.pdf). Symmetries of laws and ground states, and conserved currents.
14. Fujikawa, K. *Path-Integral Measure for Gauge-Invariant Fermion Theories*. *Physical Review Letters* **42**, 1195–1198 (1979). [DOI and original paper](https://doi.org/10.1103/PhysRevLett.42.1195). The axial anomaly and integration measure. [Tong, Gauge Theory §§3.2–3.4](https://www.damtp.cam.ac.uk/user/tong/gaugetheory/3anom.pdf) provides supplementary discussion of anomalies and their cancellation.

<p class="downloads"><a href="../index.html">한국어 리뷰</a> · <a href="review_en.pdf">English PDF</a> · <a href="../review_ko.pdf">한국어 PDF</a></p>
