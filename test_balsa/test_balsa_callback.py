
from balsa import get_logger, Balsa, __author__

log = get_logger(__file__)


def my_callback(log_record):
    print(log_record.msg)


def test_balsa_callback():
    application_name = 'test_balsa_callback'

    balsa = Balsa(application_name, __author__, verbose=True, log_directory='temp', error_callback=my_callback)
    balsa.init_logger()

    log.error('test error message')


if __name__ == '__main__':
    test_balsa_callback()
