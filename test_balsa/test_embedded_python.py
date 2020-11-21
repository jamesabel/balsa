# todo: test balsa if tkinter is not present, which can happen for embedded (frozen) Python

import sys

save_tkinter = sys.modules["tkinter"]


def test_embedded_python():
    global save_tkinter

    # emulate embedded Python by removing tkinter module
    sys.modules["tkinter"] = None

    # todo: put what test_balsa_gui.py does here ...

    sys.modules["tkinter"] = save_tkinter
