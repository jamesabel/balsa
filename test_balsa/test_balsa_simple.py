from ismain import is_main

from balsa import get_logger

from .tst_balsa import TstCLIBalsa


def test_balsa_simple():
    application_name = "test_balsa_simple"

    balsa = TstCLIBalsa(application_name)
    balsa.init_logger()

    log = get_logger(application_name)
    log.error("test error message")

    balsa.remove()


if is_main():
    test_balsa_simple()
