
import torch 
import numpy as np 
from scipy import interpolate

from ase.lattice.cubic import FaceCenteredCubic, Diamond

def get_exp_rdf(data, nbins, r_range, obs):
    # load RDF data 
    f = interpolate.interp1d(data[:,0], data[:,1])
    start = r_range[0]
    end = r_range[1]
    xnew = np.linspace(start, end, nbins)

    # make sure the rdf data is normalized
    V = (4/3)* np.pi * (end ** 3 - start ** 3)
    g_obs = torch.Tensor(f(xnew)).to(obs.device)
    g_obs_norm = ((g_obs.detach() * obs.vol_bins).sum()).item()
    g_obs = g_obs * (V/g_obs_norm)
    count_obs = g_obs * obs.vol_bins / V

    return count_obs, g_obs

pair_data_dict = {
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

    'lj_1.2_1.2': {
                'rdf_fn': '../data/LJ_data/rdf_rho1.2_T1.2_dt0.01.csv' ,
                'vacf_fn': '../data/LJ_data/vacf_rho1.2_T1.2_dt0.01.csv' ,
                'rho': 1.2,
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
            },

    'softsphere_0.7_1.0': {
            'rdf_fn': '../data/softsphere_data/rdf_rho0.7_T1.0_dt0.01.csv' ,
            'vacf_fn': '../data/softsphere_data/vacf_rho0.7_T1.0_dt0.01.csv' ,
            'rho': 0.7,
            'T': 1.0, 
            'start': 0.75, 
            'end': 3.3,
            'element': "H",
            'mass': 1.0,
            "N_unitcell": 4,
            "cell": FaceCenteredCubic
            }, 

    'yukawa_0.7_1.0': {
        'rdf_fn': '../data/Yukawa_data/rdf_rho0.7_T1.0_dt0.01.csv' ,
        'vacf_fn': '../data/Yukawa_data/vacf_rho0.7_T1.0_dt0.01.csv' ,
        'rho': 0.7,
        'T': 1.0, 
        'start': 0.5, 
        'end': 3.0,
        'element': "H",
        'mass': 1.0,
        "N_unitcell": 4,
        "cell": FaceCenteredCubic
        }, 

    'yukawa_0.5_1.0': {
        'rdf_fn': '../data/Yukawa_data/rdf_rho0.5_T1.0_dt0.01.csv' ,
        'vacf_fn': '../data/Yukawa_data/vacf_rho0.5_T1.0_dt0.01.csv' ,
        'rho': 0.5,
        'T': 1.0, 
        'start': 0.5, 
        'end': 3.0,
        'element': "H",
        'mass': 1.0,
        "N_unitcell": 4,
        "cell": FaceCenteredCubic
        }, 

    'yukawa_0.3_1.0': {
        'rdf_fn': '../data/Yukawa_data/rdf_rho0.3_T1.0_dt0.01.csv' ,
        'vacf_fn': '../data/Yukawa_data/vacf_rho0.3_T1.0_dt0.01.csv' ,
        'rho': 0.3,
        'T': 1.0, 
        'start': 0.5, 
        'end': 3.0,
        'element': "H",
        'mass': 1.0,
        "N_unitcell": 4,
        "cell": FaceCenteredCubic
        }, 

        }

exp_rdf_data_dict = {
    'Si_2.293_100K': { 'fn': '../data/a-Si/100K_2.293.csv' ,
                       'rho': 2.293,
                        'T': 100.0, 
                        'start': 1.8, 
                        'end': 7.9,
                        'element': "H",
                        'mass': 28.0855,
                        "N_unitcell": 8,
                        "cell": Diamond
                        },
                        
    'Si_2.287_83K': { 'fn': '../data/a-Si/83K_2.287_exp.csv' ,
                       'rho': 2.287,
                        'T': 83.0, 
                        'start': 1.8, 
                        'end': 10.0,
                        'element': "H",
                        'mass': 28.0855,
                        "N_unitcell": 8,
                        "cell": Diamond
                        },

    'Si_2.327_102K_cry': { 'fn': '../data/a-Si/102K_2.327_exp.csv' ,
                       'rho': 2.3267,
                        'T': 102.0, 
                        'start': 1.8, 
                        'end': 8.0,
                        'element': "H",
                        'mass': 28.0855,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        'anneal_flag': True
                        },

    'H20_0.997_298K': { 'fn': "../data/water_exp/water_exp_pccp.csv",
                        'rho': 0.997,
                        'T': 298.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond, #FaceCenteredCubic
                        "pressure": 1.0 # MPa
                        },

    'H20_0.978_342K': { 'fn': "../data/water_exp/water_exp_skinner_342K_0.978.csv",
                       'rho': 0.978,
                        'T': 342.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        "pressure": 1,  #MPa
                        "ref": "https://doi.org/10.1063/1.4902412"
                        },

    'H20_0.921_423K_soper': { 'fn': "../data/water_exp/water_exp_Soper_423K_0.9213.csv",
                       'rho': 0.9213,
                        'T': 423.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        "pressure": 10.0, # MPa
                        "ref": "https://doi.org/10.1016/S0301-0104(00)00179-8"
                        },

    'H20_0.999_423K_soper': { 'fn': "../data/water_exp/water_exp_Soper_423K_0.999.csv",
                       'rho': 0.999,
                        'T': 423.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        "pressure": 190, 
                        "ref": "https://doi.org/10.1016/S0301-0104(00)00179-8"
                        },

    'H20_298K_redd': { 'fn': "../data/water_exp/water_exp_298K_redd.csv",
                       'rho': 0.99749,
                        'T': 298.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        "pressure": 1, 
                        "ref": "https://aip.scitation.org/doi/pdf/10.1063/1.4967719"
                        },

    'H20_308K_redd': { 'fn': "../data/water_exp/water_exp_308K_redd.csv",
                       'rho': 0.99448,
                        'T': 308.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        "pressure": 1, 
                        "ref": "https://aip.scitation.org/doi/pdf/10.1063/1.4967719"
                        },

    'H20_338K_redd': { 'fn': "../data/water_exp/water_exp_338K_redd.csv",
                       'rho': 0.98103,
                        'T': 338.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        "pressure": 1, 
                        "ref": "https://aip.scitation.org/doi/pdf/10.1063/1.4967719"
                        },

    'H20_368K_redd': { 'fn': "../data/water_exp/water_exp_368K_redd.csv",
                       'rho': 0.96241,
                        'T': 368.0, 
                        'start': 1.8, 
                        'end': 7.5,
                        'element': "H" ,
                        'mass': 18.01528,
                        "N_unitcell": 8,
                        "cell": Diamond,
                        "pressure": 1, 
                        "ref": "https://aip.scitation.org/doi/pdf/10.1063/1.4967719"
                        },

    'H2O_long_correlation' : {
                        'ref': 'https://aip.scitation.org/doi/pdf/10.1063/1.4961404'
    },

    'H2O_soper': {
                        'ref': 'https://doi.org/10.1016/S0301-0104(00)00179-8'
    },

    'Argon_1.417_298k': { 'fn': "../data/argon_exp/argon_exp.csv",
                       'rho': 1.417,
                        'T': 298.0, 
                        'start': 2.0, 
                        'end': 9.0,
                        'element': "H",
                        'mass': 39.948,
                        "N_unitcell": 4,
                        "cell": FaceCenteredCubic
                        }
}


angle_data_dict = {
   "water":
        {
        2.7: '../data/water_angle_deepcg_2.7.csv',
        3.7: '../data/water_angle_deepcg_3.7.csv', 
        }
}