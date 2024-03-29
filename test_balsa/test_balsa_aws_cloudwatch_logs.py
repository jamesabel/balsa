from ismain import is_main

from yasf import sf
from balsa import get_logger, Balsa, __author__


def test_balsa_aws_cloudwatch_logs():

    from awsimple import is_mock

    print(f"{is_mock()=}")

    application_name = "test_balsa_aws_cloudwatch_logs"

    balsa = Balsa(application_name, __author__, use_aws_cloudwatch_logs=True)
    balsa.init_logger()

    log = get_logger(application_name)
    log.warning("test error message")
    log.warning(sf(is_mock=is_mock(), issue="something went wrong"))
    log.warning(sf("another message", is_mock=is_mock(), issue="something really went wrong"))


if is_main():
    test_balsa_aws_cloudwatch_logs()
