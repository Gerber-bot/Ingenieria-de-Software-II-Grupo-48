from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.servicios.auth.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, lo mandamos al inicio
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        usuario_input = request.form.get('usuario')
        password = request.form.get('password')

        # Delegamos la validación al Servicio
        service = AuthService()
        resultado = service.autenticar(usuario_input, password)

        if resultado['success']:
            # Si el servicio da el OK, configuramos la sesión con los datos
            user = resultado['user']
            session['user_id'] = user['id_usuario']
            session['user_name'] = f"{user['nombre']} {user['apellido']}"
            session['user_role'] = user['rol']
            return redirect(url_for('index'))
        else:
            # Si falla, mandamos el mensaje de error a la pantalla
            flash(resultado['message'], 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear() # Borramos todos los datos de la sesión
    return redirect(url_for('auth.login'))