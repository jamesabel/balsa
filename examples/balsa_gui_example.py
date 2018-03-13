

from balsa import init_logger, get_logger
from examples import application_name, author, something_useful

log = get_logger(name=application_name)


def main():
    init_logger(application_name, author, use_app_dirs=True, delete_existing_log_files=True, verbose=True, gui=True)

    something_useful()


if __name__ == '__main__':
    main()
