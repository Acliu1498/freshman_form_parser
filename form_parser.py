from PyQt5 import QtWidgets
import gui
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    controller = gui.MainController()
    controller.show_main()
    exit_code = app.exec()
    sys.exit(exit_code)
