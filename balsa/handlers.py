
from enum import Enum
import logging


class HandlerType(Enum):
    Console = 1
    File = 2
    DialogBox = 3
    Callback = 4
    Sentry = 5
    StringList = 6


class BalsaNullHandler(logging.NullHandler):
    """
    Hook in a callback function.  For example, this can be used to set the process return code to an error state.
    """
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def handle(self, record):
        # make sure this handler level instance is set to the level we want to deem an error - e.g. logging.ERROR
        self._callback(record)


class BalsaStringListHandler(logging.NullHandler):
    """
    keeps a buffer of the most recent log entries
    """
    def __init__(self, max_entries):
        super().__init__()
        self.max_entries = max_entries
        self.strings = []

    def handle(self, record):
        self.strings.append(self.format(record))
        if len(self.strings) > self.max_entries:
            self.strings.pop(0)
