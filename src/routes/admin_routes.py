from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from src.models.admin_user import AdminUser
from src.models.appointment import Appointment
from datetime import datetime, date, time

from src import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = AdminUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("admin.dashboard"))

        flash("Usuário ou senha inválidos")

    return render_template("admin/login.html")

# Dashboard - calendar view
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    # lê ?date=YYYY-MM-DD, se não vier usa hoje
    date_str = request.args.get("date")
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    # gera horários de 08:00 até 18:00 (inclui 18:00)
    start_hour = 8
    end_hour = 18
    times = []
    for h in range(start_hour, end_hour + 1):
        times.append(time(hour=h, minute=0))

    # consulta agendamentos do dia (somente a data)
    appointments = Appointment.query.filter(
        db.func.date(Appointment.date_time) == selected_date
    ).all()

    # mapeia appointments por hora (hora inteira)
    appt_map = {}
    for a in appointments:
        hour_key = a.date_time.hour
        appt_map[hour_key] = a

    # constrói timeslots com status
    timeslots = []
    for t in times:
        slot_hour = t.hour
        appt = appt_map.get(slot_hour)
        if appt:
            timeslots.append({
                "time": t.strftime("%H:%M"),
                "status": "busy",
                "appointment": {
                    "id": appt.id,
                    "customer_name": appt.customer.name if getattr(appt, "customer", None) else "",
                    "vehicle_plate": appt.vehicle.plate if getattr(appt, "vehicle", None) else "",
                }
            })
        else:
            timeslots.append({
                "time": t.strftime("%H:%M"),
                "status": "free",
                "appointment": None
            })

    return render_template("admin/dashboard.html",
                           timeslots=timeslots,
                           selected_date=selected_date)

# Endpoint para criar agendamento (POST via AJAX)
@admin_bp.route("/appointments/create", methods=["POST"])
@login_required
def create_appointment():
    data = request.json or request.form

    # espera: date (YYYY-MM-DD), time (HH:MM), customer_name, customer_phone, vehicle_model, vehicle_plate, notes (opcional)
    date_str = data.get("date")
    time_str = data.get("time")
    customer_name = data.get("customer_name", "").strip()
    customer_phone = data.get("customer_phone", "").strip()
    vehicle_model = data.get("vehicle_model", "").strip()
    vehicle_plate = data.get("vehicle_plate", "").strip()
    notes = data.get("notes", "").strip()

    if not (date_str and time_str and customer_name and vehicle_plate):
        return jsonify({"success": False, "message": "Dados incompletos."}), 400

    # monta datetime
    try:
        dt_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({"success": False, "message": "Formato de data/hora inválido."}), 400

    # verifica conflito: já existe agendamento para mesma hora (entre dt_obj e dt_obj + 1h)
    dt_end = dt_obj + timedelta(hours=1)
    conflict = Appointment.query.filter(
        Appointment.date_time >= dt_obj,
        Appointment.date_time < dt_end
    ).first()
    if conflict:
        return jsonify({"success": False, "message": "Horário já ocupado."}), 409

    # encontra ou cria customer (busca por telefone se informado, senão por nome)
    customer = None
    if customer_phone:
        customer = Customer.query.filter_by(phone=customer_phone).first()
    if not customer:
        customer = Customer.query.filter_by(name=customer_name).first()
    if not customer:
        customer = Customer(name=customer_name, phone=customer_phone)
        db.session.add(customer)
        db.session.flush()  # para obter id

    # encontra ou cria vehicle (busca por plate)
    vehicle = None
    if vehicle_plate:
        vehicle = Vehicle.query.filter_by(plate=vehicle_plate).first()
    if not vehicle:
        vehicle = Vehicle(model=vehicle_model or "N/A", plate=vehicle_plate, customer_id=customer.id)
        db.session.add(vehicle)
        db.session.flush()

    # cria appointment
    new_appt = Appointment(date_time=dt_obj, customer_id=customer.id, vehicle_id=vehicle.id)
    # se seu model tiver campo notes, adicione: new_appt.notes = notes
    if hasattr(Appointment, "notes") and notes:
        new_appt.notes = notes

    db.session.add(new_appt)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Agendamento criado!",
        "appointment": {
            "id": new_appt.id,
            "time": new_appt.date_time.strftime("%H:%M"),
            "customer_name": customer.name,
            "vehicle_plate": vehicle.plate
        }
    }), 201

@admin_bp.route("/appointment/<int:appointment_id>")
@login_required
def appointment_detail(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    return render_template("admin/appointment_detail.html", appointment=appointment)


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))
