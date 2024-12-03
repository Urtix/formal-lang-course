from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Set, Tuple
from pyformlang.finite_automaton import Symbol, DeterministicFiniteAutomaton
from pyformlang import rsa
import networkx as nx


def gll_based_cfpq(
    rsm: rsa.RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: Set[int] | None = None,
    final_nodes: Set[int] | None = None,
) -> Set[Tuple[int, int]]:
    if (start_nodes is None) or (start_nodes == set()):
        start_nodes = set(graph.nodes())
    if (final_nodes is None) or (final_nodes == set()):
        final_nodes = set(graph.nodes())

    gll_solver = Solver(rsm, graph)

    reach = set()
    for start_node in start_nodes:
        gll_node = gll_solver.stack.get_node(gll_solver.start_rsmstate, start_node)
        gll_node.add_reference(RsmState(Symbol("$"), "fin"), gll_solver.accept_node)
        gll_solver.add_snode(
            set([SNode(gll_node, gll_solver.start_rsmstate, start_node)])
        )

    while gll_solver.unprocessed != set():
        reach.update(gll_solver.step(gll_solver.unprocessed.pop()))

    return {(start_final) for start_final in reach if start_final[1] in final_nodes}


class Node:
    state: RsmState
    node: int
    references: Dict[RsmState, Set[Node]]
    pop_set: Set[int]

    def __init__(self, rsmstate: RsmState, node: int):
        self.state = rsmstate
        self.node = node
        self.references = {}
        self.pop_set = set()

    def pop(self, cur_node: int) -> Set[SNode]:
        res_set = set()

        if cur_node not in self.pop_set:
            for new_state in self.references:
                gses = self.references[new_state]
                for gs in gses:
                    res_set.add(SNode(gs, new_state, cur_node))
            self.pop_set.add(cur_node)

        return res_set

    def add_reference(self, rsmstate: RsmState, node: Node) -> Set[SNode]:
        res_set = set()

        state_edges = self.references.get(rsmstate, set())
        if node not in state_edges:
            state_edges.add(node)
            for cur_node in self.pop_set:
                res_set.add(SNode(node, rsmstate, cur_node))

        self.references[rsmstate] = state_edges

        return res_set


@dataclass(frozen=True)
class RsmState:
    var: Symbol
    sub_state: str


@dataclass
class RsmStateData:
    symbol_rsmstate: Dict[Symbol, RsmState]
    symbol_edges: Dict[Symbol, Tuple[RsmState, RsmState]]
    final: bool


@dataclass(frozen=True)
class SNode:
    gnode: Node
    state: RsmState
    node: int


class Stack:
    body: Dict[Tuple[RsmState, int], Node]

    def __init__(self):
        self.body = {}

    def get_node(self, rsmstate: RsmState, node: int):
        return self.body.setdefault((rsmstate, node), Node(rsmstate, node))


def filter_pop_nodes(
    accept_node: Node, snodes: Set[SNode], prev_snode: SNode
) -> Tuple[Set[SNode], Set[Tuple[int, int]]]:
    node_res_set = set()
    start_final_set = set()

    for snode in snodes:
        if snode.gnode == accept_node:
            start_node = prev_snode.gnode.node
            final_node = snode.node
            start_final_set.add((start_node, final_node))
        else:
            node_res_set.add(snode)

    return (node_res_set, start_final_set)


class Solver:
    def __init__(
        self,
        rsm: rsa.RecursiveAutomaton,
        graph: nx.DiGraph,
    ):
        self.nodes2ref: Dict[int, Dict[Symbol, Set[int]]] = {}
        self.rsmstate2data: Dict[Symbol, Dict[str, RsmStateData]] = {}
        self.start_rsmstate: RsmState

        for node in graph.nodes():
            self.nodes2ref[node] = {}

        for from_node, to_node, symbol in graph.edges(data="label"):
            if symbol is not None:
                edges = self.nodes2ref[from_node]
                s: Set = edges.get(symbol, set())
                s.add(to_node)
                edges[symbol] = s

        for var in rsm.boxes:
            self.rsmstate2data[var] = {}

        for var in rsm.boxes:
            dfa: DeterministicFiniteAutomaton = rsm.boxes[var].dfa
            graph_dfa = dfa.to_networkx()

            for sub_state in graph_dfa.nodes:
                self.rsmstate2data[var][sub_state] = RsmStateData(
                    {}, {}, sub_state in dfa.final_states
                )

            edges = graph_dfa.edges(data="label")
            for from_st, to_st, symbol in edges:
                if symbol is not None:
                    st_edges = self.rsmstate2data[var][from_st]
                    if Symbol(symbol) not in self.rsmstate2data:
                        st_edges.symbol_rsmstate[symbol] = RsmState(var, to_st)
                    else:
                        bfa: DeterministicFiniteAutomaton = rsm.boxes[
                            Symbol(symbol)
                        ].dfa
                        box_start = bfa.start_state.value
                        st_edges.symbol_edges[symbol] = (
                            RsmState(Symbol(symbol), box_start),
                            RsmState(var, to_st),
                        )

        start_dfa: DeterministicFiniteAutomaton = rsm.boxes[rsm.initial_label].dfa
        self.start_rsmstate = RsmState(rsm.initial_label, start_dfa.start_state.value)
        self.stack = Stack()
        self.accept_node = self.stack.get_node(RsmState(Symbol("$"), "fin"), -1)
        self.unprocessed: Set[SNode] = set()
        self.added: Set[SNode] = set()

    def add_snode(self, snodes: Set[SNode]):
        snodes.difference_update(self.added)
        self.added.update(snodes)
        self.unprocessed.update(snodes)

    def step(self, snode: SNode) -> Set[Tuple[int, int]]:
        rsmstate = snode.state
        rsm_data = self.rsmstate2data[rsmstate.var][rsmstate.sub_state]

        def pop_step() -> Set[Tuple[int, int]]:
            snode_set = snode.gnode.pop(snode.node)
            snode_set, start_fin_set = filter_pop_nodes(
                self.accept_node, snode_set, snode
            )
            self.add_snode(snode_set)
            return start_fin_set

        for term in rsm_data.symbol_rsmstate:
            if term in self.nodes2ref[snode.node]:
                snode_set = set()
                rsm_new_st = rsm_data.symbol_rsmstate[term]
                graph_new_nodes = self.nodes2ref[snode.node][term]
                for gn in graph_new_nodes:
                    snode_set.add(SNode(snode.gnode, rsm_new_st, gn))

                    self.add_snode(snode_set)

        result = set()
        for var in rsm_data.symbol_edges:
            node = self.stack.get_node(rsm_data.symbol_edges[var][0], snode.node)
            pop_nodes = node.add_reference(rsm_data.symbol_edges[var][1], snode.gnode)

            pop_nodes, sub_start_fin_set = filter_pop_nodes(
                self.accept_node, pop_nodes, snode
            )

            self.add_snode(pop_nodes)
            self.add_snode(
                set([SNode(node, rsm_data.symbol_edges[var][0], snode.node)])
            )

            result.update(sub_start_fin_set)

        if rsm_data.final:
            result.update(pop_step())

        return result
