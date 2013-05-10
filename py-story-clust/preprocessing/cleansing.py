from nltk.corpus import wordnet as wn


def remove_stopwords(words):
    """Return a list of words with stopwords removed."""
    # TODO: to be implemented.
    return


def morphy(word):
    """Return the shortest morph of the given word."""
    result_set = []
    result_set.insert(0, wn.morphy(word, wn.NOUN))
    result_set.append(wn.morphy(word, wn.VERB))
    result_set.append(wn.morphy(word, wn.ADJ))
    result_set.append(wn.morphy(word, wn.ADV))

    result = None

    for word in result_set:
        if word is not None:
            if result is None:
                result = word
            else:
                if len(result) > len(word):
                    result = word
    return result


def main():
    word = 'denied'
    word_morphied = morphy(word)
    print('The original word is ', word,
          ' and the morphied word is ', word_morphied)


if __name__ == '__main__':
    main()
