from flask import Flask, render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from config import Config
from database import db, login_manager
from datetime import date

def create_app(config_class=Config):

    # Crear la aplicación Flask
    app = Flask(__name__)

    # Cargar configuraciones desde Config
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    # Crear tablas y usuario administrador
    with app.app_context():

        # Importar modelos para registrarlos en SQLAlchemy
        import models

        # Crear tablas en la base de datos
        db.create_all()

        from models.usuario_model import Usuario

        # Crear admin por defecto si no existe
        if not Usuario.query.filter_by(username='admin').first():

            admin = Usuario(
                nombre='Administrador',
                username='admin',
                rol='admin'
            )

            # Asignar contraseña al admin
            admin.set_password('admin123')

            # Guardar admin en la BD
            db.session.add(admin)
            db.session.commit()

    # Importar blueprints
    from controllers.auth_controller import auth_bp
    from controllers.usuario_controller import usuario_bp
    from controllers.medico_controller import medico_bp
    from controllers.paciente_controller import paciente_bp
    from controllers.consulta_controller import consulta_bp

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(medico_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(consulta_bp)

    # Error 403 - acceso denegado
    @app.errorhandler(403)
    def acceso_denegado(e):
        return render_template('403.html'), 403

    # Error 404 - página no encontrada
    @app.errorhandler(404)
    def no_encontrado(e):
        return render_template('404.html'), 404

    # Variable global disponible en todas las plantillas
    @app.context_processor
    def inject_globals():
        return {
            'today': date.today().isoformat()
        }

    # Ruta principal del sistema
    @app.route('/')

    # Requiere iniciar sesión
    @login_required
    def dashboard():

        # Importar modelos
        from models.usuario_model import Usuario
        from models.medico_model import Medico
        from models.paciente_model import Paciente
        from models.consulta_model import Consulta

        # Obtener rol del usuario actual
        rol = current_user.rol

        # Dashboard para administrador
        if rol == 'admin':

            # Obtener últimas 5 consultas
            ultimas = (
                Consulta.query.order_by(Consulta.fecha.desc()).limit(5).all())

            return render_template(
                'dashboard.html',

                # Estadísticas generales
                total_usuarios=Usuario.query.count(),
                total_medicos=Medico.query.count(),
                total_pacientes=Paciente.query.count(),
                total_consultas=Consulta.query.count(),

                # Últimas consultas
                ultimas_consultas=ultimas,
            )

        # Dashboard para médico
        if rol == 'medico':

            # Obtener perfil médico del usuario
            medico = current_user.medico

            # Verificar si tiene perfil
            if not medico:
                return render_template('dashboard.html', sin_perfil=True)

            # Obtener últimas consultas del médico
            consultas = (Consulta.query.filter_by(id_medico=medico.id_medico).order_by(Consulta.fecha.desc()).limit(5).all())

            return render_template('dashboard.html',consultas=consultas,medico=medico)

        # Dashboard para paciente
        if rol == 'paciente':

            # Obtener perfil paciente
            paciente = current_user.paciente

            # Verificar si tiene perfil
            if not paciente:
                return render_template('dashboard.html',sin_perfil=True)

            # Obtener consultas del paciente
            consultas = (Consulta.query.filter_by(id_paciente=paciente.id_paciente).order_by(Consulta.fecha.desc()).limit(5).all())

            return render_template('dashboard.html',consultas=consultas,paciente=paciente)

        # Si no tiene permisos
        abort(403)

    # Retornar aplicación Flask
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
