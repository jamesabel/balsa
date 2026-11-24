"""
Balsa's Sentry setup for both supported Sentry SDK major versions (2.x and 3.x), which configure log handling differently.

The "sdk_2" / "sdk_3" tests fake the SDK version and spy on the logging integration, so both code paths are tested whichever SDK is installed. The
"installed_sdk" tests use the real logging integration and the real sentry_sdk.init() signature, so they check what Balsa passes against the SDK that is actually
installed. No test here touches the network: sentry_sdk.init is always replaced with a spy.

All tests in this file are AI-authored (Claude Code); the private helpers and constants below are covered by this note.
"""

import inspect
import logging

import pytest
import sentry_sdk
import sentry_sdk.consts

from balsa import balsa_dev_env_var

from .tst_balsa import TstCLIBalsa

fake_sentry_dsn = "https://0123456789abcdef0123456789abcdef@o0.ingest.sentry.io/0"


def _spy_sentry_init(monkeypatch) -> list:
    """
    Replace sentry_sdk.init with a spy.
    :return: list of kwargs dicts, one per sentry_sdk.init call
    """
    init_calls: list = []
    monkeypatch.setattr(sentry_sdk, "init", lambda *args, **kwargs: init_calls.append(kwargs))
    return init_calls


def _spy_logging_integration(monkeypatch) -> list:
    """
    Replace the Sentry logging integration that Balsa instantiates with a spy.
    :return: list of kwargs dicts, one per instantiation
    """
    integration_calls: list = []

    def fake_logging_integration(**kwargs):
        integration_calls.append(kwargs)
        return object()

    monkeypatch.setattr("balsa.balsa.SentryLoggingIntegration", fake_logging_integration)
    return integration_calls


def _installed_sdk_major_version() -> int:
    return int(sentry_sdk.VERSION.split(".")[0])


def _init_balsa_with_sentry(application_name: str, use_sentry_logs: bool) -> None:
    balsa = TstCLIBalsa(application_name)
    balsa.use_sentry = True
    balsa.use_sentry_logs = use_sentry_logs
    balsa.sentry_dsn = fake_sentry_dsn
    balsa.sentry_breadcrumb_level = logging.DEBUG
    balsa.sentry_event_level = logging.CRITICAL
    balsa.sentry_logs_level = logging.WARNING
    balsa.init_logger()
    balsa.remove()


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
@pytest.mark.parametrize("use_sentry_logs", [False, True])
def test_sentry_sdk_2(monkeypatch, use_sentry_logs):
    # sentry-sdk 2.x: "level" is the breadcrumb level, and structured logs are turned on with sentry_logs_level and the enable_logs option
    monkeypatch.delenv(balsa_dev_env_var, raising=False)
    monkeypatch.setattr(sentry_sdk, "VERSION", "2.76.0")
    init_calls = _spy_sentry_init(monkeypatch)
    integration_calls = _spy_logging_integration(monkeypatch)

    _init_balsa_with_sentry(f"test_sentry_sdk_2_{use_sentry_logs}", use_sentry_logs)

    expected_integration_kwargs = {"level": logging.DEBUG, "event_level": logging.CRITICAL}
    if use_sentry_logs:
        expected_integration_kwargs["sentry_logs_level"] = logging.WARNING
    assert integration_calls == [expected_integration_kwargs]
    assert len(init_calls) == 1
    assert init_calls[0].get("enable_logs") is (True if use_sentry_logs else None)


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
@pytest.mark.parametrize("use_sentry_logs", [False, True])
def test_sentry_sdk_3(monkeypatch, use_sentry_logs):
    # sentry-sdk 3.x: "level" is the structured logs level (None is off), breadcrumbs have their own parameter and there is no enable_logs option
    monkeypatch.delenv(balsa_dev_env_var, raising=False)
    monkeypatch.setattr(sentry_sdk, "VERSION", "3.0.0")
    init_calls = _spy_sentry_init(monkeypatch)
    integration_calls = _spy_logging_integration(monkeypatch)

    _init_balsa_with_sentry(f"test_sentry_sdk_3_{use_sentry_logs}", use_sentry_logs)

    assert integration_calls == [{"level": logging.WARNING if use_sentry_logs else None, "event_level": logging.CRITICAL, "breadcrumb_level": logging.DEBUG}]
    assert len(init_calls) == 1
    assert "enable_logs" not in init_calls[0]  # sentry_sdk.init() of 3.x raises TypeError on this option


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
@pytest.mark.parametrize("use_sentry_logs", [False, True])
def test_sentry_installed_sdk_accepts_balsa_options(monkeypatch, use_sentry_logs):
    # the real logging integration is instantiated (it raises TypeError on a parameter it does not have), and every option Balsa passes to sentry_sdk.init() must be
    # one the installed SDK knows
    monkeypatch.delenv(balsa_dev_env_var, raising=False)
    init_calls = _spy_sentry_init(monkeypatch)

    _init_balsa_with_sentry(f"test_sentry_installed_sdk_accepts_balsa_options_{use_sentry_logs}", use_sentry_logs)

    assert len(init_calls) == 1
    known_options = set(inspect.signature(sentry_sdk.consts.ClientConstructor.__init__).parameters)
    assert set(init_calls[0]) <= known_options


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
@pytest.mark.parametrize("use_sentry_logs", [False, True])
def test_sentry_installed_sdk_log_levels(monkeypatch, use_sentry_logs):
    # Balsa's Sentry levels end up on the installed SDK's logging integration (its handlers are private attributes, named differently in 2.x and 3.x)
    monkeypatch.delenv(balsa_dev_env_var, raising=False)
    init_calls = _spy_sentry_init(monkeypatch)

    _init_balsa_with_sentry(f"test_sentry_installed_sdk_log_levels_{use_sentry_logs}", use_sentry_logs)

    logging_integration = init_calls[0]["integrations"][0]
    if _installed_sdk_major_version() >= 3:
        assert logging_integration._event_handler.level == logging.CRITICAL
        assert logging_integration._breadcrumb_handler.level == logging.DEBUG
        if use_sentry_logs:
            assert logging_integration._logs_handler.level == logging.WARNING
        else:
            assert logging_integration._logs_handler is None  # structured logs are off
    else:
        assert logging_integration._handler.level == logging.CRITICAL
        assert logging_integration._breadcrumb_handler.level == logging.DEBUG
        if use_sentry_logs:
            assert logging_integration._sentry_logs_handler.level == logging.WARNING
            assert init_calls[0]["enable_logs"] is True
        else:
            assert "enable_logs" not in init_calls[0]  # structured logs are off
