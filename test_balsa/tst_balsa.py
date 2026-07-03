from pathlib import Path
import logging
import time

import pyautogui
import pytest

from balsa import Balsa, __author__

from .popup_window import is_popup_dialog_with_ok

# The fail-safe aborts pyautogui calls when the mouse is in a screen corner - where users naturally park the cursor while GUI tests run.
# These tests only use pyautogui.press("enter") (keyboard only, no mouse control), so there is no runaway-mouse scenario for the fail-safe
# to abort, and press_enter() already gives up via pytest.fail() if a popup never appears.
pyautogui.FAILSAFE = False

# for testing, no rate limits unless explicitly set
big_number = int(1e6)
default_rate_limits = {
    level: {"count": big_number, "time": 0.0}
    for level in [
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
        logging.NOTSET,
    ]
}


class TstBalsa(Balsa):

    def __init__(self, name: str, gui: bool, is_root: bool, rate_limits: dict | None):
        if rate_limits is None:
            rate_limits = default_rate_limits
        super().__init__(name, __author__, gui=gui, is_root=is_root, rate_limits=rate_limits, log_directory=Path("log", name), verbose=True, delete_existing_log_files=True)


class TstCLIBalsa(TstBalsa):

    def __init__(self, name: str, is_root: bool = False, rate_limits: dict | None = None):
        super().__init__(name, gui=False, is_root=is_root, rate_limits=rate_limits)


class TstGUIBalsa(TstBalsa):

    def __init__(self, name: str, is_root: bool = False, rate_limits: dict | None = None):
        super().__init__(name, gui=True, is_root=is_root, rate_limits=rate_limits)


def press_enter(n: int = 1, enter_press_time: float = 1.0):
    found = False
    count = 0
    while not found and count < 10:
        found = is_popup_dialog_with_ok()
        time.sleep(1.0)
        count += 1
    if not found:
        pytest.fail("press_enter: popup dialog not found")
    for i in range(n):
        time.sleep(enter_press_time)
        pyautogui.press("enter")
