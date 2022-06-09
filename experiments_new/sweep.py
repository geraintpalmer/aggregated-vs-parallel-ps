import time
import sys
import os
sys.path.append("..")
import argparse
import json
import jsq_ps.models as jsq
import jsq_ps_new.models as jsq_new
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

    # Obtain the lambdas to iterate over depending on R
    # 
    # Note: the goal is to compare all by means of load ρ
    # we assume μ=1, since ρ=λ/(cμ) we have  λ=ρ·c
    mu = 1
    lambdas_fn = lambda R: R*np.arange(cfg['rho_min'],
                                cfg['rho_max']+cfg['rho_step'],
                                cfg['rho_step'])


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
            for lambda_ in lambdas_fn(R):
                rho = round(lambda_ / R, 2)
                run_times = []
                for _ in range(cfg['repetitions']):
                    # Store the simulation in parquet
                    path = f'sweep/simulation/R={R}-rho={rho}'
                    file_path = path + f'/sim{_}.pq'
                    try:
                        os.mkdir(path)
                    except FileExistsError:
                        pass

                    print(f'simulating {file_path}')
                    S = jsq.Simulation(lambda_, mu, R, cfg['max_time'],
                                       cfg['warmup'], ps_bar=False)
                    tic = time.time()
                    S.run(seed=tic)
                    S.find_sojourn_time_cdf(times)
                    run_times.append( time.time() - tic )

                    print(f'storing simulation cdf at {file_path}')
                    pd.DataFrame({'sojourn_time': times,
                        'cdf': S.sojourn_time_cdf}).to_csv(file_path)

                    file_path = path + f'/sim{_}_recs.pq'
                    print(f'storing simulation records at {file_path}')
                    pd.DataFrame(S.recs).to_csv(file_path)

                file_path = path + '/' + path.split('/')[-1] + '-runtimes.csv'
                pd.DataFrame({'simulation': list(range(len(run_times))),
                              'run_time': run_times}).to_csv(file_path)
            

    else:
        for R in range(cfg['R_min'], cfg['R_max']+1):
            mc_limit = cfg['mc_limit'][str(R)]

            for lambda_ in lambdas_fn(R):
                rho = round(lambda_ / R, 2)

                # Path to store, e.g., at sweep/methodA/
                file_path = f'sweep/{cfg["method"]}/'
                file_path += f'mc_limit={mc_limit}-'
                file_path += f'infty={cfg["infty"]}-R={R}-rho={rho}.csv'

                print(f"computing {file_path}")

                if cfg['method'] == 'method1':
                    tic = time.process_time()
                    M = jsq.Method1(lambda_, mu, R, mc_limit, cfg['infty'])
                    M.find_sojourn_time_cdf(times)
                    tac = time.process_time()
                elif cfg['method'] == 'method2':
                    tic = time.process_time()
                    M = jsq.Method2(lambda_, mu, R, cfg['infty'])
                    M.find_sojourn_time_cdf(times)
                    tac = time.process_time()
                elif cfg['method'] == 'methodA':
                    tic = time.process_time()
                    M = jsq_new.MethodA(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
                    tac = time.process_time()
                elif cfg['method'] == 'methodB':
                    tic = time.process_time()
                    M = jsq_new.MethodB(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
                    tac = time.process_time()
                elif cfg['method'] == 'methodC':
                    tic = time.process_time()
                    M = jsq_new.MethodC(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
                    tac = time.process_time()
                elif cfg['method'] == 'methodD':
                    tic = time.process_time()
                    M = jsq_new.MethodD(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
                    tac = time.process_time()
                elif cfg['method'] == 'methodE':
                    tic = time.process_time()
                    M = jsq_new.MethodE(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
                    tac = time.process_time()
                else: # methodF
                    tic = time.process_time()
                    M = jsq_new.MethodF(lambda_, mu, R, mc_limit, cfg['infty'], times=times)
                    tac = time.process_time()
                

                print(f"storing {file_path}")
                pd.DataFrame({'sojourn_time': times,
                    'cdf': M.sojourn_time_cdf}).to_csv(file_path)
                time_path = '.'.join(file_path.split('.')[:-1]) + '-runtime.csv'
                print(f"storing run-time {file_path}")
                pd.DataFrame({'R': [R], 
                              'rho': [rho],
                              'infty': [cfg['infty']],
                              'mc_limit': [mc_limit],
                              'method': [cfg['method']],
                              'runtime': [tac - tic],
                             }).to_csv(time_path)


        
