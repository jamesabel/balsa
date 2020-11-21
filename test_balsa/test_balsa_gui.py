import time
import threading

import pyautogui

from balsa import get_logger, Balsa, __author__
from test_balsa import enter_press_time


def press_enter():
    time.sleep(enter_press_time)
    pyautogui.press("enter")


def test_balsa_gui():
    application_name = "test_balsa_gui"

    balsa = Balsa(application_name, __author__, verbose=True, log_directory="temp", gui=True, is_root=False, delete_existing_log_files=True)
    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()
    log.error("test error message")
    press_enter_thread.join()


if __name__ == "__main__":
    test_balsa_gui()
