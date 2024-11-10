import itertools
import numpy as np
from typing import Iterable
from pyformlang.finite_automaton import Symbol, State
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from scipy.sparse import csc_matrix, kron


class AdjacencyMatrixFA:
    def __init__(self, automaton: NondeterministicFiniteAutomaton = None):
        if automaton is None:
            self.number_of_states = 0
            self.state_id = dict()
            self.id_state = dict()
            self.start_states = set()
            self.start_states_id = dict()
            self.final_states = set()
            self.decomposition = dict()
            return

        self.number_of_states = len(automaton.states)
        self.state_id: dict[State, int] = {
            st: i for i, st in enumerate(automaton.states)
        }
        self.id_state: dict[int, State] = {i: st for st, i in self.state_id.items()}
        self.start_states: set[State] = automaton.start_states
        self.start_states_id: dict[State, int] = {
            st: i for i, st in enumerate(automaton.start_states)
        }
        self.final_states: set[State] = automaton.final_states
        self.decomposition: dict[Symbol, csc_matrix] = {}

        for state in self.state_id.keys():
            id = self.state_id[state]
            transitions: dict[Symbol, State | set[State]] = automaton.to_dict().get(
                state
            )
            if transitions is None:
                continue
            for symbol in transitions.keys():
                if symbol not in self.decomposition:
                    self.decomposition[symbol] = csc_matrix(
                        (self.number_of_states, self.number_of_states), dtype=bool
                    )
                if isinstance(transitions[symbol], Iterable):
                    for to_st in transitions[symbol]:
                        to_idx = self.state_id[to_st]
                        self.decomposition[symbol][id, to_idx] = True
                else:
                    to_st: State = transitions[symbol]
                    to_idx = self.state_id[to_st]
                    self.decomposition[symbol][id, to_idx] = True

    def accepts(self, word: Iterable[Symbol]) -> bool:
        states = set(self.start_states)

        for letter in word:
            if self.decomposition.get(letter) is None:
                return False

            for s1, s2 in itertools.product(states, self.state_id.keys()):
                if self.decomposition[letter][self.state_id[s1], self.state_id[s2]]:
                    states.add(s2)

        if states.intersection(self.final_states):
            return True

        return False

    def transitive_сlosure(self) -> np.ndarray:
        A = np.eye(self.number_of_states, dtype=bool)

        for dec in self.decomposition.values():
            A |= dec.toarray()

        transitive_сlosure = np.linalg.matrix_power(A, self.number_of_states).astype(
            bool
        )
        return transitive_сlosure

    def is_empty(self) -> bool:
        transitive_сlosure = self.transitive_сlosure()
        for start_state in self.start_states:
            for final_state in self.final_states:
                if transitive_сlosure[
                    self.state_id[start_state], self.state_id[final_state]
                ]:
                    return False

        return True


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    intersection_matrix = AdjacencyMatrixFA()

    intersection_matrix.number_of_states = (
        automaton1.number_of_states * automaton2.number_of_states
    )

    for s1 in automaton1.state_id.keys():
        for s2 in automaton2.state_id.keys():
            id1, id2 = automaton1.state_id[s1], automaton2.state_id[s2]
            intesection_id = id1 * automaton2.number_of_states + id2

            intersection_matrix.state_id[State((s1, s2))] = intesection_id
            if s1 in automaton1.start_states and s2 in automaton2.start_states:
                intersection_matrix.start_states.add(State((s1, s2)))
            if s1 in automaton1.final_states and s2 in automaton2.final_states:
                intersection_matrix.final_states.add(State((s1, s2)))

    intersection_matrix.decomposition = {
        key: kron(
            automaton1.decomposition[key],
            automaton2.decomposition[key],
            format="csr",
        )
        for key in automaton1.decomposition.keys()
        if key in automaton2.decomposition
    }

    return intersection_matrix
