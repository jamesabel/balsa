import threading


from balsa import get_logger, __author__

from .tst_balsa import TstGUIBalsa, press_enter


def test_gui_rate_limit():
    application_name = "test_gui_rate_limit"

    balsa = TstGUIBalsa(application_name, __author__)
    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter, args=(3,))
    press_enter_thread.start()
    for count in range(0, 4):
        log.warning(str(count))

    press_enter_thread.join()

    balsa.remove()


if __name__ == "__main__":
    test_gui_rate_limit()
