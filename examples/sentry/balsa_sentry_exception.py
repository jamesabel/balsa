from dotenv import load_dotenv
from balsa import Balsa, __author__


def balsa_sentry_exception():
    load_dotenv()  # use local .env if available

    # Balsa initializes Sentry. No need to do it here.
    balsa = Balsa("balsa_sentry_exception", __author__, use_sentry=True)  # Sentry DSN will be loaded from environment variable SENTRY_DSN
    balsa.init_logger()

    a = 1 / 0


if __name__ == '__main__':

    balsa_sentry_exception()
