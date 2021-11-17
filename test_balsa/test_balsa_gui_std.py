import time
import threading

import pyautogui

from balsa import Balsa, __author__
from test_balsa import enter_press_time


def press_enter():
    time.sleep(enter_press_time)
    pyautogui.press("enter")


def test_balsa_gui():
    application_name = "test_balsa_gui_std"

    # verbose to make the popup button happen
    balsa = Balsa(application_name, __author__, verbose=True, log_directory="temp", gui=True, is_root=False, delete_existing_log_files=True)
    balsa.init_logger()

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()
    print("GUIs should not write to stdout but I am")
    press_enter_thread.join()


if __name__ == "__main__":
    test_balsa_gui()
