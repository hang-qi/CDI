# Vocabulary


class Vocabulary(object):
    """A Vocabulary contains a word list and a dictionary."""
    def __init__(self):
        super(Vocabulary, self).__init__()
        self.word_list = []     # maps id -> word
        self.dict = dict()      # maps word -> id

    def add(self, word):
        """Add a word to vocabulary.
        Word contained in the vocabulary will not be inserted again."""
        if not self.contain(word):
            self.word_list.append(word)
            self.dict[word] = len(self.word_list) - 1

    def contain(self, word):
        """Return True is word is in the vocabulary."""
        return word in self.dict

    def get_word_index(self, word):
        """Return the word index in the vocabulary. Return -1 if no found."""
        if self.contain(word):
            return self.dict[word]
        else:
            return -1

    def get_word(self, index):
        return self.word_list[index]

    def size(self):
        return len(self.word_list)
