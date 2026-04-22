from flask import Flask, render_template, session, redirect, url_for

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

# 1. Registro de Blueprints (Módulos)
    from app.auth.routes import auth_bp
    from app.inventory.routes import inventory_bp
    from app.sales.routes import sales_bp
    from app.reports.routes import reports_bp
    from app.users.routes import users_bp
    from app.admin.routes import admin_bp      # NUEVO

    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)           # NUEVO
    
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('base.html')

    return app