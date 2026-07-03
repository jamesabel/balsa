from typing import Union
from datetime import datetime
from logging import Formatter, LogRecord


class BalsaFormatter(Formatter):
    """
    Format time in ISO 8601
    """

    def formatTime(self, record: LogRecord, datefmt: Union[str, None] = None) -> str:
        if datefmt is not None:
            # an explicit datefmt overrides the ISO 8601 default
            return super().formatTime(record, datefmt)
        time_stamp = datetime.fromtimestamp(record.created)
        return time_stamp.astimezone().isoformat()
