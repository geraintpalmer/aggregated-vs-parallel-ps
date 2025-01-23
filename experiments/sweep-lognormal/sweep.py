import sys
sys.path.append("../..")
import jsq_ps.models as jsq
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

    file_path = f"lognormal-R={R}-rho={round(rho, 2)}.csv"
    S = jsq.SimulationLognormal(lambda_=rho * R, mu=1, R=R, max_time=160000, warmup=8000, ps_bar=False, nonzero=True)
    S.run(0)
    S.find_sojourn_time_cdf(times)
    cdf = pd.DataFrame({'sojourn_time': times,'cdf': S.sojourn_time_cdf})
    cdf.to_csv(file_path)



if __name__ == '__main__':
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    args = [(R, rho) for R in Rs for rho in rhos]
    pool.starmap(write_cdf, args)
