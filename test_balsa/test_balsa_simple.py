from ismain import is_main

from balsa import get_logger, Balsa, __author__


def test_balsa_simple():
    application_name = "test_balsa_simple"

    balsa = Balsa(application_name, __author__, is_root=False)
    balsa.init_logger()

    log = get_logger(application_name)
    log.error("test error message")


if is_main():
    test_balsa_simple()
