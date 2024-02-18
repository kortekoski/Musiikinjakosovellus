import string
import random

def generate_sharecode():
    characters = string.ascii_letters + string.digits
    sharecode = ''.join(random.choice(characters) for i in range(16))
    return sharecode