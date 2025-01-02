from PyQt5.QtWidgets import QApplication, QMessageBox
from balsa import get_logger, Balsa

application_name = "balsa_gui_example"
author = "balsa"

log = get_logger(name=application_name)

def main():
    app = QApplication([])

    balsa = Balsa(application_name, author, gui=True)
    balsa.init_logger()

    dialog_box = QMessageBox()
    dialog_box.setText("Please close this window to end the demo ...")
    dialog_box.setWindowTitle(application_name)
    dialog_box.show()

    log.error('I am an error message ...')

    app.exec()

if __name__ == '__main__':
    main()