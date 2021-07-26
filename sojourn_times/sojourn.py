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

        h =  ((n / (n + 1)) * (self.mu / (self.lambda_ + self.mu)) * self.hs.get((n-1, k-1), self.h(n-1, k-1))) +\
               ((self.lambda_ / (self.lambda_ + self.mu)) * self.h(n+1, k-1))
        self.hs[(n, k)] = h
        return h


    def W(self, x):
        """
        Derive Pr[W>x], that is, the probability that the sojourn time of a
        user is >x
        """
        return sum([(1 - self.rho) * (self.rho**n) * sum([
                        ((((self.lambda_ + self.mu)**k) * (x**k)) / self.fac_ks[k]) * exp(-(self.lambda_ + self.mu) * x) * self.h(n, k)\
                        for k in range(self.infty)])
                   for n in range(self.infty)])
    



