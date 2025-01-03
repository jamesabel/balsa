from threading import Thread
from pathlib import Path
import time

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")  # ensure we can run with the TKAgg backend

from balsa import get_logger, traceback_string

from .tst_balsa import TstGUIBalsa, press_enter

exception_a_complete = False
exception_b_complete = False


def plot(y: int):

    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [1]
    ys = [y]
    ax.plot(xs, ys, marker="o", label="Sample Data")
    ax.set_title("TkAgg Backend Example (OOP Style)")
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.grid(True)
    ax.legend()
    # plt.show()
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True, parents=True)
    fig.savefig(Path(temp_dir, f"plot_{y}.png"))


class GuiThreadA(Thread):
    def run(self):
        global exception_a_complete
        application_name = "gui_thread_a"
        log = get_logger(application_name)
        try:
            log.info(f"{application_name} - before divide")
            a = 3.0 / 0.0  # generate an exception for testing (not a real error)
        except ZeroDivisionError:
            log.info(f"{application_name} - division error exception")
            log.error(traceback_string())
            log.info(f"{application_name} - after error log")
            exception_a_complete = True


class GuiThreadB(Thread):
    def run(self):

        # This will likely cause MATPLOTLIB to fail in some way, so leave it out of the test unless we're specifically trying to tolerate MATPLOTLIB failing.
        # plot(2)

        global exception_b_complete
        application_name = "gui_thread_b"
        log = get_logger(application_name)
        try:
            log.info(f"{application_name} - before divide")
            a = 2.0 / 0.0  # generate an exception for testing (not a real error)
        except ZeroDivisionError:
            log.info(f"{application_name} - division error exception")
            log.error(traceback_string())
            log.info(f"{application_name} - after error log")
            exception_b_complete = True


def test_threaded_gui():

    global exception_a_complete, exception_b_complete
    timeout = 100.0

    plot(1)

    application_name = "test_threaded_gui"
    log = get_logger(application_name)
    balsa = TstGUIBalsa(application_name, is_root=True)
    balsa.init_logger()
    log.info(f"{application_name} - starting main thread")

    exception_a_complete = False
    gui_thread_a = GuiThreadA()
    gui_thread_a.start()

    time.sleep(1.0)

    exception_b_complete = False
    gui_thread_b = GuiThreadB()
    gui_thread_b.start()

    time.sleep(1.0)

    press_enter(2)  # press enter for each thread window

    gui_thread_a.join(timeout)
    gui_thread_b.join(timeout)

    assert exception_a_complete
    assert exception_b_complete

    balsa.remove()


if __name__ == "__main__":
    test_threaded_gui()
