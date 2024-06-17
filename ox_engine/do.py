import os
import random
import string


def mk_fd(fd_path):  
    """
    Creates folder in 'fd_path'  if it doesn't exist.
    """
    if not os.path.exists(fd_path):
        os.makedirs(fd_path)

 
def generate_random_string(length=4):
    """
    Generates a random string of specified length containing digits and letters.
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))
