"""
Tests for the console_log_level configuration attribute. All tests in this file are AI-authored, as are its private helpers.
"""

import logging
from pathlib import Path

from balsa import Balsa, balsa_clone, __author__
from balsa.handlers import HandlerType


def _make_balsa(name: str, **kwargs) -> Balsa:
    balsa = Balsa(name, __author__, is_root=False, log_directory=Path("log", name), delete_existing_log_files=True, **kwargs)
    balsa.init_logger()
    return balsa


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_console_log_level_default():
    balsa = _make_balsa("test_console_log_level_default")
    assert balsa.handlers[HandlerType.Console].level == logging.WARNING
    balsa.remove()

    verbose_balsa = _make_balsa("test_console_log_level_default_verbose", verbose=True)
    assert verbose_balsa.handlers[HandlerType.Console].level == logging.INFO
    verbose_balsa.remove()


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_console_log_level_explicit():
    balsa = _make_balsa("test_console_log_level_explicit", console_log_level=logging.ERROR)
    assert balsa.handlers[HandlerType.Console].level == logging.ERROR
    # other handlers keep their levels
    assert balsa.handlers[HandlerType.File].level == logging.INFO
    assert balsa.handlers[HandlerType.StringList].level == logging.INFO
    balsa.remove()


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_console_log_level_overrides_verbose():
    balsa = _make_balsa("test_console_log_level_overrides_verbose", verbose=True, console_log_level=logging.ERROR)
    assert balsa.handlers[HandlerType.Console].level == logging.ERROR
    # verbose still drives everything else
    assert balsa.log.level == logging.DEBUG
    assert balsa.handlers[HandlerType.File].level == logging.DEBUG
    balsa.remove()


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_console_log_level_clone():
    parent = Balsa("test_console_log_level_clone", __author__, is_root=False, log_directory=Path("log", "test_console_log_level_clone"), console_log_level=logging.ERROR)
    parent.init_logger()
    config = parent.config_as_dict()
    assert config["console_log_level"] == logging.ERROR

    child = balsa_clone(config, "child")
    child.init_logger()
    assert child.handlers[HandlerType.Console].level == logging.ERROR

    parent.remove()
    child.remove()


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_console_log_level_clone_default():
    # None isn't in config_as_dict()'s pickle-able types so it's omitted - the clone must still get the verbose-driven default
    parent = Balsa("test_console_log_level_clone_default", __author__, is_root=False, log_directory=Path("log", "test_console_log_level_clone_default"))
    parent.init_logger()
    config = parent.config_as_dict()
    assert "console_log_level" not in config

    child = balsa_clone(config, "child")
    child.init_logger()
    assert child.console_log_level is None
    assert child.handlers[HandlerType.Console].level == logging.WARNING

    parent.remove()
    child.remove()
