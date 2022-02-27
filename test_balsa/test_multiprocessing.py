from pathlib import Path
from typing import Dict, Any
from multiprocessing import Process

from balsa import Balsa, __author__, get_logger, balsa_clone

application_name = "test_balsa_multiprocess"


class MyProcess(Process):
    def __init__(self, parent_balsa_as_dict: Dict[str, Any]):
        super().__init__(name="a")  # we must name this instance
        self.parent_balsa_as_dict = parent_balsa_as_dict

    def run(self):

        # creating the balsa instance must be in the run method (not __init__() )
        balsa = balsa_clone(self.parent_balsa_as_dict, self.name)  # use the Process's name as the cloned logger's name
        balsa.init_logger()

        log = get_logger(application_name)
        log.info(f"hello from {self.name}")


def test_multiprocessing():

    log_directory = Path("temp", application_name)

    balsa = Balsa(application_name, __author__, verbose=True, log_directory=log_directory, delete_existing_log_files=True)
    balsa.init_logger()

    log = get_logger(application_name)

    log.info("process started")

    balsa_config = balsa.config_as_dict()
    my_process = MyProcess(balsa_config)
    my_process.start()
    my_process.join()

    process_log_file_path = Path(log_directory, f"{application_name}_a.log")
    assert process_log_file_path.exists()
    log_text = process_log_file_path.read_text()
    # check everything except the timestamp and line number
    assert "test_balsa_multiprocess - a - test_multiprocessing.py -" in log_text
    assert "- run - INFO - hello from a" in log_text

    log.info("process finished")
