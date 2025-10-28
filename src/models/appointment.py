from src import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)

    def __repr__(self):
        return f'<Appointment {self.DateTime} - Customer {self.customer_id} - Vehicle {self.vehicle_id}>'
