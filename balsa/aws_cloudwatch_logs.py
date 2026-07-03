import logging
import json
from functools import lru_cache
import getpass
import platform

from yasf import sf_separate

log = logging.getLogger(__name__)


@lru_cache()
def get_user_name() -> str:
    return getpass.getuser()


@lru_cache()
def get_computer_name() -> str:
    return platform.node()


try:
    # user may or may not use AWS CloudWatch logs

    from awsimple import LogsAccess

    awsimple_exists = True

except ImportError:

    awsimple_exists = False

if awsimple_exists:

    class AWSCloudWatchLogHandler(logging.NullHandler):
        """
        Send logs to AWS CloudWatch logs.
        """

        def __init__(self, log_group: str, **kwargs):
            """
            Init the AWS CloudWatch logs handler
            :param log_group: AWS log group name
            :param kwargs: AWS credentials (passed to boto3 via AWSimple). e.g. profile name or key pairs.
            """
            self.log_group = log_group
            self.aws_kwargs = kwargs
            self.logs_access = None  # created lazily on first use, then reused (avoids creating a new boto3 session for every log record)
            super().__init__()

        def handle(self, record):
            try:
                args_json, kwargs_json = sf_separate(record.getMessage())
                if kwargs_json is None:
                    put_dict = {}
                else:
                    put_dict = json.loads(kwargs_json)
                if args_json is not None and len(args_json) > 0:
                    put_dict["message"] = args_json

                for attribute in ["created", "filename", "funcName", "levelname", "lineno", "module", "name", "pathname", "process", "thread", "threadName", "processName"]:
                    if attribute in put_dict:
                        attribute = f"_{attribute}"
                    put_dict[attribute] = getattr(record, attribute)

                put_dict["system_user_name"] = get_user_name()
                put_dict["system_computer_name"] = get_computer_name()

                put_string = json.dumps(put_dict)

                if self.logs_access is None:
                    self.logs_access = LogsAccess(self.log_group, **self.aws_kwargs)
                self.logs_access.put(put_string)
            except Exception:
                # a cloud logging failure (e.g. a network error) must not raise out of the user's log call
                self.handleError(record)

else:

    # mypy will complain that AWSCloudWatchLogHandler is already defined ...

    class AWSCloudWatchLogHandler(logging.NullHandler):  # type: ignore
        # dummy so we don't get an import error
        def __init__(self, log_group: str, **kwargs):
            log.error("AWS CloudWatch enabled but awsimple not installed")
            super().__init__()
