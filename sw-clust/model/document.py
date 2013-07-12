class OrignalDocument(object):
    """Content and meta data of a document."""
    def __init__(self, filename, timestamp, np1_words, vp_words, np2_words, ocr_words):
        self.filename = filename
        self.timestamp = timestamp
        self.word_lists = (np1_words, vp_words, np2_words)
        self.ocr_words = ocr_words
