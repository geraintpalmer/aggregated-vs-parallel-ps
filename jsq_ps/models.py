import aux.models as aux
import ciw
import scipy.stats

class Simulation:
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
                ciw.dists.Exponential(self.mu) for _ in range(self.R)],
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
        times: a list of time points
        """
        sojourn_times = [r.service_time for r in self.recs]
        self.sojourn_time_cdf = [(
            scipy.stats.percentileofscore(
            sojourn_times, t, kind='strict')) / 100 for t in times]

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



class Method1:
    """
    This class derives the sojourn time cdf for a JSQ-PS.
    This combines:
        + Conditional sojourn times for a single PS queue
          from (Masuyama and Takine, 2003)
        + Exact inter-queue dynamics from a Markov chain

    We can define a Markov chain of the system explicitly:
        + States of the markov chain take the form $(a_1, a_2, ..., a_R)$,
          where $a_k$ is the number of customers being served by server $k$;
        + This can be solved to give $p(j)$, the probability of being in state
          $j$, for all $j$.
        + This is computed numerically by choosing a sufficiently large cut-off
          limit, $l$ such that no more customers are admitted to any server with
          $l$ customers.
        + States can be aggregated any way we like.
    
    From (Masuyama and Takine, 2003) we know $P(S>t|n)$ for an M/M/1-PS queue;
    the probability that the sojourn time $S$ is greater than some number $t$,
    conditional on the number of customers already at queue upon arrival, $n$.
    This can be computed numerically by choosing an arbitrary large number
    instead of infinity.

    Now combining then: consider a customer arriving to our JSQ system:
        + From the Markov chain, we know the probability that they will arrive
          while the system is in state $j$ is $p(j)$.
        + Each state $j$ can be transformed into an $n$. Customers are always
          routed to the server with the least servers, so $n = min(j)$.
    Now the arriving customer is essentially arriving to an M/M/1-PS system in
    state $n$:
        + It has the same intended service times with mean $mu$.
        + However it now has state-dependant arrivals. When in state $n$ it
          receives all customers if the other servers have more customers than
          it (rate $Lambda$); $1/c$ of the customers if there are $c$ servers
          with the same number of customers as it and all others have more than
          it (rate $Lambda/c$; and it receives no customers if at least one
          other server has more customers than it (rate $0$).
        + Together then this has rate $lambda_n = pi_n Lambda$ where $pi_n$ is a
          proportion that can be found from $p(j)$.
        + These $lambda_n$'s can be used within the (Masuyama and Takine, 2003)
          to get the sojourn time cdf for this single M/M/1-PS system.
    
    Finally, to get the sojourn time cdf for the JSQ-PS system, aggregate over
    the $n$'s, by multiplying with $p(n)$ and summing.
    """
    def __init__(self, lambda_, mu, R, mc_limit, infty, zero=0):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
          zero: a sufficiently small number to act as zero, to
                avoid any numerical errors
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.mc_limit = mc_limit
        self.infty = infty
        self.zero = zero
        self.markov_chain = aux.MMkPS_mc(L=lambda_, m=mu, k=R, limit=mc_limit)
        self.markov_chain.solve()
        self.find_probs_of_n_custs_on_arrival()
        self.find_proportion_of_n_gets_arrival()
        self.lambda_ns = [self.lambda_ * p for p in self.props]

    def find_probs_of_n_custs_on_arrival(self):
        """
        Finds `n_probs`, the probability that the least busy
        queue has n customers
        """
        self.n_probs = {}
        for state in self.markov_chain.probs.keys():
            n = min(state)
            p = max(self.markov_chain.probs[state], self.zero)
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
        for n in range(self.mc_limit):
            pn = 0
            pnarr = 0
            for state in self.markov_chain.probs:
                if state[0] == n:
                    pn += self.markov_chain.probs[state]
                    if min(state) == n:
                        c = state.count(n)
                        pnarr += self.markov_chain.probs[state] / c
            if (pn > self.zero) and (pnarr > self.zero) and (pnarr / pn > self.zero):
                self.props.append(pnarr / pn)
            else:
                self.props.append(0)

    def find_sojourn_time_cdf(self, times):
        """
        Finds the sojourn time cdf
        times: a list of time points
        """
        self.S = aux.MM1PS_varying_lambda(
            mu=self.mu, lambda_ns=self.lambda_ns, infty=self.infty)
        self.sojourn_time_cdf = [max(self.zero, 1 - sum(
            [self.S.wn(t, n) * self.n_probs[n] for n in self.n_probs.keys()]
            )) for t in times]




class Method2:
    """
    This class derives the sojourn time cdf for a JSQ-PS, using an approximation
    for lambda(n) (so that no Markov chain needs to be solved)
    
    From [2] Gupta, Varun, et al. "Analysis of join-the-shortest-queue routing for
    web server farms." Performance Evaluation 64.9-12 (2007): 1062-1081.
    """
    def __init__(self, lambda_, mu, R, infty):
        """
        Parameters:
          mu: the service rate
          lambda_: the external arrival rate
          R: the number of parallel PS queues
        Hyperparameters:
          mc_limit: the truncation point of the Markov chain
          infty: the truncation point for summing to infinity
          zero: a sufficiently small number to act as zero, to
                avoid any numerical errors
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.R = R
        self.infty = infty
        self.M = aux.MMKJSQPS(self.mu, self.lambda_, self.R, self.infty)


    def find_sojourn_time_cdf(self, times):
        """
        Finds the sojourn time cdf
        times: a list of time points
        """
        self.sojourn_time_cdf = [1.0 - self.M.W(t) for t in times]
