
import time
import threading

import pyautogui

from balsa import get_logger, Balsa, __author__, traceback_string
from test_balsa import enter_press_time


def press_enter():
    for _ in range(0, 2):
        time.sleep(enter_press_time)
        pyautogui.press('enter')


def test_balsa_exception():
    application_name = 'test_balsa_exception'

    balsa = Balsa(application_name, __author__, gui=True, rate_limit_count=3)
    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter)
    press_enter_thread.start()

    try:
        a = 1.0/0.0  # generate an exception for testing (not a real error)
    except ZeroDivisionError:
        log.error('test exception')
        log.error(traceback_string())

    press_enter_thread.join()


if __name__ == '__main__':
    test_balsa_exception()
