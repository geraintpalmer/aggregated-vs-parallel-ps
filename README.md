# Source code for "Modelling the M/M/R-JSQ-PS Sojourn Time Distribution for URLLC Services"

### List of implemented methods:

+ Simulation (using the Ciw library)
  + Exponential intended service times
  + Uniform intended service times
  + Deterministic intended service times
+ Method A
  + First approximation λn (Markov chain)
  + First approximation An (Markov chain)
  + First approximation wn (matrix exponential)
+ Method B
  + First approximation λn (Markov chain)
  + Second approximation An (birth-death process)
  + First approximation wn (matrix exponential)
+ Method C
  + Second approximation λn (numerical approximations)
  + Second approximation An (birth-death process)
  + First approximation wn (matrix exponential)
+ Method D
  + First approximation λn (Markov chain)
  + First approximation An (Markov chain)
  + Second approximation wn (reccurent relation)
+ Method E
  + First approximation λn (Markov chain)
  + Second approximation An (birth-death process)
  + Second approximation wn (reccurent relation)
+ Method F
  + Second approximation λn (numerical approximations)
  + Second approximation An (birth-death process)
  + Second approximation wn (reccurent relation)



### Repository structure:

- `jsq_ps/`: this contains the `models.py` file with all the classes required to calculate sojourn time cdfs for the JSQ-PR system.
- `aux/`: this contains any auxilliary classes and functions used in the intermediate stages. E.g the markov chain and single MM1-PR models.
- `tests/`: this contains any scripts or notebooks used to test or demonstrate the models defined in `aux/` and `jsq-ps/`.
- `experiments/`: this contains all numerical experiments for the paper.


### Usage

To import the models from inside the repository and other relevant libraries:

```
>>> import numpy as np
>>> import sys
>>> sys.path.append("..")
>>> import jsq_ps.models as jsq
```

To run an instance of the (exponential) simulation:


```
>>> times = np.arange(0, 182, 0.01)  # Create a time domain to find the sojourn time cdf over
>>> S = jsq.Simulation(
...     lambda_=1.5,     # arrival rate of 1.5
...     mu=0.7,          # service rate for intended service times
...     R=3,             # number of parallel servers
...     max_time=10000,  # simulate until 10000 time units
...     warmup=1000,     # disregard results collected before 500 time units
...     times=times      # the time domain to find the cdf over
... )
>>> S.sojourn_time_cdf  # probabilities corresponding to the times in time domain `times`
[0.0,
 0.0057461692205196535,
 0.012491672218520987,
 0.01873750832778148,
 0.024317121918720853,
 0.029147235176548967,
 0.034643570952698204,
 ...]
```

For uniformly distributed services and deterministic services use `jsq.SimulationUniform` and `jsq.SimulationDeterministic` respectively, with different keyword arguments.


To run an approximation method:

```
>>> times = np.arange(0, 182, 0.01)  # Create a time domain to find the sojourn time cdf over
>>> M = jsq.MethodA(
...     lambda_=1.5,     # arrival rate of 1.5
...     mu=0.7,          # service rate for intended service times
...     R=3,             # number of parallel servers
...     limit=22,        # the markov chain limit L1
...     infty=130,       # the sum limit L2
...     times=times      # the time domain to find the cdf over
... )
>>> M.sojourn_time_cdf  # probabilities corresponding to the times in time domain `times`
[-5.329070518200751e-15,
 0.002606808439007846,
 0.005227813944854054,
 0.007862594898075392,
 0.010510736338027904,
 0.013171829870566754,
 0.015845473576975633,
 ...]
```

For the other approximations use `jsq.MethodB`, `jsq.MethodC`, `jsq.MethodD`, `jsq.MethodE`, and `jsq.MethodF`, respectively, with the same keyword arguments.


In order to find the best performing methods for each (R, ρ) pair:

```
>>> import pandas as pd
>>> best = pd.read_csv('experiments/best.csv', index_col=0)
>>> best[(best['R']==3) & (best['rho']==0.71)]['best']
268    C
Name: best, dtype: object
```

This shows that for R=3 and ρ=0.71 the best method to use is method C (`jsq.MethodC`).

