
import os
import shutil
import logging
import logging.handlers
import traceback
import raven
from raven.handlers.logging import SentryHandler

from balsa import HandlerType, BalsaNullHandler, DialogBoxHandler, BalsaStringListHandler


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


def traceback_string():
    """
    Helper function that formats most recent traceback.  Useful when a program has an overall try/except
    and it wants to output the program trace to the log.
    :return: formatted traceback string (or None if no traceback available)
    """
    tb_string = None
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    if exc_type is not None:
        display_lines_list = [str(exc_value)] + traceback.format_tb(exc_traceback)
        tb_string = '\n'.join(display_lines_list)
    return tb_string


@attrs
class Balsa(object):

    # commonly used options
    name = attrib(default=None)  # even if this is root, use the name for the log file name
    author = attrib(default=None)
    verbose = attrib(default=False)
    gui = attrib(default=False)
    delete_existing_log_files = attrib(default=False)

    max_bytes = attrib(default=100*1E6)
    backup_count = attrib(default=3)
    error_callback = attrib(default=None)
    max_string_list_entries = attrib(default=100)
    log_directory = attrib(default=None)
    log_path = attrib(default=None)
    log_formatter = attrib(default=logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(lineno)s - %(funcName)s - %(levelname)s - %(message)s'))
    handlers = attrib(default=None)
    log = attrib(default=None)
    is_root = attrib(default=False)
    propagate = attrib(default=True)  # set to False for this logger to be independent of parent(s)
    rate_limit_count = attrib(default=2)
    rate_limit_time = attrib(default=10.0)

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
        if self.is_root:
            self.log = logging.getLogger()
        else:
            self.log = logging.getLogger(self.name)
        if not self.propagate:
            self.log.propagate = False

        # set the root log level
        if self.verbose:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

        if self.log.hasHandlers():
            self.log.info('Logger already initialized.')

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
            self.log.addHandler(file_handler)
            self.handlers[HandlerType.File] = file_handler
            self.log.info('log file path : "%s" ("%s")' % (self.log_path, os.path.abspath(self.log_path)))

        if self.gui:
            # GUI will only pop up a dialog box - it's important that GUI not try to output to stdout or stderr
            # since that would likely cause a permissions error.
            dialog_box_handler = DialogBoxHandler(self.rate_limit_count, self.rate_limit_time)
            if self.verbose:
                dialog_box_handler.setLevel(logging.WARNING)
            else:
                dialog_box_handler.setLevel(logging.ERROR)
            self.log.addHandler(dialog_box_handler)
            self.handlers[HandlerType.DialogBox] = dialog_box_handler
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.log_formatter)
            if self.verbose:
                console_handler.setLevel(logging.INFO)
            else:
                console_handler.setLevel(logging.WARNING)
            self.log.addHandler(console_handler)
            self.handlers[HandlerType.Console] = console_handler

        # error handler for callback on error or above
        if self.error_callback is not None:
            error_callback_handler = BalsaNullHandler(self.error_callback)
            error_callback_handler.setLevel(logging.ERROR)
            self.log.addHandler(error_callback_handler)
            self.handlers[HandlerType.Callback] = error_callback_handler

        string_list_handler = BalsaStringListHandler(self.max_string_list_entries)
        string_list_handler.setFormatter(self.log_formatter)
        string_list_handler.setLevel(logging.INFO)
        self.log.addHandler(string_list_handler)
        self.handlers[HandlerType.StringList] = string_list_handler

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
            self.log.addHandler(sentry_handler)

    def get_string_list(self):
        return self.handlers[HandlerType.StringList].strings
