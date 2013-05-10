# Vocabulary


class Vocabulary(object):
    """docstring for Vocabulary"""
    def __init__(self, arg):
        super(Vocabulary, self).__init__()
        self.words = []
        self.dict = dict()

    def insert(self, word):
        if not self.has_word(word):
            self.words.insert(word)
            self.dict[word] = len(self.words) - 1

    def contain(self, word):
        """Return True is word is in the vocabulary"""
        return word in self.dict

    def get_word_id(self, word):
        """Return the word id in the vocabulary. Return -1 if no found."""
        if self.has_word(word):
            return self.dict[word]
        else:
            return -1

    def size(self):
        return len(self.words)
