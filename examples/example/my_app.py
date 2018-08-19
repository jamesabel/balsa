
from balsa import get_logger

application_name = 'balsa_example'

log = get_logger(application_name)


def something_useful():
    log.debug('I hate bugs.')
    log.info('Information please.')
    log.warning('Warning Will Robinson!')
    log.error('To error is human. To really foul things up requires a computer.')
    log.critical("I just can't.")
