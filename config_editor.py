import json
import traceback


class JSONConfigEditor:
    def __init__(self, file):
        self.json_data = None
        self.file = file
        try:
            with open(file) as in_file:
                self.json_data = json.load(in_file)
        except Exception as e:
            traceback.print_exc()
            raise e

    def add_table(self):
        pass

    def edit_table(self):
        pass

    def add_column(self):
        pass

    def get_existing_tables(self):
        return list(self.json_data.keys())

    def get_columns(self, table):
        return self.json_data[table]["cols"]

    def get_identifiers(self, table):
        return self.json_data[table]["identifiers"]

    def delete_column(self, table, index):
        del self.json_data[table]["cols"][index]

    def delete_identifier(self, table, index):
        del self.json_data[table]["identifiers"][index]

    def save(self):
        f = open(self.file, 'w')
        f.write(self.json_data)

