import os

from balsa import get_logger

from .tst_balsa import TstCLIBalsa


def test_balsa_sentry():
    application_name = "test_balsa_sentry"

    if "SENTRY_DSN" in os.environ:
        balsa = TstCLIBalsa(application_name)
        balsa.use_sentry = True
        balsa.inhibit_cloud_services = False
        sentry_dsn = os.environ["SENTRY_DSN"]
        print(f"{sentry_dsn=}")
        balsa.sentry_dsn = sentry_dsn
        balsa.init_logger()

        log = get_logger(application_name)
        log.error("test balsa sentry error message")

        balsa.remove()
    else:
        print("Please set SENTRY_DSN environment variable to have a good %s test" % __name__)


if __name__ == "__main__":
    test_balsa_sentry()
