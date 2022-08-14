import os
import logging


def get_logger(name):
    """
    Special get_logger.  Typically, name is the name of the application using Balsa.
    :param name: name of the logger to get, which is usually the application name. Optionally it can be a python file
    name or path (e.g. __file__).
    :return: the logger for the logger name
    """

    # if name is a python file, or a path to a python file, extract the module name
    if name.endswith(".py"):
        name = name[:-3]
        if os.sep in name:
            name = name.split(os.sep)[-1]

    return logging.getLogger(name)
