
def balsa_example_error_callback(log_record):
    print(f'{log_record.levelname} : It is {log_record.asctime}, do you know where your code is? "{log_record.msg}"')
