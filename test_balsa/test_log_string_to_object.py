from balsa import BalsaRecord


def tst_string_to_object(test_string: str):
    log_object = BalsaRecord(test_string)
    str_log_object = str(log_object)
    assert str_log_object == test_string


def test_log_string_to_object():
    tst_string_to_object('2021-10-23T21:20:26.677123-07:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp')
    tst_string_to_object('2021-10-23T21:20:26.677123-07:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp,myrules')
    tst_string_to_object('2021-10-23T21:20:26.677123-07:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp <> {"my_name": "me", "my_value": 42} <>')
    tst_string_to_object('2021-10-23T21:39:10.300016-07:00 - test_structured_logging - test_structured_logging.py - 22 - test_to_structured_logging - INFO - test,more,stuff <> {"question": "life", "answer": 42, "newline_string": "anewline", "crazy": "a crazy string", "some_float": 3.3, "a_bool": true} <>')


