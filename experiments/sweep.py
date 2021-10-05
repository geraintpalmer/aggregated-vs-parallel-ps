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

    with open(args['config']) as f:
        cfg = json.load(f)


    # we assume μ=1, so λ=ρ
    mu = 1
    lambdas = [cfg['rho_min']]
    while lambdas[-1] <= cfg['rho_max']:
        lambdas.append( lambdas[-1] + cfg['rho_step'] )



    ################
    ## SIMULATION ##
    ################
    if cfg['method'] == 'simulation':
        for R in range(cfg['R_min'], cfg['R_max']+1):
            for lambda_ in lambdas:
                for _ in range(cfg['repetitions']):
                    # Store the simulation in parquet
                    path = f'sweep/simulation/R={R}-rho={rho}'
                    os.mkdir(path)
                    file_path = path + f'/sim{_}.pq'

                    print(f'simulating {file_path}')
                    S = jsq.Simulation(lambda_, mu, R, cfg['max_time'],
                                       cfg['warmup'], ps_bar=False)
                    S.run(0)

                    print(f'storing simulation at {file_path}')
                    pd.DataFrame( S.recs ).to_parquet(file_path)
            

    else:
        for R in range(cfg['R_min'], cfg['R_max']+1):
            for lambda_ in lambdas:
                if cfg['method'] == 'method1':
                    file_path = f'sweep/method1/'
                    file_path += f'mc_limit={cfg["mc_limit"]}-'
                    file_path += f'infty={cfg["infty"]}-R={R}-rho={rho}.csv'
                elif cfg['method'] == 'method2':
                    file_path = f'sweep/method2/'
                    file_path += f'infty={cfg["infty"]}-R={R}-rho={rho}.csv'


                print(f"computing {file_path}")
                M = jsq.Method1(lambda_, mu, R, cfg['mc_limit'], cfg['infty'])\
                        if cfg['method'] == 'method1' else\
                    jsq.Method2(lambda_, mu, R, cfg['infty'])

                # Define times, note μ=1 is avg. service time
                times = [i/10 for i in range(100)]        # W=[1,10)
                times += [i for i in range(10, 50)]       # W=[10,50)
                times += [i for i in range(50, 100, 5)]   # W=[50,100]
                times += [i for i in range(100, int(cfg['sojourn_max'])+1,
                                                     10)] # W=[50,W_max]
                M.find_sojourn_time_cdf(times)
                

                print(f"storing {file_path}")
                pd.DataFrame({'sojourn_time': times,
                    'cdf': M.sojourn_time_cdf}).to_csv(file_path)

        
