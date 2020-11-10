import os
import sys 
import numpy as np
import matplotlib.pyplot as plt
import sys 
#import mdtraj
#from nglview import show_ase, show_file, show_mdtraj
import torch

import matplotlib
from scipy import interpolate

from ase.lattice.cubic import FaceCenteredCubic
from ase import units

from torchmd.interface import GNNPotentials,PairPotentials, Stack
from torchmd.system import System
from torchmd.potentials import ExcludedVolume, LennardJones
from nff.train import get_model

from torchmd.potentials import ExcludedVolume
from nff.train import get_model

from torchmd.md import NoseHooverChain 
from torchmd.observable import rdf, vacf
from torchmd.md import Simulations

matplotlib.rcParams.update({'font.size': 25})
matplotlib.rc('lines', linewidth=3, color='g')
matplotlib.rcParams['axes.linewidth'] = 2.0
matplotlib.rcParams['axes.linewidth'] = 2.0
matplotlib.rcParams["xtick.major.size"] = 6
matplotlib.rcParams["ytick.major.size"] = 6
matplotlib.rcParams["ytick.major.width"] = 2
matplotlib.rcParams["xtick.major.width"] = 2
matplotlib.rcParams['text.usetex'] = False


width_dict = {'tiny': 64,
               'low': 128,
               'mid': 256, 
               'high': 512}

gaussian_dict = {'tiny': 16,
               'low': 32,
               'mid': 64, 
               'high': 128}


data_dict = {
    'lj_0.845_1.5': { 
                      'rdf_fn': '../data/LJ_data/rdf_rho0.845_T1.5_dt0.01.csv' ,
                      'vacf_fn': '../data/LJ_data/vacf_rho0.845_T1.5_dt0.01.csv',
                       'rho': 0.845,
                        'T': 1.5, 
                        'start': 0.75, 
                        'end': 3.3,
                        'element': "H",
                        'mass': 1.0,
                        "N_unitcell": 4,
                        "cell": FaceCenteredCubic
                        },

    'lj_0.845_1.0': {
                    'rdf_fn': '../data/LJ_data/rdf_rho0.845_T1.0_dt0.01.csv' ,
                    'vacf_fn': '../data/LJ_data/vacf_rho0.845_T1.0_dt0.01.csv' ,
                   'rho': 0.845,
                    'T': 1.0, 
                    'start': 0.75, 
                    'end': 3.3,
                    'element': "H",
                    'mass': 1.0,
                    "N_unitcell": 4,
                    "cell": FaceCenteredCubic
                    },

    'lj_0.845_0.75': {
                    'rdf_fn': '../data/LJ_data/rdf_rho0.845_T0.75_dt0.01.csv' ,
                    'vacf_fn': '../data/LJ_data/vacf_rho0.845_T0.75_dt0.01.csv' ,
                   'rho': 0.845,
                    'T': 0.75, 
                    'start': 0.75, 
                    'end': 3.3,
                    'element': "H",
                    'mass': 1.0,
                    "N_unitcell": 4,
                    "cell": FaceCenteredCubic
                    },

    'lj_0.7_1.2': {
                'rdf_fn': '../data/LJ_data/rdf_rho0.7_T1.2_dt0.01.csv' ,
                'vacf_fn': '../data/LJ_data/vacf_rho0.7_T1.2_dt0.01.csv' ,
                'rho': 0.7,
                'T': 1.2, 
                'start': 0.75, 
                'end': 3.3,
                'element': "H",
                'mass': 1.0,
                "N_unitcell": 4,
                "cell": FaceCenteredCubic
                },

    'lj_0.9_1.2': {
                'rdf_fn': '../data/LJ_data/rdf_rho0.9_T1.2_dt0.01.csv' ,
                'vacf_fn': '../data/LJ_data/vacf_rho0.9_T1.2_dt0.01.csv' ,
                'rho': 0.9,
                'T': 1.2, 
                'start': 0.75, 
                'end': 3.3,
                'element': "H",
                'mass': 1.0,
                "N_unitcell": 4,
                "cell": FaceCenteredCubic
                },

    'lj_1.0_1.2': {
            'rdf_fn': '../data/LJ_data/rdf_rho1.0_T1.2_dt0.01.csv' ,
            'vacf_fn': '../data/LJ_data/vacf_rho1.0_T1.2_dt0.01.csv' ,
            'rho': 1.0,
            'T': 1.2, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic

            },
    'lj_0.5_1.2': {
            'rdf_fn': '../data/LJ_data/rdf_rho0.5_T1.2_dt0.01.csv' ,
            'vacf_fn': '../data/LJ_data/vacf_rho0.5_T1.2_dt0.01.csv' ,
            'rho': 0.5,
            'T': 1.2, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic

            }, 

    'lj_1.2_0.75': {
            'rdf_fn': '../data/LJ_data/rdf_rho1.2_T0.75_dt0.01.csv' ,
            'vacf_fn': '../data/LJ_data/vacf_rho1.2_T0.75_dt0.01.csv' ,
            'rho': 1.2,
            'T': 0.75, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic
            },

    'lj_1.0_0.75': {
            'rdf_fn': '../data/LJ_data/rdf_rho1.0_T0.75_dt0.01.csv' ,
            'vacf_fn': '../data/LJ_data/vacf_rho1.0_T0.75_dt0.01.csv' ,
            'rho': 1.0,
            'T': 0.75, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic
            },

    'lj_0.3_1.2': {
            'rdf_fn': '../data/LJ_data/rdf_rho0.3_T1.2_dt0.01.csv' ,
            'vacf_fn': '../data/LJ_data/vacf_rho0.3_T1.2_dt0.01.csv' ,
            'rho': 0.3,
            'T': 1.2, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic
            },


    'lj_0.1_1.2': {
            'rdf_fn': '../data/LJ_data/rdf_rho0.1_T1.2_dt0.01.csv' ,
            'vacf_fn': '../data/LJ_data/vacf_rho0.1_T1.2_dt0.01.csv' ,
            'rho': 0.1,
            'T': 1.2, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic
            },


    'lj_0.7_1.0': {
            'rdf_fn': '../data/LJ_data/rdf_rho0.7_T1.0_dt0.01.csv' ,
            'vacf_fn': '../data/LJ_data/vacf_rho0.7_T1.0_dt0.01.csv' ,
            'rho': 0.7,
            'T': 1.0, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic
            }

        }

from nff.nn.layers import GaussianSmearing
from torch import nn

nlr_dict =  {
    'ReLU': nn.ReLU(), 
    'ELU': nn.ELU(),
    'Tanh': nn.Tanh(),
    'LeakyReLU': nn.LeakyReLU(),
    'ReLU6':nn.ReLU6(),
    'SELU': nn.SELU(),
    'CELU': nn.CELU(),
    'Tanhshrink': nn.Tanhshrink()
}


class pairMLP(nn.Module):
    def __init__(self, n_gauss, r_start, r_end, n_layers, n_width, nonlinear ):
        super(pairMLP, self).__init__()
        

        nlr = nlr_dict[nonlinear]

        self.smear = GaussianSmearing(
            start=r_start,
            stop=r_end,
            n_gaussians=n_gauss,
            trainable=False
        )
        
        self.layers = nn.ModuleList(
            [
            nn.Linear(n_gauss, n_gauss),
            nlr,
            nn.Linear(n_gauss, n_width),
            nlr]
            )

        for _ in range(n_layers):
            self.layers.append(nn.Linear(n_width, n_width))
            self.layers.append(nlr)

        self.layers.append(nn.Linear(n_width, n_gauss))  
        self.layers.append(nlr)  
        self.layers.append(nn.Linear(n_gauss, 1)) 

        
    def forward(self, r):
        r = self.smear(r)
        for i in range(len(self.layers)):
            r = self.layers[i](r)
        return r


def plot_vacf(vacf_sim, vacf_target, fn, path, dt=0.01):

    t_range = np.linspace(0.0,  vacf_sim.shape[0], vacf_sim.shape[0]) * dt 

    plt.plot(t_range, vacf_sim, label='simulation', linewidth=4, alpha=0.6, )
    plt.plot(t_range, vacf_target, label='target', linewidth=2,linestyle='--', c='black' )

    plt.legend()
    plt.show()
    plt.savefig(path + '/vacf_{}.pdf'.format(fn), bbox_inches='tight')
    plt.close()

def plot_rdf( g_sim, rdf_target, fn, path, start, nbins):

    bins = np.linspace(start, 2.5, nbins)

    plt.plot(bins, g_sim , label='simulation', linewidth=4, alpha=0.6)
    plt.plot(bins, rdf_target , label='target', linewidth=2,linestyle='--', c='black')
    
    plt.xlabel("$\AA$")
    plt.ylabel("g(r)")

    plt.show()
    plt.savefig(path + '/rdf_{}.pdf'.format(fn), bbox_inches='tight')
    plt.close()

def get_exp_rdf(data, nbins, r_range, obs):
    # load RDF data 
    f = interpolate.interp1d(data[0], data[1])
    start = r_range[0]
    end = r_range[1]
    xnew = np.linspace(start, end, nbins)
    g_obs = torch.Tensor(f(xnew)).to(obs.device)
    
    return g_obs
    
def JS_rdf(g_obs, g):
    e0 = 1e-5
    g_m = 0.5 * (g_obs + g)
    loss_js =  ( -(g_obs + e0 ) * (torch.log(g_m + e0 ) - torch.log(g_obs +  e0)) ).mean()
    loss_js += ( -(g + e0 ) * (torch.log(g_m + e0 ) - torch.log(g + e0) ) ).mean()

    return loss_js

def get_unit_len(rho, N_unitcell):
 
    L = (N_unitcell / rho) ** (1/3)
    
    return L 


def get_system(data_str, device, size):

    rho = data_dict[data_str]['rho']
    T = data_dict[data_str]['T']

    # initialize states with ASE 
    cell_module = data_dict[data_str]['cell']
    N_unitcell = data_dict[data_str]['N_unitcell']

    L = get_unit_len(rho, N_unitcell)

    print("lattice param:", L)

    atoms = cell_module(directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                              symbol=data_dict[data_str]['element'],
                              size=(size, size, size),
                              latticeconstant= L,
                              pbc=True)
    system = System(atoms, device=device)
    system.set_temperature(T / units.kB)

    return system 

def get_observer(system, data_str, nbins, t_range):

    rdf_data_path = data_dict[data_str]['rdf_fn']
    rdf_data = np.loadtxt(rdf_data_path, delimiter=',')

    vacf_data_path = data_dict[data_str]['vacf_fn']
    vacf_target = np.loadtxt(vacf_data_path, delimiter=',')[:t_range]
    vacf_target = torch.Tensor(vacf_target).to(system.device)

    # define the equation of motion to propagate 
    rdf_start = data_dict[data_str]['start']
    rdf_end = data_dict[data_str]['end']

    xnew = np.linspace(rdf_start , rdf_end, nbins)
        # initialize observable function 
    obs = rdf(system, nbins, (rdf_start , rdf_end) )

    # get experimental rdf 
    rdf_target = get_exp_rdf(rdf_data, nbins, (rdf_start, rdf_end), obs)

    vacf_obs = vacf(system, t_range=t_range) 

    return xnew, rdf_target, obs, vacf_target, vacf_obs

def get_sim(system, model, data_str):

    T = data_dict[data_str]['T']

    diffeq = NoseHooverChain(model, 
            system,
            Q=50.0, 
            T=T,
            num_chains=5, 
            adjoint=True).to(system.device)

    # define simulator with 
    sim = Simulations(system, diffeq)

    return sim

def plot_pair(fn, path, model, prior, device): 

    pair_true = LennardJones(1.0, 1.0).to(device)
    x = torch.linspace(0.95, 2.5, 50)[:, None].to(device)
    
    u_fit = (model(x) + prior(x)).detach().cpu().numpy()
    u_fit = u_fit = u_fit - u_fit[-1] 

    plt.plot( x.detach().cpu().numpy(), 
              u_fit, 
              label='fit', linewidth=4, alpha=0.6)
    
    plt.plot( x.detach().cpu().numpy(), 
              pair_true(x).detach().cpu().numpy(),
               label='truth', 
               linewidth=2,linestyle='--', c='black')

    #plt.ylabel("g(r)")
    plt.legend()      
    plt.show()
    plt.savefig(path + '/potential_{}.jpg'.format(fn), bbox_inches='tight')
    plt.close()

    return u_fit

def fit_lj(assignments, suggestion_id, device, sys_params, project_name):

    n_epochs = sys_params['n_epochs'] 
    n_sim = sys_params['n_sim'] 
    size = sys_params['size']

    #cutoff = assignments['cutoff']
    nbins = assignments['nbins']
    tau = assignments['opt_freq']

    cutoff = 2.5
    t_range = sys_params['t_range']

    rdf_start = 0.75 #assignments['rdf_start']

    data_str_list = sys_params['data']

    if sys_params['val']:
        val_str_list = sys_params['val']
    else:
        val_str_list = []

    print(assignments)

    model_path = '{}/{}'.format(project_name, suggestion_id)
    os.makedirs(model_path)

    print("Training for {} epochs".format(n_epochs))


    system_list = []
    for data_str in data_str_list + val_str_list:
        system = get_system(data_str, device, size) 
        system_list.append(system)

    # Define prior potential

    mlp_parmas = {'n_gauss': int(cutoff//assignments['gaussian_width']), 
              'r_start': 0.0,
              'r_end': 2.5, 
              'n_width': assignments['n_width'],
              'n_layers': assignments['n_layers'],
              'nonlinear': assignments['nonlinear']}

    lj_params = {'epsilon': assignments['epsilon'], 
         'sigma': assignments['sigma'],
        "power": assignments['power']}

    NN = pairMLP(**mlp_parmas)
    pair = ExcludedVolume(**lj_params)

    model_list = []
    for i, data_str in enumerate(data_str_list + val_str_list):

        pairNN = PairPotentials(system_list[i], NN,
                    cutoff=2.5,
                    ).to(device)
        prior = PairPotentials(system_list[i], pair,
                        cutoff=2.5,
                        ).to(device)

        model = Stack({'pairnn': pairNN, 'pair': prior})
        model_list.append(model)


    sim_list = [get_sim(system_list[i], 
                        model_list[i], 
                        data_str) for i, data_str in enumerate(data_str_list + val_str_list)]

    from torchmd.observable import rdf, vacf

    nbins = assignments['nbins']

    rdf_obs_list = []
    vacf_obs_list = []

    rdf_target_list = []
    vacf_target_list = []
    rdf_bins_list = []

    for i, data_str in enumerate(data_str_list + val_str_list):
        x, rdf_target, rdf_obs, vacf_target, vacf_obs = get_observer(system_list[i], data_str, nbins, t_range=t_range)
        rdf_bins_list.append(x)

        rdf_obs_list.append(rdf_obs)
        rdf_target_list.append(rdf_target)
        vacf_obs_list.append(vacf_obs)
        vacf_target_list.append(vacf_target)

    from torchmd.md import Simulations
    optimizer = torch.optim.Adam(list(NN.parameters()), lr=assignments['lr'])

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 
                                                  'min', 
                                                  min_lr=5e-5, 
                                                  verbose=True, factor = 0.5, patience= 20,
                                                  threshold=5e-5)

    # Set up simulations 
    loss_log = []

    # 
    obs_log = dict()

    for i, data_str in enumerate(data_str_list + val_str_list):
        obs_log[data_str] = {}
        obs_log[data_str]['rdf'] = []
        obs_log[data_str]['vacf'] = []


    for i in range(sys_params['n_epochs']):

        loss_rdf = torch.Tensor([0.0]).to(device)
        loss_vacf = torch.Tensor([0.0]).to(device)

        # temperature annealing 
        for j, sim in enumerate(sim_list):

            data_str = (data_str_list + val_str_list)[j]

            # Simulate 
            v_t, q_t, pv_t = sim.simulate(steps=tau, frequency=tau, dt=0.01)

            if torch.isnan(q_t.reshape(-1)).sum().item() > 0:
                return 5 - (i / n_epochs) * 5

            _, _, g_sim = rdf_obs_list[j](q_t)

            vacf_sim = vacf_obs_list[j](v_t)

            if data_str in data_str_list:
                loss_vacf += (vacf_sim - vacf_target_list[j][:t_range]).pow(2).mean()
                loss_rdf += (g_sim - rdf_target_list[j]).pow(2).mean() + JS_rdf(g_sim, rdf_target)


            obs_log[data_str]['rdf'].append(g_sim.detach().cpu().numpy())
            obs_log[data_str]['vacf'].append(vacf_sim.detach().cpu().numpy())

            if i % 20 ==0 :
                plot_vacf(vacf_sim.detach().cpu().numpy(), vacf_target_list[j][:t_range].detach().cpu().numpy(), 
                    fn=data_str + "_{}".format(i), 
                    path=model_path)

                plot_rdf(g_sim.detach().cpu().numpy(), rdf_target_list[j].detach().cpu().numpy(), 
                    fn=data_str + "_{}".format(i),
                     path=model_path, 
                     start=rdf_start, 
                     nbins=nbins)

            if i % 20 ==0 :
                potential = plot_pair( path=model_path,
                             fn=str(i),
                              model=sim.intergrator.model.models['pairnn'].model, 
                              prior=sim.intergrator.model.models['pair'].model, 
                              device=device)

        if assignments['train_vacf'] == "True":
            loss = assignments['rdf_weight'] * loss_rdf + assignments['vacf_weight'] * loss_vacf
        else:
            loss = assignments['rdf_weight'] * loss_rdf


        # save potential file

        if np.array(loss_log[-10:]).mean(0).sum() <=  0.006: 
            np.savetxt(model_path + '/potential.txt',  potential, delimiter=',')

        loss.backward()

        optimizer.step()
        optimizer.zero_grad()
        
        print(loss_vacf.item(), loss_rdf.item())
        
        scheduler.step(loss)
        
        loss_log.append([loss_vacf.item(), loss_rdf.item() ])

        current_lr = optimizer.param_groups[0]["lr"]

        if current_lr <= 5.0e-5:
            print("training converged")
            break

    for j, sim in enumerate(sim_list):

        data_str = (data_str_list + val_str_list)[j]

        plot_vacf(np.array(obs_log[data_str]['vacf'])[-10:].mean(0), vacf_target_list[j][:t_range].detach().cpu().numpy(), 
            fn=data_str + "_{}".format("final"), 
            path=model_path)

        plot_rdf(np.array(obs_log[data_str]['rdf'])[-10:].mean(0), rdf_target_list[j].detach().cpu().numpy(), 
            fn=data_str + "_{}".format("final"),
             path=model_path, 
             start=rdf_start, 
             nbins=nbins)

    # save loss curve 
    plt.plot(np.array( loss_log)[:, 0], label='vacf', alpha=0.7)
    plt.plot(np.array( loss_log)[:, 1], label='rdf', alpha=0.7)
    plt.yscale("log")
    plt.legend()
    plt.savefig(model_path + '/loss.pdf', bbox_inches='tight')
    plt.show()
    plt.close()


    return np.array(loss_log[-10:]).mean(0).sum()
