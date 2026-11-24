"""
Failures inside the AWS CloudWatch logs handler: the failures a cloud logging call can plausibly have are reported through logging's handleError() instead of
raising out of the user's log call, while anything else (a programming error) is not swallowed.

All tests in this file are AI-authored (Claude Code); the private helpers below are covered by this note.
"""

import logging

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

from balsa.aws_cloudwatch_logs import AWSCloudWatchLogHandler


class _FailingLogsAccess:
    """
    Stands in for awsimple's LogsAccess, so no AWS (or mock AWS) call is made.
    """

    def __init__(self, exception: BaseException):
        self.exception = exception

    def put(self, message: str):
        raise self.exception


def _make_handler(monkeypatch, exception: BaseException) -> tuple:
    """
    :return: the handler, and the list of records passed to its handleError()
    """
    handler = AWSCloudWatchLogHandler("test_aws_cloudwatch_logs_errors")
    monkeypatch.setattr(handler, "logs_access", _FailingLogsAccess(exception))
    handled_records: list = []
    monkeypatch.setattr(handler, "handleError", handled_records.append)
    return handler, handled_records


def _make_record(message: str, *args) -> logging.LogRecord:
    return logging.LogRecord("test_aws_cloudwatch_logs_errors", logging.WARNING, __file__, 1, message, args, None)


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
@pytest.mark.parametrize(
    "exception",
    [
        ClientError({"Error": {"Code": "AccessDeniedException", "Message": "not allowed"}}, "PutLogEvents"),
        EndpointConnectionError(endpoint_url="https://logs.us-west-2.amazonaws.com"),
        NoCredentialsError(),
        ConnectionResetError("connection reset"),
    ],
    ids=["ClientError", "EndpointConnectionError", "NoCredentialsError", "OSError"],
)
def test_aws_cloudwatch_logs_cloud_failure_is_handled(monkeypatch, exception):
    handler, handled_records = _make_handler(monkeypatch, exception)
    record = _make_record("a message")

    handler.handle(record)  # must not raise

    assert handled_records == [record]


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_aws_cloudwatch_logs_bad_log_call_is_handled(monkeypatch):
    # a log call whose arguments don't match its format string (TypeError from getMessage) is reported the same way every other logging handler reports it
    handler, handled_records = _make_handler(monkeypatch, ZeroDivisionError())  # put() is never reached
    record = _make_record("%d items", "not a number")

    handler.handle(record)  # must not raise

    assert handled_records == [record]


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_aws_cloudwatch_logs_unexpected_exception_is_not_swallowed(monkeypatch):
    # the handler only catches the failures it expects - a programming error surfaces rather than being silently reported as a logging error
    handler, handled_records = _make_handler(monkeypatch, ZeroDivisionError("a bug"))

    with pytest.raises(ZeroDivisionError):
        handler.handle(_make_record("a message"))

    assert handled_records == []
