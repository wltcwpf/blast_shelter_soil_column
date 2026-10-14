"""Incremental axisymmetric elastic annulus with hoop membranes and cavity gas."""
from dataclasses import dataclass, asdict
import numpy as np
from numpy.polynomial.legendre import leggauss

@dataclass(frozen=True)
class Parameters:
    H: float = 0.30
    ri: float = 0.025
    ro: float = 0.05
    Es: float = 5e6
    nu: float = 0.30
    Ei: float = 1e6
    ti: float = 0.0005
    Eo: float = 100e6
    to: float = 0.001
    p_gauge: float = 50e3
    p_atm: float = 101325.0
    sealed: bool = True

    def validate(self):
        vals = list(asdict(self).values())
        if not all(np.isfinite(v) for v in vals):
            raise ValueError('All parameters must be finite.')
        if not (self.H > 0 and 0 < self.ri < self.ro):
            raise ValueError('Require positive height and 0 < inner radius < outer radius.')
        if not (self.Es > 0 and -1 < self.nu < 0.5):
            raise ValueError('Require positive soil modulus and -1 < Poisson ratio < 0.5.')
        if min(self.Ei, self.ti, self.Eo, self.to) < 0:
            raise ValueError('Membrane moduli and thicknesses must be nonnegative.')
        if self.p_atm <= 0 or self.p_atm + self.p_gauge <= 0:
            raise ValueError('Atmospheric and initial absolute pressures must be positive.')

def coefficients(p):
    a = np.array([0., -p.ri, p.ro]) / (p.ro**2-p.ri**2)
    b = np.array([0., p.ri, 0.]) - p.ri**2*a
    return a, b

def assemble(p):
    p.validate()
    G = p.Es/(2*(1+p.nu))
    lam = p.Es*p.nu/((1+p.nu)*(1-2*p.nu))
    C = 2*G*np.eye(3)+lam*np.ones((3,3))
    a,b = coefficients(p)
    x,w = leggauss(32)
    radii = (p.ro+p.ri)/2+(p.ro-p.ri)*x/2
    weights = (p.ro-p.ri)*w/2
    K = np.zeros((3,3))
    for r,weight in zip(radii,weights):
        B = np.vstack([a-b/r**2,a+b/r**2,[-1/p.H,0,0]])
        K += 2*np.pi*p.H*r*weight*(B.T@C@B)
    K += np.diag([0,2*np.pi*p.H*p.Ei*p.ti/p.ri,
                     2*np.pi*p.H*p.Eo*p.to/p.ro])
    g = np.array([-np.pi*p.ri**2,2*np.pi*p.ri*p.H,0])
    V0 = np.pi*p.ri**2*p.H
    if p.sealed:
        K += (p.p_atm+p.p_gauge)/V0*np.outer(g,g)
    return K,g,V0

def solve(p, force):
    if not np.isfinite(force) or force < 0:
        raise ValueError('Additional compression force must be finite and nonnegative.')
    K,g,V0 = assemble(p)
    q = np.zeros(3) if force == 0 else np.linalg.solve(K,[force,0,0])
    delta,ui,uo = q
    dV = float(g@q)
    dp = -(p.p_atm+p.p_gauge)*dV/V0 if p.sealed else 0.
    a,b = coefficients(p)
    r = np.linspace(p.ri,p.ro,150)
    A,B = a@q,b@q
    strains = np.vstack([A-B/r**2,A+B/r**2,np.full_like(r,-delta/p.H)])
    return dict(q=q, delta=delta, ui=ui, uo=uo, dp=dp,
                p_abs=p.p_atm+p.p_gauge+dp, p_gauge=p.p_gauge+dp,
                dV_ratio=dV/V0, max_strain=float(np.max(np.abs(strains))),
                valid_geometry=bool(p.H-delta>0 and 0<p.ri+ui<p.ro+uo),
                r=r, ur=A*r+B/r, K=K)

def sweep(p, maximum_force, count=101):
    # Linearity permits one solve for the entire loading path.
    unit = solve(p,1.)
    f = np.linspace(0,maximum_force,count)
    return dict(force_N=f, shortening_mm=unit['delta']*f*1000,
                inner_displacement_mm=unit['ui']*f*1000,
                outer_displacement_mm=unit['uo']*f*1000,
                pressure_gauge_kPa=(p.p_gauge+unit['dp']*f)/1000,
                relative_volume_change=unit['dV_ratio']*f)
