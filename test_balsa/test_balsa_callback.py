from pathlib import Path

from balsa import get_logger

log = get_logger(__file__)

from .tst_balsa import TstCLIBalsa


def my_callback(log_record):
    print(log_record.msg)


def test_balsa_callback():
    application_name = "test_balsa_callback"

    balsa = TstCLIBalsa(application_name)
    balsa.log_directory = Path("temp", application_name)
    balsa.error_callback = my_callback
    balsa.delete_existing_log_files = True
    balsa.init_logger()

    log.error(f"{application_name}\ntest error message")

    balsa.remove()


if __name__ == "__main__":
    test_balsa_callback()
