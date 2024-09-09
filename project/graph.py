import cfpq_data as cfpq
from networkx.drawing import nx_pydot


# Getting a graph by name
def load_graph(name):
    graph_path = cfpq.download(name)
    graph = cfpq.graph_from_csv(graph_path)
    return graph


# Returning the number of nodes, edges, and listing labels by graph name
def graph_info(graph_name):
    graph = load_graph(graph_name)
    return (
        graph.number_of_nodes(),
        graph.number_of_edges(),
        cfpq.get_sorted_labels(graph),
    )


# Saving the graph to the specified file in DOT format
def save_graph(graph, path: str):
    graph_to_pydot = nx_pydot.to_pydot(graph)

    graph_to_pydot.write(path)


# Constructing and saving  a graph from two cycles by the number of nodes in the cycles and the names of labels
def create_labeled_two_cycles_graph(n: int, m: int, labels: tuple[str, str], path):
    graph = cfpq.labeled_two_cycles_graph(n, m, labels=labels)
    save_graph(graph, path)
