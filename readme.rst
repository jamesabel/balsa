
balsa (logging utility)
=======================

Simple to use package that sets up Python logging.  With just a few lines of code get well formatted file and
console or GUI logging.


Simple Example
==============

.. code:: python

    from balsa import get_logger, Balsa

    application_name = 'example'

    log = get_logger(application_name)


    def main():
        balsa = Balsa(application_name, 'james abel')
        balsa.init_logger()
        log.error('my error example')


Where did the name come from?
=============================
Balsa lumber is very soft and light, with a coarse, open grain.
The Balsa package is light weight, malleable, and open source.
