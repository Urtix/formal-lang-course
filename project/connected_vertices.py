import networkx as nx

from adjacency_matrix_fa import AdjacencyMatrixFA, intersect_automata
from create_finite_automaton import regex_to_dfa, graph_to_nfa


def tensor_based_rpq(
    regex: str,
    graph: nx.MultiDiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    regex_to_matrix = AdjacencyMatrixFA(regex_to_dfa(regex))
    graph_to_matrix = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))
    intersection = intersect_automata(regex_to_matrix, graph_to_matrix)
    closure = intersection.transitive_сlosure()

    return {
        (graph_start, graph_final)
        for graph_start in graph_to_matrix.start_states
        for graph_final in graph_to_matrix.final_states
        if any(
            closure[
                intersection.states[(regex_start, graph_start)],
                intersection.states[(regex_final, graph_final)],
            ]
            for regex_start in regex_to_matrix.start_states
            for regex_final in regex_to_matrix.final_states
        )
    }
