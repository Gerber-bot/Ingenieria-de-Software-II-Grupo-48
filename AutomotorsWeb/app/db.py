import pyodbc
from config import Config

def get_db_connection():
    try:
        conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI)
        return conn
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None