import sys
sys.path.append("../..")
import jsq_ps_new.models as jsq
import numpy as np
import pandas as pd
import multiprocessing

Rs = range(1, 11)
rhos = np.linspace(0.01, 0.99, 99)

def write_cdf(R, rho):
    max_sojourn_time = 182.32
    times = []
    t = 0.0
    while t <= max_sojourn_time:
        times.append(t)
        t += 0.01

    file_path = f"expon-R={R}-rho={round(rho, 2)}.csv"
    S = jsq.Simulation(lambda_=rho * R, mu=1, R=R, max_time=160000, warmup=8000, times=times, ps_bar=False)
    S.run(0)
    S.find_sojourn_time_cdf()
    cdf = pd.DataFrame({'sojourn_time': times,'cdf': S.sojourn_time_cdf})
    cdf.to_csv(file_path)



pool = multiprocessing.Pool(16)
args = [(R, rho) for R in Rs for rho in rhos]
pool.starmap(write_cdf, args)
