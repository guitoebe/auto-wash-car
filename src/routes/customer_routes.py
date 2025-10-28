from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from src.models.customer import Customer
from src import db

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@customer_bp.route('/customers/new', methods=['GET', 'POST'])
def create_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        new_customer = Customer(name=name, phone=phone)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('customer.get_customers'))
    return render_template('create_customer.html')