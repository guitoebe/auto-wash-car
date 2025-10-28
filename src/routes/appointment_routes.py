from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from src import db
from src.models import Customer, Vehicle, Appointment

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointment_bp.route('/', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)


@appointment_bp.route('/new', methods=['GET', 'POST'])
def schedule_appointment():
    if request.method == 'POST':
        try:
            # Pega os dados do formulário
            customer_name = request.form.get('customer_name')
            customer_phone = request.form.get('customer_phone')
            vehicle_plate = request.form.get('vehicle_plate')
            vehicle_type = request.form.get('vehicle_type')
            date_time_str = request.form.get('date_time')

            print(f"📝 Dados recebidos:")
            print(f"   Cliente: {customer_name} | Telefone: {customer_phone}")
            print(f"   Placa: {vehicle_plate} | Tipo: {vehicle_type}")
            print(f"   Data/Hora: {date_time_str}")

            # Validação
            if not all([customer_name, customer_phone, vehicle_plate, vehicle_type, date_time_str]):
                flash('Preencha todos os campos!', 'danger')
                return redirect(url_for('appointments.schedule_appointment'))

            # Converte a data/hora
            date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M")

            # Busca ou cria o cliente
            customer = Customer.query.filter_by(phone=customer_phone).first()
            if not customer:
                customer = Customer(name=customer_name, phone=customer_phone)
                db.session.add(customer)
                db.session.flush()
                print(f"✅ Novo cliente criado: {customer.name} (ID: {customer.id})")
            else:
                print(f"✅ Cliente existente: {customer.name} (ID: {customer.id})")

            # Busca ou cria o veículo
            vehicle = Vehicle.query.filter_by(plate=vehicle_plate).first()
            if not vehicle:
                vehicle = Vehicle(
                    plate=vehicle_plate, 
                    type=vehicle_type,  # ✅ Aqui usa 'type' mesmo
                    customer_id=customer.id
                )
                db.session.add(vehicle)
                db.session.flush()
                print(f"✅ Novo veículo criado: {vehicle.plate} (ID: {vehicle.id})")
            else:
                print(f"✅ Veículo existente: {vehicle.plate} (ID: {vehicle.id})")

            # Verifica se o horário já está ocupado
            existing = Appointment.query.filter_by(date_time=date_time).first()
            if existing:
                flash('Este horário já está ocupado!', 'warning')
                return redirect(url_for('appointments.schedule_appointment'))

            # Cria o agendamento
            appointment = Appointment(
                date_time=date_time,
                customer_id=customer.id,
                vehicle_id=vehicle.id
            )
            db.session.add(appointment)
            db.session.commit()

            print(f"✅ Agendamento criado com sucesso! ID: {appointment.id}")
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('appointments.get_appointments'))

        except ValueError as e:
            db.session.rollback()
            print(f"❌ Erro de formato: {e}")
            flash('Formato de data/hora inválido!', 'danger')
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar agendamento: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Erro ao criar agendamento: {str(e)}', 'danger')
        
        return redirect(url_for('appointments.schedule_appointment'))

    return render_template('appointment_form.html')


@appointment_bp.route('/occupied/<date>', methods=['GET'])
def get_occupied_times(date):
    """Retorna os horários ocupados do dia"""
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        appointments = Appointment.query.filter(
            db.func.date(Appointment.date_time) == selected_date
        ).all()
        
        # Retorna horários no formato HH:MM
        occupied_times = [a.date_time.strftime("%H:%M") for a in appointments]
        
        print(f"📅 Data consultada: {selected_date}")
        print(f"📊 Total de agendamentos: {len(appointments)}")
        print(f"🕐 Horários ocupados: {occupied_times}")
        
        return jsonify(occupied_times), 200
        
    except Exception as e:
        print(f"❌ Erro ao buscar horários: {e}")
        return jsonify([]), 500