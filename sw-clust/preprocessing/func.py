# Defines some useful functions


def ispronoun(word):
    pronoun_set = ['they', 'he', 'she', 'his', 'her', 'they', 'their', 'those', 'that', 'these', 'which', 'its']
    if word in pronoun_set:
        return True
    else:
        return False
