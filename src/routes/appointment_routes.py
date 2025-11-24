from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
from src import db
from src.models import Customer, Vehicle, Appointment

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

# ------------------------------------------------------
# 🔹 DASHBOARD COM FILTRO POR CELULAR (ATUALIZADO)
# ------------------------------------------------------
@appointment_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Tela principal de busca por telefone"""
    phone = request.args.get('phone', '').strip()
    filtered_appointments = None
    
    if phone:
       
        filtered_appointments = Appointment.query.join(Customer).filter(
            Customer.phone.like(f"%{phone}%")
        ).order_by(Appointment.date_time.desc()).all()
        
        if not filtered_appointments:
            flash(f'Nenhum agendamento encontrado para o telefone {phone}', 'warning')
    
    return render_template(
        "appointments.html",
        appointments=filtered_appointments,
        phone_searched=phone
    )


# ------------------------------------------------------
# 🔹 LISTAR TODOS OS AGENDAMENTOS
# ------------------------------------------------------
@appointment_bp.route('/', methods=['GET'])
def list_appointments():
    """Redireciona para o dashboard"""
    return redirect(url_for('appointments.dashboard'))


# ------------------------------------------------------
# 🔹 TELA DE NOVO AGENDAMENTO
# ------------------------------------------------------
@appointment_bp.route('/new', methods=['GET', 'POST'])
def schedule_appointment():
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name')
            customer_phone = request.form.get('customer_phone')
            vehicle_plate = request.form.get('vehicle_plate')
            vehicle_type = request.form.get('vehicle_type')
            date_time_str = request.form.get('date_time')

            if not all([customer_name, customer_phone, vehicle_plate, vehicle_type, date_time_str]):
                flash('Preencha todos os campos!', 'danger')
                return redirect(url_for('appointments.schedule_appointment'))

            date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M")

            # Cliente
            customer = Customer.query.filter_by(phone=customer_phone).first()
            if not customer:
                customer = Customer(name=customer_name, phone=customer_phone)
                db.session.add(customer)
                db.session.flush()

            # Veículo
            vehicle = Vehicle.query.filter_by(plate=vehicle_plate).first()
            if not vehicle:
                vehicle = Vehicle(
                    plate=vehicle_plate,
                    type=vehicle_type,
                    customer_id=customer.id
                )
                db.session.add(vehicle)
                db.session.flush()

            # Horário ocupado
            if Appointment.query.filter_by(date_time=date_time).first():
                flash('Este horário já está ocupado!', 'warning')
                return redirect(url_for('appointments.schedule_appointment'))

            # Criar agendamento
            appointment = Appointment(
                date_time=date_time,
                customer_id=customer.id,
                vehicle_id=vehicle.id
            )
            db.session.add(appointment)
            db.session.commit()

            flash('Agendamento criado com sucesso! 🎉', 'success')
            return redirect(url_for('appointments.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar agendamento: {str(e)}', 'danger')
            return redirect(url_for('appointments.schedule_appointment'))

    return render_template('appointment_form.html')


# ------------------------------------------------------
# 🔹 API — BUSCAR HORÁRIOS OCUPADOS
# ------------------------------------------------------
@appointment_bp.route('/occupied/<date>', methods=['GET'])
def get_occupied_times(date):
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()

        appointments = Appointment.query.filter(
            db.func.date(Appointment.date_time) == selected_date
        ).all()

        occupied_times = [a.date_time.strftime("%H:%M") for a in appointments]

        return jsonify(occupied_times), 200

    except Exception as e:
        return jsonify([]), 500


# ------------------------------------------------------
# 🔹 BOTÃO ADMIN — LOGIN SIMPLES
# ------------------------------------------------------
@appointment_bp.route('/admin/login')
def admin_login():
    session['admin'] = True
    flash("✅ Logado como ADMIN!", "success")
    return redirect(url_for("appointments.dashboard"))