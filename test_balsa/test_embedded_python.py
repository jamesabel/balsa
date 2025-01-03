# todo: test balsa if tkinter is not present, which can happen for embedded (frozen) Python

import sys

from balsa import get_logger

save_tkinter = sys.modules["tkinter"]

from .tst_balsa import TstCLIBalsa

application_name = "test_embedded_python"


def test_embedded_python():
    global save_tkinter

    # emulate embedded Python by removing tkinter module
    del sys.modules["tkinter"]

    balsa = TstCLIBalsa(application_name)
    balsa.init_logger()

    log = get_logger(application_name)
    log.warning(f"{application_name} ... test warning message")
    balsa.remove()

    sys.modules["tkinter"] = save_tkinter
