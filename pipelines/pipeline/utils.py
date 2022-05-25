import string
import random


def random_secret(n=45):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(n))
