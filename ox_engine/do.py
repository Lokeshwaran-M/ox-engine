import os



def mk_fd(fd_path):  
    """
    Creates folder in 'fd_path'  if it doesn't exist.
    """
    if not os.path.exists(fd_path):
        os.makedirs(fd_path)


