import time
import logging
import os
import threading

from tobool import to_bool_strict

from . import __application_name__

use_mttkinter = to_bool_strict(os.environ.get(f"{__application_name__}_USE_MTTKINTER", True))  # in case the user doesn't want to use mttkinter (multi-threaded tkinter)

mttkinter_imported = False
try:
    if use_mttkinter:
        # importing mttkinter monkey-patches tkinter to be thread-safe
        import mttkinter  # noqa: F401

        mttkinter_imported = True
except ModuleNotFoundError:
    pass

try:
    import tkinter
    from tkinter import messagebox

    tkinter_present = True
except ModuleNotFoundError:
    tkinter_present = False

if tkinter_present and mttkinter_imported:
    # mtTkinter's Tk.__init__ hook schedules a perpetual 10 ms "after" chain (_check_events) on every Tk it wraps (which is every Tk in the process, e.g. also
    # matplotlib TkAgg windows), but its destroy hook never cancels the pending timer. The stale timer stays in the thread's shared Tcl timer queue after
    # destroy and fires an 'invalid command name "..._check_events"' background error in whichever Tk event loop runs next on that thread. Wrap destroy to
    # cancel this Tk's pending "after" timers first.
    _wrapped_tk_destroy = tkinter.Tk.destroy

    def _tk_destroy_cancel_afters(self):
        try:
            for after_id in self.tk.call("after", "info"):
                self.tk.call("after", "cancel", after_id)
        except tkinter.TclError:
            pass  # already partially torn down - proceed to destroy
        _wrapped_tk_destroy(self)

    tkinter.Tk.destroy = _tk_destroy_cancel_afters  # type: ignore[method-assign]


# Creating and destroying a Tcl interpreter per dialog box - especially from multiple threads - can corrupt Tcl's process-global state and make a later
# tkinter.Tk() fail with 'Can't find a usable init.tcl ... couldn't read file ... "No error"' even though the file exists. So each thread gets one persistent
# hidden Tk root that is reused for every dialog box and intentionally never destroyed.
_tk_creation_lock = threading.Lock()  # Tcl interpreter creation is not safe to run concurrently from multiple threads
_tk_per_thread = threading.local()
# A Tcl interpreter has thread affinity, but garbage collection can finalize (and thus Tcl_DeleteInterp) an unreferenced Tk root from any thread - e.g. after
# the creating thread has exited. Keep a strong reference to every root ever created so that never happens (bounded by the number of threads that show dialogs).
_tk_roots: "list[tkinter.Tk]" = []


def init_tkinter() -> "tkinter.Tk | None":
    """
    Get the current thread's persistent hidden Tk root, creating it on first use.
    :return: the Tk root for this thread, or None if tkinter is not available
    """
    if not tkinter_present:
        return None

    tk = getattr(_tk_per_thread, "tk", None)
    if tk is None:
        with _tk_creation_lock:
            tk = tkinter.Tk()
        tk.withdraw()  # don't show the 'main' Tk window

        if use_mttkinter:
            # check that if we're using tkinter, mttkinter is installed
            is_mttkinter = any("mttkinter" in d.lower() for d in dir(tk))
            assert is_mttkinter, "mttkinter is not installed"

        _tk_per_thread.tk = tk
        _tk_roots.append(tk)

    # make sure popup window has focus (re-asserted on every dialog since the root is reused)
    tk.wm_attributes("-topmost", 1)
    tk.focus_force()

    return tk


def _drop_thread_tk_root():
    """
    Forget the current thread's cached Tk root (e.g. after a TclError) so the next dialog box attempt starts with a fresh one. The broken root stays referenced
    in _tk_roots rather than being destroyed, since destroying it may fail the same way and garbage collecting it from another thread is unsafe.
    """
    _tk_per_thread.tk = None


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
        self._in_handle = threading.local()  # re-entrancy guard (a dialog box failure that gets logged must not try to pop up another dialog box)

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

        if getattr(self._in_handle, "active", False):
            # re-entrant call on this thread (e.g. a dialog box failure reported via stderr that is redirected back into the log) - don't recurse
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
            self._in_handle.active = True
            try:
                tk = init_tkinter()
                if tk is not None:
                    self._get_message_box(record.levelno)(f"{record.name} : {record.levelname}", record.getMessage(), parent=tk)
                    if limit_reached:
                        t = "Limit Reached"
                        s = "Message box limit of %d in %.1f seconds for %s reached" % (
                            int(rate_limit["count"]),
                            float(rate_limit["time"]),
                            str(record.levelname),
                        )
                        messagebox.showinfo(t, s, parent=tk)
            except tkinter.TclError:
                # Tk/Tcl failed (e.g. "Can't find a usable init.tcl") - a dialog box must never break the application's logging call, so report via the
                # standard logging error path (stderr, subject to logging.raiseExceptions) and start fresh on the next dialog box
                _drop_thread_tk_root()
                self.handleError(record)
            finally:
                self._in_handle.active = False
