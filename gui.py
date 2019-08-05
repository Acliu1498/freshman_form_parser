import sys
import init
import config_editor
from PyQt5 import QtCore, QtGui, uic, QtWidgets

# base off of this tutorial: https://www.pythonforengineers.com/your-first-gui-app-with-python-and-pyqt/
# UI generated uisng the Qt creator

qtMainWindow = "mainwindow.ui"
qtEditWindow = "editwindow.ui"
qtEditTableWindow = "edittablewindow.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainWindow)
Ui_EditWindow, QtEditClass = uic.loadUiType(qtEditWindow)
Ui_EditTableWindow, QtEditTableClass = uic.loadUiType(qtEditTableWindow)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    switch_edit_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.btn_begin_parse.clicked.connect(self.run_parsing)
        self.btn_go_to_edit_window.clicked.connect(self.edit_tables)

    def run_parsing(self):
        init.main("SurveryResults FA2018.xlsx")

    def edit_tables(self):
        self.switch_edit_window.emit()


class EditMainWindow(QtWidgets.QMainWindow, Ui_EditWindow):
    switch_edit_table_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_EditWindow.__init__(self)
        self.setupUi(self)
        tables = config_editor.get_existing_tables()
        for table in tables:
            self.list_existing_tables.addItem(table)

        self.list_existing_tables.currentItemChanged.connect(self.item_change)

    def item_change(self):
        self.btn_edit_table.setEnabled(True)

    def edit_table(self):
        self.switch_edit_table_window.emit()


class EditTableWindow(QtWidgets.QMainWindow, qtEditTableWindow):
    def __init__(self, table):
        QtWidgets.QMainWindow.__init__(self)
        Ui_EditWindow.__init__(self)
        self.setupUi(self)


class MainController:

    def __init__(self):
        pass

    def show_main(self):
        self.window = MainWindow()
        self.window.switch_edit_window.connect(self.show_edit_tables)
        self.window.show()

    def show_edit_tables(self):
        self.window = EditMainWindow()
        self.window.show()

    def show_edit_table(self):
        if self.window is not EditTableWindow:
            raise TypeError('Window accessed illegally')

        self.window = EditTableWindow(self.window.list_existing_tables.currentItem.text())



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    controller = MainController()
    controller.show_main()
    sys.exit(app.exec_())
