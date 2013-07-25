# Vocabulary

import codecs


class Vocabulary(object):
    """A Vocabulary contains a word list and a dictionary."""
    def __init__(self):
        super(Vocabulary, self).__init__()
        self.word_list = []     # maps id -> word
        self.dict = dict()      # maps word -> id

    def __contains__(self, word):
        return word in self.dict

    def __len__(self):
        return len(self.word_list)

    def __getitem__(self, index):
        return self.word_list[index]

    def build_by_list(self, word_list):
        super(Vocabulary, self).__init__()
        self.word_list = []     # maps id -> word
        self.dict = dict()      # maps word -> id
        for w in word_list:
            self.add(w)

    def add(self, word):
        """Add a word to vocabulary.
        Word contained in the vocabulary will not be inserted again."""
        if not self.contain(word):
            self.word_list.append(word)
            self.dict[word] = len(self.word_list) - 1

    def contain(self, word):
        """Return True is word is in the vocabulary."""
        return self.__contains__(word)

    def size(self):
        return self.__len__()

    def get_word_index(self, word):
        """Return the word index in the vocabulary. Return -1 if no found."""
        if self.contain(word):
            return self.dict[word]
        else:
            raise ValueError('Cannot find the word: {0}'.format(word))

    def get_word(self, index):
        return self.__getitem__(index)

    def save(self, filename):
        with codecs.open(filename, "w", encoding='ISO-8859-1') as f:
            for val in self.word_list:
                f.writelines(val + '\n')
        return

    def load(self, filename):
        self.dict = {}
        self.word_list = []
        with codecs.open(filename, "r", encoding='ISO-8859-1') as f:
            for line in f:
                word = line.strip('\n')
                self.word_list.append(word)
                self.dict[word] = len(self.word_list) - 1
        return
