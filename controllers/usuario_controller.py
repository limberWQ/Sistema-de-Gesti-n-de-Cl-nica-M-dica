"""
usuario_controller.py
Responsabilidad exclusiva: CRUD de la tabla `usuarios`.
No crea médicos ni pacientes — eso lo hacen sus propios controllers.
NO hace render_template directamente → delega a views/usuario_view.py
"""
from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required
from database import db, solo_admin
from models.usuario_model import Usuario
from views.usuario_view import render_index, render_crear, render_crear_con_error, render_editar

usuario_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

ROLES_VALIDOS = ('admin', 'medico', 'paciente')


@usuario_bp.route('/')
@login_required
@solo_admin
def index():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_index(usuarios)


@usuario_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@solo_admin
def crear():
    if request.method == 'POST':
        nombre   = request.form.get('nombre', '').strip()
        username = request.form.get('username', '').strip()
        password = f"{username}{'123'}"
        rol      = request.form.get('rol', 'paciente')

        # Validaciones
        if not nombre or not username or not password:
            return render_crear_con_error('Todos los campos son obligatorios.')

        if rol not in ROLES_VALIDOS:
            return render_crear_con_error('Rol no válido.')

        if Usuario.query.filter_by(username=username).first():
            return render_crear_con_error('El nombre de usuario ya existe.')

        try:
            u = Usuario(nombre=nombre, username=username, rol=rol)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash('Usuario creado correctamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception:
            db.session.rollback()
            flash('Error al crear el usuario.', 'danger')

    return render_crear()


@usuario_bp.route('/editar/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
@solo_admin
def editar(id_usuario):
    u = Usuario.query.get_or_404(id_usuario)

    if request.method == 'POST':
        nombre_nuevo   = request.form.get('nombre', '').strip()
        username_nuevo = request.form.get('username', '').strip()
        rol_nuevo      = request.form.get('rol', u.rol)
        nueva_pw       = request.form.get('password', '').strip()

        if not nombre_nuevo or not username_nuevo:
            flash('Nombre y username son obligatorios.', 'warning')
            return render_editar(u)

        if rol_nuevo not in ROLES_VALIDOS:
            flash('Rol no válido.', 'danger')
            return render_editar(u)

        # Verificar username único (excluyendo el propio usuario)
        duplicado = Usuario.query.filter(
            Usuario.username == username_nuevo,
            Usuario.id_usuario != id_usuario
        ).first()
        if duplicado:
            flash('Ese username ya está en uso por otro usuario.', 'warning')
            return render_editar(u)

        try:
            u.nombre   = nombre_nuevo
            u.username = username_nuevo
            u.rol      = rol_nuevo
            if nueva_pw:
                u.set_password(nueva_pw)
            db.session.commit()
            flash('Usuario actualizado correctamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception:
            db.session.rollback()
            flash('Error al actualizar el usuario.', 'danger')

    return render_editar(u)


@usuario_bp.route('/eliminar/<int:id_usuario>', methods=['POST'])
@login_required
@solo_admin
def eliminar(id_usuario):
    u = Usuario.query.get_or_404(id_usuario)
    try:
        db.session.delete(u)
        db.session.commit()
        flash('Usuario eliminado correctamente.', 'info')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar el usuario.', 'danger')
    return redirect(url_for('usuarios.index'))
