from ismain import is_main

from balsa import __author__, Balsa, get_logger, sf


def test_to_structured_logging():
    application_name = "test_structured_logging"

    balsa = Balsa(application_name, __author__, verbose=True)
    balsa.init_logger()

    log = get_logger(application_name)

    question = "life"
    answer = 42
    log.info(sf("test structured logging", question=question, answer=answer))

    crazy = 'a "crazy" string'
    newline_string = "a\nnewline"
    some_float = 3.3
    a_bool = True
    log.info(sf("test", "more,stuff", question=question, answer=answer, newline_string=newline_string, crazy=crazy, some_float=some_float, a_bool=a_bool))

    complex_value = 1 + 2j
    log.info(sf(complex_value=complex_value))


if is_main():
    test_to_structured_logging()
