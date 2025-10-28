from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging


# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Initialize extensions
    db.init_app(app)

     # Importa modelos após inicializar o db
    from src.models import Customer, Vehicle, Appointment
    from src.routes import appointment_bp, customer_bp

    # Registra blueprint
    
    app.register_blueprint(customer_bp)

    app.register_blueprint(appointment_bp)
    
    logging.debug('testee')

    with app.app_context():
        db.create_all()

    return app