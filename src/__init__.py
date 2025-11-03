from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# Inicializa SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configurações do app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Inicializa extensões
    db.init_app(app)

    # Importa modelos
    from src.models import Customer, Vehicle, Appointment

    # Importa e registra rotas (blueprints)
    from src.routes.appointment_routes import appointment_bp
    from src.routes.customer_routes import customer_bp
    from src.routes.vehicle_routes import vehicle_bp

    app.register_blueprint(customer_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(vehicle_bp)

    logging.debug('✅ App inicializado com sucesso!')

    with app.app_context():
        db.create_all()

    return app
