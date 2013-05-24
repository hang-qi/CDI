Generate similarity matrix
==========================

Before create similarity matrix, please make sure you have
preprocessed corpus ready in the sense:

* Each individual file is a document / story.
* In each file, words are stored separated by spaces.
* Preprocessing such as morphing and removing stopwords shall be performed.

Calculate sub distribution matrix
---------------------------------

First use `gen_sub_distribution_mat.py` to calculate distribution matrix for each
document in the corpus.

    python gen_sub_distribution_mat.py

Please specify the location of corpus and the pattern for the subset you want to
use in the `main` function.

    story_files = glob.glob('/dataset/08cleaned/2008-0[567]*.txt')

After running this scripts, you will get a set of results:

* A full vocabulary consists by the whole corpus.
* A set of distribution matrices (unnormalized) and its corresponding vocabulary.
Each matrix is of dimension `m*n` where `m` = # of words in the subset, `n` is the # 
of words in full vocabulary. 

Calculate the similarity matrix of interest
-------------------------------------------

This step uses the sub distribution matrices to calculate a similarity matrix 
on a particular vocabulary of interest.

    python gen_cooccur_mat.py

After running this script, you will get the following result:

* A similarity matrix and vocabulary for NP.
* A similarity matrix and vocabulary for VP.
* A vocabulary of words that we do not have distribution information, for NP and VP respectively.

View Similarity Matrix
======================
We also provided a tool to view the content of similarity matrix.

    python matrix_viewer.py ../mat/np_mat.npy  ../mat/np.voc

Running this tool, you will be provided options as follows.

    Please choose what to do:
    [1]: view matrix
    [2]: view words
    [3]: view similar words by word id
    [4]: view similar words by word
    [0]: quit
