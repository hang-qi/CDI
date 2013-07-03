# The whole SW Process
from algorithm import sw
from model import segment
from model.nodes import Node, Nodes
from preprocessing import readingfiles
from statistics.statistics import Statistics


def SW_Process():
    [all_nodes, true_segment, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob] = readingfiles.preprocessing('2008081519', 'model_segmenter.txt')
    node_number = all_nodes.node_num
    edges = []
    for i in range(0, node_number-1):
        j = i + 1
        edges.append([i, j])
    adj_graph = sw.AdjacencyGraph(node_number, edges)
    swclass = sw.SWCuts()
    stat = Statistics(all_nodes, class_num, np1_voc, vp_voc, np2_voc, np1_prob, vp_prob, np2_prob, class_prior_prob, transition_prob)
    swclass.sample(adj_graph, stat.calculate_Qe, stat.target_evaluation_func)
