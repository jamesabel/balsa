from typing import Union
from datetime import datetime
from logging import Formatter, LogRecord


class BalsaFormatter(Formatter):

    """
    Format time in ISO 8601
    """

    def formatTime(self, record: LogRecord, datefmt: Union[str, None] = None) -> str:
        assert datefmt is None  # static format
        time_stamp = datetime.fromtimestamp(record.created)
        return time_stamp.astimezone().isoformat()
