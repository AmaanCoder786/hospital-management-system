import sqlite3

def get_db_connection():
    connection = sqlite3.connect("database/hospital.db")

    # Return rows as dictionary-like objects instead of tuples
    connection.row_factory = sqlite3.Row
    return connection