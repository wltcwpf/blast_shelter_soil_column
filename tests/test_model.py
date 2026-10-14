import unittest
from dataclasses import replace
import numpy as np
from model import Parameters, assemble, coefficients, solve

class MechanicsTests(unittest.TestCase):
    def test_zero_and_linearity(self):
        p=Parameters()
        np.testing.assert_allclose(solve(p,0)['q'],0)
        np.testing.assert_allclose(solve(p,200)['q'],2*solve(p,100)['q'])
    def test_free_uniaxial_solution(self):
        p=replace(Parameters(),Ei=0,Eo=0,sealed=False)
        F=100
        r=solve(p,F)
        stress=F/(np.pi*(p.ro**2-p.ri**2))
        np.testing.assert_allclose(r['delta'],stress*p.H/p.Es,rtol=1e-10)
        np.testing.assert_allclose([r['ui'],r['uo']],p.nu*stress/p.Es*np.array([p.ri,p.ro]),rtol=1e-10)
    def test_stiffness_and_equilibrium(self):
        p=Parameters()
        K,_,_=assemble(p)
        np.testing.assert_allclose(K,K.T,rtol=1e-12,atol=1e-8)
        self.assertGreater(np.linalg.eigvalsh(K).min(),0)
        np.testing.assert_allclose(K@solve(p,100)['q'],[100,0,0],atol=1e-10)
    def test_gas_and_boundaries(self):
        p=Parameters()
        res=solve(p,100)
        a,b=coefficients(p)
        for r,idx in [(p.ri,1),(p.ro,2)]:
            self.assertAlmostEqual((a@res['q'])*r+(b@res['q'])/r,res['q'][idx])
        sealed=solve(p,100)
        regulated=solve(replace(p,sealed=False),100)
        self.assertLessEqual(sealed['delta'],regulated['delta'])
        self.assertAlmostEqual(sealed['dp'],-(p.p_atm+p.p_gauge)*sealed['dV_ratio'])
        self.assertEqual(regulated['dp'],0)
    def test_invalid_input(self):
        for p in [replace(Parameters(),ri=0.1),replace(Parameters(),nu=0.5),replace(Parameters(),Es=-1)]:
            with self.assertRaises(ValueError): solve(p,100)
        with self.assertRaises(ValueError): solve(Parameters(),float('nan'))

if __name__=='__main__': unittest.main()
