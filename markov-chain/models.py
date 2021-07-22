import itertools
import numpy as np

class MM2PS:
    """
    A class to hold the queueing network object
    """

    def __init__(self, L, m, limit=30):
        """
        Initialises the Network object
        """
        self.L = L
        self.m = m
        self.State_Space = list(itertools.product(range(limit), range(limit)))
        self.write_transition_matrix()
        self.discretise_transition_matrix()

    def find_transition_rates(self, state1, state2):
        """
        Finds the transition rates for given state transition
        """
        delta = (state2[0] - state1[0], state2[1] - state1[1])
        if delta == (1, 0):
            # This is an arrival to the first node. Only arrive here if second node is as busy or busier than it
            if state1[1] >= state1[0]:
                return self.L
        if delta == (0, 1):
            # This is an arrival at the 2nd node. Only arrive here is first not is busier than it
            if state1[0] > state1[1]:
                return self.L
        if delta == (-1, 0):
            # This is an exit from the first node.
            return self.m
        if delta == (0, -1):
            # This is an exit from the 2nd node.
            return self.m
        return 0.0

    def write_transition_matrix(self):
        """
        Writes the transition matrix for the markov chain
        """
        self.transition_matrix = [[self.find_transition_rates(s1, s2) for s2 in self.State_Space] for s1 in self.State_Space]
        for i in range(len(self.transition_matrix)):
            a = sum(self.transition_matrix[i])
            self.transition_matrix[i][i] = -a
            self.transition_matrix = np.array(self.transition_matrix)

    def discretise_transition_matrix(self):
        """
        Disctetises the transition matrix
        """
        self.time_step = 1 / max([abs(self.transition_matrix[i][i]) for i in range(len(self.transition_matrix))])
        self.discrete_transition_matrix = self.transition_matrix*self.time_step + np.identity(len(self.transition_matrix))

    def solve(self):
        lenmat = len(self.State_Space)
        A=np.append(np.transpose(self.discrete_transition_matrix)-np.identity(lenmat),[[1 for _ in range(lenmat)]], axis=0)
        b=np.transpose(np.array([0 for _ in range(lenmat)]+[1]))
        sol = np.linalg.solve(np.transpose(A).dot(A), np.transpose(A).dot(b))
        self.probs =  {self.State_Space[i]: sol[i] for i in range(lenmat)}

    def aggregate_states(self):
        agg_probs = {}
        for state in self.probs.keys():
            agg_state = sum(state)
            if agg_state in agg_probs:
                agg_probs[agg_state] += self.probs[state]
            else:
                agg_probs[agg_state] = self.probs[state]
        self.aggregate_probs = agg_probs
