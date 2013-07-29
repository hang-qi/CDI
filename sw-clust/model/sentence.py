class Sentence(object):
    def __init__(self, np1, vp, np2, start_with_pronoun=False):
        self.NP1 = []
        self.VP = []
        self.NP2 = []
        self.pronoun = start_with_pronoun
