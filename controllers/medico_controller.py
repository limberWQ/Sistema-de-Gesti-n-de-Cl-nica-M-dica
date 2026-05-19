from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db, solo_admin, solo_roles
from models.medico_model import Medico
from models.paciente_model import Paciente
from models.consulta_model import Consulta
from models.usuario_model import Usuario
from datetime import datetime
from views.medico_view import (
    render_listar, render_registrar, render_registrar_con_error,
    render_editar, render_listar_consultas, render_registrar_consulta
)

medico_bp = Blueprint('medicos', __name__, url_prefix='/medicos')


# ---------------Admin: gestión de perfiles de médico -------------------------

@medico_bp.route('/')
@login_required
@solo_admin
def listar():
    """Lista todos los médicos registrados."""
    medicos = Medico.query.join(Usuario).order_by(Usuario.nombre).all()
    return render_listar(medicos)


@medico_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
@solo_admin
def registrar():
    """
    Asigna perfil de médico a un usuario existente con rol='medico'.
    Solo muestra usuarios que aún NO tienen perfil de médico.
    """
    usuarios_disponibles = (
        Usuario.query
        .filter_by(rol='medico')
        .filter(~Usuario.medico.has())
        .order_by(Usuario.nombre)
        .all()
    )

    if request.method == 'POST':
        id_usuario   = request.form.get('id_usuario', '').strip()
        especialidad = request.form.get('especialidad', '').strip()
        telefono     = request.form.get('telefono', '').strip()
        correo       = request.form.get('correo', '').strip()

        #------Validaciones ---------------
        if not id_usuario or not especialidad:
            return render_registrar_con_error(
                usuarios_disponibles, 'Usuario y especialidad son obligatorios.')

        try:
            id_usuario = int(id_usuario)
        except ValueError:
            return render_registrar_con_error(
                usuarios_disponibles, 'ID de usuario no válido.')

        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return render_registrar_con_error(
                usuarios_disponibles, 'El usuario seleccionado no existe.')

        if usuario.rol != 'medico':
            return render_registrar_con_error(
                usuarios_disponibles, 'El usuario no tiene rol de médico.')

        # Evitar duplicado (aunque la UI ya lo filtra, validar en backend)
        if Medico.query.filter_by(id_usuario=id_usuario).first():
            return render_registrar_con_error(
                usuarios_disponibles, 'Este usuario ya tiene perfil de médico.')

        try:
            m = Medico(
                id_usuario=id_usuario,
                especialidad=especialidad,
                telefono=telefono,
                correo=correo
            )
            db.session.add(m)
            db.session.commit()
            flash('Perfil de médico registrado correctamente.', 'success')
            return redirect(url_for('medicos.listar'))
        except Exception:
            db.session.rollback()
            flash('Error al registrar el médico.', 'danger')

    return render_registrar(usuarios_disponibles)


@medico_bp.route('/editar/<int:id_medico>', methods=['GET', 'POST'])
@login_required
@solo_admin
def editar(id_medico):
    m = Medico.query.get_or_404(id_medico)

    if request.method == 'POST':
        especialidad = request.form.get('especialidad', '').strip()
        if not especialidad:
            flash('La especialidad es obligatoria.', 'warning')
            return render_editar(m)

        try:
            m.especialidad = especialidad
            m.telefono     = request.form.get('telefono', '').strip()
            m.correo       = request.form.get('correo', '').strip()
            db.session.commit()
            flash('Médico actualizado correctamente.', 'success')
            return redirect(url_for('medicos.listar'))
        except Exception:
            db.session.rollback()
            flash('Error al actualizar el médico.', 'danger')

    return render_editar(m)


@medico_bp.route('/eliminar/<int:id_medico>', methods=['POST'])
@login_required
@solo_admin
def eliminar(id_medico):
    m = Medico.query.get_or_404(id_medico)
    try:
        db.session.delete(m)
        db.session.commit()
        flash('Perfil de médico eliminado.', 'info')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar el médico.', 'danger')
    return redirect(url_for('medicos.listar'))


# ── Médico (y admin): ver consultas ─────────────────────────────────

@medico_bp.route('/mis-consultas')
@login_required
@solo_roles('medico', 'admin')
def listar_consultas():
    if current_user.rol == 'admin':
        consultas = Consulta.query.order_by(Consulta.fecha.desc()).all()
    else:
        medico = current_user.medico
        if not medico:
            flash('Tu cuenta aún no tiene un perfil de médico asignado.', 'warning')
            return redirect(url_for('dashboard'))
        consultas = (
            Consulta.query
            .filter_by(id_medico=medico.id_medico)
            .order_by(Consulta.fecha.desc())
            .all()
        )
    return render_listar_consultas(consultas)


# ── Médico (y admin): registrar consulta ────────────────────────────

@medico_bp.route('/registrar-consulta', methods=['GET', 'POST'])
@login_required
@solo_roles('medico', 'admin')
def registrar_consulta():
    medicos_lista   = Medico.query.join(Usuario).order_by(Usuario.nombre).all()
    pacientes_lista = Paciente.query.join(Usuario).order_by(Usuario.nombre).all()

    if request.method == 'POST':
        fecha_str   = request.form.get('fecha', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()
        tratamiento = request.form.get('tratamiento', '').strip()
        id_paciente = request.form.get('id_paciente', '').strip()

        if not fecha_str or not diagnostico or not id_paciente:
            flash('Fecha, diagnóstico y paciente son obligatorios.', 'warning')
            return render_registrar_consulta(medicos_lista, pacientes_lista)

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return render_registrar_consulta(medicos_lista, pacientes_lista)

        # El médico usa su propio perfil; el admin elige
        if current_user.rol == 'medico':
            medico = current_user.medico
            if not medico:
                flash('Tu cuenta no tiene perfil de médico asignado.', 'warning')
                return redirect(url_for('dashboard'))
            id_medico = medico.id_medico
        else:
            id_medico = request.form.get('id_medico', '').strip()
            if not id_medico:
                flash('Debes seleccionar un médico.', 'warning')
                return render_registrar_consulta(medicos_lista, pacientes_lista)

        try:
            c = Consulta(
                fecha=fecha,
                diagnostico=diagnostico,
                tratamiento=tratamiento,
                id_medico=int(id_medico),
                id_paciente=int(id_paciente)
            )
            db.session.add(c)
            db.session.commit()
            flash('Consulta registrada correctamente.', 'success')
            return redirect(url_for('medicos.listar_consultas'))
        except Exception:
            db.session.rollback()
            flash('Error al registrar la consulta.', 'danger')

    return render_registrar_consulta(medicos_lista, pacientes_lista)
