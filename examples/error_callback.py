
def balsa_example_error_callback(log_record):
    try:
        # in case formatting is not yet set
        asc_time = log_record.asctime
    except AttributeError:
        asc_time = None

    if asc_time is None:
        print(f'{log_record.levelname} : "{log_record.msg}"')
    else:
        print(f"{log_record.levelname} : it's {asc_time}, do you know where your code is?")
