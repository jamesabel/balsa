
from setuptools import setup

from balsa import __version__, __title__, __author__, __author_email__, __url__, __download_url__

with open('readme.rst', encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name=__title__,

    description='Comparison utility',
    long_description=long_description,
    long_description_content_type='text/x-rst',

    version=__version__,
    author=__author__,
    author_email=__author_email__,
    license='MIT License',
    url=__url__,
    download_url=__download_url__,
    keywords=['directory', 'file', 'comparison', 'utility'],
    packages=[__title__],
    install_requires=[],
    classifiers=[]
)
