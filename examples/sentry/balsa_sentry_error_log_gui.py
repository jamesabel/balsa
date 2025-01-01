from dotenv import load_dotenv
from balsa import Balsa, __author__, get_logger

application = "balsa_sentry_error_log_gui"

log = get_logger(application)


def balsa_sentry_error_log_gui():
    load_dotenv()

    balsa = Balsa(application, __author__, gui=True, use_sentry=True)
    balsa.init_logger()

    log.error("test balsa sentry error message", stack_info=True)


if __name__ == '__main__':
    balsa_sentry_error_log_gui()
