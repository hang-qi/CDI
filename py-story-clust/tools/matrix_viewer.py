import sys
import numpy as np

sys.path.append('..')
from vocabulary import vocabulary


def show_top_words(wid, matrix, voc):
    if wid < 0:
        print('Word not found.')
        return
    try:
        word = voc.get_word(wid)
        pass
    except Exception, e:
        print('Word not found.')
        return

    print('Top 10 simiar words for ({1}) [{0}]'.format(word, wid))
    array = matrix[wid]
    indexes = np.argsort(array)
    top_words_id = indexes[::-1][0:10]
    for i in top_words_id:
        print("({0})\t{1}\t\t{2}".format(i, voc.get_word(i), array[i]))


def main():
    if (len(sys.argv) != 3):
        print('Please give matrix file and vocabulary file.')
        print('Usage: python matrix_viewer.py matrix_file vocabulary_file')

    voc = vocabulary.Vocabulary()
    try:
        matrix = np.load(sys.argv[1])
        voc.load(sys.argv[2])
    except Exception, e:
        print('Failed to load matrix or vocabulary')
        print('Exception: {0}'.format(e))
        return

    while True:
        print('Please choose what to do:')
        print('[1]: view matrix')
        print('[2]: view words')
        print('[3]: view similar words by word id')
        print('[4]: view similar words by word')
        print('[0]: quit')
        try:
            cmd = input("> ")
        except Exception:
            continue

        if cmd == 0:
            return
        elif cmd == 1:
            print(matrix)
        elif cmd == 2:
            print(voc.dict)
            print('Vocabulary Size: {0}'.format(voc.size()))
        elif cmd == 3:
            try:
                word_id = input("Please input word id (-1 to cancel): ")
            except Exception:
                continue

            if word_id != '-1':
                show_top_words(word_id, matrix, voc)
            else:
                continue
        elif cmd == 4:
            try:
                word_to_find = raw_input("Please input a word: ")
            except Exception:
                continue
            try:
                show_top_words(int(voc.get_word_index(word_to_find)), matrix, voc)
            except ValueError:
                print('Word not found.')
                continue

        print("")
    return


if __name__ == '__main__':
    main()
