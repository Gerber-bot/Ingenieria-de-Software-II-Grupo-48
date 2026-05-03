class BackupRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def ejecutar_backup(self, archivo_bak):
        cursor = self.conn.cursor()
        query = f"BACKUP DATABASE Automotors TO DISK = '{archivo_bak}' WITH FORMAT, MEDIANAME = 'AutomotorsBackup', NAME = 'Full Backup'"
        cursor.execute(query)