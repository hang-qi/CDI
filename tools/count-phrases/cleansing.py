
import re
from nltk.corpus import wordnet as wn


def clean(words):
    if words is None:
        return None
    words = [w.lower() for w in words]
    words = [__morphy(w) for w in words]
    cleaned_words = __remove_stopwords(words)
    #if len(cleaned_words) > 0:
    #    cleaned_words = [morphy(w) for w in cleaned_words]
    return cleaned_words


def __remove_stopwords(words):
    """Return a list of words with stopwords removed."""
    stopwords_file = open('stopwords.txt', 'r')
    data = stopwords_file.read()
    stopwords = set(data.split(', '))
    stopwords.add('')

    filtered_words = []
    for i in range(0, len(words)):
        filtered_words.append(__filter(words[i]))

    filtered_words = [w for w in filtered_words if not w in stopwords]
    return filtered_words


def __filter(word):
    """Filter punctuations out of word."""
    filtered_word = word.replace('--', '').replace('\'s', '')

    chars = [',', '.', '!', ';', '?', ':', '/', '\\', ' ', '\"', '#', '$', '%',
             '&', '\'', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
             '\n', '\r']
    filtered_word = re.sub('[%s]' % ''.join(chars), '', filtered_word)
    filtered_word = filtered_word.strip('-')
    return filtered_word


def __morphy(word):
    """Return the shortest morph of the given word."""
    result_set = []
    result_set.insert(0, wn.morphy(word, wn.NOUN))
    result_set.append(wn.morphy(word, wn.VERB))
    result_set.append(wn.morphy(word, wn.ADJ))
    result_set.append(wn.morphy(word, wn.ADV))
    result = None
    for r in result_set:
        if r is not None:
            if result is None:
                result = r
            else:
                if len(result) > len(r):
                    result = r
    if result is None:
        return word
    return result


def main():
    word = 'denied'
    word_morphied = __morphy(word)
    print('The original word is ', word,
          ' and the morphied word is ', word_morphied)
    words = ['a', 'news', 'turn', 'walk', 'talk']
    words_rm_stopwords = __remove_stopwords(words)
    print('Words: ', words, ' and the words after removing the stopwords: ', words_rm_stopwords)


if __name__ == '__main__':
    main()
