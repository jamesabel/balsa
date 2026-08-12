import time
import logging
import os
import threading

from tobool import to_bool_strict

from . import __application_name__

use_mttkinter = to_bool_strict(os.environ.get(f"{__application_name__}_USE_MTTKINTER", True))  # in case the user doesn't want to use mttkinter (multi-threaded tkinter)

try:
    if use_mttkinter:
        # importing mttkinter monkey-patches tkinter to be thread-safe
        import mttkinter  # noqa: F401
except ModuleNotFoundError:
    pass

try:
    import tkinter
    from tkinter import messagebox

    tkinter_present = True
except ModuleNotFoundError:
    tkinter_present = False


def init_tkinter() -> "tkinter.Tk | None":
    if tkinter_present:
        tk = tkinter.Tk()
        tk.withdraw()  # don't show the 'main' Tk window

        # make sure popup window has focus
        tk.wm_attributes("-topmost", 1)
        tk.focus_force()

        if use_mttkinter:
            # check that if we're using tkinter, mttkinter is installed
            is_mttkinter = any("mttkinter" in d.lower() for d in dir(tk))
            assert is_mttkinter, "mttkinter is not installed"

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
        # keys may be str (e.g. from a JSON round-trip of the Balsa config) - normalize to int so record.levelno lookups work
        self.rate_limits = {int(level): limits for level, limits in rate_limits.items()}

        self.count = 0
        self.start_display_time_window = None
        self.rate_limit_lock = threading.Lock()  # handle() can be called from multiple threads

        super().__init__()

    @staticmethod
    def _get_message_box(levelno: int):
        # select the message box based on the level, including custom levels (Tk doesn't go any higher than error)
        if levelno >= logging.ERROR:
            return messagebox.showerror
        elif levelno >= logging.WARNING:
            return messagebox.showwarning
        return messagebox.showinfo

    def handle(self, record):

        if not tkinter_present:
            return

        now = time.time()
        with self.rate_limit_lock:
            if record.levelno in self.rate_limits:
                rate_limit = self.rate_limits[record.levelno]
            else:
                # no limit for custom levels
                rate_limit = {"count": 1000, "time": 0.0}
            if self.start_display_time_window is None or now - self.start_display_time_window >= rate_limit["time"]:
                # start a new rate limit time window
                self.count = 0
                self.start_display_time_window = now
            display = self.count < rate_limit["count"]
            if display:
                self.count += 1
            limit_reached = display and self.count >= rate_limit["count"]

        # display the message box outside the lock since it blocks until the user dismisses it
        if display:
            tk = init_tkinter()
            if tk is not None:
                try:
                    self._get_message_box(record.levelno)(f"{record.name} : {record.levelname}", record.getMessage(), parent=tk)
                    if limit_reached:
                        t = "Limit Reached"
                        s = "Message box limit of %d in %.1f seconds for %s reached" % (
                            int(rate_limit["count"]),
                            float(rate_limit["time"]),
                            str(record.levelname),
                        )
                        messagebox.showinfo(t, s, parent=tk)
                finally:
                    tk.destroy()  # don't leak Tk root windows
