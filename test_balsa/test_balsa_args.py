
from balsa import get_logger, Balsa, __author__

application_name = 'test_balsa'

log = get_logger(application_name)


def test_balsa_args():
    balsa = Balsa(application_name, __author__, is_root=False)
    balsa.init_logger_from_args(None)  # args is fake for now ...
    log.info(__file__)
