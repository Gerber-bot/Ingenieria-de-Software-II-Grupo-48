class MedioPagoRepository:

    def __init__(self, db_connection):
        self.conn = db_connection

    def inicializar_medios_pago(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM MedioPago")

        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO MedioPago (nombre)
                VALUES ('Efectivo'), ('Transferencia'), ('Financiado')
            """)
            self.conn.commit()

    def obtener_medios_pago(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id_medio_pago, nombre
            FROM MedioPago
            ORDER BY id_medio_pago
        """)

        columnas = [columna[0].lower() for columna in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]