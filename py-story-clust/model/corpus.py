# This file defines classes to model corpus.

import numpy as np

from model import *


class Corpus(object):
    """A Corpus object includes all documents' content and corpus statistics."""
    def __init__(self, corpus_stat):
        self.documents = []
        self.statistics = corpus_stat

    def add_document(self, doc, doc_stat):
        self.documents.append(doc)
        self.statistics.add_doc_stat(doc_stat)

    def get_document_name(self, doc_id):
        return self.documents[doc_id].name

    def size(self):
        return len(self.documents)


class CorpusStatistics(object):
    """Corpus statistics contains vocabulary used and document statistics."""
    def __init__(self, np1_vocab, vp_vocab, np2_vocab):
        self.documents_stats = []
        self.vocabularies = (np1_vocab, vp_vocab, np2_vocab)
        pass

    def add_doc_stat(self, document_stat):
        self.documents_stats.append(document_stat)

    def size(self):
        return len(self.documents_stats)


class Document(object):
    """Content of a document, including filename and all types of word lists."""
    def __init__(self, name, np1_words, vp_words, np2_words, ocr_words):
        self.name = name
        self.word_lists = (np1_words, vp_words, np2_words, ocr_words)


class DocumentStatistics(object):
    """Statistics of a document. This contains a distribution for each type of word."""
    def __init__(self, distributions, ocr_words=None):
        self.distributions = distributions
        if ocr_words is None:
            self.ocr_words = []
        else:
            self.ocr_words = ocr_words


class BranchStatistics(DocumentStatistics):
    def __init__(self, document_stat):
        super(BranchStatistics, self).__init__(document_stat.distributions, document_stat.ocr_words)
        self.intra_distance = 2

    def combine(self, other_document):
        for (i, dist) in enumerate(self.distributions):
            self.distributions[i].combine(other_document.distributions[i])
        self.ocr_words.extend(other_document.ocr_words)

    def synthesize_title(self, num_words=5):
        word_ids = []
        for dist in self.distributions:
            word_ids.append(dist.synthesize(num_words))
        return word_ids

    def calcualte_intra_distance(self, corpus_stat, terminals):
        """Intra branch distance is the pair of terminal nodes with maximum
        distance (measured by TV norm)."""
        d_max = 0
        for doc_i in terminals:
            for doc_j in terminals:
                if doc_i >= doc_j:
                    # Only compute half since the distance is symmetric.
                    continue

                # Calculate distance between doc_i and doc_j.
                d = 0
                word_types_to_use = [WORD_TYPE_NP1, WORD_TYPE_VP, WORD_TYPE_NP2]
                for type_id in word_types_to_use:
                    distr_i = corpus_stat.documents_stats[doc_i].distributions[type_id].hist
                    distr_j = corpus_stat.documents_stats[doc_j].distributions[type_id].hist
                    tv_norm = calculate_tv_norm(distr_i, distr_j)
                    d += tv_norm
                d /= len(word_types_to_use)

                # Update the maximum distance.
                if d > d_max:
                    d_max = d
        self.intra_distance = d_max


class Distribution(object):
    """Histogram (normalized to 1)."""
    def __init__(self, hist, denominator):
        self.hist = hist
        self.denominator = denominator

    def combine(self, other):
        # Recover the histogram before normalization and add up two histograms
        self.hist = self.hist * self.denominator + other.hist * other.denominator

        # Re-normalize to 1
        denominator = self.hist.sum()
        if denominator != 0:
            self.hist /= denominator
        self.denominator = denominator

    def synthesize(self, num_words):
        """Synthesize a set of words from the distribution."""
        indexes = np.argsort(self.hist)
        top_words_id = indexes[0][::-1][0:min(num_words, np.shape(self.hist)[1])]
        return top_words_id.tolist()

    def __getitem__(self, word_id):
        return self.hist[0, word_id]
