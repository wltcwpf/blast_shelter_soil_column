"""In-app teaching guide for the existing incremental mechanics model."""
import numpy as np
import streamlit as st


def render_guide(p, result, force):
    st.header('Understand the model, step by step')
    st.markdown('Follow the steps in order: define the specimen, choose what movements are allowed, calculate how each component resists movement, and balance the additional load. Each step explains both the equation and its physical meaning.')
    st.info('The numerical examples below update with your sidebar settings. Dimensions and pressure refer to an already pressurized specimen; the calculated displacements begin from that reference state.')

    with st.expander('Step 1 · Define the hollow specimen and reference state', expanded=True):
        st.markdown('The specimen is a cylindrical **ring of soil**, bounded by an inner and an outer membrane. The central hollow space contains air. A longitudinal section therefore shows soil on both sides of the central air cavity.')
        st.latex(r'A_s=\pi(r_o^2-r_i^2),\qquad V_0=\pi r_i^2H')
        st.markdown('Here H is height, rᵢ is the cavity radius, rₒ is the outer soil radius, Aₛ is the soil cross-sectional area, and V₀ is initial air volume. Membrane thicknesses are treated as small and are not subtracted from these dimensions.')
        st.write(f'Current specimen: H = {p.H*1000:.1f} mm, rᵢ = {p.ri*1000:.1f} mm, rₒ = {p.ro*1000:.1f} mm. Soil area = {np.pi*(p.ro**2-p.ri**2)*1e6:.1f} mm²; cavity volume = {np.pi*p.ri**2*p.H*1e6:.1f} cm³.')
        st.markdown('**Starting condition:** The input dimensions describe the specimen after pressurization. The app calculates the additional deformation caused by the vertical load. It does not simulate the initial inflation.')

    with st.expander('Step 2 · Specify loading, supports, and the three unknowns'):
        st.markdown('A rigid top plate spans **both the annular soil and the central air cavity**. F is the additional total downward force on this shared plate. The bottom is fixed vertically. Frictionless plates allow radial movement at the ends; the model does not include end restraint from friction.')
        st.latex(r'\mathbf q=[\delta,u_i,u_o]^T,\qquad H^{\prime}=H-\delta,\quad r_i^{\prime}=r_i+u_i,\quad r_o^{\prime}=r_o+u_o')
        st.markdown('δ is positive for vertical shortening. uᵢ and uₒ are positive for outward movement. A negative uᵢ means the cavity narrows. These movements are solved together; the app does not force the inner membrane to move inward.')
        st.warning('If your load acts only on the annular soil and the cavity has a mechanically independent end cap, the shared-plate boundary condition must be changed. The current equations do not represent that setup.')

    with st.expander('Step 3 · Approximate the displacement field'):
        st.markdown('The model solves only three movements: top shortening δ, inner-wall radial movement uᵢ, and outer-wall radial movement uₒ. To describe movement at every soil point, we assume the following displacement shapes. Here r is the original distance from the axis and z is the original height above the bottom.')
        st.markdown('**Vertical movement — uniform shortening.** The bottom stays fixed and the top moves downward by δ. We assume displacement changes linearly with height:')
        st.latex(r'u_z(z)=-\delta z/H')
        st.markdown('Thus the bottom moves 0, the middle moves −δ/2, and the top moves −δ. Every horizontal layer has the same axial strain; this is an assumption rather than a prediction about heightwise variation.')
        st.markdown('**Radial movement.** The soil moves inward or outward as the column is compressed. To describe how this movement varies through the soil thickness, we use the classical elastic-cylinder displacement form:')
        st.latex(r'u_r(r)=Ar+B/r')
        st.markdown('This form follows from radial equilibrium for homogeneous, isotropic, linearly elastic material with axisymmetric, height-independent radial displacement, constant axial strain, and no radial body force. These assumptions reduce radial equilibrium to:')
        st.latex(r'\frac{d^2u_r}{dr^2}+\frac{1}{r}\frac{du_r}{dr}-\frac{u_r}{r^2}=0')
        st.markdown('Integrating this equation gives Ar + B/r. Thus the radial shape has a basis in elasticity theory. Using it throughout our specimen assumes that the radial movement is the same at every height.')
        st.markdown('**Reference:** M. S. Kazimi, N. E. Todreas, and L. Wolf, *Introduction to Structural Mechanics*, MIT OpenCourseWare, Section 4.1, printed p. 28 (PDF p. 31), Eqs. (4.7a)–(4.8a). [Read the lecture notes](https://ocw.mit.edu/courses/22-312-engineering-of-nuclear-reactors-fall-2015/eb49bc4f3e701be60ca651c5a109312f_MIT22_312F15_note_L4.pdf#page=31). The notes derive the zero-axial-strain case. Allowing a spatially constant axial strain, as in this app, leaves the radial differential equation unchanged. This reference supports the radial displacement form; the coupled soil–membrane–air model includes the additional assumptions explained in the following steps.')
        st.markdown('Positive radial movement is outward. The shape must match the inner and outer wall movements:')
        st.latex(r'Ar_i+B/r_i=u_i,\qquad Ar_o+B/r_o=u_o')
        st.markdown('Solving these two boundary equations determines A and B:')
        st.latex(r'A=\frac{r_o u_o-r_i u_i}{r_o^2-r_i^2},\qquad B=r_i u_i-Ar_i^2')
        st.markdown('A and B set the radial displacement profile. Once the inner and outer wall movements are known, these two equations determine A and B. No additional displacement unknowns are needed.')
        st.markdown('**Key assumptions:** (1) axisymmetry: movement is identical around the circumference, with no twisting; (2) radial movement is independent of height: points at the same radius move radially by the same amount at the bottom, middle, and top; (3) vertical displacement varies linearly with height and is the same at every radius. Consequently, the model permits uniform widening or narrowing but cannot reproduce midheight barreling, end-friction effects, or asymmetric buckling.')

    with st.expander('Step 4 · Convert displacement into soil strain'):
        st.markdown('Strain measures relative change in length. The radial strain measures stretching through the annulus thickness; hoop strain measures change in circumference; axial strain measures change in height.')
        st.latex(r'\varepsilon_r=\frac{du_r}{dr}=A-\frac{B}{r^2},\quad \varepsilon_\theta=\frac{u_r}{r}=A+\frac{B}{r^2},\quad\varepsilon_z=-\frac{\delta}{H}')
        st.markdown('Positive normal strain means extension, and negative normal strain means compression. The app reports the amount of axial compression as the positive value δ/H. The assumed displacement field produces no shear strain.')
        st.markdown('**Small-strain assumption:** These equations describe small changes in length and shape. They neglect higher-order terms that become important when deformation is large.')
        st.write(f'At the current load, axial compressive strain is {100*result["delta"]/p.H:.4f}%; the largest absolute normal strain sampled through the soil is {100*result["max_strain"]:.4f}%.')

    with st.expander('Step 5 · Calculate the elastic resistance of the soil'):
        st.markdown('**Purpose of this step:** use the soil stiffness and the strains from Step 4 to calculate how strongly the soil resists deformation. The soil is treated as homogeneous (the same properties everywhere), isotropic (the same properties in every direction), and linearly elastic (stress is proportional to strain and deformation is recoverable).')
        st.markdown(r"""| Symbol | Physical name | Meaning | Units |
|---|---|---|---|
| $E_s$ | Soil Young’s modulus | Axial stiffness in an unconfined uniaxial elastic test; larger values mean stiffer soil | Pa or MPa |
| $\nu$ | Soil Poisson ratio | Negative lateral-to-axial strain ratio in an unconfined uniaxial test | Dimensionless |
| $G$ | Shear modulus; second Lamé parameter | Resistance to shear deformation | Pa or MPa |
| $\lambda$ | First Lamé parameter | Elastic constant coupling normal stress to volumetric strain; **not damping** | Pa or MPa |
| $\varepsilon_r,\varepsilon_\theta,\varepsilon_z$ | Radial, hoop, and axial normal strains | Relative length changes in the three directions | Dimensionless |
| $w_s$ | Soil elastic strain-energy density | Recoverable elastic energy per unit soil volume | J/m³ |
| $U_s$ | Total soil elastic strain energy | Energy density integrated over the soil volume | J |""")
        st.markdown('**Elastic constants.** The inputs Eₛ and ν fully specify the soil’s elastic properties in this model. We calculate G and λ from those inputs because they provide a convenient way to write the stress and energy equations.')
        st.latex(r'G=\frac{E_s}{2(1+\nu)},\qquad \lambda=\frac{E_s\nu}{(1+\nu)(1-2\nu)}')
        G=p.Es/(2*(1+p.nu))
        lam=p.Es*p.nu/((1+p.nu)*(1-2*p.nu))
        st.write(f'For the current inputs: soil Young’s modulus Eₛ = {p.Es/1e6:.3f} MPa, Poisson ratio ν = {p.nu:.2f}, shear modulus G = {G/1e6:.3f} MPa, and first Lamé parameter λ = {lam/1e6:.3f} MPa.')
        st.markdown('λ is related to volume change but is not the bulk modulus. The bulk modulus is K = λ + 2G/3. Neither G nor λ represents damping; this model has no damping or energy dissipation.')
        st.markdown('**Using energy to find equilibrium.** A spring stores elastic energy U = kx²/2, where k is its stiffness and x is its displacement. The derivative dU/dx = kx gives the force that resists movement. We use the same principle for the column: calculate the energy associated with soil deformation, membrane movement, and air compression, then use its derivatives to balance their resistance against the applied load in Step 8.')
        st.markdown('For this strain field, the elastic energy stored per unit soil volume is:')
        st.latex(r'w_s=G(\varepsilon_r^2+\varepsilon_\theta^2+\varepsilon_z^2)+\frac{\lambda}{2}(\varepsilon_r+\varepsilon_\theta+\varepsilon_z)^2')
        st.markdown('The sum εᵣ + εθ + εz is the small volumetric strain: the relative volume change of a soil element. The squared strains describe the stored elastic energy. The G term also contributes to resistance to volume change; it should not be interpreted as a shear-only energy term.')
        st.latex(r'U_s=2\pi H\int_{r_i}^{r_o}w_s\,r\,dr')
        st.markdown('Here r is the original radial coordinate, rᵢ and rₒ are the inner and outer soil radii, and H is the initial height. A thin cylindrical shell has volume 2πrH dr; adding its energy over all radii gives the total soil energy. The solver evaluates this integral numerically.')
        st.markdown('**Material assumptions:** stiffness does not change with stress or loading history. There is no yield, plasticity, hardening, pore-water-pressure calculation, or consolidation. Choose elastic properties appropriate to the intended stress range and drainage conditions. ν = 0.5 is excluded because this compressible formulation becomes singular.')

    with st.expander('Step 6 · Represent each membrane as a hoop spring'):
        st.markdown('When a cylindrical membrane moves radially by u, its circumference changes by 2πu. Its hoop strain is therefore u/r. Multiplying the elastic energy density by the reference membrane volume gives:')
        st.latex(r'U_m=\frac12k_iu_i^2+\frac12k_ou_o^2,\qquad k_j=\frac{2\pi HE_jt_j}{r_j}\quad(j=i,o)')
        st.markdown('**Symbols:** Uₘ is total membrane elastic energy (J); kᵢ and kₒ are inner and outer generalized radial spring stiffnesses (N/m); uᵢ and uₒ are radial movements (m). For membrane j, Eⱼ is Young’s modulus (Pa), tⱼ is thickness (m), and rⱼ is radius (m); j = i denotes the inner wall and j = o the outer wall. H is specimen height (m).')
        ki=2*np.pi*p.H*p.Ei*p.ti/p.ri
        ko=2*np.pi*p.H*p.Eo*p.to/p.ro
        st.write(f'Current effective hoop springs: inner kᵢ = {ki/1000:,.2f} N/mm; outer kₒ = {ko/1000:,.2f} N/mm.')
        st.markdown('Each spring describes the resistance of an entire membrane to uniform radial movement. A higher Young’s modulus or a greater thickness increases this resistance. The formula also includes membrane height and radius. Since the two membranes have the same height, compare Eᵢtᵢ/rᵢ with Eₒtₒ/rₒ to see which offers greater radial resistance.')
        st.markdown('**Membrane assumptions:** thin walls, maintained contact, hoop resistance only, and no axial membrane force, bending, or Poisson coupling. The springs resist either sign of incremental movement. A real soft membrane may wrinkle or buckle if its total hoop tension is lost; this model does not check that condition or calculate initial membrane tension.')

    with st.expander('Step 7 · Couple cavity volume to air pressure'):
        st.markdown('The exact cylindrical volume would be π(rᵢ + uᵢ)²(H − δ). Keeping only terms linear in displacement gives:')
        st.latex(r'\Delta V=2\pi r_iHu_i-\pi r_i^2\delta,\qquad V_0=\pi r_i^2H')
        st.markdown('**Symbols:** V₀ is initial cavity volume (m³); ΔV is its additional volume change (m³); δ is top shortening (m); uᵢ is inner-wall radial movement (m). The symbol Δ means change from the initial pressurized state.')
        st.markdown('The first term increases volume when the inner membrane moves outward; the second decreases volume when the plate moves downward. Thus cavity volume can decrease even when the inner membrane moves outward.')
        st.latex(r'p_{0,\mathrm{abs}}=p_{\mathrm{atm}}+p_{0,\mathrm{gauge}}')
        st.markdown('**Pressure symbols:** p₀,abs is initial absolute air pressure, pₐₜₘ is atmospheric pressure, and p₀,gauge is initial pressure above atmosphere (all in Pa internally). Below, Δp is pressure change (Pa), and Uₐ is the incremental gas-resistance energy used by this model (J). Uₐ is not a calculation of the gas’s total thermodynamic internal energy.')
        st.markdown('**Sealed air:** no air enters or leaves. Slow loading is approximated as isothermal, meaning constant temperature. With ideal-gas behavior, pV = p₀V₀; its first-order change is:')
        st.latex(r'\Delta p=-\frac{p_{0,\mathrm{abs}}}{V_0}\Delta V,\qquad U_a=\frac{p_{0,\mathrm{abs}}}{2V_0}(\Delta V)^2')
        st.markdown('Compression of the cavity raises pressure; expansion lowers it. Absolute pressure controls compressibility, so even zero gauge pressure gives gas resistance. Pressure is assumed spatially uniform; fast-loading thermal effects and gas flow dynamics are omitted.')
        st.markdown('**Regulated air:** a regulator exchanges air to keep pressure constant, giving Δp = 0. Initial pressure forces remain balanced in the reference state; the gas adds no incremental stiffness in this simplified formulation.')
        st.write(f'Current mode: {"sealed isothermal" if p.sealed else "regulated constant pressure"}. Initial absolute pressure = {(p.p_atm+p.p_gauge)/1000:.3f} kPa; relative volume change = {100*result["dV_ratio"]:+.4f}%; pressure increment = {result["dp"]/1000:+.4f} kPa.')
        st.markdown('**Prestress approximation:** the model omits geometric stiffness from initial pressure and membrane tension. Changing initial pressure changes the gas stiffness only; it does not solve a new inflated equilibrium or update soil properties. This omission may matter at high initial pressure even when additional strains are small.')

    with st.expander('Step 8 · Balance the load by minimizing total potential energy'):
        st.markdown('**Rationale:** for a single spring under force F, setting d(U − Fx)/dx = 0 gives kx = F. Here we apply the same force-balance principle to three coupled displacements. The stable equilibrium minimizes the quadratic total potential energy.')
        st.markdown('Soil deformation, membrane movement, and gas compression store energy. The applied force does work Fδ. Equilibrium occurs when the first change in total potential energy is zero for each of the three allowed movements:')
        st.latex(r'\Pi=U_s+U_m+U_a-F\delta,\qquad \frac{\partial\Pi}{\partial\mathbf q}=\mathbf0')
        st.markdown('**Symbols:** Π is total incremental potential energy (J); Uₛ, Uₘ, and Uₐ are the soil, membrane, and gas contributions (J). F is additional vertical force (N); Fδ is its work (J). The vector q = [δ, uᵢ, uₒ]ᵀ contains the three movements. Setting each partial derivative to zero enforces equilibrium for its associated movement.')
        st.latex(r'(\mathbf K_s+\mathbf K_m+\mathbf K_a)\mathbf q=[F,0,0]^T')
        st.latex(r'\mathbf K_m=\operatorname{diag}(0,k_i,k_o),\quad\mathbf g=[-\pi r_i^2,\,2\pi r_iH,\,0]^T,\quad\mathbf K_a=\frac{p_{0,\mathrm{abs}}}{V_0}\mathbf g\mathbf g^T')
        st.markdown('The vector g converts movement to cavity-volume change through ΔV = gᵀq; its entries have units of m². A superscript T denotes transpose. The matrices Kₛ, Kₘ, and Kₐ have units of N/m. These stiffness matrices are distinct from the scalar bulk modulus K mentioned in Step 5.')
        st.markdown('Kₛ, Kₘ, and Kₐ are the soil, membrane, and gas stiffness matrices. For regulated air, Kₐ = 0. The right-hand side has zeros in its radial entries because no *additional independent generalized radial forces* are applied; radial soil, membrane, and gas forces still act and balance.')
        st.markdown('Solving these three equations gives the top shortening and the two wall movements together. The stiffnesses stay constant in this model, so doubling the additional force doubles each displacement. This produces straight load–response curves. Real soil may depart from this behavior as the load increases.')

    with st.expander('Step 9 · Interpret the plots and the current solution'):
        st.markdown('**Deformation view:** brown bands are the soil annulus, blue is the cavity, and dashed lines show initial boundaries. The exaggeration factor changes only the displayed movements. Reported dimensions, pressures, strains, and exported values use the actual solution.')
        st.markdown('**Radial profile:** displacement is plotted against original radius, showing how movement varies through the soil thickness. It is not a profile versus height.\n\n**Load curves:** the horizontal axis is additional force, not elapsed time. The dotted vertical line identifies your selected load. The comparison holds all inputs fixed except sealed versus regulated air.\n\n**Apparent axial stiffness:** F/δ, equivalently the inverse unit-load compliance, in N/mm. It combines soil, membranes, and gas; it is not the soil modulus.')
        st.write(f'At F = {force:.2f} N: shortening = {result["delta"]*1000:.5f} mm; inner movement = {result["ui"]*1000:+.5f} mm; outer movement = {result["uo"]*1000:+.5f} mm; final gauge pressure = {result["p_gauge"]/1000:.4f} kPa.')
        st.markdown('**Try a controlled comparison:** keep geometry and material inputs fixed, then switch the air condition. Sealed air adds a positive-semidefinite stiffness, so the model predicts no greater axial shortening under the same force. Individual radial displacements need not change in the same direction. Increase outer membrane modulus or thickness to explore how restricting the outside redistributes radial movement.')

    with st.expander('Step 10 · Check whether the approximation fits your experiment'):
        st.markdown('''| Assumption | What it leaves out or requires |
|---|---|
| Small strain and volume change | Finite deformation and strong nonlinear gas compression |
| Axisymmetric response | Ovalization, eccentric loading, asymmetric collapse |
| Uniform radial movement with height | End-friction effects and barreling |
| Linear elastic soil | Yielding, permanent compaction, stress-dependent stiffness |
| Hoop-only membrane springs | Axial membrane resistance, wrinkling and buckling |
| Maintained contact | Gaps, detachment and contact redistribution |
| Already equilibrated pressure | Initial inflation and initial-stress determination |
| No prestress geometric stiffness | Pressure/tension contributions to geometric tangent stiffness |
| Quasi-static, isothermal sealed air | Inertia and rapid-loading thermal effects |
| Shared moving top plate | Soil-only loading with an independent cavity cap |''')
        st.markdown('The app flags maximum sampled absolute normal strain above **2%**, absolute relative cavity-volume change above **5%**, or a membrane thickness exceeding **10%** of its radius. These are illustrative screening thresholds, not calibrated accuracy guarantees or failure limits. Inverted geometry or nonpositive absolute pressure is nonphysical. Passing the screens does not validate the material model or omitted prestress effects.')
        st.markdown('Use this model to explore mechanisms and parameter sensitivity. Compare measured load, shortening, radial movement, and pressure before interpreting it quantitatively for a real specimen. The companion `MODEL.md` gives the mathematical specification.')
