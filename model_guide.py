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
        st.markdown('**Reference-state assumption:** air pressure, soil stress, membrane tension, and support reactions already balance before additional loading. Setting the load to zero returns zero *additional* displacement; it does not mean an unpressurized or unstressed specimen. Changing initial pressure keeps the input geometry fixed rather than simulating inflation.')

    with st.expander('Step 2 · Specify loading, supports, and the three unknowns'):
        st.markdown('A rigid top plate spans **both the annular soil and the central air cavity**. F is the additional total downward force on this shared plate. The bottom is fixed vertically. Frictionless plates allow radial movement at the ends; the model does not include end restraint from friction.')
        st.latex(r'\mathbf q=[\delta,u_i,u_o]^T,\qquad H^{\prime}=H-\delta,\quad r_i^{\prime}=r_i+u_i,\quad r_o^{\prime}=r_o+u_o')
        st.markdown('δ is positive for vertical shortening. uᵢ and uₒ are positive for outward movement. A negative uᵢ means the cavity narrows. These movements are solved together; the app does not force the inner membrane to move inward.')
        st.warning('If your load acts only on the annular soil and the cavity has a mechanically independent end cap, the shared-plate boundary condition must be changed. The current equations do not represent that setup.')

    with st.expander('Step 3 · Approximate the displacement field'):
        st.markdown('Instead of solving displacement at thousands of mesh points, use a smooth radial shape controlled by the two boundary movements. Let r be distance from the axis and z be height above the bottom.')
        st.latex(r'u_r(r)=Ar+\frac{B}{r},\qquad u_z(z)=-\frac{\delta}{H}z')
        st.latex(r'A=\frac{r_ou_o-r_iu_i}{r_o^2-r_i^2},\qquad B=r_iu_i-Ar_i^2')
        st.markdown('A and B are shape coefficients, not extra independent unknowns. Their formulas enforce uᵣ(rᵢ) = uᵢ and uᵣ(rₒ) = uₒ. Vertical displacement is zero at the bottom and −δ at the top.')
        st.markdown('**Axisymmetric assumption:** every direction around the axis behaves identically. **Heightwise approximation:** radial displacement does not vary with height. Thus the walls remain straight in the longitudinal view; barreling and asymmetric buckling cannot appear.')

    with st.expander('Step 4 · Convert displacement into soil strain'):
        st.markdown('Strain measures relative change in length. The radial strain measures stretching through the annulus thickness; hoop strain measures change in circumference; axial strain measures change in height.')
        st.latex(r'\varepsilon_r=\frac{du_r}{dr}=A-\frac{B}{r^2},\quad \varepsilon_\theta=\frac{u_r}{r}=A+\frac{B}{r^2},\quad\varepsilon_z=-\frac{\delta}{H}')
        st.markdown('Positive normal strain means extension; negative means compression. The app displays axial **compressive** strain as +δ/H for readability. Shear strains are zero for this chosen displacement field.')
        st.markdown('**Small-strain assumption:** products of displacement gradients are neglected. This makes the strain equations linear. Large shortening or cavity distortion requires different kinematics.')
        st.write(f'At the current load, axial compressive strain is {100*result["delta"]/p.H:.4f}%; the largest absolute normal strain sampled through the soil is {100*result["max_strain"]:.4f}%.')

    with st.expander('Step 5 · Calculate the elastic resistance of the soil'):
        st.markdown('The soil is modeled as a homogeneous, isotropic, linearly elastic solid. Eₛ controls stiffness and ν controls coupling between axial and lateral deformation. In an unconstrained uniaxial test, positive ν produces lateral expansion during axial compression; the membranes and air modify that response here.')
        st.latex(r'G=\frac{E_s}{2(1+\nu)},\qquad \lambda=\frac{E_s\nu}{(1+\nu)(1-2\nu)}')
        st.markdown('G and λ are elastic constants derived from Eₛ and ν. The stored energy density wₛ is energy per unit soil volume:')
        st.latex(r'w_s=G(\varepsilon_r^2+\varepsilon_\theta^2+\varepsilon_z^2)+\frac{\lambda}{2}(\varepsilon_r+\varepsilon_\theta+\varepsilon_z)^2')
        st.latex(r'U_s=2\pi H\int_{r_i}^{r_o}w_s\,r\,dr')
        st.markdown('The factor 2πrH dr is the volume of a thin cylindrical soil shell. Adding the energies of these shells gives the total soil energy. The solver evaluates this integral using 32-point Gauss–Legendre quadrature.')
        st.markdown('**Material assumptions:** stiffness does not change with stress or loading history, and deformation is recoverable. There is no yield, plasticity, soil hardening, pore-water-pressure calculation, or consolidation. Choose elastic parameters appropriate to the intended stress range and drainage conditions; those conditions are not solved separately. ν = 0.5 is excluded because this compressible formulation becomes singular.')

    with st.expander('Step 6 · Represent each membrane as a hoop spring'):
        st.markdown('When a cylindrical membrane moves radially by u, its circumference changes by 2πu. Its hoop strain is therefore u/r. Multiplying the elastic energy density by the reference membrane volume gives:')
        st.latex(r'U_m=\frac12k_iu_i^2+\frac12k_ou_o^2,\qquad k_j=\frac{2\pi HE_jt_j}{r_j}\quad(j=i,o)')
        ki=2*np.pi*p.H*p.Ei*p.ti/p.ri
        ko=2*np.pi*p.H*p.Eo*p.to/p.ro
        st.write(f'Current effective hoop springs: inner kᵢ = {ki/1000:,.2f} N/mm; outer kₒ = {ko/1000:,.2f} N/mm.')
        st.markdown('These are generalized stiffnesses for uniform radial movement of the entire wall. Both modulus **and thickness** matter, as do radius and height; modulus alone does not determine which boundary is effectively stiffer.')
        st.markdown('**Membrane assumptions:** thin walls, maintained contact, hoop resistance only, and no axial membrane force, bending, or Poisson coupling. The springs resist either sign of incremental movement. A real soft membrane may wrinkle or buckle if its total hoop tension is lost; this model does not check that condition or calculate initial membrane tension.')

    with st.expander('Step 7 · Couple cavity volume to air pressure'):
        st.markdown('The exact cylindrical volume would be π(rᵢ + uᵢ)²(H − δ). Keeping only terms linear in displacement gives:')
        st.latex(r'\Delta V=2\pi r_iHu_i-\pi r_i^2\delta,\qquad V_0=\pi r_i^2H')
        st.markdown('The first term increases volume when the inner membrane moves outward; the second decreases volume when the plate moves downward. Thus cavity volume can decrease even when the inner membrane moves outward.')
        st.latex(r'p_{0,\mathrm{abs}}=p_{\mathrm{atm}}+p_{0,\mathrm{gauge}}')
        st.markdown('**Sealed air:** no air enters or leaves. Slow loading is approximated as isothermal, meaning constant temperature. With ideal-gas behavior, pV = p₀V₀; its first-order change is:')
        st.latex(r'\Delta p=-\frac{p_{0,\mathrm{abs}}}{V_0}\Delta V,\qquad U_a=\frac{p_{0,\mathrm{abs}}}{2V_0}(\Delta V)^2')
        st.markdown('Compression of the cavity raises pressure; expansion lowers it. Absolute pressure controls compressibility, so even zero gauge pressure gives gas resistance. Pressure is assumed spatially uniform; fast-loading thermal effects and gas flow dynamics are omitted.')
        st.markdown('**Regulated air:** a regulator exchanges air to keep pressure constant, giving Δp = 0. Initial pressure forces remain balanced in the reference state; the gas adds no incremental stiffness in this simplified formulation.')
        st.write(f'Current mode: {"sealed isothermal" if p.sealed else "regulated constant pressure"}. Initial absolute pressure = {(p.p_atm+p.p_gauge)/1000:.3f} kPa; relative volume change = {100*result["dV_ratio"]:+.4f}%; pressure increment = {result["dp"]/1000:+.4f} kPa.')
        st.markdown('**Prestress approximation:** the model omits geometric stiffness from initial pressure and membrane tension. Changing initial pressure changes the gas stiffness only; it does not solve a new inflated equilibrium or update soil properties. This omission may matter at high initial pressure even when additional strains are small.')

    with st.expander('Step 8 · Balance the load by minimizing total potential energy'):
        st.markdown('Soil deformation, membrane movement, and gas compression store energy. The applied force does work Fδ. Equilibrium occurs when the first change in total potential energy is zero for each of the three allowed movements:')
        st.latex(r'\Pi=U_s+U_m+U_a-F\delta,\qquad \frac{\partial\Pi}{\partial\mathbf q}=\mathbf0')
        st.latex(r'(\mathbf K_s+\mathbf K_m+\mathbf K_a)\mathbf q=[F,0,0]^T')
        st.latex(r'\mathbf K_m=\operatorname{diag}(0,k_i,k_o),\quad\mathbf g=[-\pi r_i^2,\,2\pi r_iH,\,0]^T,\quad\mathbf K_a=\frac{p_{0,\mathrm{abs}}}{V_0}\mathbf g\mathbf g^T')
        st.markdown('Kₛ, Kₘ, and Kₐ are the soil, membrane, and gas stiffness matrices. For regulated air, Kₐ = 0. The right-hand side has zeros in its radial entries because no *additional independent generalized radial forces* are applied; radial soil, membrane, and gas forces still act and balance.')
        st.markdown('The 3 × 3 system is solved simultaneously. All stiffnesses are constant, so displacement is proportional to additional force. Straight load–response curves are a consequence of this assumption, not evidence that real soil stays elastic at every load.')

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
