from src import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # Relacionamentos
    vehicles = db.relationship('Vehicle', backref='customer', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='customer', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Customer {self.name}>'
