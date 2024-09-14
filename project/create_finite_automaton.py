from networkx import MultiDiGraph
import pyformlang.finite_automaton as fa


def regex_to_dfa(regex: str) -> fa.DeterministicFiniteAutomaton:
    nfa = regex.to_epsilon_nfa()
    dfa = nfa.to_deterministic()

    return dfa.minimize()
