
from balsa import get_logger, Balsa

application_name = 'example'

log = get_logger(application_name)


def main():
    balsa = Balsa(application_name, 'james abel')
    balsa.init_logger()
    log.error('my error example')


if __name__ == '__main__':
    main()
