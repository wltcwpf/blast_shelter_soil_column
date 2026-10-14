# Mathematical model

## Reference state and boundary conditions

The reference cylinder is already in equilibrium under initial air pressure and its associated soil stresses, membrane tension, and plate reactions. F is an additional total compression force applied to a rigid top plate covering the annulus and air cavity. The bottom is fixed vertically. Radial movement at the plates is unconstrained. Soil–membrane contact is maintained. No initial inflation is solved.

The unknown vector is q = [δ, ui, uo], with positive δ downward shortening and positive ui, uo outward movement. Use meters, pascals, and newtons.

## Displacement and strain

Approximate ur(r) = A r + B/r and uz(z) = -δ z/H, where:

A = (ro uo - ri ui)/(ro² - ri²)
B = ri ui - A ri²

The normal strains are εr = A - B/r², εθ = A + B/r², εz = -δ/H. Shear strain is zero in this approximation. The approximation cannot reproduce friction-induced barreling.

## Soil strain energy

For isotropic linear elasticity, G = Es/[2(1+ν)] and λ = Es ν/[(1+ν)(1-2ν)]. Define the normal-strain constitutive matrix C = 2G I + λ 11ᵀ. Then:

Us = 2πH ∫[G(εr² + εθ² + εz²) + λ(εr + εθ + εz)²/2] r dr

The integral is over ri ≤ r ≤ ro. If ε = Bstrain(r) q, the soil stiffness is Ks = 2πH ∫ Bstrainᵀ C Bstrain r dr. model.py uses 32-point Gauss–Legendre integration.

## Membranes

Each hoop membrane has circumferential strain u/r. With reference membrane volume 2πrHt, its elastic energy is E(u/r)²(2πrHt)/2. Thus k = 2πHEt/r and Um = (ki ui² + ko uo²)/2.

These are bilateral hoop springs, not nonlinear shell elements. Axial membrane stiffness, bending stiffness, Poisson coupling, wrinkling, and buckling are omitted. A real flexible membrane may be unable to sustain the modeled compressive hoop increment without adequate initial tension.

## Air

Absolute initial pressure p0 = patm + pgauge. Reference volume V0 = πri²H. Linearized volume change:

ΔV = 2πriH ui - πri²δ = gᵀq

g = [-πri², 2πriH, 0]ᵀ.

For sealed isothermal ideal gas, pV = p0 V0, hence Δp = -p0 ΔV/V0 to first order. The incremental gas energy is Ua = p0(gᵀq)²/(2V0), giving Kair = (p0/V0)ggᵀ. Absolute pressure, including atmospheric pressure, controls gas compressibility.

For regulated constant pressure, Δp = 0 and Kair = 0. This does not mean initial pressure forces vanish: they are balanced in the reference state. The regulator exchanges air to maintain pressure.

The linear prestress work cancels against reference equilibrium. Geometric stiffness from reference pressure and membrane tension is omitted, as are all second-order kinematic volume terms. Consequently this is a deliberately simplified material/gas tangent model, not the complete small-on-large prestressed tangent. Increasing initial pressure changes gas tangent stiffness only; it does not recalibrate the soil modulus or reference geometry. Strong prestress may require a more complete model even if additional displacements are small.

## Equilibrium and outputs

Minimize Π = Us + Um + Ua - Fδ, giving:

(Ks + diag[0,ki,ko] + Kair)q = [F,0,0]ᵀ.

Outputs are H-δ, ri+ui, ro+uo, linearized pressure p0+Δp, and the displacement profile. Linearized ΔV and pressure are used consistently; no exact finite-deformation gas calculation is mixed into the linear solver. Sealed gas adds a positive semidefinite stiffness and cannot increase total axial compliance in this model.

The displayed cross section is longitudinal through the central axis: two brown soil bands flank the blue air cavity. Displacement magnification changes the plot only. Curves are linear because the model is linear.

## Screening and limitations

The app warns above 2% maximum absolute normal strain or 5% relative cavity-volume change. These thresholds are illustrative screening choices, not physical failure criteria. It also flags inverted geometry, nonpositive predicted absolute pressure, and membrane thickness/radius above 10%. Soil must be calibrated for the relevant drainage state and stress range; ν = 0.5 is not supported. No yielding, consolidation, time dependence, instability, or contact loss is represented.

## References

Ideal gas and fluid cavity coupling, official Abaqus theory documentation:
https://docs.software.vt.edu/abaqusv2025/English/SIMACAETHERefMap/simathe-c-fluidelem.htm

The annular displacement approximation, hoop spring energies, and stiffness assembly here are derived directly from the stated strain field and elastic energy; they are not a validated constitutive law for a particular soil specimen.
