from PyQt5 import QtCore, uic, QtWidgets

import init, config_editor, db_connector, traceback, json

# UI generated uisng the Qt creator
curr_dir = QtCore.QDir()


qtMainWindow = "resources/ui/mainwindow.ui"
qtEditWindow = "resources/ui/editwindow.ui"
qtEditTableWindow = "resources/ui/edittablewindow.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainWindow)
Ui_EditWindow, QtEditClass = uic.loadUiType(qtEditWindow)
Ui_EditTableWindow, QtEditTableClass = uic.loadUiType(qtEditTableWindow)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    switch_edit_window = QtCore.pyqtSignal()
    switch_config_file = QtCore.pyqtSignal()

    def __init__(self, settings):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.line_config_file.setText(settings['config_file'])
        self.line_db_server.setText(settings['database_server'])
        self.line_db_name.setText(settings['database_name'])
        self.btn_begin_parse.clicked.connect(self.run_parsing)
        self.btn_go_to_edit_window.clicked.connect(self.edit_tables)
        self.btn_select_config.clicked.connect(self.select_config_file)
        self.btn_select_form.clicked.connect(self.select_form_file)
        self.btn_test_connection.clicked.connect(self.print_test_connection)

        self.config_file = ""
        self.form_file = ""

    def run_parsing(self):
        con = self.test_connection()
        if not self.form_file or not self.config_file:
            self.show_message('Warning', 'Parse Warning',
                              "Config, Form, or Access File has not been set!",
                              QtWidgets.QMessageBox.Warning)
        if not con:
            self.show_message('Warning', 'Connection Warning',
                              'Cannot Connect to the database \nnCheck log for details.',
                              QtWidgets.QMessageBox.Warning)
        else:
            self.btn_begin_parse.setEnabled(False)
            try:
                init.main(self.form_file, self.config_file, con.cursor())
                pass
            except Exception as e:
                exception_throw()
            finally:
                con.close()
            self.btn_begin_parse.setEnabled(True)
            self.done_parsing()

    def edit_tables(self):
        if not self.config_file:
            self.show_message('Warning', 'Edit Warning', 'Config file has not been set!',
                              QtWidgets.QMessageBox.Warning)
        else:
            self.switch_edit_window.emit()

    def select_config_file(self):
        self.config_file = self.get_file("JSON (*.JSON)")
        self.line_config_file.setText(self.config_file)
        self.switch_config_file.emit()

    def select_form_file(self):
        self.form_file = self.get_file("Excel (*.xlsx)")
        self.line_form_file.setText(self.form_file)

    def get_file(self, file_type):

        file_dialog = QtWidgets.QFileDialog()
        filename = file_dialog.getOpenFileName(
            self,
            "Open Document",
            curr_dir.currentPath(),
            file_type
        )

        return filename[0]

    def done_parsing(self):
        self.show_message('Success', 'Parsing Finished!', '', QtWidgets.QMessageBox.Information)

    def get_config_file(self):
        return self.config_file

    def print_test_connection(self):
        if not self.get_connection() == None:
            self.show_message('Success', 'Connection Succeeded!', '', QtWidgets.QMessageBox.Information)
        else:
            self.show_message('Warning', 'Connection Failed', 'Check Log For Details', QtWidgets.QMessageBox.Warning)

    def get_connection(self):
        server = self.line_db_server.text()
        db = self.line_db_name.text()
        try:
            con = db_connector.create_connection(server, db)
            con.close()
            return con
        except Exception:
            traceback.print_exc()
            return None

    def show_message(self, title, text, info, icon):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(icon)

        msg_box.setText(text)
        msg_box.setInformativeText(info)
        msg_box.setWindowTitle(title)
        msg_box.exec()


class EditMainWindow(QtWidgets.QMainWindow, Ui_EditWindow):
    switch_edit_table_window = QtCore.pyqtSignal()

    def __init__(self, json_editor):
        QtWidgets.QMainWindow.__init__(self)
        Ui_EditWindow.__init__(self)
        self.setupUi(self)
        self.json_editor = json_editor
        tables = self.json_editor.get_existing_tables()
        for table in tables:
            self.list_existing_tables.addItem(table)

        self.list_existing_tables.currentItemChanged.connect(self.item_change)

    def item_change(self):
        self.btn_edit_table.setEnabled(True)

    def edit_table(self):
        self.switch_edit_table_window.emit()


class EditTableWindow(QtWidgets.QMainWindow, Ui_EditTableWindow):
    def __init__(self, table, json_editor):
        QtWidgets.QMainWindow.__init__(self)
        Ui_EditWindow.__init__(self)
        self.setupUi(self)
        self.json_editor = json_editor
        cols = self.json_editor.get_columns(table)
        ids = self.json_editor.get_identifiers(table)
        for col in cols:
            self.list_existing_columns.addItem(col["col_name"])
        for identifier in ids:
            self.list_existing_identifiers.addItem(identifier["col_name"])


class MainController:

    def __init__(self):
        self.window = None
        self.json_editor = None
        self.settings = None
        with open('resources/Settings.JSON') as settings:
            self.settings = json.load(settings)

    def show_main(self):
        self.window = MainWindow(self.settings)
        self.window.switch_edit_window.connect(self.show_edit_tables)
        self.window.switch_config_file.connect(self.set_config)
        self.window.show()

    def show_edit_tables(self):
        self.window = EditMainWindow(self.json_editor)
        self.window.show()

    def show_edit_table(self):
        if type(self.window) is not EditMainWindow:
            raise TypeError('Window accessed illegally')

        self.window = EditTableWindow(self.window.list_existing_tables.currentItem.text(), self.json_editor)

    def set_config(self):
        if type(self.window) is not MainWindow:
            raise TypeError('Window accessed illegally')
        self.json_editor = config_editor.JSONConfigEditor(self.window.get_config_file())


def exception_throw():
    exception_msg_box = QtWidgets.QMessageBox()
    exception_msg_box.setIcon(QtWidgets.QMessageBox.Warning)
    exception_msg_box.setText("An error has occurred!")
    exception_msg_box.setInformativeText("Check log for details.")
    exception_msg_box.exec()
