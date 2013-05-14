import sys
import glob
import logging

from cooccurrence import cooccur_mat


def main():
    if not len(sys.argv) > 1:
        print("Usage: python cooccur_mat.py files")
        print("e.g. python cooccur_mat.py /*.txt")
        return

    logging.basicConfig(level=logging.DEBUG)

    #story_files = glob.glob(sys.argv[1])
    story_files = sys.argv[1:]
    cooccur_mat.learn_matrix(story_files)


if __name__ == '__main__':
    main()
