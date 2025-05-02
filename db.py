import pyodbc

# Azure SQL connection settings
server = 'cdm-server1.database.windows.net'
database = 'cdm-db1'
username = 'cdm'
password = 'Keerthi@111'

# Establish connection
def get_connection():
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    return conn
