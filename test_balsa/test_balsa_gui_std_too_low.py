import time
import threading

import pyautogui

from balsa import Balsa, __author__
from test_balsa import enter_press_time


def press_enter():
    time.sleep(enter_press_time)


def test_balsa_gui_std_too_low():
    application_name = "test_balsa_gui_std_too_low"

    # verbose to make the popup button happen
    balsa = Balsa(application_name, __author__, verbose=False, log_directory="temp", gui=True, is_root=False, delete_existing_log_files=True)
    balsa.init_logger()

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()
    print("YOU SHOULD NOT SEE ME!!!")  # will be too low of a log level and not do anything
    press_enter_thread.join()


if __name__ == "__main__":
    test_balsa_gui_std_too_low()
