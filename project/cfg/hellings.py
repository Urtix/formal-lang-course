import networkx as nx

from pyformlang.cfg import CFG, Terminal

from project.cfg.wcnf import cfg_to_weak_normal_form


def hellings_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    wcnf = cfg_to_weak_normal_form(cfg)

    trip_set = set(
        (v, p, v) for v in set(graph.nodes) for p in cfg.get_nullable_symbols()
    )

    for u, v, label in graph.edges(data="label"):
        if label is None:
            continue
        for production in wcnf.productions:
            if (
                len(production.body) == 1
                and isinstance(production.body[0], Terminal)
                and production.body[0].value == label
            ):
                trip_set.add((u, production.head, v))

    not_end = True
    while not_end:
        not_end = False
        trip = set()

        for u1, p1, v1 in trip_set:
            for u2, p2, v2 in trip_set:
                if v1 == u2:
                    for production in wcnf.productions:
                        if (
                            len(production.body) == 2
                            and production.body[0] == p1
                            and production.body[1] == p2
                        ):
                            new_trip = (u1, production.head, v2)
                            if new_trip not in trip_set:
                                trip.add(new_trip)
                                not_end = True

        trip_set.update(trip)

    return set(
        (u, v)
        for u, p, v in trip_set
        if (
            p == wcnf.start_symbol
            and (not start_nodes or u in start_nodes)
            and (not final_nodes or v in final_nodes)
        )
    )
