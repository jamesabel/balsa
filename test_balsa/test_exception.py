import threading
import logging


from balsa import get_logger, Balsa, __author__, traceback_string

from .tst_balsa import press_enter


def test_balsa_exception():
    application_name = "test_balsa_exception"

    balsa = Balsa(application_name, __author__, gui=True, is_root=False)
    balsa.rate_limits[logging.ERROR]["count"] = 4  # we have 3 messages
    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter, args=(2,))
    press_enter_thread.start()

    try:
        a = 1.0 / 0.0  # generate an exception for testing (not a real error)
    except ZeroDivisionError:
        log.error("test exception")
        log.error(traceback_string())

    press_enter_thread.join()


if __name__ == "__main__":
    test_balsa_exception()
