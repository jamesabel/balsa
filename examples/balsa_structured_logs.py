from balsa import get_logger, Balsa, sf

from example import application_name, author

log = get_logger(application_name)


def main():

    balsa = Balsa(application_name, author, verbose=True)
    balsa.init_logger()

    my_value = 42
    log.info(sf(my_value=my_value))


if __name__ == '__main__':
    main()
