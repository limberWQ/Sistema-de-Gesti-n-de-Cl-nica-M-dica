from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models.usuario_model import Usuario
from views.auth_view import render_login, render_registro

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Completa todos los campos.', 'warning')
            return render_login()

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            flash(f'Bienvenido/a, {usuario.nombre}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_login()


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        rol = request.form.get('rol', 'paciente')

        # Validaciones
        if not nombre or not username or not password:
            flash('Todos los campos son obligatorios.', 'warning')
            return render_registro()

        if rol not in ('medico', 'paciente'):
            flash('Rol no válido.', 'danger')
            return render_registro()

        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'warning')
            return render_registro()

        try:
            nuevo = Usuario(nombre=nombre, username=username, rol=rol)
            nuevo.set_password(password)
            db.session.add(nuevo)
            db.session.commit()
            flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash('Error al crear la cuenta. Intenta nuevamente.', 'danger')

    return render_registro()


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))
