import logging

log = logging.getLogger(__name__)

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
            super().__init__(**kwargs)

        def handle(self, record):
            message = self.format(record)
            noci_cloud_log_access = LogsAccess(self.log_group)
            noci_cloud_log_access.put(message)

else:

    # mypy will complain that AWSCloudWatchLogHandler is already defined ...

    class AWSCloudWatchLogHandler(logging.NullHandler):  # type: ignore
        # dummy so we don't get an import error
        def __init__(self, log_group: str):
            log.error("AWS CloudWatch enabled but awsimple not installed")
            super().__init__()
