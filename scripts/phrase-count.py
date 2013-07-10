import threading
import Queue

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


def count(phrases, i, q):
    #with write_lock:
    q.put(i)


def main():
    phrases = read_phrases('phrases.csv')
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
