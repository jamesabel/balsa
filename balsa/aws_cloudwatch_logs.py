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
    from botocore.exceptions import BotoCoreError, ClientError  # botocore is installed with awsimple

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
            except (BotoCoreError, ClientError, OSError, TypeError, ValueError, KeyError):
                # A cloud logging failure must not raise out of the user's log call. The failures this can plausibly have:
                #   BotoCoreError - no credentials, unknown profile, endpoint connection and other HTTP client errors
                #   ClientError - AWS rejected the request (e.g. access denied, throttling)
                #   OSError - network and socket errors not wrapped by botocore, and getpass.getuser() when there is no user name (KeyError before Python 3.13)
                #   TypeError, ValueError - the log call's arguments don't match its format string, or the message or its structured (JSON) part can't be parsed or serialized
                self.handleError(record)

else:

    class AWSCloudWatchLogHandler(logging.NullHandler):
        # dummy so we don't get an import error
        def __init__(self, log_group: str, **kwargs):
            log.error("AWS CloudWatch enabled but awsimple not installed")
            super().__init__()
