from dotenv import load_dotenv
from balsa import Balsa, __author__, get_logger

log = get_logger("balsa_sentry_exception_gui")


def balsa_sentry_exception_gui():
    load_dotenv()  # use local .env if available

    # Balsa initializes Sentry. No need to do it here.
    # gui=True will capture stdout and stderr and send it to the log file.
    balsa = Balsa("balsa_sentry_exception_gui", __author__, gui=True, use_sentry=True)  # Sentry DSN will be loaded from environment variable SENTRY_DSN
    balsa.init_logger()

    # log.error(f'"log_directory={balsa.log_directory}"')  # will pop up a dialog box with the log directory

    # note that stdout/stderr is captured by Balsa and send to the log file.
    # "ZeroDivisionError: division by zero" is actually 3 log events (3 writes to stdout/stderr):
    #       "ZeroDivisionError"
    #       ": "
    #       "division by zero"
    # So it will be on 3 different log lines.
    a = 1 / 0


if __name__ == '__main__':
    balsa_sentry_exception_gui()
