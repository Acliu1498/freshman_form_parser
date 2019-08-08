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
    curr_dir = QtCore.QDir()

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.btn_begin_parse.clicked.connect(self.run_parsing)
        self.btn_go_to_edit_window.clicked.connect(self.edit_tables)
        self.btn_select_config.clicked.connect(self.select_config_file)
        self.btn_select_form.clicked.connect(self.select_form_file)
        self.btn_select_access_file.clicked.connect(self.select_access_file)

        self.config_file = ""
        self.form_file = ""
        self.access_file = ""

    def run_parsing(self):
        if not self.form_file or not self.config_file or not self.access_file:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)

            msg_box.setText("Parse Warning!")
            msg_box.setInformativeText("Config, Form, or Access File has not been set!")
            msg_box.setWindowTitle("Warning")
            msg_box.exec()
        else:
            self.btn_begin_parse.setEnabled(False)
            try:
                init.main(self.form_file, self.config_file, self.access_file)
            except Exception as e:
                exception_throw()

            self.btn_begin_parse.setEnabled(True)
            self.done_parsing()

    def edit_tables(self):
        self.switch_edit_window.emit()

    def select_config_file(self):
        self.config_file = self.get_file("JSON (*.JSON)")
        self.line_config_file.setText(self.config_file)

    def select_form_file(self):
        self.form_file = self.get_file("Excel (*.xlsx)")
        self.line_form_file.setText(self.form_file)

    def select_access_file(self):
        self.access_file = self.get_file("Access (*.mdb, *.accdb)")
        self.line_access_file.setText(self.access_file)

    def get_file(self, file_type):

        file_dialog = QtWidgets.QFileDialog()
        filename = file_dialog.getOpenFileName(
            self,
            "Open Document",
            self.curr_dir.currentPath(),
            file_type
        )

        return filename[0]

    def done_parsing(self):
        finished_msg_box = QtWidgets.QMessageBox()
        finished_msg_box.setIcon(QtWidgets.QMessageBox.Information)
        finished_msg_box.setText("Parsing Finished!")
        finished_msg_box.exec()

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


class EditTableWindow(QtWidgets.QMainWindow, Ui_EditTableWindow):
    def __init__(self, table):
        QtWidgets.QMainWindow.__init__(self)
        Ui_EditWindow.__init__(self)
        self.setupUi(self)


class MainController:

    def __init__(self):
        self.window = None
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


def exception_throw():
    exception_msg_box = QtWidgets.QMessageBox()
    exception_msg_box.setIcon(QtWidgets.QMessageBox.Warning)
    exception_msg_box.setText("An error has occurred!")
    exception_msg_box.setInformativeText("Check log for details.")
    exception_msg_box.exec()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    controller = MainController()
    controller.show_main()
    sys.exit(app.exec_())
