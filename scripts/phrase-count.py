import threading
import Queue

import cleansing

#write_lock = threading.Lock()


class Phrase(object):
    def __init__(self, stub, phrase, original, length):
        super(Phrase, self).__init__()
        self.stub = stub.strip('\"')
        self.phrase = phrase.strip('\"')
        self.original = original.strip('\"')
        self.words = self.phrase.split()
        self.length = int(length.strip('\"'))
        try:
            assert(len(self.words) == self.length)
        except AssertionError, e:
            print(self.phrase)
            print(self.words)
            print(self.length)
            raise e


def read_phrases(phrase_file):
    phrases = []
    length_set = set()
    with open(phrase_file, 'r') as f:
        line_counter = 0
        for line in f:
            line_counter += 1
            # Skip the header line
            # "","PHRASE_STUB","PHRASE","ORIGINALPHRASE","WORDS","ALPHA","BETA","DEM_COUNT","REP_COUNT","slant","Rshare"
            if (line_counter == 1):
                continue

            parts = line.split(',')
            phrase = Phrase(stub=parts[1], phrase=parts[2], original=parts[3], length=parts[4])
            length_set.add(phrase.length)
            phrases.append(phrase)
    assert(len(phrases) == 1000)
    print(length_set)
    return phrases


def read_caption_and_clean(captionfile):
    words = []
    content_tags = set(['CC0', 'CC1', 'TR0', 'TR1'])
    with open(captionfile, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            if line[0] == '2' or line[0:3] in content_tags:
                content = line.split('|')[-1]
                words.extend(content.split())
    return cleansing.clean(words)


def count(phrases, i, q):
    #with write_lock:
    q.put(i)


def main():
    phrases = read_phrases('phrases.csv')
    stopwords = read_stopwords('stopwords.txt')
    #result = count(phrases)
    q = Queue.Queue()

    threads = []
    for i in range(1, 100):
        t = threading.Thread(target=count, args=([], i, q))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    #s = q.get()
    print(q.get())
    pass

if __name__ == '__main__':
    main()
