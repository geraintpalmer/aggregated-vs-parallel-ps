import itertools
import numpy as np
import tqdm

class MMkPS:
    """
    A class to hold the queueing network object
    """
    def __init__(self, L, m, k, limit=30):
        """
        Initialises the Network object
        """
        self.L = L
        self.m = m
        self.k = k
        self.State_Space = list(itertools.product(*[range(limit) for _ in range(self.k)]))
        self.lenmat = len(self.State_Space)
        self.write_transition_matrix()
        self.discretise_transition_matrix()

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
                if arriving_node == state1.index(min_custs):
                    return self.L
        return 0.0

    def write_transition_matrix(self):
        """
        Writes the transition matrix for the markov chain
        """
        transition_matrix = np.array([[self.find_transition_rates(s1, s2) for s2 in self.State_Space] for s1 in self.State_Space])
        row_sums = np.sum(transition_matrix, axis=1)
        self.time_step = 1 / np.max(row_sums)
        self.transition_matrix = transition_matrix - np.multiply(np.identity(self.lenmat), row_sums)

    def discretise_transition_matrix(self):
        """
        Disctetises the transition matrix
        """
        self.discrete_transition_matrix = self.transition_matrix*self.time_step + np.identity(self.lenmat)

    def solve(self):
        A = np.append(np.transpose(self.discrete_transition_matrix) - np.identity(self.lenmat), [[1 for _ in range(self.lenmat)]], axis=0)
        b = np.transpose(np.array([0 for _ in range(self.lenmat)] + [1]))
        sol = np.linalg.solve(np.transpose(A).dot(A), np.transpose(A).dot(b))
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
