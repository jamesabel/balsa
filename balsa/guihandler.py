
import time
import logging

tkinter_present = None
pyqt_present = None

try:
    # embedded Python does not have tkinter
    import tkinter
    from tkinter.simpledialog import messagebox
    from mttkinter import mtTkinter  # merely importing this puts it in use (do not delete even though it seems to not be used)
    tkinter_present = True
except ModuleNotFoundError:
    tkinter_present = False

if not tkinter_present:
    # no tkinter - try PyQt
    try:
        import PyQt5
        pyqt_present = True
    except ModuleNotFoundError:
        pyqt_present = False


class DialogBoxHandler(logging.NullHandler):
    """
    For GUI apps, display an error message dialog box.  Uses the built-in tkinter module so we don't have any
    special package dependencies.
    """

    def __init__(self, rate_limit_count, rate_limit_time):
        """
        :param rate_limit_count: maximum number of dialog boxes that pop up
        :param rate_limit_time: within this time (in seconds)
        """
        self.rate_limit_count = rate_limit_count
        self.rate_limit_time = rate_limit_time

        self.count = None
        self.start_display_time_window = None

        super().__init__()

    def handle(self, record):
        now = time.time()
        if self.start_display_time_window is None or now - self.start_display_time_window > self.rate_limit_time:
            self.count = 0
            self.start_display_time_window = now
        if self.count < self.rate_limit_count:
            if tkinter_present:
                boxes = {
                    logging.INFO: messagebox.showinfo,
                    logging.WARNING: messagebox.showwarning,
                    logging.ERROR: messagebox.showerror,
                    logging.CRITICAL: messagebox.showerror  # Tk doesn't go any higher than error
                }
                tk = tkinter.Tk()
                tk.withdraw()  # don't show the 'main' Tk window
                boxes[record.levelno]('%s : %s' % (record.name, record.levelname), record.msg, parent=tk)
            elif pyqt_present:
                boxes = {
                    logging.INFO: PyQt5.QMessageBox.info,
                    logging.WARNING: PyQt5.QMessageBox.warning,
                    logging.ERROR: PyQt5.QMessageBox.error,
                    logging.CRITICAL: PyQt5.QMessageBox.fatal
                }
                boxes[record.levelno](self, record.levelname, record.msg)
            self.count += 1
            if self.count == self.rate_limit_count:
                t = 'Limit Reached'
                s = f'Message box limit of {self.rate_limit_count} in {self.rate_limit_time} seconds reached'
                if tkinter_present:
                    tk = tkinter.Tk()
                    tk.withdraw()  # don't show the 'main' Tk window
                    messagebox.showinfo(t, s, parent=tk)
                elif pyqt_present:
                    PyQt5.QMessageBox.info(self, t, s)

