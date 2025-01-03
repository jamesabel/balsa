from argparse import Namespace

from balsa import get_logger

application_name = "test_balsa"

log = get_logger(application_name)

from .tst_balsa import TstCLIBalsa


def test_balsa_args():
    namespace = Namespace(verbose=True)
    balsa = TstCLIBalsa(application_name)
    balsa.init_logger_from_args(namespace)
    log.info(__file__)
    balsa.remove()
