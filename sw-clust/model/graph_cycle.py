import networkx as nx
import logging

class graph_edge(object):
    def __init__(self, i, j, value):
        self.cor_i = i
        self.cor_j = j
        self.edge_value = value
    def __repr__(self):
        return repr((self.cor_i, self.cor_j, self.edge_value))


def judge_cycle(edgelist):
    """Judge if more than one cycle exist in one graph constructed by the given edges"""
    if len(edgelist) == 1:
        return 0
    g = nx.Graph()
    g.add_edges_from(edgelist)
    sub_g = nx.connected_component_subgraphs(g)
    for sg in sub_g:
        num_nodes = len(sg.nodes())
        num_edges = len(sg.edges())
        dif = num_edges - num_nodes
        #logging.debug('Edges: {0}'.format(sg.edges()))
        #logging.debug('Dif: {0}'.format(dif))
        if  dif > num_nodes:
            return 1
    return 0