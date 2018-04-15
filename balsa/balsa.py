
import os
import shutil
from enum import Enum, auto
import logging
import logging.handlers

import tkinter
from tkinter.simpledialog import messagebox

import appdirs


def get_logger(name):
    """
    Special get_logger.  Typically name is the name of the application using Balsa.
    :param name: name of the logger to get, which is usually the application name. Optionally it can be a python file
    name or path (e.g. __file__).
    :return: the logger for the logger name
    """

    # if name is a python file, or a path to a python file, extract the module name
    if name.endswith('.py'):
        name = name[:-3]
        if os.sep in name:
            name = name.split(os.sep)[-1]

    return logging.getLogger(name)


class HandlerType(Enum):
    Console = auto()
    File = auto()
    DialogBox = auto()
    Callback = auto()


class BalsaNullHandler(logging.NullHandler):
    """
    Hook in a callback function.  For example, this can be used to set the process return code to an error state.
    """
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def handle(self, record):
        # make sure this handler level instance is set to the level we want to deem an error - e.g. logging.ERROR
        self._callback(record)


class DialogBoxHandler(logging.NullHandler):
    """
    For GUI apps, display an error message dialog box.  Uses the built-in tkinter module so we don't have any
    special package dependencies.
    """
    def handle(self, record):
        boxes = {logging.INFO: messagebox.showinfo,
                 logging.WARNING: messagebox.showwarning,
                 logging.ERROR: messagebox.showerror,
                 logging.CRITICAL: messagebox.showerror  # Tk doesn't go any higher than error
                 }
        tk = tkinter.Tk()
        tk.withdraw()  # don't show the 'main' Tk window
        boxes[record.levelno](f'{record.name} : {record.levelname}', "{:<40}".format(record.msg))


class Balsa:
    def __init__(self, name, author, log_directory=None, use_app_dirs=False, verbose=False,
                 delete_existing_log_files=False, error_callback=None, gui=False):
        """
        :param name: name of the application being logged
        :param author: name of the author of the application being logged
        :param log_directory: directory where the log files will be written.
        :param use_app_dirs: True to use the appdirs package to determine the log directory
        :param verbose: sets the log levels to more verbose level
        :param delete_existing_log_files: True to delete all files in log directory
        # set max_bytes and backup_count both to 0 for one big file
        :param error_callback: callback function on error or above
        :param gui: set to True for GUI messages
        """
        self.name = name
        self.author = author
        self.log_directory = log_directory
        self.use_app_dirs = use_app_dirs
        self.verbose = verbose
        self.delete_existing_log_files = delete_existing_log_files
        self.error_callback = error_callback
        self.gui = gui

        self.log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(lineno)s - %(funcName)s - %(levelname)s - %(message)s')

        # File log settings.  These can be changed prior to calling init_logger()
        self.max_bytes = 100*1E6
        self.backup_count = 3

        self.handlers = {}
        self.root_log = None

    def init_logger(self):
        """
        Initialize the logger.  Call exactly once.
        :return: an instance of the logger
        """

        self.root_log = logging.getLogger()  # we init the root logger so all child loggers inherit this functionality

        if self.root_log.hasHandlers():
            self.root_log.error('Logger already initialized.')
            return self.root_log

        # set the root log level
        if self.verbose:
            self.root_log.setLevel(logging.DEBUG)
        else:
            self.root_log.setLevel(logging.INFO)

        if self.gui:
            # GUI will only pop up a dialog box - it's important that GUI not try to output to stdout or stderr
            # since that would likely cause a permissions error.
            dialog_box_handler = DialogBoxHandler()
            if self.verbose:
                dialog_box_handler.setLevel(logging.WARNING)
            else:
                dialog_box_handler.setLevel(logging.ERROR)
            self.root_log.addHandler(dialog_box_handler)
            self.handlers[HandlerType.DialogBox] = dialog_box_handler
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.log_formatter)
            if self.verbose:
                console_handler.setLevel(logging.INFO)
            else:
                console_handler.setLevel(logging.WARNING)
            self.root_log.addHandler(console_handler)
            self.handlers[HandlerType.DialogBox.Console] = console_handler

        # create file handler
        if self.use_app_dirs:
            self.log_directory = appdirs.user_log_dir(self.name, self.author)
        if self.log_directory is not None:
            if self.delete_existing_log_files:
                shutil.rmtree(self.log_directory, ignore_errors=True)
            os.makedirs(self.log_directory, exist_ok=True)
            fh_path = os.path.join(self.log_directory, '%s.log' % self.name)
            file_handler = logging.handlers.RotatingFileHandler(fh_path, maxBytes=self.max_bytes, backupCount=self.backup_count)
            file_handler.setFormatter(self.log_formatter)
            if self.verbose:
                file_handler.setLevel(logging.DEBUG)
            else:
                file_handler.setLevel(logging.INFO)
            self.root_log.addHandler(file_handler)
            self.handlers[HandlerType.File] = file_handler
            self.root_log.info('log file path : "%s" ("%s")' % (fh_path, os.path.abspath(fh_path)))

        # error handler for callback on error or above
        if self.error_callback is not None:
            error_callback_handler = BalsaNullHandler(self.error_callback)
            error_callback_handler.setLevel(logging.ERROR)
            self.root_log.addHandler(error_callback_handler)
            self.handlers[HandlerType.Callback] = error_callback_handler
