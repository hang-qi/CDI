Generate similarity matrix
==========================

Before create similarity matrix, please make sure you have
preprocessed corpus ready in the sense:

* Each individual file is a document / story.
* In each file, words are stored separated by spaces.
* Preprocessing such as morphing and removing stopwords has been be performed.

Step 1. Calculate sub distribution matrix
---------------------------------

To avoid build the gigantic distribution matrix in memory, we first build 
multiple distribution matrices, each of which is calculated from a subset of
the entire corpus. Each of the matrix is of size `m * n`, where `m` = # of 
words in the subset, `n` is the # of words in full vocabulary.

_Note: If these matrices have been calculated already, you can skip this step._

First, please specify (a) the corpus to be used and (b) the output 
directory in the `main()` function of `gen_sub_distribution_mat.py`.

    corpus = '/dataset/08cleaned/2008-0[567]*.txt'  # corpus used to build the matrix
    output_dir = '../data/'   # directory to store the distribution matrices

Run the script to generate distribution matrices.

    $ python gen_sub_distribution_mat.py

After running the scripts, you will get a set of files in the `output_dir`:

* `corpus_vocabulary.voc`: a full vocabulary consists by the whole corpus
* `sub_matrix_{i}.npy` and `sub_matrix_{i}.voc`: a set of distribution matrices
 (unnormalized) and its corresponding vocabulary.

Step 2. Calculate the similarity matrix of interest
-------------------------------------------

This step uses the sub distribution matrices to calculate a similarity matrix 
on a particular vocabulary of interest.

First, you need to specify the following two values in the
 `main()` of `gen_similarity_mat.py`:

    distribution_matrix_dir = '../data/'    # the directory contain distribution matrices.
    vocabularies_of_interest = ['../mat/np.voc', '../mat/vp.voc']  # can give multiple vocabularies.

To run the script

    $ python gen_similarity_mat.py

After running this script, you will get the following result for _each of the 
vocabularies_ of interest:

* A similarity matrix and its corresponding vocabulary. They will be in the 
same directory of the input file, but named with suffix `_co_mat.npy` and `_co_mat.voc`.

View Similarity Matrix
======================
We also provided a tool to view the content of similarity matrix.

    $ python matrix_viewer.py ../mat/np_co_mat.npy  ../mat/np_co_mat.voc

You will be provided with options as follows.

    Please choose what to do:
    [1]: view matrix
    [2]: view words
    [3]: view similar words by word id
    [4]: view similar words by word
    [0]: quit
