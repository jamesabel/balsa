
from balsa import get_logger, Balsa, __author__, traceback_string


def test_balsa_exception():
    application_name = 'test_balsa_exception'

    balsa = Balsa(application_name, __author__, gui=True)
    balsa.init_logger()

    log = get_logger(application_name)
    try:
        a = 1.0/0.0  # generate an exception for testing (not a real error)
    except ZeroDivisionError:
        log.error('test exception')
        log.error(traceback_string())


if __name__ == '__main__':
    test_balsa_exception()
