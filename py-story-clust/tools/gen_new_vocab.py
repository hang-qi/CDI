import sys

sys.path.append('..')
from vocabulary import vocabulary


def main():
    voc_np_old = vocabulary.Vocabulary()
    voc_np_old.load('../mat/vp_before_calculate_matrix.voc')
    print('Before delete: {0}'.format(voc_np_old.size()))

    voc_np_to_delete = vocabulary.Vocabulary()
    voc_np_to_delete.load('../mat/vp_to_delete.voc')
    print('To delete: {0}'.format(voc_np_to_delete.size()))

    new_word_list = [w for w in voc_np_old.word_list if not w in voc_np_to_delete.word_list]
    voc_np_new = vocabulary.Vocabulary()
    voc_np_new.build_by_list(new_word_list)
    print('After deletion: {0}'.format(len(new_word_list)))
    voc_np_new.save('../mat/vp.voc')
    return


if __name__ == '__main__':
    main()
