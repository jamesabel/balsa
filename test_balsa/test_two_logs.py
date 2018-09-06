
from balsa import get_logger, Balsa, __author__


def test_two_logs():
    log_names = ['a', 'b', 'c']

    # instantiate the balsa objects
    # The 'a' log is the root and therefore the catch-all
    # The 'b' log has no propagation and is therefore only its messages
    balsas = {'a': Balsa('a', __author__, verbose=True, is_root=True),
              'b': Balsa('b', __author__, verbose=True, propagate=False)}

    [b.init_logger() for k, b in balsas.items()]

    logs = [get_logger(test_name) for test_name in log_names]  # get the loggers

    for index, log in enumerate(logs):
        # log something
        log.info(log_names[index])

    # check the contents

    assert(len(balsas['a'].get_string_list()) == 2)  # gets the 'c' log in addition to the 'a' log
    assert(len(balsas['b'].get_string_list()) == 1)  # just the 'b'

    log_string_min_length = 35  # SWAG to try to ensure the log string includes the time stamp, level, etc.

    assert(balsas['a'].get_string_list()[0][-1] == 'a')
    assert(len(balsas['a'].get_string_list()[0]) > log_string_min_length)

    assert(balsas['a'].get_string_list()[1][-1] == 'c')
    assert(len(balsas['a'].get_string_list()[1]) > log_string_min_length)

    assert(balsas['b'].get_string_list()[0][-1] == 'b')
    assert(len(balsas['b'].get_string_list()[0]) > log_string_min_length)


if __name__ == '__main__':
    test_two_logs()
