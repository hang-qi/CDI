import sys

sys.path.append('..')
from vocabulary import vocabulary


def delete_words_in_vocab(old_vocab, to_delete):
    voc_old = vocabulary.Vocabulary()
    voc_old.load(old_vocab)
    print('Before delete: {0}'.format(voc_old.size()))

    voc_to_delete = vocabulary.Vocabulary()
    voc_to_delete.load(to_delete)
    print('To delete: {0}'.format(voc_to_delete.size()))

    new_word_list = [w for w in voc_old.word_list if not w in voc_to_delete.word_list]
    voc_new = vocabulary.Vocabulary()
    voc_new.build_by_list(new_word_list)
    print('After deletion: {0}'.format(len(new_word_list)))

    return voc_new


def main():
    # convert np vocabulary
    voc_new = delete_words_in_vocab(
        '../mat/np_before_calculate_matrix.voc', '../mat/np_to_delete.voc')
    voc_new.save('../mat/np.voc')

    # convert vp vocabulary
    voc_new = delete_words_in_vocab(
        '../mat/vp_before_calculate_matrix.voc', '../mat/vp_to_delete.voc')
    voc_new.save('../mat/vp.voc')


if __name__ == '__main__':
    main()
