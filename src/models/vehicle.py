from src import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10), nullable=False, unique=True)
    type = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    appointments = db.relationship('Appointment', backref='vehicle', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Vehicle {self.plate} - {self.type}>'
