from flask import Flask, render_template, session, redirect, url_for

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from app.auth.auth_controller import auth_bp
    from app.inventario.vehiculo_controller import vehiculos_bp
    from app.inventario.marca_controller import marcas_bp
    from app.inventario.servicio_controller import servicios_bp
    from app.ventas.ventas_controller import ventas_bp
    from app.ventas.detalle_venta_controller import detalle_venta_bp
    from app.ventas.detalle_servicio_controller import detalle_servicio_bp
    from app.clientes.cliente_controller import clientes_bp
    from app.reportes.reportes_controller import reportes_bp
    from app.admin.admin_controller import admin_bp
    from app.cuotas.cuotas_controller import cuotas_bp
    from app.medios_pago.medio_pago_controller import medios_pago_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vehiculos_bp)
    app.register_blueprint(marcas_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(detalle_venta_bp)
    app.register_blueprint(detalle_servicio_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cuotas_bp)
    app.register_blueprint(medios_pago_bp)

    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('base.html')

    return app