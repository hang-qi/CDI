# Vocabulary


class Vocabulary(object):
    """A Vocabulary contains a word list and a dictionary."""
    def __init__(self, arg):
        super(Vocabulary, self).__init__()
        self.word_list = []
        self.dict = dict()

    def insert(self, word):
        """Insert a word to vocabulary.
        Word contained in the vocabulary will not be inserted again."""
        if not self.contain(word):
            self.word_list.insert(word)
            self.dict[word] = len(self.word_list) - 1

    def contain(self, word):
        """Return True is word is in the vocabulary."""
        return word in self.dict

    def get_word_id(self, word):
        """Return the word id in the vocabulary. Return -1 if no found."""
        if self.contain(word):
            return self.dict[word]
        else:
            return -1

    def size(self):
        return len(self.word_list)
