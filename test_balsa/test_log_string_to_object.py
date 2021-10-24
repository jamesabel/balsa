from balsa import BalsaRecord


def test_log_string_to_object():
    test_string = '2021-10-23T21:20:26.677123-07:00 - balsa_example - balsa_structured_logs.py - 15 - main - INFO - myapp <> {"my_name": "me", "my_value": 42} <>'
    log_object = BalsaRecord(test_string)
    print()
    print(test_string)
    print(log_object)
    str_log_object = str(log_object)
    assert str_log_object == test_string
