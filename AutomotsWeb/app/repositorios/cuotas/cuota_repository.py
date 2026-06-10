class CuotaRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def registrar_pago(self, id_plan_cuota):
        cursor = self.conn.cursor()
        # Modificamos solo el estado de la cuota específica
        cursor.execute("""
            UPDATE PlanCuotas 
            SET estado = 'Pagado', fecha_pago = GETDATE() 
            WHERE id_plan_cuota = ?
        """, (id_plan_cuota,))