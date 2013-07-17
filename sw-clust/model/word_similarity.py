from nltk.corpus import wordnet as wn


def calculate_word_similarity_using_wordnet(word1, word2):
    """Calculate the similarity between two words"""
    max_similarity = 0
    for w1 in wn.synsets(word1):
        for w2 in wn.synsets(word2):
            sim = w1.path_similarity(w2)
            if sim > max_similarity:
                max_similarity = sim
    return max_similarity


def calculate_words_similarity(words1, words2):
    """Calculate the similarity of one word set to the other"""
    all_word_similarity = []
    for word1 in words1:
        sim_max = 0
        for word2 in words2:
            sim = calculate_word_similarity_using_wordnet(word1, word2)
            if sim > sim_max:
                sim_max = sim
        all_word_similarity.append(sim_max)
    all_word_similarity_sorted = sorted(all_word_similarity, key=float, reverse=True)
    word_sim_num = int(len(words1)/2)
    result = 0
    for i in range(0, word_sim_num):
        result += all_word_similarity_sorted[i]
    result /= word_sim_num
    return result


def word_set_similarity(word_set1, word_set2):
    """Give the similarity score between two word sets"""
    similarity12 = calculate_words_similarity(word_set1, word_set2)
    similarity21 = calculate_words_similarity(word_set2, word_set1)
    return (similarity12 + similarity21)/2
