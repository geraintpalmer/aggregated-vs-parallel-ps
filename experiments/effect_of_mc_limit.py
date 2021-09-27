import sys
sys.path.append("..")
import jsq_ps.models as jsq
import aux.models as aux
import timeit
import matplotlib.pyplot as plt
import numpy as np
import tqdm
import pandas as pd

def MC_find_sojourn(lambda_, mu, R, mc_limit, infty, times):
    M1 = jsq.Method1(lambda_, mu, R, mc_limit, infty)
    M1.find_sojourn_time_cdf(times)



lambda_ = 14.5
mu = 6.2
R = 3
infty = 130
botlim = 0
toplim = 2.0
number_ts = 50
max_time = 20000
warmup = 1000
num_repetitions = 20
times = np.linspace(botlim, toplim, number_ts)

# Run Simulation for reference
S = jsq.Simulation(lambda_, mu, R, max_time, warmup)
S.run(0)
S.find_sojourn_time_cdf(times)

cdfs = {}
runtimes = []
wasserstein = []
for mc_limit in tqdm.tqdm(range(2, 14)):
	M1 = jsq.Method1(lambda_, mu, R, mc_limit, infty)
	M1.find_sojourn_time_cdf(times)
	cdfs[mc_limit] = M1.sojourn_time_cdf
	w = aux.wasserstein_distance(S.sojourn_time_cdf, M1.sojourn_time_cdf, (toplim - botlim) / number_ts)
	t = timeit.timeit(lambda: MC_find_sojourn(lambda_, mu, R, mc_limit, infty, times), number=num_repetitions)
	wasserstein.append(w)
	runtimes.append(t / num_repetitions)

cdfs_df = pd.DataFrame(cdfs, index=times)
cdfs_df['Simulation'] = S.sojourn_time_cdf
cdfs_df.to_csv('data/effect_mclimit_cdfs_R3.csv')
with open('data/effect_mclimit_wasserstein_R3.csv', 'w') as f:
	f.write(str(wasserstein)[1:-1])
with open('data/effect_mclimit_runtime_R3.csv', 'w') as f:
	f.write(str(runtimes)[1:-1])

