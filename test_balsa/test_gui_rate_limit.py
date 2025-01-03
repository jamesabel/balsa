import threading
import logging

import pytest

from balsa import get_logger, __author__

from .tst_balsa import TstGUIBalsa, press_enter
from .popup_window import is_popup_dialog_with_ok

def test_gui_rate_limit():
    application_name = "test_gui_rate_limit"

    rate_limit_count = 2
    balsa = TstGUIBalsa(application_name, __author__)
    rate_limits = {
            level: {"count": rate_limit_count, "time": 60.0}
            for level in [
                logging.CRITICAL,
                logging.ERROR,
                logging.WARNING,
                logging.INFO,
                logging.DEBUG,
                logging.NOTSET,
            ]
        }
    balsa.rate_limits = rate_limits

    balsa.init_logger()

    log = get_logger(application_name)

    press_enter_thread = threading.Thread(target=press_enter, args=(rate_limit_count + 1,))
    press_enter_thread.start()
    # make sure the rate limit is hit
    for count in range(0, rate_limit_count + 5):
        log.warning(str(count))

    popup_present = is_popup_dialog_with_ok()
    if popup_present:
        pytest.fail("test_balsa_gui_std_too_low: popup dialog found when it should not have")

    press_enter_thread.join()

    balsa.remove()


if __name__ == "__main__":
    test_gui_rate_limit()
