import logging

from balsa import Balsa, __author__


def test_not_root():
    """
    test that a non-root log does not pick up the logging to another logger
    """
    balsa = Balsa("a", __author__, verbose=True, is_root=False)
    balsa.init_logger()

    some_other_logger = logging.getLogger("b")
    some_other_logger.error("some log")  # will only be processed by default settings (no formatting, only to stdout)

    assert len(balsa.get_string_list()) == 0  # ensure the other logger didn't get caught by the balsa logger


if __name__ == "__main__":
    test_not_root()
