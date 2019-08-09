import pyodbc
import re
import os
import json


class DBInteractor():

    def __init__(self):
        import pyodbc
        SQL_ATTR_CONNECTION_TIMEOUT = 113
        login_timeout = 1
        connection_timeout = 3
        conn = pyodbc.connect(
            r'Driver={ODBC Driver 17 for SQL Server};'
            r'Server=localhost;'
            r'Database=InternTest;'
            r'Trusted_Connection=yes;',
            timeout=login_timeout,
            attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout}
        )
        self.cursor = conn.cursor()

    """
    method that updates database given a config
    """
    def update(self, config):
        # update db with each entry in the config
        for key in config:
            entry = config[key]
            # fill in any derived entries
            entry = self.fill_derived(entry)
            exists = self.check_existing(entry)
            # if it does no insert it
            if not exists:
                statement = self.format_insert(entry)
                print(statement)
                self.cursor.execute(statement)
                self.cursor.commit()
                if entry['save_new']:
                    self.save_new(entry)

    """
    method to fill any derived identifiers
    """
    def fill_derived(self, entry):
        for identifier in entry["identifiers"]:
            if identifier['derived']:
                id = self.get_derived(identifier)
                identifier['value'] = id
        return entry

    """
    method to check if an entry already exists in the database
    """
    def check_existing(self, entry):
        # first check if the entry exists already
        return self.select_entry(entry) is not None

    """
    helper method to get an entry form the database
    """
    def select_entry(self, entry):
        statement = 'SELECT * FROM ' + entry['table'] + ' WHERE \"'
        for identifier in entry["identifiers"]:
            statement += identifier['col_name'] + '\" = '
            # if it is a number, leave as number else place quotes
            if is_num(identifier['value']):
                statement += identifier['value']
            else:
                statement += '\'' + identifier['value'] + '\''
            statement += ' AND \"'
        statement = statement[:len(statement) - 6]
        print(statement)
        return self.cursor.execute(statement).fetchone()

    """
    helper method to format an insert statement
    """
    def format_insert(self, entry):
        stmt_cols = 'INSERT INTO ' + entry['table'] + ' (['
        # adds identifier cols to stmt
        for identifier in entry["identifiers"]:
            stmt_cols += identifier['col_name'] + ', '
        # add cols to statement
        for col in entry['cols']:
            stmt_cols += col["col_name"] + ', '
        stmt_cols = stmt_cols[0:len(stmt_cols) - 2] + "]) "
        stmt_cols = re.sub(r',\s?', "], [", stmt_cols)

        # add the values to the stmt
        stmt_vals = 'VALUES (\''
        # adds identifier values to stmt
        for identifier in entry['identifiers']:
            stmt_vals += identifier['value'] + ', '
        # add col values to stmt
        for col in entry['cols']:
            stmt_vals += str(col["value"]) + ', '

        stmt_vals = stmt_vals[0:len(stmt_vals) - 2] + '\');'
        # replace commas to show separation of values
        stmt_vals = re.sub(r'(?<!\\),\s?', "\', \'", stmt_vals)
        # replace escaped commas to regular commas
        stmt_vals = re.sub(r'\\,\s?', ",", stmt_vals)
        # concat cols to values
        statement = stmt_cols + stmt_vals

        return statement

    def get_derived(self, identifier):
        stmt = 'SELECT ' + identifier['derv_col_name'] + ' FROM ' + identifier['table'] + ' WHERE \"'

        for question in identifier['questions']:
            stmt += question['col_name'] + '\" = \'' + question['value'] + '\' AND '
        stmt = stmt[:len(stmt) - 5] + ';'

        resp = self.cursor.execute(stmt).fetchone()
        if resp:
            id = str(resp[0])
        else:
            id = ""
        return id

    def save_new(self, entry):
        # creates if not exists a path for new entries
        if not os.path.exists('New Entries'):
            os.makedirs('New Entries')
        # creates if not exists a file for new entries for specified table
        if not os.path.exists('New Entries/' + entry['table'] + '_new_entries.JSON'):
            f = open('New Entries/' + entry['table'] + '_new_entries.JSON', "a+")
            f.write('[]')
        # adds new entry to file
        with open('New Entries/' + entry['table'] + '_new_entries.JSON') as new_entry_data:
            try:
                data = json.load(new_entry_data)
            except ValueError:
                data = []
            data.append({
                "table": entry['table'],
                "id": str(self.select_entry(entry)[0]),
                "value": str(entry['identifiers'][0]['value']),
                "correct_id": -1
            })
            f = open('New Entries/' + entry['table'] + '_new_entries.JSON', "w")
            f.write(json.dumps(data))
        pass


# taken from https://stackoverflow.com/questions/40097590/detect-whether-a-python-string-is-a-number-or-a-letter/40097699
def is_num(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`,
                   # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True
