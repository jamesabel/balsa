.. this file is kept in the docs\source directory and COPIED to the project root directory.
.. DO NOT edit the copy in the project root directory.

balsa (logging utility)
=======================

Simple to use package that sets up Python logging.  With just a few lines of code get well formatted logging to the
console, log file, popup windows and exception services.

Here is a short `Presentation on Balsa <https://www.abel.co/balsa_lightening_talk.pdf>`_.

Installation
============

.. code-block:: console

    pip install balsa

Major Features
==============
- Simple to use.  Add full-featured Python logging in just a few lines of code.
- Sane default log levels.  Single `verbose` flag.  (All levels can be overridden if desired.)
- Both console (stdout) and GUI (popup window) support.
- Log file support. Uses `appdirs` for log file paths.
- Structured logging (optional - you can still use simple strings and/or legacy logging string formatting).
- `Sentry <http://www.sentry.io/>`_ support. Just provide your `Sentry DSN <https://docs.sentry.io/quickstart/#configure-the-dsn>`_.
- Informative log message formatting (or you can change it if you like).
- ISO 8601 timestamp format (with fractional seconds).
- Cross platform (Windows, Linux, MacOS).  Pure Python.

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


This will yield output of this form:

.. code-block:: console

    2021-10-24T10:49:04.150790-07:00 - example - balsa_simple_example.py - 12 - main - ERROR - my error example

Releases
========
- 0.9 : Add structured logging and ISO 8601 timestamp format.
- 0.6 : Add rate control to popup windows. Automated GUI testing.
- 0.5 : Allow more than one logger.
- 0.3 : Initial release.

Where did the name come from?
=============================
Balsa lumber is very soft and light, with a coarse, open grain.
The Balsa package is light weight, malleable, and open source.