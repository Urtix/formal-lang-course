import networkx as nx

from pyformlang.cfg import CFG, Terminal
from project.cfg.wcnf import cfg_to_weak_normal_form
from collections import defaultdict
from scipy.sparse import lil_matrix


def matrix_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    wcnf = cfg_to_weak_normal_form(cfg)
    eps_prods = set()
    term_prods = defaultdict(set)
    non_term_prods = defaultdict(set)

    for production in wcnf.productions:
        if len(production.body) == 0:
            eps_prods.add(production.head)
        elif len(production.body) == 1:
            term_prods[production.head].add(production.body[0])
        else:
            non_term_prods[production.head].add(
                (production.body[0], production.body[1])
            )
    nodes = list(graph.nodes)
    indexes_nodes = {node: i for i, node in enumerate(nodes)}
    numer_of_nodes = graph.number_of_nodes()

    matrices = {
        var: lil_matrix((numer_of_nodes, numer_of_nodes), dtype=bool)
        for var in wcnf.variables
    }

    for i in range(numer_of_nodes):
        for var in eps_prods:
            matrices[var][i, i] = True

    for u, v, label in graph.edges(data="label"):
        i, j = indexes_nodes[u], indexes_nodes[v]
        for var, vars in term_prods.items():
            matrices[var][i, j] |= Terminal(label) in vars

    while True:
        old_nnz = sum([v.nnz for v in matrices.values()])
        for head, body in non_term_prods.items():
            for vars in body:
                matrices[head] += matrices[vars[0]] @ matrices[vars[1]]
        if old_nnz == sum([v.nnz for v in matrices.values()]):
            break

    result_pairs = set()
    nodes_indexes: dict[int, any] = {idx: node for node, idx in indexes_nodes.items()}
    if wcnf.start_symbol in matrices:
        final_matrix = matrices[wcnf.start_symbol].tocoo()
        for u_idx, v_idx in zip(final_matrix.row, final_matrix.col):
            u = nodes_indexes[u_idx]
            v = nodes_indexes[v_idx]
            if (not start_nodes or u in start_nodes) and (
                not final_nodes or v in final_nodes
            ):
                result_pairs.add((u, v))

    return result_pairs
