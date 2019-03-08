
import os

from balsa import get_logger, Balsa, __author__


def test_balsa_sentry():
    application_name = 'test_balsa_sentry'

    if 'SENTRY_DSN' in os.environ:
        dsn = os.environ['SENTRY_DSN']
        balsa = Balsa(
            application_name,
            __author__,
            use_sentry=True,
            inhibit_cloud_services=False,
            is_root=False,
            sentry_dsn=dsn
        )
        balsa.init_logger()

        log = get_logger(application_name)
        log.error('test balsa sentry error message')
    else:
        print('Please set SENTRY_DSN environment variable to have a good %s test' % __name__)


if __name__ == '__main__':
    test_balsa_sentry()
