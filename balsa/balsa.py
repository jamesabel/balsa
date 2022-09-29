import argparse
import os
import logging
import logging.handlers
import traceback
import sys
from typing import List, Union, Dict, Any
from pathlib import Path
from copy import deepcopy

import attr

try:
    import sentry_sdk
    import sentry_sdk.utils
    from sentry_sdk.integrations.logging import LoggingIntegration as SentryLoggingIntegration
except ImportError:
    pass

from balsa.get_logger import get_logger
from balsa.handlers import HandlerType, BalsaNullHandler, BalsaStringListHandler
from balsa.guihandler import DialogBoxHandler
from balsa.formatter import BalsaFormatter
from balsa.__version__ import __application_name__
from balsa.aws_cloudwatch_logs import AWSCloudWatchLogHandler

import appdirs
from attr import attrs, attrib

# args
verbose_arg_string = "verbose"
log_dir_arg_string = "logdir"
delete_existing_arg_string = "dellog"


log = get_logger(__application_name__)


def traceback_string():
    """
    Helper function that formats most recent traceback.  Useful when a program has an overall try/except,
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

    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level

    def write(self, buf: str):
        for line in buf.strip().splitlines():
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                self.logger.log(self.level, stripped_line)

    def flush(self):
        pass


@attrs
class Balsa(object):

    # commonly used options
    name = attrib(default=None, type=str)  # log name
    author = attrib(default=None, type=str)
    verbose = attrib(default=False, type=bool)
    gui = attrib(default=False, type=bool)
    delete_existing_log_files = attrib(default=False, type=bool)

    max_bytes = attrib(default=100 * 1e6, type=float)
    backup_count = attrib(default=3, type=int)
    error_callback = attrib(default=None)
    max_string_list_entries = attrib(default=100, type=int)

    log_directory = attrib(default=None)  # type: Union[Path, str]
    log_path = attrib(default=None, type=Path)
    log_extension = attrib(default=".log")
    log_formatter_string = attrib(default="%(asctime)s - %(name)s - %(processName)s - %(filename)s - %(lineno)s - %(funcName)s - %(levelname)s - %(message)s")
    log_console_prefix = attrib(default="")  # set to "\r" (rewrite existing line) or "\n" (new line) to avoid logs appended to current line

    handlers = attrib(default=None)
    log = attrib(default=None)
    is_root = attrib(default=True)
    propagate = attrib(default=True)  # set to False for this logger to be independent of parent(s)

    # cloud services
    # set inhibit_cloud_services to True to inhibit messages from going to cloud services (good for testing)
    inhibit_cloud_services = attrib(default=False, type=bool)

    # sentry
    use_sentry = attrib(default=False, type=bool)
    use_sentry_flask = attrib(default=False, type=bool)
    use_sentry_django = attrib(default=False, type=bool)
    use_sentry_lambda = attrib(default=False, type=bool)
    use_sentry_sqlalchemy = attrib(default=False, type=bool)
    use_sentry_celery = attrib(default=False, type=bool)

    sentry_dsn = attrib(default=None, type=str)
    # As of this writing Sentry's default is 512, but if we log a stack trace it tends to get truncated. Set to None to use the default from Sentry.
    sentry_max_string_len = attrib(default=8 * 1024)  # type: Union[int, None]
    sentry_breadcrumb_level = logging.INFO  # the Sentry default level (AKA breadcrumb level) is also INFO
    sentry_event_level = logging.ERROR  # e.g. set to logging.WARNING if you want Sentry to also notify on warnings (the Sentry default event level is also ERROR)

    # AWS CloudWatch logs
    use_aws_cloudwatch_logs = attrib(default=False, type=bool)
    aws_credentials = attrib(default=dict(), type=dict)  # kwargs that will get sent to boto3 (via AWSimple)

    instance_name = attrib(default=None, type=str)

    use_file_logging = True

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

    def init_logger_from_args(self, args: argparse.Namespace):
        """
        init logger from (specific) command line args
        :param args: args object, e.g. from argparse's parse_args()
        """
        if hasattr(args, log_dir_arg_string) and args.logdir is not None:
            self.log_directory = Path(args.logdir)
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
                self.log_directory = Path(appdirs.user_log_dir(self.name, self.author))

            if self.log_directory is not None:

                if isinstance(self.log_directory, str):
                    self.log_directory = Path(self.log_directory)

                self.log_directory.mkdir(parents=True, exist_ok=True)
                if self.delete_existing_log_files:
                    # need to glob since there are potentially many files due to the "rotating" file handler
                    for file_path in Path.glob(self.log_directory, f"*{self.log_extension}"):
                        try:
                            file_path.unlink()
                        except OSError:
                            pass

                if self.instance_name is None:
                    file_name = f"{self.name}{self.log_extension}"
                else:
                    file_name = f"{self.name}_{self.instance_name}{self.log_extension}"
                self.log_path = Path(self.log_directory, file_name)

                file_handler = logging.handlers.RotatingFileHandler(self.log_path, maxBytes=self.max_bytes, backupCount=self.backup_count)
                file_handler.setFormatter(log_formatter)
                if self.verbose:
                    file_handler.setLevel(logging.DEBUG)
                else:
                    file_handler.setLevel(logging.INFO)
                self.log.addHandler(file_handler)
                self.handlers[HandlerType.File] = file_handler
                self.log.info(f'log file path : "{self.log_path}" ("{self.log_path.absolute()}")')

        if self.gui:
            # GUI will only pop up a dialog box - it's important that GUI apps not try to output to stdout or stderr
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

            if self.sentry_max_string_len is not None:
                sentry_sdk.utils.MAX_STRING_LENGTH = self.sentry_max_string_len

            sample_rate = 0.0 if self.inhibit_cloud_services else 1.0

            sentry_logging = SentryLoggingIntegration(
                level=self.sentry_breadcrumb_level,  # Capture info and above as breadcrumbs
                event_level=self.sentry_event_level  # Send errors as events
            )

            integrations = [sentry_logging]
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
                if (sentry_dsn := self.get_sentry_dsn_via_env_var()) is None:
                    raise ValueError("Missing Sentry DSN - either set as an environmental variable or a parameter to the Balsa constructor")
                else:
                    sentry_sdk.init(
                        dsn=sentry_dsn,
                        sample_rate=sample_rate,
                        integrations=integrations,
                    )
            else:
                sentry_sdk.init(
                    dsn=self.sentry_dsn,
                    sample_rate=sample_rate,
                    integrations=integrations,
                )

        if self.use_aws_cloudwatch_logs:
            aws_cloudwatch_log_handler = AWSCloudWatchLogHandler(self.name, **self.aws_credentials)
            aws_cloudwatch_log_handler.setFormatter(log_formatter)
            aws_cloudwatch_log_handler.setLevel(logging.WARNING)
            self.log.addHandler(aws_cloudwatch_log_handler)
            self.handlers[HandlerType.AWSCloudWatch] = aws_cloudwatch_log_handler

        # error handler for callback on error or above
        # (this is last since the user may do a sys.exit() in the error callback)
        if self.error_callback is not None:
            error_callback_handler = BalsaNullHandler(self.error_callback)
            error_callback_handler.setLevel(logging.ERROR)
            self.log.addHandler(error_callback_handler)
            self.handlers[HandlerType.Callback] = error_callback_handler

        _set_global_balsa(self)

    def get_sentry_dsn_via_env_var(self) -> Union[str, None]:
        """
        Get the Sentry DSN via an environmental variable. Derived classes should override this to use a different environmental variable.
        :return: Sentry DSN or None if environmental variable not set
        """
        return os.environ.get("SENTRY_DSN")

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

    def get_log_path(self) -> Path:
        if self.instance_name is None:
            file_name = "{self.name}{self.log_extension}"
        else:
            file_name = "{self.name}_{self.instance_name}{self.log_extension}"
        log_path = Path(self.log_directory, file_name)
        return log_path

    def get_string_list(self) -> List[str]:
        """
        Get a list of strings with the most recent logs.
        :return:
        """
        return self.handlers[HandlerType.StringList].strings

    def config_as_dict(self) -> Dict[str, Any]:
        """
        Get the Balsa configuration as a dict. Useful for passing to balsa_clone().
        :return: dict of Balsa configuration
        """
        config = {}
        config_types = [bool, str, Path, int, float]  # only pickle-able types
        for k, v in attr.asdict(self).items():
            if any([isinstance(v, config_type) for config_type in config_types]):
                config[k] = v
        return config

    def remove(self):
        """
        remove all file handlers, essentially stopping all logging that's been configured by this instance
        """
        if self.log is not None:
            self.log.handlers.clear()  # removeHandler() doesn't work


def balsa_clone(config_dict: Dict[str, Any], instance_name: str, parent_instance: Balsa = None) -> Balsa:
    """
    Create another Balsa instance from a config dict and modify it with a given instance name. Note that init_logger() must still be called.

    This is particularly useful for multiprocessing since the new Process's logging subsystem is separate from the main process. The config dict is passed to the
    Process (since the config dict can be pickled) and that process can instantiate its own logger with this config. This should be done in the run() function (not in __init__() ).

    :param config_dict: config dict from the "parent" Balsa instance
    :param instance_name: unique name of the new instance
    :param parent_instance: Balsa instance (or instance of a Balsa derived class) to use to clone from. If not given, the base Balsa class itself is used.
    :return: a Balsa instance
    """

    if parent_instance is None:
        balsa_instance = Balsa()
    else:
        balsa_instance = parent_instance
    config_dict = deepcopy(config_dict)  # so we don't modify the caller's dict
    config_dict["instance_name"] = instance_name
    config_dict["delete_existing_log_files"] = False  # deletion of existing log files is only possible by the original Balsa instance since all files in the directory are removed
    new_balsa = attr.evolve(balsa_instance, **config_dict)
    return new_balsa


# will be set when Balsa initialized
_g_balsa = None  # type: Union[Balsa, None]


def _set_global_balsa(balsa: Balsa):
    """
    Set the global balsa instance.  Automatically called in Balsa.init_logger().
    :param balsa: Balsa instance
    """
    global _g_balsa
    _g_balsa = balsa


def get_global_balsa() -> Balsa:
    """
    Get the global Balsa.
    :return: global Balsa instance
    """
    if _g_balsa is None:
        raise RuntimeError("Balsa not yet initialized")
    return _g_balsa


def get_global_config() -> Dict[str, Any]:
    """
    Get the global Balsa configuration for this process.
    :return: dict with Balsa config
    """
    global_balsa = get_global_balsa()
    return global_balsa.config_as_dict()
