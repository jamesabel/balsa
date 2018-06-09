
import os
import shutil
from enum import Enum
import logging
import logging.handlers
import raven
from raven.handlers.logging import SentryHandler

import tkinter
from tkinter.simpledialog import messagebox
from mttkinter import mtTkinter  # merely importing this puts it in use (do not delete even though it seems to not be used)

import appdirs
from attr import attrs, attrib

# args
verbose_arg_string = 'verbose'
log_dir_arg_string = 'logdir'
delete_existing_arg_string = 'dellog'


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
    Console = 1
    File = 2
    DialogBox = 3
    Callback = 4
    Sentry = 5


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
        boxes[record.levelno]('%s : %s' % (record.name, record.levelname), record.msg)


@attrs
class Balsa(object):

    # commonly used options
    name = attrib()
    author = attrib()
    verbose = attrib(default=False)
    gui = attrib(default=False)
    delete_existing_log_files = attrib(default=False)

    max_bytes = attrib(default=100*1E6)
    backup_count = attrib(default=3)
    error_callback = attrib(default=None)
    log_directory = attrib(default=None)
    log_path = attrib(default=None)
    log_formatter = attrib(default=logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(lineno)s - %(funcName)s - %(levelname)s - %(message)s'))
    handlers = attrib(default=None)
    root_log = attrib(default=None)

    # cloud services
    # set inhibit_cloud_services to True to inhibit messages from going to cloud services (good for testing)
    inhibit_cloud_services = attrib(default=False)

    # sentry
    use_sentry = attrib(default=False)
    sentry_client = attrib(default=None)
    sentry_dsn = attrib(default=None)

    def init_logger_from_args(self, args):
        """
        init logger from (specific) command line args
        :param args: args object, e.g. from argparse's parse_args()
        """
        if hasattr(args, log_dir_arg_string) and args.logdir is not None:
            self.log_directory = args.logdir
        if hasattr(args, verbose_arg_string) and args.verbose is True:
            self.verbose = True
        if hasattr(args, delete_existing_arg_string) and args.dellog is True:
            self.delete_existing_log_files = True
        self.init_logger()

    def init_logger(self):
        """
        Initialize the logger.  Call exactly once.
        """
        self.handlers = {}
        self.root_log = logging.getLogger()  # we init the root logger so all child loggers inherit this functionality

        # set the root log level
        if self.verbose:
            self.root_log.setLevel(logging.DEBUG)
        else:
            self.root_log.setLevel(logging.INFO)

        if self.root_log.hasHandlers():
            self.root_log.info('Logger already initialized.')

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
            self.handlers[HandlerType.Console] = console_handler

        # create file handler
        if self.log_directory is None:
            self.log_directory = appdirs.user_log_dir(self.name, self.author)
        if self.log_directory is not None:
            if self.delete_existing_log_files:
                shutil.rmtree(self.log_directory, ignore_errors=True)
            os.makedirs(self.log_directory, exist_ok=True)
            self.log_path = os.path.join(self.log_directory, '%s.log' % self.name)
            file_handler = logging.handlers.RotatingFileHandler(self.log_path, maxBytes=self.max_bytes, backupCount=self.backup_count)
            file_handler.setFormatter(self.log_formatter)
            if self.verbose:
                file_handler.setLevel(logging.DEBUG)
            else:
                file_handler.setLevel(logging.INFO)
            self.root_log.addHandler(file_handler)
            self.handlers[HandlerType.File] = file_handler
            self.root_log.info('log file path : "%s" ("%s")' % (self.log_path, os.path.abspath(self.log_path)))

        # error handler for callback on error or above
        if self.error_callback is not None:
            error_callback_handler = BalsaNullHandler(self.error_callback)
            error_callback_handler.setLevel(logging.ERROR)
            self.root_log.addHandler(error_callback_handler)
            self.handlers[HandlerType.Callback] = error_callback_handler

        # setting up Sentry error handling
        # For the Client to work you need a SENTRY_DSN environmental variable set, or one must be provided.
        if self.use_sentry:
            sample_rate = 0.0 if self.inhibit_cloud_services else 1.0
            if self.sentry_dsn is None:
                self.sentry_client = raven.Client(
                    sample_rate=sample_rate,
                )
            else:
                self.sentry_client = raven.Client(
                    dsn=self.sentry_dsn,
                    sample_rate=sample_rate,
                )

            sentry_handler = SentryHandler(self.sentry_client)
            sentry_handler.setLevel(logging.ERROR)
            self.handlers[HandlerType.Sentry] = sentry_handler
            self.root_log.addHandler(sentry_handler)
