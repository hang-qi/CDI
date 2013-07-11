import re
import datetime
import os
import threading
import codecs
import logging

import cleansing

# global configurations
g_filenameParser = re.compile(r"""(20\d\d)-(\d\d)-(\d\d)_(\d\d)(\d\d)_(\w\w)_(.+)\.txt""", re.I | re.X)
g_content_tags = set(['CC0', 'CC1', 'TR0', 'TR1'])


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
    return phrases


def _parse_filename(filename):
    m = g_filenameParser.match(filename)
    g = m.groups()
    assert(len(g) == 7)

    utc_time = datetime.datetime(2000, 1, 1, 0, 0)
    utc_time = utc_time.replace(
        year=int(g[0]),
        month=int(g[1]),
        day=int(g[2]),
        hour=int(g[3]),
        minute=int(g[4]))
    country = g[5]
    network_and_show = g[6]
    return (utc_time, country, network_and_show)


def _read_caption_and_clean(captionfile):
    words = []
    with codecs.open(captionfile, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            if line[0] == '2' or line[0:3] in g_content_tags:
                content = line.split('|')[-1]
                words.extend(content.split())
    return cleansing.clean(words)


def _get_all_captionfiles(root_dir):
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if (filename[-4:].lower() == ".txt"):
                files.append(os.path.join(dirpath, filename))
    files.sort()
    return files


def _count_gram(words, i_start, ngram, phrases_dict, feature_vector):
    gram = words[i_start:i_start+ngram]
    if len(gram) == ngram:
        phrase = ' '.join(gram)
        if phrase in phrases_dict:
            logging.info('Phrase Found: {0}'.format(phrase))
            feature_vector[phrases_dict[phrase]] += 1
    return feature_vector


def _count_phrases(captionfile, phrases_dict):
    """Returns a count vector."""
    feature_vector = [0] * len(phrases_dict)
    words = _read_caption_and_clean(captionfile)
    for i in range(0, len(words)):
        feature_vector = _count_gram(words, i, 2, phrases_dict, feature_vector)
        feature_vector = _count_gram(words, i, 3, phrases_dict, feature_vector)
    return feature_vector


def count_year_month(year, month, phrases_dict):
    logging.info('Counting for {0}-{1:02d} started.'.format(year, month))
    outputfile = 'data/count_{0}-{1:02}.txt'.format(year, month)
    with open(outputfile, 'w') as fout:
        # Get all files in the year
        caption_files = []
        for day in range(1, 31):
            caption_files.extend(_get_all_captionfiles('/tv/{0}/{0}-{1:02d}/{0}-{1:02d}-{2:02d}/'.format(year, month, day)))
        logging.info('Files found for {0}-{1:02d}.'.format(year, month))

        # Count files one by one
        for captionfile in caption_files:
            # Extract meta-data from the filename
            filename = captionfile.split('/')[-1]
            (broadcast_datetime, country, network_and_show) = _parse_filename(filename)

            # Only count for US network
            if country != 'US':
                continue

            # Count
            logging.info('Counting: {0}'.format(filename))
            feature_vector = _count_phrases(captionfile, phrases_dict)

            feature_string = [str(x) for x in feature_vector]
            # output counting result
            fout.write('{date:%Y-%m-%d}, {hour:%H:%M}, {show}, {feature}\n'.format(
                date=broadcast_datetime, hour=broadcast_datetime, show=network_and_show, feature=', '.join(feature_string)))
    logging.info('Counting for year {0}-{1:02d} done.'.format(year, month))


def main():
    logging.basicConfig(level=logging.INFO)

    phrases = read_phrases('phrases.csv')
    phrases_dict = dict()
    for (index, phrase) in enumerate(phrases):
        phrases_dict[phrase.phrase] = index

    threads = []
    #for year in range(2006, 2014):
    for year in range(2006, 2007):
        for month in range(1, 3):
            #count_whole_year(year, phrases_dict)
            t = threading.Thread(target=count_year_month, args=(year, month, phrases_dict))
            t.daemon = True
            t.start()
            threads.append(t)

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
