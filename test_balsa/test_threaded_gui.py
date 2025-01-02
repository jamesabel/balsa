from threading import Thread
import time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")  # ensure we can run with the TKAgg backend

from balsa import get_logger, Balsa, __author__, traceback_string

exception_complete = False

def plot(y: int):

    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [1]
    ys = [y]
    ax.plot(xs, ys, marker='o', label="Sample Data")
    ax.set_title("TkAgg Backend Example (OOP Style)")
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.grid(True)
    ax.legend()
    # plt.show()
    fig.savefig(Path("temp", f"plot_{y}.png"))

class QtGuiThread(Thread):
    def run(self):

        # plot(2)

        global exception_complete
        application_name = "qt_gui_thread"
        log = get_logger(application_name)
        try:
            log.info(f"{application_name} - before divide")
            a = 2.0 / 0.0  # generate an exception for testing (not a real error)
        except ZeroDivisionError:
            log.info(f"{application_name} - division error exception")
            log.error(traceback_string())
            log.info(f"{application_name} - after error log")
            exception_complete = True

class GuiThread(Thread):
    def run(self):
        global exception_complete
        application_name = "gui_thread"
        log = get_logger(application_name)
        try:
            log.info(f"{application_name} - before divide")
            a = 3.0 / 0.0  # generate an exception for testing (not a real error)
        except ZeroDivisionError:
            log.info(f"{application_name} - division error exception")
            log.error(traceback_string())
            log.info(f"{application_name} - after error log")
            exception_complete = True

def test_threaded_gui():

    global exception_complete
    timeout = 10

    plot(1)

    application_name = "main_thread"
    log = get_logger(application_name)
    balsa = Balsa(application_name, __author__, verbose=True, log_directory="temp", gui=True, is_root=False, delete_existing_log_files=True)
    balsa.init_logger()
    log.info("starting main thread")

    exception_complete = False
    gui_thread = QtGuiThread()
    gui_thread.start()
    loop_count = 0
    while loop_count < timeout:
        time.sleep(1)
        loop_count += 1
    assert exception_complete

    exception_complete = False
    gui_thread = GuiThread()
    gui_thread.start()
    gui_thread.join(timeout)
    assert exception_complete

if __name__ == "__main__":
    test_threaded_gui()


