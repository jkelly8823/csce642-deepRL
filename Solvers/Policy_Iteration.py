# Licensing Information:  You are free to use or extend this codebase for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide the following
# attribution:
# This CSCE-689 RL assignment codebase was developed at Texas A&M University.
# The core code base was developed by Guni Sharon (guni@tamu.edu).

import numpy as np
from Solvers.Abstract_Solver import AbstractSolver, Statistics


class PolicyIteration(AbstractSolver):

    def __init__(self, env, eval_env, options):
        assert str(env.observation_space).startswith( 'Discrete' ), str(self) + \
                                                                    " cannot handle non-discrete state spaces"
        assert str(env.action_space).startswith('Discrete'), str(self) + " cannot handle non-discrete action spaces"
        super().__init__(env, eval_env, options)
        self.V = np.zeros(env.observation_space.n)
        # Start with a random policy
        self.policy = np.ones([env.observation_space.n, env.action_space.n]) / env.action_space.n

    def train_episode(self):
        """
            Run a single Policy iteration. Evaluate and improves the policy.

            Use:
                self.policy: [S, A] shaped matrix representing the policy.
                self.env: OpenAI environment.
                    env.P represents the transition probabilities of the environment.
                    env.P[s][a] is a list of transition tuples (prob, next_state, reward, done).
                    env.nS is a number of states in the environment.
                    env.nA is a number of actions in the environment.
                self.options.gamma: Gamma discount factor.
                np.eye(self.env.action_space.n)[action]
        """

        # Evaluate the current policy
        self.policy_eval()

        # For each state...
        for s in range(self.env.observation_space.n):
            # Find the best action by one-step lookahead
            # Ties are resolved by returning the first action with maximum value (Hint: use max/argmax directly).

            ################################
            #   YOUR IMPLEMENTATION HERE   #
            ################################
            oldA = self.policy[s]

            lah = self.one_step_lookahead(s)
            a = np.argmax(lah)

            self.policy[s] = a


            # p = self.env.P[s][a]



            # sums = 0
            # for st in p:
            #     sums += st[0] * (st[2] + self.options.gamma * self.V[st[1]])
            #
            # self.policy[s] = sums

        # In DP methods we don't interact with the environment so we will set the reward to be the sum of state values
        # and the number of steps to -1 representing an invalid value
        self.statistics[Statistics.Rewards.value] = np.sum(self.V)
        self.statistics[Statistics.Steps.value] = -1

    def __str__(self):
        return "Policy Iteration"

    def one_step_lookahead(self, state):
        """
        Helper function to calculate the value for all action in a given state.

        Args:
            state: The state to consider (int)
            V: The value to use as an estimator, Vector of length env.nS

        Returns:
            A vector of length env.nA containing the expected value of each action.
        """
        A = np.zeros(self.env.action_space.n)
        for a in range(self.env.action_space.n):
            for prob, next_state, reward, done in self.env.P[state][a]:
                A[a] += prob * (reward + self.options.gamma * self.V[next_state])
        return A

    def policy_eval(self):
        """
        Evaluate a policy given an environment and a full description of the environment's dynamics.
        Use a linear system solver sallied by numpy (np.linalg.solve)

        Use:
            self.policy: [S, A] shaped matrix representing the policy.
            self.env: OpenAI env. env.P represents the transition probabilities of the environment.
                env.P[s][a] is a list of transition tuples (prob, next_state, reward, done).
                env.nS is a number of states in the environment.
                env.nA is a number of actions in the environment.
            self.options.gamma: Gamma discount factor.
            np.linalg.solve(a, b) # Won't work with discount factor = 0!
        """
        ################################
        #   YOUR IMPLEMENTATION HERE   #
        ################################

        coeff = []
        outs = []

        for s in range(self.env.observation_space.n):
            a = np.argmax(self.policy[s])

            p = self.env.P[s][a]

            cfs = np.zeros(self.env.observation_space.n)
            eq = 0
            # print('HERE WITH', s)
            for prob, next_state, reward, done in self.env.P[s][a]:
                # print(prob, next_state, reward, done)
                cfs[next_state] = prob * self.options.gamma
                eq -= prob * reward

            cfs[s] -= 1
            # p1 (r1 + g s1)
            # p1r1 + p1g s1
            coeff.append(cfs)
            outs.append(eq)

        sol = np.linalg.solve(coeff, outs)

        # print(coeff, '\n\n', outs, '\n\n', sol)
        # print('VERIFY:', np.allclose(np.dot(coeff, sol), outs))

        for s in range(self.env.observation_space.n):
            self.V[s] = sol[s]


        # for s in range(self.env.observation_space.n):
        #     v = self.V[s]
        #
        #     a = np.argmax(self.policy[s])
        #
        #     p = self.env.P[s][a]
        #
        #     sums = 0
        #     for st in p:
        #         sums += st[0] * (st[2] + self.options.gamma * self.V[st[1]])
        #
        #     self.V[s] = sums

    def create_greedy_policy(self):
        """
        Return the currently known policy.


        Returns:
            A function that takes an observation as input and greedy action as integer
        """
        def policy_fn(state):
            return np.argmax(self.policy[state])

        return policy_fn
