
from balsa import get_logger, Balsa, __author__


def test_balsa_simple():
    application_name = 'test_balsa'

    balsa = Balsa(application_name, __author__)
    balsa.init_logger()

    log = get_logger(application_name)
    log.error('test error message')


if __name__ == '__main__':
    test_balsa_simple()
