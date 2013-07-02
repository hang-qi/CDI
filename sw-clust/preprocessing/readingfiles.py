# Defines the method to read in the test file for Story Segmentation
import glob
import sys
sys.path.append('..')

import func
import cleansing
from model import segment
from model.nodes import Node, Nodes



def read_test_file(filenameprefix):
    file_name = 'triplet_files/' + filenameprefix + '*.txt'
    files.sort()
    true_segment = segment.Segment()
    all_nodes = Nodes()
    line_count = 0
    for segments_file in files:
        with open(segments_file, 'r') as f:
            for line in f:
            	if(line[0] != '<'):
            		line_count += 1
            		line = (line[:-2]).lower()
            		triplets = line.split('|')
            		np1 = triplets[0].split()
            		if func.ispronoun(np1[0]):
            			pronoun_flag = True
            		else:
            			pronoun_flag = False
            		np1 = cleansing.clean(triplets[0].split())
            		vp = cleansing.clean(triplets[1].split())
            		np2 = cleansing.clean(triplets[2].split())
            		current_node = Node()
            		current_node.set_node(np1, vp, np2, pronoun_flag)
            		all_nodes.add_node(current_node)
        true_segment.add_boundary(line_count - 1)
    return [all_nodes, true_segment]


def read_training_classification_data(file_in):
    
    return


def read_training_clusters(file_in):
    return

