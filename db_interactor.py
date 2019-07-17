import pyodbc
import re

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\alexl\PycharmProjects\FreshmanFormReader\coe_database_empty.accdb;')
cursor = conn.cursor()
# print(cursor.execute('INSERT INTO tbl_Student ([Student ID], [First Name], [Last Name], [Personal Phone Number], [City], [State], [Country], [graduation date]) VALUES (\'683329\', \'Gabriel\', \'Duenas\', "9097326387", "Pomona", "Ca", "USA", "FALL 2018");').fetchone())


def update(config):
    for entry in config:
        exists = check_existing(entry)
        # if it does no insert it
        if exists:
            statement = format_insert(entry)
            print(statement)
            cursor.execute(statement)
            cursor.commit()


def check_existing(entry):
    # first check if the entry exists already
    statement = 'SELECT * FROM ' + entry['table'] + ' WHERE \"'
    for identifier in entry["identifiers"]:
        statement += identifier['col_name'] + '\" = '
        # if it is a number, leave as number else place quotes
        if is_num(identifier['value']):
            statement += identifier['value']
        else:
            statement += '\'' + identifier['value'] + '\''
    return cursor.execute(statement).fetchone() is None


def format_insert(entry):
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


def get_derived(identifier, entry):
    stmt = 'SELECT ' + identifier['col'] + ' F'


# taken from https://stackoverflow.com/questions/40097590/detect-whether-a-python-string-is-a-number-or-a-letter/40097699
def is_num(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`,
                   # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True


