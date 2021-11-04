import time
import sys
import os
sys.path.append("..")
import argparse
import json
import jsq_ps.models as jsq
import pandas as pd
import numpy as np

# sweep/
#  | /method1
#  |   mc_limit=?-R=?-rho=?.csv
#  | /method2
#  |   infty=?-R=?-rho=?.csv
#  | /sim
#  |   /R=?-rho=?
#  |     sim0.pq
#  |     sim1.pq
#  |       ...
#  |     sim39.pq




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='JSON file w/ simulation config')
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)


    # we assume μ=1, so λ=ρ
    mu = 1
    lambdas = [cfg['rho_min']]
    while lambdas[-1] < cfg['rho_max']:
        lambdas.append( round(lambdas[-1] + cfg['rho_step'], 4) )

    # create times
    times = []
    t = 0.0
    while t <= cfg['sojourn_max']:
        times.append(t)
        t += 0.01


    ################
    ## SIMULATION ##
    ################
    if cfg['method'] == 'simulation':
        for R in range(cfg['R_min'], cfg['R_max']+1):
            for lambda_ in lambdas:
                run_times = []
                for _ in range(cfg['repetitions']):
                    # Store the simulation in parquet
                    path = f'sweep/simulation/R={R}-rho={lambda_}'
                    file_path = path + f'/sim{_}.pq'
                    try:
                        os.mkdir(path)
                    except FileExistsError:
                        pass

                    print(f'simulating {file_path}')
                    S = jsq.Simulation(lambda_, mu, R, cfg['max_time'],
                                       cfg['warmup'], ps_bar=False)
                    tic = time.time()
                    S.run(0)
                    S.find_sojourn_time_cdf(times)
                    run_times.append( time.time() - tic )

                    print(f'storing simulation cdf at {file_path}')
                    pd.DataFrame({'sojourn_time': times,
                        'cdf': S.sojourn_time_cdf}).to_csv(file_path)

                file_path = path + '/' + path.split('/')[-1] + '-runtimes.csv'
                pd.DataFrame({'simulation': list(range(len(run_times))),
                              'run_time': run_times}).to_csv(file_path)
            

    else:
        for R in range(cfg['R_min'], cfg['R_max']+1):
            mc_limit = cfg['mc_limit'][str(R)]

            for lambda_ in lambdas:
                if cfg['method'] == 'method1':
                    file_path = f'sweep/method1/'
                    file_path += f'mc_limit={mc_limit}-'
                    file_path += f'infty={cfg["infty"]}-R={R}-rho={lambda_}.csv'
                elif cfg['method'] == 'method2':
                    file_path = f'sweep/method2/'
                    file_path += f'infty={cfg["infty"]}-R={R}-rho={lambda_}.csv'


                print(f"computing {file_path}")

                if cfg['method'] == 'method1':
                    tic = time.time()
                    M = jsq.Method1(lambda_, mu, R, mc_limit, cfg['infty'])
                    M.find_sojourn_time_cdf(times)
                    tac = time.time()
                else:
                    tic = time.time()
                    M = jsq.Method2(lambda_, mu, R, cfg['infty'])
                    M.find_sojourn_time_cdf(times)
                    tac = time.time()
                

                print(f"storing {file_path}")
                pd.DataFrame({'sojourn_time': times,
                    'cdf': M.sojourn_time_cdf}).to_csv(file_path)
                time_path = '.'.join(file_path.split('.')[:-1]) + '-runtime.csv'
                print(f"storing run-time {file_path}")
                pd.DataFrame({'R': [R], 
                              'rho': [lambda_],
                              'infty': [cfg['infty']],
                              'mc_limit': [mc_limit],
                              'method': [cfg['method']],
                              'runtime': [tac - tic],
                             }).to_csv(time_path)


        
