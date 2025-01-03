import threading


from balsa import get_logger, Balsa, __author__

from .tst_balsa import press_enter


def test_gui_rate_limit():
    application_name = "test_gui_rate_limit"

    balsa = Balsa(application_name, __author__, verbose=True, log_directory="temp", gui=True, is_root=False, delete_existing_log_files=True)
    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter, args=(3,))
    press_enter_thread.start()
    for count in range(0, 4):
        log.warning(str(count))

    press_enter_thread.join()


if __name__ == "__main__":
    test_gui_rate_limit()
