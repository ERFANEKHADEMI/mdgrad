import argparse
from fit_2_comp import *
from gen_mix_data import * 
from datetime import datetime
from datetime import date
import random
import numpy as np
from ase import io 
from munch import Munch

def prepare_sim(sys, x, params, pairmlp11, pairmlp12, pairmlp22):

    device = params['device']
    sys[x] = Munch()

    # load target rdfs 
    sys[x].target_rdf11 = np.loadtxt(mix_data[x]['rdf11'], delimiter=',')[1]
    sys[x].target_rdf12 = np.loadtxt(mix_data[x]['rdf12'], delimiter=',')[1]
    sys[x].target_rdf22 = np.loadtxt(mix_data[x]['rdf22'], delimiter=',')[1]

    rdf_range = mix_data[x]['rdf_range']


    L = get_unit_len(rho=mix_data[x]['rho'], N_unitcell=4)
    size = mix_data[x]['size']

    # get system 
    atoms = io.read(mix_data[x]['xyz'])
    system = System(atoms, device=device)
    system.set_temperature(mix_data[x]['T'])
    system, atom1_index, atom2_index = mix_system(system, x)

    sys[x].system = system 

    atom1_index = torch.LongTensor(atom1_index)
    atom2_index = torch.LongTensor(atom2_index)
        
    pair = LJFamily(epsilon=2.0, sigma=params['sigma'], rep_pow=6, attr_pow=3) 

    mlp11 = PairPotentials(system, pairmlp11, cutoff=2.5, 
                         nbr_list_device=device, 
                         index_tuple=(atom1_index, atom1_index)).to(device)

    mlp12 = PairPotentials(system, pairmlp12, cutoff=2.5, 
                         nbr_list_device=device, 
                         index_tuple=(atom1_index, atom2_index)).to(device)

    mlp22 = PairPotentials(system, pairmlp22, cutoff=2.5, 
                         nbr_list_device=device, 
                         index_tuple=(atom2_index, atom2_index)).to(device)

    prior = PairPotentials(system, pair, cutoff=2.5, 
                           nbr_list_device=device).to(device) # prior over all patricles 

    model = Stack({'mlppot11': mlp11, 'mlppot22': mlp22, 'mlppot12': mlp12, 'prior': prior})

    # define 
    diffeq = NoseHooverChain(model, 
            system,
            Q=50.0, 
            T=1.2,
            num_chains=5, 
            adjoint=True,
            topology_update_freq=10).to(device)

    sys[x].diffeq = diffeq

    sim = Simulations(system, diffeq)

    sys[x].sim = sim 

    sys[x].rdf11 = rdf(system, nbins=100, r_range=rdf_range, index_tuple=(atom1_index, atom1_index))
    sys[x].rdf22 = rdf(system, nbins=100, r_range=rdf_range, index_tuple=(atom2_index, atom2_index))
    sys[x].rdf12 = rdf(system, nbins=100, r_range=rdf_range, index_tuple=(atom1_index, atom2_index))   

    return sys

def run_mix(params):


    now = datetime.now()
    dt_string = now.strftime("%m-%d-%H-%M-%S") + str(random.randint(0, 100))

    subjob = params['subjob'] + dt_string

    model_path = '{}/{}'.format(params['logdir'], subjob)
    os.makedirs(model_path)

    device = params['device']

    # initialize pair neural nets 
    mlp_parmas = {'n_gauss': int(params['cutoff']//params['gaussian_width']), 
              'r_start': 0.0,
              'r_end': params['cutoff'], 
              'n_width': params['n_width'],
              'n_layers': params['n_layers'],
              'nonlinear': params['nonlinear']}


    # # Define prior potential
    pairmlp11 = pairMLP(**mlp_parmas)
    pairmlp22 = pairMLP(**mlp_parmas)
    pairmlp12 = pairMLP(**mlp_parmas)

    # Define potentials for the ground truth 
    pair11 = LennardJones(epsilon=1.0, sigma=0.9).to(device)
    pair22 = LennardJones(epsilon=1.0, sigma=1.1).to(device)
    pair12 = LennardJones(epsilon=1.0, sigma=1.0).to(device)


    train_sys = {} 
    val_sys = {}

    for x in  params['trainx']: 
        train_sys = prepare_sim(train_sys, x, params, pairmlp11, pairmlp12, pairmlp22)


    if params['valx'] != None:
        for x in  params['valx']: 
            val_sys = prepare_sim(val_sys, x, params, pairmlp11, pairmlp12, pairmlp22)


    # try simulating 
    optimizer = torch.optim.Adam(list(pairmlp11.parameters()) + list(pairmlp22.parameters()) + \
                                 list(pairmlp12.parameters()), lr=params['lr'])

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 
                                              'min', 
                                              min_lr=0.9e-7, 
                                              verbose=True, factor = 0.5, patience=50,
                                              threshold=1e-5)

    print(f"start training for {params['nepochs']} epochs")
    for i in range(params['nepochs']): 

        loss = torch.Tensor([0.0]).to(device)

        for x in params['trainx']:
            v_t, q_t, pv_t = train_sys[x].sim.simulate(steps=50, dt=0.005, frequency=50)

            # check for NaN
            if torch.isnan(q_t.reshape(-1)).sum().item() > 0:
                print("encounter NaN")
                return 10.0, True 

            _, _, sim_rdf11 = train_sys[x].rdf11(q_t)
            _, _, sim_rdf12 = train_sys[x].rdf12(q_t)
            _, _, sim_rdf22 = train_sys[x].rdf22(q_t)

            loss += (sim_rdf11 - torch.Tensor(train_sys[x].target_rdf11).to(device) ).pow(2).mean() + \
                    (sim_rdf12 - torch.Tensor(train_sys[x].target_rdf12).to(device) ).pow(2).mean() + \
                    (sim_rdf22 - torch.Tensor(train_sys[x].target_rdf22).to(device) ).pow(2).mean() 


            if i % 5 == 0:
                plot_pairs(train_sys[x].sim, pair11, pair12, pair22, fn=f'{model_path}/x_{x}_{str(i).zfill(3)}_pot.pdf')
                plot_sim_rdfs(sim_rdf11.detach().cpu(), sim_rdf12.detach().cpu(), sim_rdf22.detach().cpu(), 
                              train_sys[x].target_rdf11, train_sys[x].target_rdf12, train_sys[x].target_rdf22, 
                              mix_data[x]['rdf_range'],
                              f'{model_path}/x_{x}_{str(i).zfill(3)}_rdf.pdf')

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        print(loss.item())

        scheduler.step(loss)


    # run equilibrabtion 

    all_sys = {**train_sys, **val_sys}

    rdf_devs = 0.0

    for x in all_sys.keys():
        for i in range(params['nsim']):
            v_t, q_t, pv_t = all_sys[x].sim.simulate(steps=50, dt=0.005, frequency=50)


        # loop over to compute observables 
        trajs = torch.Tensor( np.stack( all_sys[x].sim.log['positions'])).to(device).detach()

        skip = trajs.shape[0] // 3

        xrange, sim_rdf11 = collect_equilibrium_rdf(trajs[skip:], all_sys[x].rdf11)
        xrange, sim_rdf12 = collect_equilibrium_rdf(trajs[skip:], all_sys[x].rdf12)
        xrange, sim_rdf22 = collect_equilibrium_rdf(trajs[skip:], all_sys[x].rdf22)

        # combine save rdf 
        save_rdf(sim_rdf11, mix_data[x]['rdf_range'], f"{model_path}/equi_x_{x}_rdf11.csv")
        save_rdf(sim_rdf12, mix_data[x]['rdf_range'], f"{model_path}/equi_x_{x}_rdf12.csv")
        save_rdf(sim_rdf22, mix_data[x]['rdf_range'], f"{model_path}/equi_x_{x}_rdf22.csv")

        plot_sim_rdfs(sim_rdf11, sim_rdf12, sim_rdf22, 
                    all_sys[x].target_rdf11, all_sys[x].target_rdf12, all_sys[x].target_rdf22, 
                    mix_data[x]['rdf_range'],
                    f"{model_path}/equi_x_{x}_rdf.pdf")

        plot_pairs(all_sys[x].sim, pair11, pair12, pair22, f"{model_path}/equi_x_{x}_pot", save=True, nbins=1000)

        # save potentials 

        rdf_devs += np.abs(sim_rdf11 - all_sys[x].target_rdf11).mean() + np.abs(sim_rdf12 - all_sys[x].target_rdf12).mean() + \
                     np.abs(sim_rdf22 - all_sys[x].target_rdf22).mean()

        print(rdf_devs)
    return rdf_devs, False


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-logdir", type=str)
    parser.add_argument("-subjob", type=str)
    parser.add_argument("-device", type=int, default=0)
    parser.add_argument("-nepochs", type=int, default=30)
    parser.add_argument("-nsim", type=int, default=40)
    parser.add_argument("-trainx", type=float, nargs='+')
    parser.add_argument("-valx", type=float, nargs='+')
    parser.add_argument("-lr", type=float, default=3e-3)
    parser.add_argument("-gaussian_width", type=float, default=0.25)
    parser.add_argument("-cutoff", type=float, default=2.5)
    parser.add_argument("-sigma", type=float, default=1.0)
    parser.add_argument("-n_width", type=int, default=128)
    parser.add_argument("-n_layers", type=int, default=2)
    parser.add_argument("-nonlinear", type=str, default='SELU')


    params = vars(parser.parse_args())

    run_mix(params)
