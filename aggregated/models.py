from math import factorial as fac


class MMRPS_aggregate:
    def __init__(self, L, m, R, limit=30):
        self.L = L
        self.m = m
        self.R = R
        self.limit = limit
        self.N = float('inf')
        self.rho = self.L / (self.R * self.m)
        self.erlang = self.E2(self.R, self.R * self.rho)

    def E2(self, R, A):
        """
        Earlang function for R servers and A=R·rho
        taken from eq. (6.19) of "Radio Access Network Dimensioning for 3G UMTS"
        """
        num = (A**R / fac(R)) * (R / (R-A))
        den = sum([(A ** i) / fac(i) for i in range(R)]) + (((A ** R) / fac(R)) * (R / (R - A)))
        return num / den

    def p(self, j):
        """
        State probability of having j users in the system in a M/G/R/N-PS model
        lambda_ being the arrival rate mu_ being the service rate
        """
        if j < self.R:
            num = (1 - self.rho) * (fac(self.R) / fac(j)) * ((self.R * self.rho)**(j - self.R)) * self.erlang
            den = 1 - (self.erlang * (self.rho ** (self.N - self.R)) * self.rho)
            return num / den
        elif self.R <= j <= self.N:
            num = self.erlang * (self.rho ** (j - self.R)) * (1 - self.rho)
            den = 1 - (self.erlang * (self.rho ** (self.N - self.R)) * self.rho)
            return num / den
        return 0

    def get_probs(self):
        """
        Get all probabilities
        """
        probs = {}
        for state in range(self.limit):
            probs[state] = self.p(state)
        self.probs = probs
