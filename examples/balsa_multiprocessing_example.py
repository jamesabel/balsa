from typing import Dict, Any
from multiprocessing import Process

from balsa import Balsa, get_logger, balsa_clone
from ismain import is_main

application_name = "my_application"
author = "me"


class MyProcess(Process):
    def __init__(self, parent_balsa_as_dict: Dict[str, Any]):
        super().__init__(name="my_process")  # we must name this instance
        self.parent_balsa_as_dict = parent_balsa_as_dict

    def run(self):

        # creating the balsa instance must be in the run method (not __init__() )
        balsa = balsa_clone(self.parent_balsa_as_dict, self.name)  # use the Process's name as the cloned logger's name
        balsa.init_logger()

        # must get the logger in the run() method (not at the top of the module)
        log = get_logger(application_name)
        log.info(f"hello from {self.name}")


def test_multiprocessing():

    balsa = Balsa(application_name, author, verbose=True)
    balsa.init_logger()
    log = get_logger(application_name)
    log.info("process started")

    my_process = MyProcess(balsa.config_as_dict())
    my_process.start()
    my_process.join()

    log.info("process finished")


if is_main():
    test_multiprocessing()
