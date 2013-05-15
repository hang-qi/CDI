# Triplet Vocabulary including NP and VP
import codecs


class TripletVocabulary(object):
    """A Vocabulary contains a word list and a dictionary."""
    def __init__(self):
        super(TripletVocabulary, self).__init__()
        self.np_list = []     # maps id -> word
        self.vp_list = []

    def add_np(self, word):
        """Add a word to np vocabulary.
        Word contained in the vocabulary will not be inserted again."""
        if not self.np_contain(word):
            self.np_list.append(word)

    def add_vp(self, word):
        """Add a word to vp vocabulary.
        Word contained in the vocabulary will not be inserted again."""
        if not self.vp_contain(word):
            self.vp_list.append(word)

    def np_contain(self, word):
        """Return True is word is in the vocabulary."""
        return word in self.np_list

    def vp_contain(self, word):
        """Return True is word is in the vocabulary."""
        return word in self.vp_list

    def np_size(self):
        return len(self.np_list)

    def vp_size(self):
        return len(self.vp_list)

    def np_index(self, word):
        return self.np_list.index(word)

    def vp_index(self, word):
        return self.vp_list.index(word)

    def save(self, filename):
        with codecs.open('{0}.np_list'.format(filename), "w", encoding='ISO-8859-1') as f:
            for val in self.np_list:
                f.writelines(val + '\n')
        with codecs.open('{0}.vp_list'.format(filename), "w", encoding='ISO-8859-1') as f:
            for val in self.vp_list:
                f.writelines(val + '\n')
        return

    def load(self, filename):
        self.np_list = []
        self.vp_list = []
        with codecs.open('{0}.np_list'.format(filename), "r", encoding='ISO-8859-1') as f:
            for line in f:
                self.np_list.append(line.strip('\n'))
        with codecs.open('{0}.vp_list'.format(filename), "r", encoding='ISO-8859-1') as f:
            for line in f:
                self.vp_list.append(line.strip('\n'))
        return
