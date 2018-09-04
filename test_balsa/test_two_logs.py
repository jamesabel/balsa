
from balsa import get_logger, Balsa, __author__


def test_two_logs():
    test_names = ['a', 'b']

    # instantiate the balsa objects
    balsas = [Balsa(test_name, __author__, verbose=True) for test_name in test_names]
    [b.init_logger() for b in balsas]

    logs = [get_logger(test_name) for test_name in test_names]  # get the loggers

    for index, log in enumerate(logs):
        # log something
        log.info(test_names[index])

    for index, log in enumerate(logs):
        # make sure each log has exactly one entry
        assert(len(balsas[index].get_string_list()) == 1)
        # check the contents ... at least the message we gave it
        assert(balsas[index].get_string_list()[0][-1] == test_names[index])


if __name__ == '__main__':
    test_two_logs()
