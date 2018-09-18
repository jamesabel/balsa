
import time
import threading

import pyautogui

from balsa import get_logger, Balsa, __author__
from test_balsa import enter_press_time


def press_enter():
    for _ in range(0, 3):
        time.sleep(enter_press_time)
        pyautogui.press('enter')


def test_gui_rate_limit():
    application_name = 'test_gui_rate_limit'

    balsa = Balsa(application_name, __author__, verbose=True, log_directory='temp', gui=True, delete_existing_log_files=True)
    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()
    for count in range(0, 4):
        log.warning(str(count))

    press_enter_thread.join()


if __name__ == '__main__':
    test_gui_rate_limit()
