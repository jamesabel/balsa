from balsa import get_logger

from .tst_balsa import TstCLIBalsa


def test_two_logs():
    """
    test two logs where one is the root (catch-all) and other is separate (no propagation to root)
    """
    log_names = ["a", "b", "c"]

    # instantiate the balsa objects
    # The 'a' log is the root and therefore the catch-all
    # The 'b' log has no propagation and is therefore only its messages
    balsas = {}
    balsas["a"] = TstCLIBalsa("a", is_root=True)
    balsa_b = TstCLIBalsa("b")
    balsa_b.propagate = False
    balsas["b"] = TstCLIBalsa("b")

    [b.init_logger() for k, b in balsas.items()]

    logs = [get_logger(test_name) for test_name in log_names]  # get the loggers

    for index, log in enumerate(logs):
        # log something
        log.info(log_names[index])

    # check the contents

    sl = balsas["a"].get_string_list()
    assert len(sl) == 5  # gets the 'b' and 'c' log in addition to the 'a' log

    assert len(balsas["b"].get_string_list()) == 1  # just the 'b'

    log_string_min_length = 35  # SWAG to try to ensure the log string includes the time stamp, level, etc.

    sl = balsas["a"].get_string_list()
    assert sl[2][-1] == "a"
    assert len(balsas["a"].get_string_list()[0]) > log_string_min_length

    sl = balsas["a"].get_string_list()
    assert sl[-1][-1] == "c"
    assert len(balsas["a"].get_string_list()[1]) > log_string_min_length

    assert balsas["b"].get_string_list()[0][-1] == "b"
    assert len(balsas["b"].get_string_list()[0]) > log_string_min_length

    for b in balsas.values():
        b.remove()


if __name__ == "__main__":
    test_two_logs()
