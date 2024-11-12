import networkx as nx

from pyformlang.rsa import RecursiveAutomaton
from project.regex.adjacency_matrix_fa import AdjacencyMatrixFA, intersect_automata
from scipy.sparse import csc_matrix
from pyformlang.finite_automaton import Symbol, State
from project.regex.create_finite_automaton import graph_to_nfa
from project.rsm import rsm_to_nfa


def tensor_based_cfpq(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    rsm_matrix = AdjacencyMatrixFA(rsm_to_nfa(rsm))

    graph_matrix = AdjacencyMatrixFA(
        graph_to_nfa(nx.MultiDiGraph(graph), start_nodes, final_nodes)
    )

    while True:
        transitive_closure = intersect_automata(
            graph_matrix, rsm_matrix
        ).transitive_сlosure()
        delta: dict[Symbol, csc_matrix] = {}

        for i, j in zip(*transitive_closure.nonzero()):
            rsm_i = i % rsm_matrix.number_of_states
            rsm_j = j % rsm_matrix.number_of_states
            st1, st2 = rsm_matrix.id_state[rsm_i], rsm_matrix.id_state[rsm_j]

            if st1 in rsm_matrix.start_states and st2 in rsm_matrix.final_states:
                assert st1.value[0] == st2.value[0]
                nonterm = st1.value[0]
                graph_i, graph_j = (
                    i // rsm_matrix.number_of_states,
                    j // rsm_matrix.number_of_states,
                )
                if (
                    nonterm in graph_matrix.decomposition
                    and graph_matrix.decomposition[nonterm][graph_i, graph_j]
                ):
                    continue
                if nonterm not in delta:
                    delta[nonterm] = csc_matrix(
                        (graph_matrix.number_of_states, graph_matrix.number_of_states),
                        dtype=bool,
                    )
                delta[nonterm][graph_i, graph_j] = True

        if not delta:
            break

        for symbol in delta.keys():
            if symbol not in graph_matrix.decomposition:
                graph_matrix.decomposition[symbol] = delta[symbol]
            else:
                graph_matrix.decomposition[symbol] += delta[symbol]

    start_matrix = graph_matrix.decomposition.get(rsm.initial_label)

    if start_matrix is None:
        return set()

    return {
        (start, final)
        for start in start_nodes
        for final in final_nodes
        if start_matrix[
            graph_matrix.state_id[State(start)], graph_matrix.state_id[State(final)]
        ]
    }
