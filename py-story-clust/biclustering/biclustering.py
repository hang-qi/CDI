import bibench.algorithms.biclust as ba
import numpy as np
import bibench.bicluster as bb


def do_biclustering(matrix):
    #result = ba.plaid(matrix, row_release=0.3, col_release=0.3, max_layers=5, verbose=True)  # Choose the efficient method based on the real data
    result = ba.spectral(matrix)
    return result


def main():
    matrix = np.loadtxt('../cooccurrence/cooccur_mat_final.txt')
    matrix = matrix/1000
    print(matrix[0])
    biclust_result = do_biclustering(matrix)
    print(biclust_result)
    bb.write_biclusters(biclust_result, "biclust_result.txt")
    # print the word
    return


if __name__ == '__main__':
    main()
