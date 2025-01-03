from pathlib import Path

import threading


from balsa import get_logger, __author__


from .tst_balsa import TstGUIBalsa, press_enter


def test_balsa_gui():
    application_name = "test_balsa_gui"

    balsa = TstGUIBalsa(application_name, __author__)
    balsa.log_directory = Path("temp", application_name)
    balsa.delete_existing_log_files = True
    balsa.verbose = True
    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()
    log.error("test error message")
    press_enter_thread.join()

    balsa.remove()


if __name__ == "__main__":
    test_balsa_gui()
