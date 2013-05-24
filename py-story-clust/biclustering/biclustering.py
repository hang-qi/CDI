import sys
sys.path.append('..')
import bibench.algorithms.biclust as ba
import numpy as np
import bibench.bicluster as bb
import bibench.all as biall
from vocabulary import vocabulary


def do_biclustering(matrix):
    #result = ba.plaid(matrix, row_release=0.3, col_release=0.3, max_layers=5, verbose=True)  # Choose the efficient method based on the real data
    #result = ba.isa(matrix)
    #result = ba.spectral(matrix)
    #result = ba.bimax(matrix)
    #result = ba.fabia(matrix, data=2)
    #matrix = biall.qubic_binarize_up(matrix)
    print(matrix[0])
    #result = ba.spectral(matrix)
    result = ba.plaid(matrix, max_layers=50, verbose=True)
    result1 = bb.filter(result, max_overlap=0.3)
    return result1


def main():
    matrix = np.loadtxt('../cooccurrence/cooccur_mat_final.txt')
    #matrix = matrix/10
    biclust_result = do_biclustering(matrix)
    #print(biclust_result)
    bb.write_biclusters(biclust_result, "biclust_result.txt")
    # print the word
    np_voc = vocabulary.Vocabulary()
    vp_voc = vocabulary.Vocabulary()
    np_voc.load('../mat/np.voc')
    vp_voc.load('../mat/vp.voc')
    count = 0
    with open("biclust_result_word.txt", 'w') as outfile:
        for bicluster in biclust_result:
            sub_matrix = matrix[np.ix_(bicluster.rows, bicluster.cols)]
            sum_np = sub_matrix.sum(axis=1)
            sum_vp = sub_matrix.sum(axis=0)
            dist_np = sum_np / (sum_np.sum())
            dist_vp = sum_vp / (sum_vp.sum())
            top_nps = np.argsort(dist_np)
            top_vps = np.argsort(dist_vp)

            # reverse so that the index will be ordered in descendant order.
            top_nps = top_nps[::-1]
            top_vps = top_vps[::-1]

            #print('\n---BICLUSTER---')
            outfile.write('\n---BICLUSTER {0}---\n'.format(count))
            count += 1
            #print('Top 20 NPs:')
            outfile.write('Top 20 NPs:\n')
            for i in range(1, len(bicluster.rows)):
                r_idx = top_nps[i]
                wid = bicluster.rows[r_idx]
                #print('{0} \t {1}'.format(np_voc.get_word(wid), dist_np[r_idx]))
                outfile.write('{0} \t {1}'.format(np_voc.get_word(wid), dist_np[r_idx]))
                outfile.write('\n')

            #print('Top 20 VPs:')
            outfile.write('Top 20 VPs:\n')
            for i in range(1, len(bicluster.cols)):
                c_idx = top_vps[i]
                wid = bicluster.cols[c_idx]
                #print('{0} \t {1}'.format(vp_voc.get_word(wid), dist_vp[c_idx]))
                outfile.write('{0} \t {1}'.format(vp_voc.get_word(wid), dist_vp[c_idx]))
                outfile.write('\n')

            #nps = [np_voc.get_word(r) for r in bicluster.rows]
            #outfile.write(" ".join(nps))
            #outfile.write('\n')

            #vps = [vp_voc.get_word(c) for c in bicluster.cols]
            #outfile.write(" ".join(vps))
            #outfile.write('\n')
            #outfile.write('\n')
    return


if __name__ == '__main__':
    main()
