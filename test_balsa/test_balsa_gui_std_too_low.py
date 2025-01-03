import threading

from .tst_balsa import TstGUIBalsa, press_enter


def test_balsa_gui_std_too_low():
    application_name = "test_balsa_gui_std_too_low"

    # verbose to make the popup button happen
    balsa = TstGUIBalsa(application_name)
    balsa.init_logger()

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()
    print("YOU SHOULD NOT SEE ME!!!")  # will be too low of a log level and not do anything
    press_enter_thread.join()

    balsa.remove()


if __name__ == "__main__":
    test_balsa_gui_std_too_low()
