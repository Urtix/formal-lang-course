import os
from pathlib import Path

from project.regex.graph import graph_info, create_labeled_two_cycles_graph


class TestGraph:
    def test_graph_info(self):
        # Test of the graph_info function on the built-in file "skos"
        graph_info_skos = (
            144,
            252,
            [
                "type",
                "definition",
                "isDefinedBy",
                "label",
                "subPropertyOf",
                "comment",
                "scopeNote",
                "inverseOf",
                "range",
                "domain",
                "contributor",
                "disjointWith",
                "creator",
                "example",
                "first",
                "rest",
                "description",
                "seeAlso",
                "subClassOf",
                "title",
                "unionOf",
            ],
        )
        assert graph_info("skos") == graph_info_skos

        # Test of the graph_info function on the built-in file "wc"
        graph_info_wc = (
            332,
            269,
            ["d", "a"],
        )
        assert graph_info("wc") == graph_info_wc

    # Checking the create_labeled_two_cycles_graph function using a graph saved in DOT format (test_graph_file.dot)
    def test_create_labeled_two_cycles_graph(self):
        path_test_graph: str = "test_graph.dot"
        create_labeled_two_cycles_graph(10, 10, ("6", "9"), path_test_graph)
        assert (
            open(path_test_graph, "r").read()
            == open(Path("tests/test_graph_file.dot"), "r").read()
        )
        os.remove(path_test_graph)
