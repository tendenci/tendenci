VERSION = (0, 1, 5, "final")

def get_version():
    if VERSION[3] != "final":
        return "{}.{}.{}{}".format(VERSION[0], VERSION[1], VERSION[2], VERSION[3])
    else:
        return "{}.{}.{}".format(VERSION[0], VERSION[1], VERSION[2])

__version__ = get_version()
