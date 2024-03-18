import random


def random_true(probability):
    """Returns True with the given probability."""
    return random.random() < probability
