import hashlib
from app.db import get_db_connection
from app.repositorios.auth.auth_repository import AuthRepository

class AuthService:
    def autenticar(self, usuario_input, password):
        #Acceso rapido para pruebas /Admin por defecto
        if usuario_input == 'admin' and password == 'admin123':
            return {
                'success': True, 
                'user': {
                    'id_usuario': 0, 
                    'nombre': 'Admin', 
                    'apellido': 'Principal', 
                    'rol': 'Administrador'
                }
            }

        #Validación contra la Base de Datos
        conn = get_db_connection()
        if not conn:
            return {'success': False, 'message': 'Error de conexión a la base de datos.'}

        try:
            repo = AuthRepository(conn)
            user = repo.buscar_usuario_activo(usuario_input)
            
            if user:
                # Generamos el hash de la contraseña ingresada
                password_hasheada = hashlib.sha256(password.encode('utf-8')).digest()
                
                # Comparamos los bytes del hash
                if user['password_hash'] == password_hasheada:
                    return {'success': True, 'user': user}
                else:
                    return {'success': False, 'message': 'Contraseña incorrecta.'}
            else:
                return {'success': False, 'message': 'Usuario no encontrado o inactivo.'}
                
        except Exception as e:
            print(f"LOG ERROR (AuthService): {str(e)}")
            return {'success': False, 'message': 'Error interno al validar credenciales.'}
        finally:
            conn.close()