# This module provides definitions and operations of the topic And-Or Tree.


class OrNode(object):
    """Or Node in the tree"""
    def __init__(self):
        #super(AndOrTree, self).__init__()
        self.root = OrNode()
        self.children = []

    def add_child(self, node):
        self.children.append(node)


class TopicNode(object):
    """Terminal node in the topic And-Or Tree."""
    def __init__(self):
        self.is_generic = False
        self.NP1 = []
        self.VP = []
        self.NP2 = []
        self.matrix = []

    def synthesis_topic(self):
        return 'synthesized topic'


class AndOrTree(object):
    """AndOrTree"""
    def __init__(self):
        #super(AndOrTree, self).__init__()
        self.root = OrNode()

    def get_score(self):
        return 0

    def print_hierarchy(self):
        return 0
