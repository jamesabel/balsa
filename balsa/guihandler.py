import time
import logging
from pathlib import Path
from datetime import datetime

tkinter_present = False

# multi-threaded tkinter
try:
    # in case the user doesn't want to use mttkinter
    import mttkinter as tkinter
except ModuleNotFoundError:
    pass

try:
    import tkinter

    tkinter_present = True
except ModuleNotFoundError:
    tkinter_present = False


def init_tkinter() -> tkinter.Tk | None:
    if tkinter_present:
        tk = tkinter.Tk()
        tk.withdraw()  # don't show the 'main' Tk window

        # make sure popup window has focus
        tk.wm_attributes("-topmost", 1)
        tk.focus_force()
    else:
        tk = None

    return tk


class DialogBoxHandler(logging.NullHandler):
    """
    For GUI apps, display an error message dialog box.  Uses the built-in tkinter module so we don't have any
    special package dependencies.
    """

    def __init__(self, rate_limits):
        """
        :param rate_limits: dict with rate limits (in seconds) for each level, e.g. {logging.ERROR: {"count": 10, "time": 60.0}}
        """
        self.rate_limits = rate_limits

        self.count = None
        self.start_display_time_window = None

        super().__init__()

    def handle(self, record):

        Path("temp", "debug.txt").open("a").write(f"{datetime.now()}: {tkinter_present=},{record=}\n")

        now = time.time()
        if record.levelno in self.rate_limits:
            rate_limit = self.rate_limits[record.levelno]
        else:
            # no limit for custom levels
            rate_limit = {"count": 1000, "time": 0.0}
        if self.start_display_time_window is None or now - self.start_display_time_window >= rate_limit["time"]:
            self.count = 0
            self.start_display_time_window = now
        if self.count < rate_limit["count"]:
            if tkinter_present:
                from tkinter import messagebox

                boxes = {
                    logging.INFO: messagebox.showinfo,
                    logging.WARNING: messagebox.showwarning,
                    logging.ERROR: messagebox.showerror,
                    logging.CRITICAL: messagebox.showerror,  # Tk doesn't go any higher than error
                }
                tk = init_tkinter()
                if tk is not None:
                    boxes[record.levelno](f"{record.name} : {record.levelname}", record.msg, parent=tk)
            else:
                messagebox = None
            self.count += 1
            if self.count >= rate_limit["count"] and messagebox is not None:
                t = "Limit Reached"
                s = "Message box limit of %d in %.1f seconds for %s reached" % (
                    int(rate_limit["count"]),
                    float(rate_limit["time"]),
                    str(record.levelname),
                )
                if tkinter_present:
                    tk = init_tkinter()
                    if tk is not None:
                        messagebox.showinfo(t, s, parent=tk)
            self.start_display_time_window = now  # window is the time when the last window was closed
