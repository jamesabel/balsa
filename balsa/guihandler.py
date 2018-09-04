
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
    def handle(self, record):
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
