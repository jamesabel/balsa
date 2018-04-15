

from balsa import get_logger, Balsa
from examples import application_name, author, something_useful

log = get_logger(name=application_name)


def main():
    balsa = Balsa(application_name, author, use_app_dirs=True, delete_existing_log_files=True, verbose=True, gui=True)
    balsa.init_logger()

    something_useful()


if __name__ == '__main__':
    main()
