import os
from glob import glob
import logging
import logging.handlers
import traceback
import sys

import sentry_sdk

from balsa import HandlerType, BalsaNullHandler, DialogBoxHandler, BalsaStringListHandler, BalsaFormatter

import appdirs
from attr import attrs, attrib

# args
verbose_arg_string = "verbose"
log_dir_arg_string = "logdir"
delete_existing_arg_string = "dellog"


def get_logger(name):
    """
    Special get_logger.  Typically name is the name of the application using Balsa.
    :param name: name of the logger to get, which is usually the application name. Optionally it can be a python file
    name or path (e.g. __file__).
    :return: the logger for the logger name
    """

    # if name is a python file, or a path to a python file, extract the module name
    if name.endswith(".py"):
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
        tb_string = "\n".join(display_lines_list)
    return tb_string


class StreamToLogger:
    """
    Fake file-like stream object that redirects writes to a logger instance, useful for stdout and stderr.
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, buf):
        for line in buf.strip().splitlines():
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                self.logger.log(self.level, stripped_line)

    def flush(self):
        self.logger.flush()


@attrs
class Balsa(object):

    # commonly used options
    name = attrib(default=None)  # even if this is root, use the name for the log file name
    author = attrib(default=None)
    verbose = attrib(default=False)
    gui = attrib(default=False)
    delete_existing_log_files = attrib(default=False)

    max_bytes = attrib(default=100 * 1e6)
    backup_count = attrib(default=3)
    error_callback = attrib(default=None)
    max_string_list_entries = attrib(default=100)

    use_file_logging = True
    log_directory = attrib(default=None)
    log_path = attrib(default=None)
    log_extension = attrib(default=".log")
    log_formatter_string = attrib(default="%(asctime)s - %(name)s - %(filename)s - %(lineno)s - %(funcName)s - %(levelname)s - %(message)s")
    log_console_prefix = attrib(default="")  # set to "\r" (rewrite existing line) or "\n" (new line) to avoid logs appended to current line

    handlers = attrib(default=None)
    log = attrib(default=None)
    is_root = attrib(default=True)
    propagate = attrib(default=True)  # set to False for this logger to be independent of parent(s)

    # cloud services
    # set inhibit_cloud_services to True to inhibit messages from going to cloud services (good for testing)
    inhibit_cloud_services = attrib(default=False)

    # sentry
    use_sentry = attrib(default=False)
    use_sentry_flask = attrib(default=False)
    use_sentry_django = attrib(default=False)
    use_sentry_lambda = attrib(default=False)
    use_sentry_sqlalchemy = attrib(default=False)
    use_sentry_celery = attrib(default=False)

    sentry_client = attrib(default=None)
    sentry_dsn = attrib(default=None)

    # a separate rate limit for each level
    rate_limits = attrib(
        default={
            level: {"count": 2, "time": 60.0}
            for level in [
                logging.CRITICAL,
                logging.ERROR,
                logging.WARNING,
                logging.INFO,
                logging.DEBUG,
                logging.NOTSET,
            ]
        }
    )

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

        log_formatter = BalsaFormatter(self.log_formatter_string)

        assert self.name is not None
        assert self.author is not None
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
            self.log.info("Logger already initialized.")

        # use turn off file logging, e.g. for cloud environments where it's not recommended and/or possible to write to the local file system
        if self.use_file_logging:
            # create file handler
            if self.log_directory is None:
                self.log_directory = appdirs.user_log_dir(self.name, self.author)
            if self.log_directory is not None:
                if self.delete_existing_log_files:
                    for file_path in glob(os.path.join(self.log_directory, "*%s" % self.log_extension)):
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass
                os.makedirs(self.log_directory, exist_ok=True)
                self.log_path = os.path.join(self.log_directory, "%s%s" % (self.name, self.log_extension))
                file_handler = logging.handlers.RotatingFileHandler(self.log_path, maxBytes=self.max_bytes, backupCount=self.backup_count)
                file_handler.setFormatter(log_formatter)
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
            dialog_box_handler = DialogBoxHandler(self.rate_limits)
            if self.verbose:
                dialog_box_handler.setLevel(logging.WARNING)
            else:
                dialog_box_handler.setLevel(logging.ERROR)
            self.log.addHandler(dialog_box_handler)
            self.handlers[HandlerType.DialogBox] = dialog_box_handler

            self.set_std()  # redirect stdout and stderr to log
        else:
            console_handler = logging.StreamHandler()
            # prefix for things like "\n" or "\r"
            console_handler.setFormatter(BalsaFormatter(f"{self.log_console_prefix}{self.log_formatter_string}"))
            if self.verbose:
                console_handler.setLevel(logging.INFO)
            else:
                console_handler.setLevel(logging.WARNING)
            self.log.addHandler(console_handler)
            self.handlers[HandlerType.Console] = console_handler

        string_list_handler = BalsaStringListHandler(self.max_string_list_entries)
        string_list_handler.setFormatter(log_formatter)
        string_list_handler.setLevel(logging.INFO)
        self.log.addHandler(string_list_handler)
        self.handlers[HandlerType.StringList] = string_list_handler

        # setting up Sentry error handling
        # For the Client to work you need a SENTRY_DSN environmental variable set, or one must be provided.
        if self.use_sentry:
            sample_rate = 0.0 if self.inhibit_cloud_services else 1.0
            integrations = []
            if self.use_sentry_django:
                from sentry_sdk.integrations.django import DjangoIntegration

                integrations.append(DjangoIntegration())
            if self.use_sentry_flask:
                from sentry_sdk.integrations.flask import FlaskIntegration

                integrations.append(FlaskIntegration())
            if self.use_sentry_lambda:
                from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

                integrations.append(AwsLambdaIntegration())
            if self.use_sentry_sqlalchemy:
                from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

                integrations.append(SqlalchemyIntegration())
            if self.use_sentry_celery:
                from sentry_sdk.integrations.celery import CeleryIntegration

                integrations.append(CeleryIntegration())

            if self.sentry_dsn is None:
                if "SENTRY_DSN" not in os.environ:
                    raise ValueError("Missing sentry_dsn")
                else:
                    sentry_sdk.init(
                        dsn=os.environ["SENTRY_DSN"],
                        sample_rate=sample_rate,
                        integrations=integrations,
                    )
            else:
                sentry_sdk.init(
                    dsn=self.sentry_dsn,
                    sample_rate=sample_rate,
                    integrations=integrations,
                )

        # error handler for callback on error or above
        # (this is last since the user may do a sys.exit() in the error callback)
        if self.error_callback is not None:
            error_callback_handler = BalsaNullHandler(self.error_callback)
            error_callback_handler.setLevel(logging.ERROR)
            self.log.addHandler(error_callback_handler)
            self.handlers[HandlerType.Callback] = error_callback_handler

    def set_std(self):
        """
        Send stdout and stderr to logs. Generally used for GUI apps since GUI apps should not write to stdout or stderr. Derived classes can override this method to choose a
        different set of levels (or just "pass" to avoid the redirect completely).
        """
        if self.verbose:
            sys.stdout = StreamToLogger(self.log, logging.WARNING)
            sys.stderr = StreamToLogger(self.log, logging.WARNING)
        else:
            sys.stdout = StreamToLogger(self.log, logging.INFO)
            sys.stderr = StreamToLogger(self.log, logging.INFO)

    def get_string_list(self):
        return self.handlers[HandlerType.StringList].strings
