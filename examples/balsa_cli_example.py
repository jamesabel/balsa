
import argparse

from balsa import get_logger, Balsa

from example import application_name, author, something_useful
from example.error_callback import balsa_example_error_callback

log = get_logger(name=application_name)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
    args = parser.parse_args()

    balsa = Balsa(application_name, author, error_callback=balsa_example_error_callback)
    balsa.init_logger_from_args(args)

    something_useful()


if __name__ == '__main__':
    main()
