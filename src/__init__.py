from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging

# Inicializa SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "admin.login"  # rota para onde o usuário vai se não estiver logado


def create_app():
    app = Flask(__name__)

    # Configurações do app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)

    # Importa modelos
    from src.models import Customer, Vehicle, Appointment, AdminUser

    # Função obrigatória do Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # Importa e registra rotas (blueprints)
    from src.routes.appointment_routes import appointment_bp
    from src.routes.customer_routes import customer_bp
    from src.routes.vehicle_routes import vehicle_bp
    from src.routes.admin_routes import admin_bp 

    app.register_blueprint(customer_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(admin_bp)  

    logging.debug('App inicializado com sucesso!')

    # Cria tabelas se não existirem
    with app.app_context():
        db.create_all()

    return app
