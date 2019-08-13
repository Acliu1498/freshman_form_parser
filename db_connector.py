import pyodbc


def create_connection(server, db):
    SQL_ATTR_CONNECTION_TIMEOUT = 113
    login_timeout = 1
    connection_timeout = 3
    conn = pyodbc.connect(
        r'Driver={ODBC Driver 17 for SQL Server};'
        rf'Server={server};'
        rf'Database={db};'
        r'Trusted_Connection=yes;',
        timeout=login_timeout,
        attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout}
    )
    conn
    return conn

