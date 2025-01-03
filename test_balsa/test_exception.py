import threading


from balsa import get_logger, traceback_string

from .tst_balsa import press_enter, TstGUIBalsa


def test_balsa_exception():
    application_name = "test_balsa_exception"

    balsa = TstGUIBalsa(application_name)
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

    balsa.remove()


if __name__ == "__main__":
    test_balsa_exception()
