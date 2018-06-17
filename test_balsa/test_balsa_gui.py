
from balsa import get_logger, Balsa, __author__


def test_balsa_gui():
    application_name = 'test_balsa_gui_simple'

    balsa = Balsa(application_name, __author__, verbose=True, log_directory='temp', gui=True, delete_existing_log_files=True)
    balsa.init_logger()

    log = get_logger(application_name)
    log.error('test error message')


if __name__ == '__main__':
    test_balsa_gui()
