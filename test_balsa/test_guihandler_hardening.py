import logging
import tkinter

from ismain import is_main

from balsa import guihandler
from balsa.guihandler import DialogBoxHandler

big_number = int(1e6)
no_rate_limits = {logging.ERROR: {"count": big_number, "time": 0.0}}


def make_error_record(message: str) -> logging.LogRecord:
    return logging.LogRecord(name="tst_guihandler", level=logging.ERROR, pathname=__file__, lineno=1, msg=message, args=(), exc_info=None)


def reset_thread_tk_root():
    # forget this thread's persistent Tk root so each test observes Tk creation deterministically
    guihandler._tk_per_thread.tk = None


# Test created by AI (Claude Code)
def test_tk_root_reused_across_dialogs(monkeypatch):
    reset_thread_tk_root()

    created = []
    real_tk = guihandler.tkinter.Tk

    def counting_tk(*args, **kwargs):
        created.append(1)
        return real_tk(*args, **kwargs)

    shown = []
    monkeypatch.setattr(guihandler.tkinter, "Tk", counting_tk)
    monkeypatch.setattr(guihandler.messagebox, "showerror", lambda *args, **kwargs: shown.append(args))

    handler = DialogBoxHandler(no_rate_limits)
    handler.handle(make_error_record("first"))
    handler.handle(make_error_record("second"))

    assert len(shown) == 2
    assert len(created) == 1  # one persistent Tk root per thread, not one per dialog


# Test created by AI (Claude Code)
def test_tcl_error_does_not_break_logging(monkeypatch):
    reset_thread_tk_root()

    def failing_tk(*args, **kwargs):
        raise tkinter.TclError("Can't find a usable init.tcl in the following directories:")

    handle_errors = []
    handler = DialogBoxHandler(no_rate_limits)
    monkeypatch.setattr(guihandler.tkinter, "Tk", failing_tk)
    monkeypatch.setattr(handler, "handleError", lambda record: handle_errors.append(record))

    handler.handle(make_error_record("tcl failure"))  # must not raise into the application's logging call

    assert len(handle_errors) == 1
    assert getattr(guihandler._tk_per_thread, "tk", None) is None  # broken root dropped so the next dialog starts fresh


# Test created by AI (Claude Code)
def test_recovery_after_tcl_error(monkeypatch):
    reset_thread_tk_root()

    handler = DialogBoxHandler(no_rate_limits)

    def failing_tk(*args, **kwargs):
        raise tkinter.TclError("simulated Tcl failure")

    with monkeypatch.context() as failure_context:
        failure_context.setattr(guihandler.tkinter, "Tk", failing_tk)
        failure_context.setattr(handler, "handleError", lambda record: None)
        handler.handle(make_error_record("fails"))

    # Tk works again - the handler must recover with a fresh root
    shown = []
    monkeypatch.setattr(guihandler.messagebox, "showerror", lambda *args, **kwargs: shown.append(args))
    handler.handle(make_error_record("recovers"))

    assert len(shown) == 1
    assert getattr(guihandler._tk_per_thread, "tk", None) is not None


# Test created by AI (Claude Code)
def test_no_recursive_dialogs(monkeypatch):
    reset_thread_tk_root()

    handler = DialogBoxHandler(no_rate_limits)
    calls = []

    def reentrant_showerror(*args, **kwargs):
        calls.append(args)
        handler.handle(make_error_record("re-entrant"))  # e.g. a failure inside dialog display that gets logged back through this handler

    monkeypatch.setattr(guihandler.messagebox, "showerror", reentrant_showerror)
    handler.handle(make_error_record("outer"))

    assert len(calls) == 1  # the re-entrant call must not pop up another dialog


if is_main():
    print("run via pytest (uses monkeypatch)")
