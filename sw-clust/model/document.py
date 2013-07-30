class OrignalDocument(object):
    """Content and meta data of a document."""
    def __init__(self, filename, timestamp, np1_words, vp_words, np2_words, ocr_words):
        self.filename = filename
        self.timestamp = timestamp
        # vp_words and np2_words can be empty when no triplets exist
        self.word_lists = (np1_words, vp_words, np2_words)
        # ocr_words can be empty when there are no corresponding ocr results
        self.ocr_words = ocr_words
