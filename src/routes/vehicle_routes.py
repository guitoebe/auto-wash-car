from flask import Blueprint, render_template
from src.models import Vehicle

vehicle_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@vehicle_bp.route('/', methods=['GET'])
def list_vehicles():
    vehicles = Vehicle.query.all()
    return render_template('vehicles.html', vehicles=vehicles)

