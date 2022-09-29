import time
import sys
import os
sys.path.append("..")
import argparse

import os
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["NUMEXPR_NUM_THREADS"] = "1" 
os.environ["OMP_NUM_THREADS"] = "1" 

import json
import jsq_ps.models as jsq
import pandas as pd
import numpy as np
import multiprocessing


def get_cdf(R, lambda_, cfg):
    mc_limit = cfg['mc_limit'][str(R)]
    rho = round(lambda_ / R, 2)

    # Path to store, e.g., at sweep/methodA/
    file_path = f'sweep/{cfg["method"]}/'
    file_path += f'mc_limit={mc_limit}-'
    file_path += f'infty={cfg["infty"]}-R={R}-rho={rho}.csv'

    if cfg['method'] == 'methodA':
        tic = time.process_time()
        M = jsq.MethodA(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
        tac = time.process_time()
    elif cfg['method'] == 'methodB':
        tic = time.process_time()
        M = jsq.MethodB(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
        tac = time.process_time()
    elif cfg['method'] == 'methodC':
        tic = time.process_time()
        M = jsq.MethodC(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
        tac = time.process_time()
    elif cfg['method'] == 'methodD':
        tic = time.process_time()
        M = jsq.MethodD(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
        tac = time.process_time()
    elif cfg['method'] == 'methodE':
        tic = time.process_time()
        M = jsq.MethodE(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
        tac = time.process_time()
    else: # methodF
        tic = time.process_time()
        M = jsq.MethodF(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
        tac = time.process_time()
                

    pd.DataFrame({'sojourn_time': times,
        'cdf': M.sojourn_time_cdf}).to_csv(file_path)
    time_path = '.'.join(file_path.split('.')[:-1]) + '-runtime.csv'
    pd.DataFrame({'R': [R], 
                  'rho': [rho],
                  'infty': [cfg['infty']],
                  'mc_limit': [mc_limit],
                  'method': [cfg['method']],
                  'runtime': [tac - tic],
                 }).to_csv(time_path)


        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('method', help='Method')
    # parser.add_argument('Rmin', help='Minmum R')
    # parser.add_argument('Rmax', help='Maximum R')
    parser.add_argument('n_cores', help='Number of Cores to use')
    args = parser.parse_args()

    todoF = [('F', 1, 0.96), ('F', 2, 0.06), ('F', 2, 0.96), ('F', 3, 0.96), ('F', 4, 0.04), ('F', 4, 0.96), ('F', 5, 0.96), ('F', 6, 0.03), ('F', 6, 0.96), ('F', 7, 0.96), ('F', 8, 0.03), ('F', 8, 0.96), ('F', 9, 0.96), ('F', 10, 0.03), ('F', 10, 0.96)]
    todoC = [('C', 1, 0.96), ('C', 2, 0.05), ('C', 3, 0.96), ('C', 4, 0.04), ('C', 4, 0.96), ('C', 5, 0.96), ('C', 6, 0.03), ('C', 6, 0.96), ('C', 7, 0.96), ('C', 8, 0.01), ('C', 8, 0.96), ('C', 9, 0.96), ('C', 10, 0.02), ('C', 10, 0.96)]

    fname = f'sweep-configs/sweep-methodC.json'
    with open(fname) as f:
        cfg = json.load(f)

    # Rmin = int(args.Rmin)
    # Rmax = int(args.Rmax)
    n_cores = int(args.n_cores)

    # Obtain the lambdas to iterate over depending on R
    # 
    # Note: the goal is to compare all by means of load ρ
    # we assume μ=1, since ρ=λ/(cμ) we have  λ=ρ·c
    mu = 1
    # lambdas_fn = lambda R: R*np.arange(cfg['rho_min'],
    #                             cfg['rho_max']+cfg['rho_step'],
    #                             cfg['rho_step'])
    # create times
    times = []
    t = 0.0
    while t <= cfg['sojourn_max']:
        times.append(t)
        t += 0.01
    
    pool = multiprocessing.Pool(n_cores)
    func_arguments = [(R, rho * R, cfg) for m, R, rho in todoC]
    pool.starmap(get_cdf, func_arguments)
