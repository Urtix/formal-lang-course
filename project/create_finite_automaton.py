from networkx import MultiDiGraph
import pyformlang.finite_automaton as fa
from pyformlang.regular_expression import Regex


def regex_to_dfa(regex: str) -> fa.DeterministicFiniteAutomaton:
    nfa = Regex(regex).to_epsilon_nfa()
    dfa = nfa.to_deterministic()

    return dfa.minimize()


def graph_to_nfa(
    graph: MultiDiGraph, start_states: set[int], final_states: set[int]
) -> fa.NondeterministicFiniteAutomaton:
    enfa = fa.NondeterministicFiniteAutomaton.from_networkx(graph)
    nfa = enfa.remove_epsilon_transitions()

    if not start_states:
        start_states = set(int(n) for n in graph.nodes)

    if not final_states:
        final_states = set(int(n) for n in graph.nodes)

    for s in start_states:
        nfa.add_start_state(s)

    for f in final_states:
        nfa.add_final_state(f)

    return nfa
