
import os
import shutil
import logging
import logging.handlers

import tkinter
from tkinter.simpledialog import messagebox

import appdirs

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(lineno)s - %(funcName)s - %(levelname)s - %(message)s')


def get_logger(name):
    """
    special "get logger" where you can pass in __file__ and it extracts the module name
    :param name: name of the logger to get, optionally as a python file path
    :return: a logger
    """

    # if name is a python file, or a path to a python file, extract the module name
    if os.sep in name:
        name = name.split(os.sep)[-1]
    if name.endswith('.py'):
        name = name[:-3]

    return logging.getLogger(name)


class ErrorSetHandler(logging.NullHandler):
    """
    Callback function is called when we get an error or above.  This can be used to set the return code
    to an error state.
    """
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def handle(self, record):
        # make sure this handler level instance is set to the level we want to deem an error - e.g. logging.ERROR
        self._callback(record)


class DialogBoxHandler(logging.NullHandler):
    def handle(self, record):
        boxes = {logging.INFO: messagebox.showinfo,
                 logging.WARNING: messagebox.showwarning,
                 logging.ERROR: messagebox.showerror,
                 logging.CRITICAL: messagebox.showerror  # Tk doesn't go any higher than error
                 }
        tk = tkinter.Tk()
        tk.withdraw()  # don't show the 'main' Tk window
        boxes[record.levelno](f'{record.name} : {record.levelname}', "{:<40}".format(record.msg))


def init_logger(name, author, log_directory=None, use_app_dirs=False, verbose=False, delete_existing_log_files=False,
                max_bytes=100*1E6, backup_count=3, error_callback=None, gui=False):
    """
    Initialize the logger.  Call once from the application 'main'.
    :param name: name of the application being logged
    :param author: name of the author of the applicatio being logged
    :param log_directory: directory where the log files will be written.
    :param use_app_dirs: True to use the appdirs package to determine the log directory
    :param verbose: sets the log levels to more verbose level
    :param delete_existing_log_files: True to delete all files in log directory
    # set max_bytes and backup_count both to 0 for one big file
    :param max_bytes: max log file size (0 for no limit)
    :param backup_count: number of log files in rotation (0 for one file)
    :param error_callback: callback function on error or above
    :param gui: set to True for GUI messages
    :return: an instance of the logger and a dict with the handlers (in case the user wants to change the levels)
    """

    log = logging.getLogger()  # we init the root logger so all child loggers inherit this functionality
    handlers = {}

    if log.hasHandlers():
        log.warning('logger already initialized')
        return log

    # set the root log level
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if gui:
        dialog_box_handler = DialogBoxHandler()
        if verbose:
            dialog_box_handler.setLevel(logging.WARNING)
        else:
            dialog_box_handler.setLevel(logging.ERROR)
        log.addHandler(dialog_box_handler)
        handlers['dialog'] = dialog_box_handler
    else:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        if verbose:
            console_handler.setLevel(logging.INFO)
        else:
            console_handler.setLevel(logging.WARNING)
        log.addHandler(console_handler)
        handlers['console'] = console_handler

    # create file handler
    if use_app_dirs:
        log_directory = appdirs.user_log_dir(name, author)
    if log_directory is not None or use_app_dirs:
        if delete_existing_log_files:
            shutil.rmtree(log_directory, ignore_errors=True)
        os.makedirs(log_directory, exist_ok=True)
        fh_path = os.path.join(log_directory, '%s.log' % name)
        file_handler = logging.handlers.RotatingFileHandler(fh_path, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(log_formatter)
        if verbose:
            file_handler.setLevel(logging.DEBUG)
        else:
            file_handler.setLevel(logging.INFO)
        log.addHandler(file_handler)
        handlers['file'] = file_handler
        log.info('log file path : "%s" ("%s")' % (fh_path, os.path.abspath(fh_path)))

    # error handler for callback on error or above
    if error_callback is not None:
        error_handler = ErrorSetHandler(error_callback)
        error_handler.setLevel(logging.ERROR)
        log.addHandler(error_handler)
        handlers['error'] = error_handler

    return log, handlers
