from threading import Thread
import time

try:
    from PyQt5.QtCore import QThread

    from balsa import get_logger, Balsa, __author__, traceback_string


    exception_complete = False


    class QtGuiThread(QThread):
        def run(self):
            global exception_complete
            application_name = "qt_gui_thread"
            log = get_logger(application_name)
            try:
                print(f"{application_name} - before divide")
                a = 2.0 / 0.0  # generate an exception for testing (not a real error)
            except ZeroDivisionError:
                print(f"{application_name} - division error exception")
                log.error(traceback_string())
                print(f"{application_name} - after error log")
                exception_complete = True


    class GuiThread(Thread):
        def run(self):
            global exception_complete
            application_name = "gui_thread"
            log = get_logger(application_name)
            try:
                print(f"{application_name} - before divide")
                a = 3.0 / 0.0  # generate an exception for testing (not a real error)
            except ZeroDivisionError:
                print(f"{application_name} - division error exception")
                log.error(traceback_string())
                print(f"{application_name} - after error log")
                exception_complete = True


    def test_threaded_gui():

        global exception_complete
        timeout = 10

        application_name = "main_thread"
        log = get_logger(application_name)
        balsa = Balsa(application_name, __author__, verbose=True, log_directory="temp", gui=True, is_root=False, delete_existing_log_files=True)
        balsa.init_logger()
        log.info("starting main thread")

        exception_complete = False
        gui_thread = QtGuiThread()
        gui_thread.start()
        loop_count = 0
        while gui_thread.isRunning() and loop_count < timeout:
            time.sleep(1)
            loop_count += 1
        assert exception_complete

        exception_complete = False
        gui_thread = GuiThread()
        gui_thread.start()
        gui_thread.join(timeout)
        assert exception_complete

    if __name__ == "__main__":
        test_threaded_gui()

except ModuleNotFoundError:
    # if we don't have PyQt we can't run this test case
    pass
