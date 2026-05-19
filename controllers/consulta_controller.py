from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required
from database import db, solo_admin
from models.consulta_model import Consulta
from models.medico_model import Medico
from models.paciente_model import Paciente
from models.usuario_model import Usuario
from datetime import datetime
from views.consulta_view import render_listar, render_registrar, render_editar

consulta_bp = Blueprint('consultas', __name__, url_prefix='/consultas')


@consulta_bp.route('/')
@login_required
@solo_admin
def listar():
    consultas = Consulta.query.order_by(Consulta.fecha.desc()).all()
    return render_listar(consultas)


@consulta_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
@solo_admin
def registrar():
    medicos_lista   = Medico.query.join(Usuario).order_by(Usuario.nombre).all()
    pacientes_lista = Paciente.query.join(Usuario).order_by(Usuario.nombre).all()

    if request.method == 'POST':
        fecha_str = request.form.get('fecha', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()
        tratamiento = request.form.get('tratamiento', '').strip()
        id_medico = request.form.get('id_medico', '').strip()
        id_paciente = request.form.get('id_paciente', '').strip()

        if not fecha_str or not diagnostico or not id_medico or not id_paciente:
            flash('Fecha, diagnóstico, médico y paciente son obligatorios.', 'warning')
            return render_registrar(medicos_lista, pacientes_lista)

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return render_registrar(medicos_lista, pacientes_lista)

        try:
            c = Consulta(
                fecha = fecha,
                diagnostico = diagnostico,
                tratamiento = tratamiento,
                id_medico = int(id_medico),
                id_paciente = int(id_paciente)
            )
            db.session.add(c)
            db.session.commit()
            flash('Consulta registrada correctamente.', 'success')
            return redirect(url_for('consultas.listar'))
        except Exception:
            db.session.rollback()
            flash('Error al registrar la consulta.', 'danger')

    return render_registrar(medicos_lista, pacientes_lista)


@consulta_bp.route('/editar/<int:id_consulta>', methods=['GET', 'POST'])
@login_required
@solo_admin
def editar(id_consulta):
    c = Consulta.query.get_or_404(id_consulta)
    medicos_lista = Medico.query.join(Usuario).order_by(Usuario.nombre).all()
    pacientes_lista = Paciente.query.join(Usuario).order_by(Usuario.nombre).all()

    if request.method == 'POST':
        fecha_str = request.form.get('fecha', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()
        tratamiento = request.form.get('tratamiento', '').strip()
        id_medico = request.form.get('id_medico', '').strip()
        id_paciente = request.form.get('id_paciente', '').strip()

        if not diagnostico:
            flash('El diagnóstico es obligatorio.', 'warning')
            return render_editar(c, medicos_lista, pacientes_lista)

        try:
            if fecha_str:
                c.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            c.diagnostico = diagnostico
            c.tratamiento = tratamiento
            if id_medico:
                c.id_medico = int(id_medico)
            if id_paciente:
                c.id_paciente = int(id_paciente)
            db.session.commit()
            flash('Consulta actualizada correctamente.', 'success')
            return redirect(url_for('consultas.listar'))
        except Exception:
            db.session.rollback()
            flash('Error al actualizar la consulta.', 'danger')

    return render_editar(c, medicos_lista, pacientes_lista)


@consulta_bp.route('/eliminar/<int:id_consulta>', methods=['POST'])
@login_required
@solo_admin
def eliminar(id_consulta):
    c = Consulta.query.get_or_404(id_consulta)
    try:
        db.session.delete(c)
        db.session.commit()
        flash('Consulta eliminada.', 'info')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar la consulta.', 'danger')
    return redirect(url_for('consultas.listar'))
