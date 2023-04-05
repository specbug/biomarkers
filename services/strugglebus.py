import os
import random

from models.strugglebus import Event


def get_random_action_state(event: Event) -> bool:
    probability = float(os.getenv(event))
    return random.random() < probability
