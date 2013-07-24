from nltk.corpus import wordnet as wn
import numpy
import logging


def calculate_word_similarity_using_wordnet(word1, word2):
    """Calculate the similarity between two words"""
    max_similarity = 0
    for w1 in wn.synsets(word1, pos=wn.NOUN):
        for w2 in wn.synsets(word2, pos=wn.NOUN):
            sim = w1.path_similarity(w2)
            if sim > max_similarity:
                max_similarity = sim
    return max_similarity


def word_set_similarity(words1, words2):
    """Calculate the similarity of one word set to the other"""
    similarity_between_words = numpy.empty((len(words1), len(words2)))
    for i, word1 in enumerate(words1):
        for j, word2 in enumerate(words2):
            sim = calculate_word_similarity_using_wordnet(word1, word2)
            similarity_between_words[i][j] = sim

    all_word_similarity_12 = numpy.amax(similarity_between_words, axis=1)
    all_word_similarity_21 = numpy.amax(similarity_between_words, axis=0)
    all_word_similarity_12_sort = sorted(all_word_similarity_12, key=float, reverse=True)
    all_word_similarity_21_sort = sorted(all_word_similarity_21, key=float, reverse=True)

    word_sim_num1 = int(len(words1)/2)
    word_sim_num2 = int(len(words2)/2)
    result1 = 0
    for i in range(0, word_sim_num1):
        result1 += all_word_similarity_12_sort[i]
    result1 /= word_sim_num1
    result2 = 0
    for j in range(0, word_sim_num2):
        result2 += all_word_similarity_21_sort[j]
    result2 /= word_sim_num2
    return (result1 + result2)/2
