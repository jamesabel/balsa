import logging
import os

import sentry_sdk

from balsa import get_logger, balsa_dev_env_var

from .tst_balsa import TstCLIBalsa

fake_sentry_dsn = "https://0123456789abcdef0123456789abcdef@o0.ingest.sentry.io/0"


def _spy_sentry_init(monkeypatch) -> list:
    """
    Replace sentry_sdk.init with a spy so tests can assert whether Sentry was initialized, without any network access.
    :return: list of kwargs dicts, one per sentry_sdk.init call
    """
    init_calls = []
    monkeypatch.setattr(sentry_sdk, "init", lambda *args, **kwargs: init_calls.append(kwargs))
    return init_calls


def test_balsa_sentry():
    application_name = "test_balsa_sentry"

    if "SENTRY_DSN" in os.environ:
        balsa = TstCLIBalsa(application_name)
        balsa.use_sentry = True
        balsa.inhibit_cloud_services = False
        sentry_dsn = os.environ["SENTRY_DSN"]
        print(f"{sentry_dsn=}")
        balsa.sentry_dsn = sentry_dsn
        balsa.init_logger()

        log = get_logger(application_name)
        log.error("test balsa sentry error message")

        balsa.remove()
    else:
        print("Please set SENTRY_DSN environment variable to have a good %s test" % __name__)


def test_sentry_initialized(monkeypatch):
    # baseline: without BALSA_DEV or inhibit_cloud_services, Sentry is initialized
    application_name = "test_sentry_initialized"
    monkeypatch.delenv(balsa_dev_env_var, raising=False)
    init_calls = _spy_sentry_init(monkeypatch)

    balsa = TstCLIBalsa(application_name)
    balsa.use_sentry = True
    balsa.sentry_dsn = fake_sentry_dsn
    balsa.init_logger()

    assert len(init_calls) == 1
    assert init_calls[0]["dsn"] == fake_sentry_dsn
    assert "enable_logs" not in init_calls[0]  # Sentry structured logs are opt-in

    balsa.remove()


def test_sentry_logs_enabled(monkeypatch):
    # use_sentry_logs sends log records to Sentry structured logs (https://docs.sentry.io/platforms/python/logs/)
    application_name = "test_sentry_logs_enabled"
    monkeypatch.delenv(balsa_dev_env_var, raising=False)
    init_calls = _spy_sentry_init(monkeypatch)

    balsa = TstCLIBalsa(application_name)
    balsa.use_sentry = True
    balsa.use_sentry_logs = True
    balsa.sentry_dsn = fake_sentry_dsn
    balsa.init_logger()

    assert len(init_calls) == 1
    assert init_calls[0]["enable_logs"] is True
    sentry_logging_integration = init_calls[0]["integrations"][0]
    assert sentry_logging_integration._sentry_logs_handler.level == logging.INFO

    balsa.remove()


def test_balsa_dev_disables_sentry(monkeypatch):
    application_name = "test_balsa_dev_disables_sentry"
    monkeypatch.setenv(balsa_dev_env_var, "TRUE")
    init_calls = _spy_sentry_init(monkeypatch)

    balsa = TstCLIBalsa(application_name)
    balsa.use_sentry = True
    balsa.sentry_dsn = fake_sentry_dsn  # even with a DSN available, BALSA_DEV wins
    balsa.init_logger()

    assert len(init_calls) == 0

    balsa.remove()


def test_balsa_dev_no_dsn_does_not_raise(monkeypatch):
    # the issue #7 use case: development mode must not require a DSN to be configured
    application_name = "test_balsa_dev_no_dsn_does_not_raise"
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.setenv(balsa_dev_env_var, "TRUE")

    balsa = TstCLIBalsa(application_name)
    balsa.use_sentry = True
    balsa.init_logger()

    balsa.remove()


def test_balsa_dev_invalid_value_keeps_sentry_enabled(monkeypatch):
    # an invalid (e.g. typo'd) BALSA_DEV value is treated as False and must not crash logger initialization
    application_name = "test_balsa_dev_invalid_value_keeps_sentry_enabled"
    monkeypatch.setenv(balsa_dev_env_var, "ture")
    init_calls = _spy_sentry_init(monkeypatch)

    balsa = TstCLIBalsa(application_name)
    balsa.use_sentry = True
    balsa.sentry_dsn = fake_sentry_dsn
    balsa.init_logger()

    assert len(init_calls) == 1

    balsa.remove()


def test_inhibit_cloud_services_disables_sentry(monkeypatch):
    application_name = "test_inhibit_cloud_services_disables_sentry"
    monkeypatch.delenv(balsa_dev_env_var, raising=False)
    init_calls = _spy_sentry_init(monkeypatch)

    balsa = TstCLIBalsa(application_name)
    balsa.use_sentry = True
    balsa.inhibit_cloud_services = True
    balsa.sentry_dsn = fake_sentry_dsn
    balsa.init_logger()

    assert len(init_calls) == 0

    balsa.remove()


if __name__ == "__main__":
    test_balsa_sentry()
