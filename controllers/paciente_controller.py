from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from database import db, solo_admin, solo_roles
from models.paciente_model import Paciente
from models.consulta_model import Consulta
from models.usuario_model import Usuario
from views.paciente_view import (
    render_listar, render_registrar, render_registrar_con_error,
    render_editar, render_listar_consultas, render_cancelar_consulta
)

paciente_bp = Blueprint('pacientes', __name__, url_prefix='/pacientes')


# ── Admin: gestión de perfiles de paciente ──────────────────────────

@paciente_bp.route('/')
@login_required
@solo_admin
def listar():
    """Lista todos los pacientes registrados."""
    pacientes = Paciente.query.join(Usuario).order_by(Usuario.nombre).all()
    return render_listar(pacientes)


@paciente_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
@solo_admin
def registrar():
    """
    Asigna perfil de paciente a un usuario existente con rol='paciente'.
    Solo muestra usuarios que aún NO tienen perfil de paciente.

    ── Por qué fallaba antes ──────────────────────────────────────────
    El código original hacía:
        p = Paciente(id_usuario=id_usuario, ...)
        db.session.add(p)
        db.session.commit()
    Sin verificar si id_usuario era None, vacío o apuntaba a un usuario
    inexistente. Cuando el formulario enviaba id_usuario='' (campo vacío),
    SQLAlchemy intentaba insertar NULL en la columna NOT NULL → IntegrityError.
    Sin rollback, la sesión quedaba "sucia" y los siguientes commits
    fallaban también (error: "Esta sesión está en estado de error").
    """
    usuarios_disponibles = (
        Usuario.query
        .filter_by(rol='paciente')
        .filter(~Usuario.paciente.has())
        .order_by(Usuario.nombre)
        .all()
    )

    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario', '').strip()
        edad       = request.form.get('edad', '').strip()
        direccion  = request.form.get('direccion', '').strip()
        telefono   = request.form.get('telefono', '').strip()

        # ── Validación 1: campo obligatorio ──────────────────────────
        if not id_usuario:
            return render_registrar_con_error(
                usuarios_disponibles,
                'Debes seleccionar un usuario.')

        # ── Validación 2: id numérico ─────────────────────────────────
        try:
            id_usuario = int(id_usuario)
        except ValueError:
            return render_registrar_con_error(
                usuarios_disponibles,
                'ID de usuario no válido.')

        # ── Validación 3: el usuario existe ──────────────────────────
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return render_registrar_con_error(
                usuarios_disponibles,
                'El usuario seleccionado no existe.')

        # ── Validación 4: el usuario tiene rol correcto ──────────────
        if usuario.rol != 'paciente':
            return render_registrar_con_error(
                usuarios_disponibles,
                'El usuario seleccionado no tiene rol de paciente.')

        # ── Validación 5: evitar duplicado ───────────────────────────
        if Paciente.query.filter_by(id_usuario=id_usuario).first():
            return render_registrar_con_error(
                usuarios_disponibles,
                'Este usuario ya tiene perfil de paciente.')

        # ── Validación 6: edad numérica si se ingresó ────────────────
        edad_int = None
        if edad:
            try:
                edad_int = int(edad)
                if edad_int < 0 or edad_int > 150:
                    raise ValueError
            except ValueError:
                return render_registrar_con_error(
                    usuarios_disponibles,
                    'La edad debe ser un número entre 0 y 150.')

        # ── Persistencia con rollback en caso de error ────────────────
        try:
            p = Paciente(
                id_usuario=id_usuario,
                edad=edad_int,
                direccion=direccion,
                telefono=telefono
            )
            db.session.add(p)
            db.session.commit()
            flash('Perfil de paciente registrado correctamente.', 'success')
            return redirect(url_for('pacientes.listar'))
        except Exception as exc:
            db.session.rollback()
            flash(f'Error al registrar el paciente: {exc}', 'danger')

    return render_registrar(usuarios_disponibles)


@paciente_bp.route('/editar/<int:id_paciente>', methods=['GET', 'POST'])
@login_required
@solo_admin
def editar(id_paciente):
    p = Paciente.query.get_or_404(id_paciente)

    if request.method == 'POST':
        edad      = request.form.get('edad', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono  = request.form.get('telefono', '').strip()

        edad_int = None
        if edad:
            try:
                edad_int = int(edad)
                if edad_int < 0 or edad_int > 150:
                    raise ValueError
            except ValueError:
                flash('La edad debe ser un número entre 0 y 150.', 'warning')
                return render_editar(p)

        try:
            p.edad      = edad_int
            p.direccion = direccion
            p.telefono  = telefono
            db.session.commit()
            flash('Paciente actualizado correctamente.', 'success')
            return redirect(url_for('pacientes.listar'))
        except Exception:
            db.session.rollback()
            flash('Error al actualizar el paciente.', 'danger')

    return render_editar(p)


@paciente_bp.route('/eliminar/<int:id_paciente>', methods=['POST'])
@login_required
@solo_admin
def eliminar(id_paciente):
    p = Paciente.query.get_or_404(id_paciente)
    try:
        db.session.delete(p)
        db.session.commit()
        flash('Perfil de paciente eliminado.', 'info')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar el paciente.', 'danger')
    return redirect(url_for('pacientes.listar'))


# ── Paciente (y admin): ver consultas ───────────────────────────────

@paciente_bp.route('/mis-consultas')
@login_required
@solo_roles('paciente', 'admin')
def listar_consultas():
    if current_user.rol == 'admin':
        consultas = Consulta.query.order_by(Consulta.fecha.desc()).all()
    else:
        paciente = current_user.paciente
        if not paciente:
            flash('Tu cuenta aún no tiene un perfil de paciente asignado.', 'warning')
            return redirect(url_for('dashboard'))
        consultas = (
            Consulta.query
            .filter_by(id_paciente=paciente.id_paciente)
            .order_by(Consulta.fecha.desc())
            .all()
        )
    return render_listar_consultas(consultas)


# ── Paciente: cancelar consulta ─────────────────────────────────────

@paciente_bp.route('/cancelar-consulta/<int:id_consulta>', methods=['GET', 'POST'])
@login_required
@solo_roles('paciente', 'admin')
def cancelar_consulta(id_consulta):
    consulta = Consulta.query.get_or_404(id_consulta)

    # El paciente solo puede cancelar sus propias consultas
    if current_user.rol == 'paciente':
        paciente = current_user.paciente
        if not paciente or consulta.id_paciente != paciente.id_paciente:
            abort(403)

    if request.method == 'POST':
        try:
            db.session.delete(consulta)
            db.session.commit()
            flash('Consulta cancelada correctamente.', 'info')
        except Exception:
            db.session.rollback()
            flash('Error al cancelar la consulta.', 'danger')
        return redirect(url_for('pacientes.listar_consultas'))

    return render_cancelar_consulta(consulta)
