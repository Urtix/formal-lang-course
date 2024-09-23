import pytest

from project.graph import load_graph, load_graph_from_dot
from project.create_finite_automaton import regex_to_dfa, graph_to_nfa


class TestFA:
    # Checking the regex_to_dfa function using a regular expression
    def test_regex_to_dfa(self):
        dfa = regex_to_dfa("a*b|c|d")

        assert dfa.accepts("ab")
        assert dfa.accepts("aab")
        assert dfa.accepts("b")
        assert dfa.accepts("c")
        assert dfa.accepts("d")
        assert not dfa.accepts("a")
        assert dfa.is_deterministic()
        assert dfa.is_equivalent_to(dfa.minimize())

    # Checking the graph_to_nfa function using the generated graph saved in DOT format
    def test_generated_graph_to_nfa(self):
        graph = load_graph_from_dot("tests/test_graph_file.dot")
        nfa = graph_to_nfa(graph, (), ())

        assert nfa.start_states == nfa.final_states == nfa.states
        assert (
            len(nfa.start_states)
            == len(nfa.final_states)
            == len(nfa.states)
            == len(graph.nodes)
            == 21
        )

    # Checking the regex_to_dfa function using a graph loaded by name
    @pytest.mark.parametrize(
        "graph_name, start_states, final_states",
        [
            pytest.param("skos", {1}, {2}, id="skos_with_start_and_final"),
            pytest.param("skos", (), (), id="skos"),
            pytest.param("wc", {1}, {2}, id="wc_with_start_and_final"),
            pytest.param("wc", (), (), id="wc"),
        ],
    )
    def test_loaded_graph_to_nfa(
        self, graph_name: str, start_states: set[int], final_states: set[int]
    ):
        graph = load_graph(graph_name)
        nfa = graph_to_nfa(graph, start_states, final_states)

        if len(start_states) == len(final_states) == 0:
            assert nfa.start_states == nfa.final_states == nfa.states
        else:
            assert len(nfa.start_states) == len(start_states)
            assert len(nfa.final_states) == len(final_states)
            assert len(set(int(state.value) for state in nfa.states)) == len(
                graph.nodes
            )
