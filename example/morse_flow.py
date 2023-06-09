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


# create the potential
def pot_func(pos):
    '''Potential function desired.'''
    pos = pos-2.
    return 0.5*(torch.exp(-2.*(pos)) - 2.*torch.exp(-pos)).view(-1, 1)

# nanalytic solution


def sol(pos):
    '''Analytical solution of the 1D harmonic oscillator.'''
    pos = pos-2
    vn = torch.exp(-torch.exp(-pos)-0.5*pos)
    return vn / torch.max(vn)


# create the flow
dim = 1  # number of dimensions
K = 1

# define normal base dist
mu = torch.tensor([-3.], requires_grad=True)
sigma = torch.tensor([0.5], requires_grad=True)
q0 = torch.distributions.Normal(mu, sigma)


# define affin trans
loc = torch.tensor([1.], requires_grad=True)
s = torch.tensor([1.], requires_grad=True)
affine_transform = T.AffineTransform(loc=loc, scale=s)

# define exp trans
exp_transform = T.ExpTransform()

# define pow trans
s = torch.tensor([1.], requires_grad=True)
pow_transform = T.PowerTransform(s)
flow_transform = [affine_transform, exp_transform, pow_transform]

flow = Flow(q0, flow_transform)


wf = WaveFunctionFlow1D(pot_func, flow)

# optimizer
opt = optim.Adam(
    [affine_transform.loc, affine_transform.scale]
    + [q0.loc, q0.scale]
    + [pow_transform.exponent], lr=0.05)

# solver
solver = FlowSolver(wf=wf, optimizer=opt)

domain = {'min': -5., 'max': 10.}
plotter = plotter1d(wf, domain, 100, sol=sol,
                    xlim=(-5, 10), ylim=(-1, 1.), flow=True)
solver.run(500, 1000, loss='energy-manual', plot=plotter)

# plot the final wave function
plot_results_1d(solver, domain, 100, sol,
                e0=-0.125, load='model.pth', flow=True)
