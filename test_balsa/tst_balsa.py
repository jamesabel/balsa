from pathlib import Path
import logging
import time

import pyautogui

from balsa import Balsa, __author__

# for testing, no rate limits unless explicitly set
big_number = 1e6
default_rate_limits = {logging.info: big_number, logging.error: big_number, logging.warning: big_number, logging.debug: big_number, logging.critical: big_number}


class TstBalsa(Balsa):

    def __init__(self, name: str, gui: bool, is_root: bool, rate_limits: dict | None):
        if rate_limits is None:
            rate_limits = default_rate_limits
        super().__init__(name, __author__, gui=gui, is_root=is_root, rate_limits=rate_limits, log_directory=Path("log", name), delete_existing_log_files=True)


class TstCLIBalsa(TstBalsa):

    def __init__(self, name: str, is_root: bool = False, rate_limits: dict | None = None):
        super().__init__(name, gui=False, is_root=is_root, rate_limits=rate_limits)


class TstGUIBalsa(TstBalsa):

    def __init__(self, name: str, is_root: bool = False, rate_limits: dict | None = None):
        super().__init__(name, gui=True, is_root=is_root, rate_limits=rate_limits)


def press_enter(n: int = 1, enter_press_time: float = 1.0):
    for i in range(n):
        time.sleep(enter_press_time)
        pyautogui.press("enter")
