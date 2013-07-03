# Defines the nodes in the graph


class Node(object):
    def __init__(self):
        self.NP1 = []
        self.VP = []
        self.NP2 = []
        self.pronoun = False

    def set_node(self, np1, vp, np2, ispronounflag):
        self.NP1 = np1
        self.VP = vp
        self.NP2 = np2
        self.pronoun = ispronounflag


class Nodes(object):
    def __init__(self):
        self.node_num = 0
        self.nodes = []

    def add_node(self, newnode):
        self.nodes.append(newnode)
        self.node_num += 1
