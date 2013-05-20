import sys
sys.path.append('..')
import bibench.algorithms.biclust as ba
import numpy as np
import bibench.bicluster as bb
from vocabulary import vocabulary


def do_biclustering(matrix):
    #result = ba.plaid(matrix, row_release=0.3, col_release=0.3, max_layers=5, verbose=True)  # Choose the efficient method based on the real data
    result = ba.spectral(matrix)
    return result


def main():
    matrix = np.loadtxt('../cooccurrence/cooccur_mat.txt')
    matrix = matrix
    print(matrix[0])
    biclust_result = do_biclustering(matrix)
    print(biclust_result)
    bb.write_biclusters(biclust_result, "biclust_result.txt")
    # print the word
    np_voc = vocabulary.Vocabulary()
    vp_voc = vocabulary.Vocabulary()
    np_voc.load('../mat/np.voc')
    vp_voc.load('../mat/vp.voc')
    with open("biclust_result_word.txt", 'w') as outfile:
        for bicluster in biclust_result:
            nps = [np_voc.get_word(r) for r in bicluster.rows]
            outfile.write(" ".join(nps))
            outfile.write('\n')

            vps = [vp_voc.get_word(c) for c in bicluster.cols]
            outfile.write(" ".join(vps))
            outfile.write('\n')
            outfile.write('\n')
    return


if __name__ == '__main__':
    main()
