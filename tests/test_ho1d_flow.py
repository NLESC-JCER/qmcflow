from matplotlib import scale
import torch
from torch import optim
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.distributions import constraints
from torch.distributions.transforms import ExpTransform


from qmcflow.wavefunction.wave_function_flow_1d import WaveFunctionFlow1D, Flow, GaussianTransform
from qmcflow.solver.flow_solver import FlowSolver

import pyro.distributions as dist
import pyro.distributions.transforms as T
from pyro.nn import AutoRegressiveNN

import matplotlib.pyplot as plt
from qmcflow.solver.plot import plot_results_1d, plotter1d
from torch.autograd import grad, Variable

from pyro.distributions.transforms.spline import ConditionedSpline
from pyro.distributions.torch_transform import TransformModule

import unittest

# create the potential
def pot_func(pos):
    '''Potential function desired.'''
    return 0.5*pos**2

# analytic solution


def sol(pos):
    '''Analytical solution of the 1D harmonic oscillator.'''
    return torch.exp(-0.5*pos**2)

class TestHarmonicOscillator1D(unittest.TestCase):

    def setUp(self):

        # Set up Wavefunction
        # create base dist
        self.mu = torch.tensor([2.], requires_grad=True)
        self.sigma = torch.tensor([1.], requires_grad=True)
        self.q0 = torch.distributions.Normal(self.mu, self.sigma)

        # create 0 layer flow
        self.flow = Flow(self.q0, [])

        self.wf = WaveFunctionFlow1D(pot_func, self.flow)

        # optimizer
        self.opt = optim.Adam([self.q0.loc, self.q0.scale], lr=0.05)

        # solver
        self.solver = FlowSolver(wf=self.wf, optimizer=self.opt)

        self.domain = {'min': -5., 'max': 5.}

    def test_optimization(self):

        self.solver.run(250, 1000, loss='energy-manual', plot=None)
        
        pos = self.wf.flow.sample([1000])
        pos, e, v = self.solver.single_point(1000, pos=pos, prt=False)
        assert np.allclose([e.data.numpy(), v.data.numpy()], [
                           0.5, 0], atol=1E-3)

if __name__ == "__main__":
    unittest.main()
