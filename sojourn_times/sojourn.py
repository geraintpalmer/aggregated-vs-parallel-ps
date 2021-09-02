from math import factorial as fac
from math import exp
import numpy as np


class MM1PS:
    """
    This class implements the logic proposed in [1] for an M/M/1/PS system.

    [1] Masuyama, Hiroyuki, and Tetsuya Takine. "Sojourn time distribution in a
    MAP/M/1 processor-sharing queue." Operations Research Letters 31.5 (2003):
    406-412.
    """

    def __init__(self, mu, lambda_, infty=1000):
        """
        mu: the arrival rate
        lambda_: the service rate
        infty: number to consider as infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.infty = infty
        self.rho = lambda_ / mu
        self.fac_ks = {k: fac(k) for k in range(infty)}
        self.hs = {}

    def h(self, n, k):
        """
        Derive h_{n,k}. See the expression in Corollary 2 of [1]
        """
        if k <= 0:
            return 1
        if n == -1:
            return 0
        if n >= self.infty:
            return 1
        if (n, k) in self.hs:
            return self.hs[(n, k)]

        h =  ((n / (n + 1)) * (self.mu / (self.lambda_ + self.mu)) * self.h(n-1, k-1)) +\
               ((self.lambda_ / (self.lambda_ + self.mu)) * self.h(n+1, k-1))
        self.hs[(n, k)] = h
        return h

    def wn(self, x, n):
        """
        Derive Pr[W>x|n] where n is the number of customers in the system upon arrival
        """
        return sum([((((self.lambda_ + self.mu)**k) * (x**k)) / self.fac_ks[k]) * exp(-(self.lambda_ + self.mu) * x) * self.h(n, k) for k in range(self.infty)])



    def W(self, x):
        """
        Derive Pr[W>x], that is, the probability that the sojourn time of a
        user is >x
        """
        return sum([(1 - self.rho) * (self.rho**n) * self.wn(x, n) for n in range(self.infty)])
    



class MMKJSQPS:
    """
    This class implements the logic proposed in [2] for an M/M/K/JSQ/PS system.

    [2] Gupta, Varun, et al. "Analysis of join-the-shortest-queue routing for
    web server farms." Performance Evaluation 64.9-12 (2007): 1062-1081.
    """

    def __init__(self, mu, lambda_, K, infty=1000):
        """
        mu: the arrival rate
        lambda_: the service rate
        K: number of servers
        infty: number to consider as infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.K = K
        self.infty = infty
        self.rho = lambda_ / (K*mu)
        self.fac_ks = {k: fac(k) for k in range(infty)}
        self.hs = {}


    def lamb(self, n):
        """
        Derives λ(n), i.e., the arrival rate to a single queue given that it
        has n clients in the queue

        n: number of clients in a queue
        """
        rho = self.rho
        mu = self.mu
        K = self.K

        if n == 0: # use approx. (12) in [2]
            ap = rho / (1-rho)
            bp = (-.0263*rho**2+.0054*rho+.1155)/(rho**2-1.939*rho+.9534)
            cp = -6.2973*rho**4+14.3382*rho**3-12.3532*rho**2+6.2557*rho-1.005
            dp = (-226.1839*rho**2+342.3814*rho+10.2851) /\
                 (rho**3-146.2751*rho**2-481.1256*rho+599.9166)
            ep = .4462*rho**3-1.8317*rho**2+2.4376*rho-.0512

            return mu*(ap - bp*cp**K - dp*ep**K) # (11) in [2]
        elif n == 1:
            c3 = -.29
            c2 = .8822
            c1 = -.5349
            c0 = 1.0112
            c2_ = -.1864
            c1_ = 1.195
            c0_ = -.016

            up = c3*rho**3 + c2*rho**2 + c1*rho + c0
            vp = c2_*rho**2 + c1_*rho + c0_

            return mu*(up*vp**K)

        # n>=3
        return rho**K * mu # (7) from [2]
 

    def h(self, n, k):
        """
        Derive h_{n,k}. See the expression in Corollary 2 of [1]
        """
        lamb_ = max([self.lamb(i) for i in range(self.infty)])

        if k <= 0:
            return 1
        if n == -1:
            return 0
        if n >= self.infty:
            return 1
        if (n, k) in self.hs:
            return self.hs[(n, k)]

        h =  ((n / (n + 1)) * (self.mu / (lamb_ + self.mu)) * self.h(n-1, k-1)) +\
               ((self.lamb(n) / (lamb_ + self.mu)) * self.h(n+1, k-1))
        self.hs[(n, k)] = h
        return h

    def wn(self, x, n):
        """
        Derive Pr[W>x|n] where n is the number of customers in the system upon arrival
        """
        return sum([((((self.lambda_ + self.mu)**k) * (x**k)) / self.fac_ks[k]) * exp(-(self.lambda_ + self.mu) * x) * self.h(n, k) for k in range(self.infty)])



    def W(self, x):
        """
        Derive Pr[W>x], that is, the probability that the sojourn time of a
        user is >x
        """
        return sum([(1 - self.rho) * (self.rho**n) * self.wn(x, n) for n in range(self.infty)])
    

