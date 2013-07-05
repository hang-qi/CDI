from model import topic_model as tm


def main():
    initial_corpus = []

    topic_model = tm.TopicModel()
    topic_model.feed(initial_corpus)

    #for batch in batches:
    #    topic_model.feed(batch)


if __name__ == '__main__':
    main()
