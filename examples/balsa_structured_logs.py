from balsa import get_logger, Balsa, sf

from example import application_name, author

log = get_logger(application_name)


def main():

    balsa = Balsa(application_name, author, verbose=True)
    balsa.init_logger()

    my_value = 42
    my_name = "me"
    log.info(sf("myapp", my_name=my_name, my_value=my_value))


if __name__ == '__main__':
    main()
