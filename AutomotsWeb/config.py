import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    # Cadena de conexión usando pyodbc y SQL Server Native Client / ODBC Driver
    # Ajustá el nombre del driver según el que tengas instalado en tu PC (ej: 'ODBC Driver 17 for SQL Server')
    SQLALCHEMY_DATABASE_URI = (
        r"Driver={ODBC Driver 17 for SQL Server};"
        r"Server=localhost\SQLEXPRESS;"
        r"Database=Automotors;"
        r"Trusted_Connection=yes;"
    )