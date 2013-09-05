import networkx as nx

class graph_edge(object):
    def __init__(self, i, j, value):
        self.cor_i = i
        self.cor_j = j
        self.edge_value = value
    def __repr__(self):
        return repr((self.cor_i, self.cor_j, self.edge_value))


def judge_if_exist_cycle(edgelist):
    """Judge if cycle exist in one graph constructed by the given edges"""
    if len(edgelist) == 1:
        return 0
    g = nx.Graph()
    g.add_edges_from(edgelist)
    sub_g = nx.connected_component_subgraphs(g)
    for sg in sub_g:
        if len(sg.edges()) >= len(sg.nodes()):
            return 1
    return 0