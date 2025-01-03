import threading

from .tst_balsa import TstGUIBalsa, press_enter


def test_balsa_gui_std():
    application_name = "test_balsa_gui_std"

    # verbose to make the popup button happen
    balsa = TstGUIBalsa(application_name)
    balsa.init_logger()

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()
    print("GUIs should not write to stdout but I am")
    press_enter_thread.join()

    balsa.remove()


if __name__ == "__main__":
    test_balsa_gui_std()
