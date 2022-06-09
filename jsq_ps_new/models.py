import numpy as np
import itertools
import ciw
import scipy.stats

class Simulation:
    """
    This class derives the sojourn time cdf for a JSQ-PS vis simulation.
    The simulation methodology is via Ciw (v.2.2.0).
    """
    def __init__(self, lambda_, mu, R, max_time, warmup, times, tracker=ciw.trackers.StateTracker(), ps_bar=True):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          max_time: the amount of simulation time to run for
          warmup: the amount of warmup and cooldown time to not collect results
        """
        self.lambda_ = lambda_
        self.mu = mu
        self.R = R
        self.max_time = max_time
        self.warmup = warmup
        self.tracker = tracker
        self.ps_bar = ps_bar
        self.times = times
        self.N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(self.lambda_)] + [
                ciw.dists.NoArrivals() for _ in range(self.R)],
            service_distributions=[
                ciw.dists.Deterministic(0)] + [
                ciw.dists.Exponential(self.mu) for _ in range(self.R)],
            number_of_servers=[float('inf') for _ in range(self.R + 1)],
            routing=[[0 for row in range(self.R+1)] for col in range(self.R+1)]
        )
        self.run(0)
        self.find_sojourn_time_cdf()

    def run(self, seed):
        """
        Runs the simulation.
        seed: the seed to set the random number stream
        """
        ciw.seed(seed)
        self.Q = ciw.Simulation(
            self.N, node_class=[
            self.RoutingDecision] + [ciw.PSNode for _ in range(self.R)],
            tracker=self.tracker)
        self.Q.simulate_until_max_time(self.max_time, progress_bar=self.ps_bar)
        self.recs = self.Q.get_all_records()
        self.recs = [
            r for r in self.recs if (r.arrival_date > self.warmup) and
            (r.arrival_date < self.max_time - self.warmup) and (r.node != 1)]

    def find_sojourn_time_cdf(self):
        """
        Finds the sojourn time cdf
        times: a list of increasing time points, e.g.: [1,2,3,...]
        """
        sojourn_times = [r.service_time for r in self.recs]
        self.sojourn_time_cdf = [0]
        for t in self.times:
            if self.sojourn_time_cdf[-1] < 1:
                per = scipy.stats.percentileofscore(
                        sojourn_times, t, kind='strict') / 100
                self.sojourn_time_cdf.append( per )
            else:
                self.sojourn_time_cdf.append( 1 )
        del self.sojourn_time_cdf[0]

    class RoutingDecision(ciw.Node):
        def next_node(self, ind):
            """
            Finds the next node by looking at the other nodes,
            seeing how busy they are, and routing to the least busy.
            When there is a tie, choose randomly.
            """
            busyness = {n:
                self.simulation.nodes[n].number_of_individuals for n in range(
                    2, self.simulation.network.number_of_nodes + 1)}
            least_busy = min(busyness.values())
            chosen_n = ciw.random_choice(
                [k for k in busyness.keys() if busyness[k] == least_busy])
            return self.simulation.nodes[chosen_n]


class SimulationUniform:
    """
    This class derives the sojourn time cdf for a JSQ-PS vis simulation.
    The simulation methodology is via Ciw (v.2.2.0).
    """
    def __init__(self, lambda_, mu, R, max_time, warmup, tracker=ciw.trackers.StateTracker(), ps_bar=True):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          max_time: the amount of simulation time to run for
          warmup: the amount of warmup and cooldown time to not collect results
        """
        self.lambda_ = lambda_
        self.mu = mu
        self.R = R
        self.max_time = max_time
        self.warmup = warmup
        self.tracker = tracker
        self.ps_bar = ps_bar
        self.N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(self.lambda_)] + [
                ciw.dists.NoArrivals() for _ in range(self.R)],
            service_distributions=[
                ciw.dists.Deterministic(0)] + [
                ciw.dists.Uniform(0, 2 / self.mu) for _ in range(self.R)],
            number_of_servers=[float('inf') for _ in range(self.R + 1)],
            routing=[[0 for row in range(self.R+1)] for col in range(self.R+1)]
        )

    def run(self, seed):
        """
        Runs the simulation.
        seed: the seed to set the random number stream
        """
        ciw.seed(seed)
        self.Q = ciw.Simulation(
            self.N, node_class=[
            self.RoutingDecision] + [ciw.PSNode for _ in range(self.R)],
            tracker=self.tracker)
        self.Q.simulate_until_max_time(self.max_time, progress_bar=self.ps_bar)
        self.recs = self.Q.get_all_records()
        self.recs = [
            r for r in self.recs if (r.arrival_date > self.warmup) and
            (r.arrival_date < self.max_time - self.warmup) and (r.node != 1)]

    def find_sojourn_time_cdf(self, times):
        """
        Finds the sojourn time cdf
        times: a list of increasing time points, e.g.: [1,2,3,...]
        """
        sojourn_times = [r.service_time for r in self.recs]
        self.sojourn_time_cdf = [0]
        for t in times:
            if self.sojourn_time_cdf[-1] < 1:
                per = scipy.stats.percentileofscore(
                        sojourn_times, t, kind='strict') / 100
                self.sojourn_time_cdf.append( per )
            else:
                self.sojourn_time_cdf.append( 1 )
        del self.sojourn_time_cdf[0]

    class RoutingDecision(ciw.Node):
        def next_node(self, ind):
            """
            Finds the next node by looking at the other nodes,
            seeing how busy they are, and routing to the least busy.
            When there is a tie, choose randomly.
            """
            busyness = {n:
                self.simulation.nodes[n].number_of_individuals for n in range(
                    2, self.simulation.network.number_of_nodes + 1)}
            least_busy = min(busyness.values())
            chosen_n = ciw.random_choice(
                [k for k in busyness.keys() if busyness[k] == least_busy])
            return self.simulation.nodes[chosen_n]


class SimulationDeterministic:
    """
    This class derives the sojourn time cdf for a JSQ-PS vis simulation.
    The simulation methodology is via Ciw (v.2.2.0).
    """
    def __init__(self, lambda_, mu, R, max_time, warmup, tracker=ciw.trackers.StateTracker(), ps_bar=True):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          max_time: the amount of simulation time to run for
          warmup: the amount of warmup and cooldown time to not collect results
        """
        self.lambda_ = lambda_
        self.mu = mu
        self.R = R
        self.max_time = max_time
        self.warmup = warmup
        self.tracker = tracker
        self.ps_bar = ps_bar
        self.N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(self.lambda_)] + [
                ciw.dists.NoArrivals() for _ in range(self.R)],
            service_distributions=[
                ciw.dists.Deterministic(0)] + [
                ciw.dists.Deterministic(1 / self.mu) for _ in range(self.R)],
            number_of_servers=[float('inf') for _ in range(self.R + 1)],
            routing=[[0 for row in range(self.R+1)] for col in range(self.R+1)]
        )

    def run(self, seed):
        """
        Runs the simulation.
        seed: the seed to set the random number stream
        """
        ciw.seed(seed)
        self.Q = ciw.Simulation(
            self.N, node_class=[
            self.RoutingDecision] + [ciw.PSNode for _ in range(self.R)],
            tracker=self.tracker)
        self.Q.simulate_until_max_time(self.max_time, progress_bar=self.ps_bar)
        self.recs = self.Q.get_all_records()
        self.recs = [
            r for r in self.recs if (r.arrival_date > self.warmup) and
            (r.arrival_date < self.max_time - self.warmup) and (r.node != 1)]

    def find_sojourn_time_cdf(self, times):
        """
        Finds the sojourn time cdf
        times: a list of increasing time points, e.g.: [1,2,3,...]
        """
        sojourn_times = [r.service_time for r in self.recs]
        self.sojourn_time_cdf = [0]
        for t in times:
            if self.sojourn_time_cdf[-1] < 1:
                per = scipy.stats.percentileofscore(
                        sojourn_times, t, kind='strict') / 100
                self.sojourn_time_cdf.append( per )
            else:
                self.sojourn_time_cdf.append( 1 )
        del self.sojourn_time_cdf[0]

    class RoutingDecision(ciw.Node):
        def next_node(self, ind):
            """
            Finds the next node by looking at the other nodes,
            seeing how busy they are, and routing to the least busy.
            When there is a tie, choose randomly.
            """
            busyness = {n:
                self.simulation.nodes[n].number_of_individuals for n in range(
                    2, self.simulation.network.number_of_nodes + 1)}
            least_busy = min(busyness.values())
            chosen_n = ciw.random_choice(
                [k for k in busyness.keys() if busyness[k] == least_busy])
            return self.simulation.nodes[chosen_n]





class MMk_JSQ_PS_mc:
    """
    A class to hold the Markov chain object for an M/M/R-JSQ-PS system
    """
    def __init__(self, L, m, k, limit=30, zero=0):
        """
        Initialises the Network object
        """
        self.L = L
        self.m = m
        self.k = k
        self.zero=0
        self.limit = limit
        self.State_Space = list(itertools.product(*[range(self.limit) for _ in range(self.k)]))
        self.lenmat = len(self.State_Space)
        self.write_transition_matrix()
        self.solve()
        self.find_proportion_of_n_gets_arrival()

    def find_transition_rates(self, state1, state2):
        """
        Finds the transition rates for given state transition
        """
        delta = tuple(state2[i] - state1[i] for i in range(self.k))
        if delta.count(0) == self.k - 1:
            if delta.count(-1) == 1:
                return self.m
            elif delta.count(1) == 1:
                arriving_node = delta.index(1)
                min_custs = min(state1)
                num_arrival_nodes = state1.count(min_custs)
                arrival_nodes = [i for i, s in enumerate(state1) if s == min_custs]
                if arriving_node in arrival_nodes:
                    return self.L / num_arrival_nodes
        return 0.0

    def write_transition_matrix(self):
        """
        Writes the transition matrix for the markov chain
        """
        transition_matrix = np.array([[self.find_transition_rates(s1, s2) for s2 in self.State_Space] for s1 in self.State_Space])
        row_sums = np.sum(transition_matrix, axis=1)
        self.time_step = 1 / np.max(row_sums)
        self.transition_matrix = transition_matrix - np.multiply(np.identity(self.lenmat), row_sums)

    def solve(self):
        A = np.vstack((self.transition_matrix.transpose()[:-1], np.ones(self.lenmat)))
        b = np.vstack((np.zeros((self.lenmat - 1, 1)), [1]))
        sol = np.linalg.solve(A, b).transpose()[0]
        self.probs =  {self.State_Space[i]: sol[i] for i in range(self.lenmat)}

    def aggregate_states(self):
        """
        Aggregates from individual states to 
        """
        agg_probs = {}
        for state in self.probs.keys():
            agg_state = sum(state)
            if agg_state in agg_probs:
                agg_probs[agg_state] += self.probs[state]
            else:
                agg_probs[agg_state] = self.probs[state]
        self.aggregate_probs = agg_probs

    def find_probs_of_n_custs_on_arrival(self):
        """
        Finds `n_probs`, the probability that the least busy
        queue has n customers
        """
        self.n_probs = {}
        for state in self.probs.keys():
            n = min(state)
            p = max(self.probs[state], self.zero)
            if n in self.n_probs:
                self.n_probs[n] += max(p, self.zero)
            else:
                self.n_probs[n] = max(p, self.zero)

    def find_proportion_of_n_gets_arrival(self):
        """
        Finds `props`, the proportion of arrivals a single PR queue will
        receive if it has `n` customers.
        """
        self.props = []
        for n in range(self.limit):
            pn = 0
            pnarr = 0
            for state in self.probs:
                if state[0] == n:
                    pn += self.probs[state]
                    if min(state) == n:
                        c = state.count(n)
                        pnarr += self.probs[state] / c
            if (pn > self.zero) and (pnarr > self.zero) and (pnarr / pn > self.zero):
                self.props.append(pnarr / pn)
            else:
                self.props.append(0)



class T_defective_mc:
    """
    A class to hold the defective infinitesimal generatror for finding sojourn times
    """
    def __init__(self, lambdas, m, k, infty=130):
        """
        Initialises the Network object
        """
        self.lambdas = lambdas
        self.infty = infty
        self.m = m
        self.State_Space = list(range(infty))
        self.write_transition_matrix()

    def find_transition_rates(self, state1, state2):
        """
        Finds the transition rates for given state transition
        """
        delta = state2 - state1
        if delta == 1:
            return self.lambdas[state1]
        if delta == -1:
            return (state1 - 1) * self.m / state1
        if delta == 0:
            if state1 == 0:
                return -self.lambdas[0]
            if state1 == self.infty - 1:
                return - self.m
            else:
                return -self.lambdas[state1] - self.m
        return 0.0

    def write_transition_matrix(self):
        """
        Writes the transition matrix for the markov chain
        """
        self.transition_matrix = np.array([[self.find_transition_rates(s1, s2) for s2 in self.State_Space] for s1 in self.State_Space])

    def wn(self, times):
        """
        Finds wn(t)
        """
        w = [scipy.linalg.expm(self.transition_matrix * t) @ np.ones(self.infty) for t in times]
        self.wns = [[w[i][n] for i, t in enumerate(times)] for n in range(self.infty)]




class ArrivalRateApproximation:
    def __init__(self, rho, mu, R, infty):
        self.rho = rho
        self.mu = mu
        self.R = R
        self.infty = infty
        self.lambda_ns = [self.lamb(n) for n in range(self.infty)]

    def lamb(self, n):
        """
        Derives λ(n), i.e., the arrival rate to a single queue given that it
        has n clients in the queue

        n: number of clients in a queue
        """
        if n == 0: 
            ap = self.rho / (1-self.rho)
            bp = (-.0263*self.rho**2+.0054*self.rho+.1155)/(self.rho**2-1.939*self.rho+.9534)
            cp = -6.2973*self.rho**4+14.3382*self.rho**3-12.3532*self.rho**2+6.2557*self.rho-1.005
            dp = (-226.1839*self.rho**2+342.3814*self.rho+10.2851) /\
                 (self.rho**3-146.2751*self.rho**2-481.1256*self.rho+599.9166)
            ep = .4462*self.rho**3-1.8317*self.rho**2+2.4376*self.rho-.0512

            return self.mu*(ap - bp*cp**self.R - dp*ep**self.R) # (12) in [2]
        elif n == 1:
            num = self.mu/self.lamb(0) * (self.rho-self.rho**(self.R+1))/(1-self.rho) + self.rho**self.R - 1
            den = 1 + self.lamb(2)/self.mu - self.rho**self.R
            return self.mu * num / den # (9) in [2]
        elif n == 2:
            c3 = -.29
            c2 = .8822
            c1 = -.5349
            c0 = 1.0112
            c2_ = -.1864
            c1_ = 1.195
            c0_ = -.016

            up = c3*self.rho**3 + c2*self.rho**2 + c1*self.rho + c0
            vp = c2_*self.rho**2 + c1_*self.rho + c0_

            return self.mu*(up*vp**self.R) # (11) in [2]

        # n>=3
        return self.rho**self.R * self.mu # (7) from [2]


class SojournTimeEquations:
    def __init__(self, lambda_ns, mu, R, Ans, infty, times):
        self.lambda_ns = lambda_ns
        self.lamb_max = self.lambda_ns[0]
        self.mu = mu
        self.R = R
        self.infty = infty
        self.times = times
        self.Ans = Ans
        tmp = len(Ans)
        if tmp < self.infty:
            self.Ans = [Ans[i] for i in range(tmp)] + [Ans[tmp-1] for _ in range(self.infty - tmp)]
        self.hs = {}
        self.fac_ks = {k: np.math.factorial(k) for k in range(self.infty)}

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

        h =  ((n / (n + 1)) * (self.mu / (self.lamb_max + self.mu)) * self.h(n-1, k-1)) +\
            (1 - ((self.lambda_ns[n] + self.mu)/(self.lamb_max + self.mu))) * self.h(n,k-1) +\
               ((self.lambda_ns[n] / (self.lamb_max + self.mu)) * self.h(n+1, k-1))
        self.hs[(n, k)] = h
        return h

    def wn(self, x, n):
        """
        Derive Pr[W>x|n] where n is the number of customers in the system upon arrival
        """
        return sum([((((self.lamb_max + self.mu)**k) * (x**k)) / self.fac_ks[k])
            * np.exp(-(self.lamb_max + self.mu) * x) * self.h(n, k) for k in range(self.infty)])

    def W(self, x):
        """
        Derive Pr[W>x], that is, the probability that the sojourn time of a
        user is >x
        """
        return sum([self.Ans[n] * self.wn(x, n) for n in range(self.infty)])




def wasserstein_distance(U, V, gap):
    diffs = [abs(u - v) for u, v in zip(U, V)]
    return sum(diffs) * gap




class MethodA:
    def __init__(self, lambda_, mu, R, limit, infty, times):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.limit = limit
        self.infty = infty
        self.times = times

        # Find \lambda_n
        self.M = MMk_JSQ_PS_mc(L=lambda_, m=mu, k=R, limit=limit)
        self.M.solve()
        self.lambda_ns = [self.lambda_ * p for p in self.M.props[:-2]] + [self.lambda_ * self.M.props[-2] for _ in range(self.infty - self.limit + 2)]

        # Find A_n
        self.M.find_probs_of_n_custs_on_arrival()
        self.Ans = self.M.n_probs

        # Find sojourn times
        self.T = T_defective_mc(lambdas=self.lambda_ns, m=self.mu, k=self.R, infty=self.infty)
        self.T.wn(self.times)
        self.sojourn_time_cdf = [1 - sum([self.Ans[n] * self.T.wns[n][i] for n in range(self.limit)]) for i, t in enumerate(self.times)]



class MethodB:
    def __init__(self, lambda_, mu, R, limit, infty, times):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.limit = limit
        self.infty = infty
        self.times = times

        # Find \lambda_n
        self.M = MMk_JSQ_PS_mc(L=lambda_, m=mu, k=R, limit=limit)
        self.M.solve()
        self.lambda_ns = [self.lambda_ * p for p in self.M.props[:-2]] + [self.lambda_ * self.M.props[-2] for _ in range(self.infty - self.limit + 2)]

        # Find A_n
        self.p0 = 1 / (1 + sum([np.prod([l / self.mu for l in self.lambda_ns][:i]) for i in range(self.infty)]))
        self.Ans = [np.prod([l / self.mu for l in self.lambda_ns][:n]) * self.p0 for n in range(self.infty)]

        # Find sojourn times
        self.T = T_defective_mc(lambdas=self.lambda_ns, m=self.mu, k=self.R, infty=self.infty)
        self.T.wn(self.times)
        self.sojourn_time_cdf = [1 - sum([self.Ans[n] * self.T.wns[n][i] for n in range(self.limit)]) for i, t in enumerate(self.times)]



class MethodC:
    def __init__(self, lambda_, mu, R, limit, infty, times):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.limit = limit
        self.infty = infty
        self.times = times

        # Find \lambda_n
        self.Approx = ArrivalRateApproximation(rho=self.lambda_/(self.R * self.mu), mu=self.mu, R=self.R, infty=self.infty)
        self.lambda_ns = self.Approx.lambda_ns

        # Find A_n
        self.p0 = 1 / (1 + sum([np.prod([l / self.mu for l in self.lambda_ns][:i]) for i in range(self.infty)]))
        self.Ans = [np.prod([l / self.mu for l in self.lambda_ns][:n]) * self.p0 for n in range(self.infty)]

        # Find sojourn times
        self.T = T_defective_mc(lambdas=self.lambda_ns, m=self.mu, k=self.R, infty=self.infty)
        self.T.wn(self.times)
        self.sojourn_time_cdf = [1 - sum([self.Ans[n] * self.T.wns[n][i] for n in range(self.limit)]) for i, t in enumerate(self.times)]


class MethodD:
    def __init__(self, lambda_, mu, R, limit, infty, times):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.limit = limit
        self.infty = infty
        self.times = times

        # Find \lambda_n
        self.M = MMk_JSQ_PS_mc(L=lambda_, m=mu, k=R, limit=limit)
        self.M.solve()
        self.lambda_ns = [self.lambda_ * p for p in self.M.props[:-2]] + [self.lambda_ * self.M.props[-2] for _ in range(self.infty - self.limit + 2)]

        # Find A_n
        self.M.find_probs_of_n_custs_on_arrival()
        self.Ans = self.M.n_probs

        # Find sojourn times
        self.STE = SojournTimeEquations(lambda_ns=self.lambda_ns, mu=self.mu, R=self.R, Ans=self.Ans, infty=self.infty, times=self.times)
        self.sojourn_time_cdf = [1 - self.STE.W(t) for t in self.times]



class MethodE:
    def __init__(self, lambda_, mu, R, limit, infty, times):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.limit = limit
        self.infty = infty
        self.times = times

        # Find \lambda_n
        self.M = MMk_JSQ_PS_mc(L=lambda_, m=mu, k=R, limit=limit)
        self.M.solve()
        self.lambda_ns = [self.lambda_ * p for p in self.M.props[:-2]] + [self.lambda_ * self.M.props[-2] for _ in range(self.infty - self.limit + 2)]

        # Find A_n
        self.p0 = 1 / (1 + sum([np.prod([l / self.mu for l in self.lambda_ns][:i]) for i in range(self.infty)]))
        self.Ans = [np.prod([l / self.mu for l in self.lambda_ns][:n]) * self.p0 for n in range(self.infty)]

        # Find sojourn times
        self.STE = SojournTimeEquations(lambda_ns=self.lambda_ns, mu=self.mu, R=self.R, Ans=self.Ans, infty=self.infty, times=self.times)
        self.sojourn_time_cdf = [1 - self.STE.W(t) for t in self.times]



class MethodF:
    def __init__(self, lambda_, mu, R, limit, infty, times):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.limit = limit
        self.infty = infty
        self.times = times

        # Find \lambda_n
        self.Approx = ArrivalRateApproximation(rho=self.lambda_/(self.R * self.mu), mu=self.mu, R=self.R, infty=self.infty)
        self.lambda_ns = self.Approx.lambda_ns

        # Find A_n
        self.p0 = 1 / (1 + sum([np.prod([l / self.mu for l in self.lambda_ns][:i]) for i in range(self.infty)]))
        self.Ans = [np.prod([l / self.mu for l in self.lambda_ns][:n]) * self.p0 for n in range(self.infty)]

        # Find sojourn times
        self.STE = SojournTimeEquations(lambda_ns=self.lambda_ns, mu=self.mu, R=self.R, Ans=self.Ans, infty=self.infty, times=self.times)
        self.sojourn_time_cdf = [1 - self.STE.W(t) for t in self.times]
