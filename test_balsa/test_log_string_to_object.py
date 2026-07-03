import logging

from balsa import BalsaRecord, get_logger

from .tst_balsa import TstCLIBalsa


def tst_string_to_object(test_string: str):
    log_object = BalsaRecord(test_string)
    assert log_object.valid
    str_log_object = str(log_object)
    assert str_log_object == test_string


def test_log_string_to_object():
    tst_string_to_object("2021-10-23T21:20:26.677123-07:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp")
    tst_string_to_object("2021-10-23T21:20:26.677123-07:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp,myrules")
    tst_string_to_object('2021-10-23T21:20:26.677123-07:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp <> {"my_name": "me", "my_value": 42} <>')
    tst_string_to_object(
        '2021-10-23T21:39:10.300016-07:00 - test_structured_logging - test_structured_logging.py - 22 - test_to_structured_logging - INFO - test,more,stuff <> {"question": "life", "answer": 42, "newline_string": "anewline", "crazy": "a crazy string", "some_float": 3.3, "a_bool": true} <>'
    )


def test_log_string_with_process_name_to_object():
    # current default log format, which includes %(processName)s
    tst_string_to_object("2021-10-23T21:20:26.677123-07:00 - balsa_example - MainProcess - balsa_structured_logs.py - 15 - main - INFO - myapp")
    tst_string_to_object('2021-10-23T21:20:26.677123-07:00 - balsa_example - MainProcess - balsa_structured_logs.py - 15 - main - INFO - myapp <> {"my_name": "me", "my_value": 42} <>')

    log_object = BalsaRecord("2021-10-23T21:20:26.677123-07:00 - balsa_example - MainProcess - balsa_structured_logs.py - 15 - main - INFO - myapp")
    assert log_object.process_name == "MainProcess"
    assert log_object.file_name == "balsa_structured_logs.py"
    assert log_object.line_number == 15


def test_log_string_positive_utc_offset_to_object():
    # timezones east of UTC have a "+" in the timestamp
    tst_string_to_object("2021-10-23T21:20:26.677123+02:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp")
    tst_string_to_object("2021-10-23T21:20:26.677123+02:00 - balsa_example - MainProcess - balsa_structured_logs.py - 15 - main - INFO - myapp")


def test_real_log_round_trip():
    # round trip an actual log line produced with the default log format (not a hand-written string)
    application_name = "test_real_log_round_trip"
    balsa = TstCLIBalsa(application_name)
    balsa.init_logger()
    log = get_logger(application_name)
    log.info("hello")

    log_string = balsa.get_string_list()[-1]
    log_object = BalsaRecord(log_string)
    assert log_object.valid
    assert log_object.name == application_name
    assert len(log_object.process_name) > 0
    assert log_object.file_name == "test_log_string_to_object.py"
    assert log_object.line_number > 0
    assert log_object.function_name == "test_real_log_round_trip"
    assert log_object.log_level == logging.INFO
    assert log_object.message == "hello"
    assert str(log_object) == log_string

    balsa.remove()


def test_bad_log_string_to_object():
    log_object = BalsaRecord("I am not a log")  # invalid structured log string
    assert not log_object.valid
    assert log_object.log_level == logging.NOTSET
