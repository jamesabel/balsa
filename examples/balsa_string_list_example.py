
from balsa import get_logger, Balsa

application_name = 'example'

log = get_logger(application_name)


def main():
    balsa = Balsa(application_name, 'james abel')
    balsa.init_logger()
    log.info('I am a message')
    log.info('So am I')
    for s in balsa.get_string_list():
        print(s)


if __name__ == '__main__':
    main()
