import sys
sys.path.append("..")
import jsq_ps.models as jsq
import aux.models as aux
import timeit
import numpy as np
import tqdm
import pandas as pd
import math


def compare_all_three(rho, mc_limit, sim_cdf):
        
    # Expon
    expon_cdf = [1 - math.exp(-mu * t) for t in times]
    
    # Method 1
    M1 = jsq.Method1(lambda_, mu, R, mc_limit, infty)
    M1.find_sojourn_time_cdf(times)
    
    # Method 2
    M2 = jsq.Method2(lambda_, mu, R, infty)
    M2.find_sojourn_time_cdf(times)
    
    w_expon = aux.wasserstein_distance(sim_cdf, expon_cdf, gap)
    w_M1 = aux.wasserstein_distance(sim_cdf, M1.sojourn_time_cdf, gap)
    w_M2 = aux.wasserstein_distance(sim_cdf, M2.sojourn_time_cdf, gap)
    
    return w_expon, w_M1, w_M2



R = 3
max_time = 25000
warmup = 1000
lambda_ = 10
infty = 135
num_repetitions = 20
times = np.linspace(0, 1.25, 40)
gap = times[1] - times[0]


# rhos = np.linspace(0.05, 0.95, 19)
rhos = np.linspace(0.05, 0.95, 19)
mc_limits = range(2, 14)
w_expons = []
w_M1s = []
w_M2s = []
rhos_df = []
mc_limit_df = []
for rho in tqdm.tqdm(rhos):
    for mc_limit in tqdm.tqdm(mc_limits):
        mu = lambda_ / (rho * R)
        S = jsq.Simulation(lambda_, mu, 3, max_time, warmup, ps_bar=False)
        S.run(0)
        S.find_sojourn_time_cdf(times)
        w_expon, w_M1, w_M2 = compare_all_three(rho, mc_limit, S.sojourn_time_cdf)
        w_expons.append(w_expon)
        w_M1s.append(w_M1)
        w_M2s.append(w_M2)
        rhos_df.append(rho)
        mc_limit_df.append(mc_limit)

results = pd.DataFrame({
    'w_exp': w_expons,
    'w_M1': w_M1s,
    'w_M2': w_M2s,
    'rhos': rhos_df,
    'mc_limit': mc_limit_df}
)

results.to_csv('data/all_three_comparison.csv')