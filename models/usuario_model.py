from database import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(100), nullable=False)
    username   = db.Column(db.String(50),  unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    rol        = db.Column(db.String(20),  nullable=False)  # 'admin' | 'medico' | 'paciente'

    # Relaciones 1-to-1 (uselist=False)
    # cascade='all, delete-orphan' → al eliminar usuario se eliminan sus perfiles
    medico   = db.relationship('Medico',   back_populates='usuario',
                               uselist=False, cascade='all, delete-orphan')
    paciente = db.relationship('Paciente', back_populates='usuario',
                               uselist=False, cascade='all, delete-orphan')

    # Flask-Login requiere que get_id() devuelva string
    def get_id(self):
        return str(self.id_usuario)

    def set_password(self, raw_password: str) -> None:
        """Genera y almacena el hash seguro de la contraseña"""
        if not raw_password:
            raise ValueError('La contraseña no puede estar vacía')
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verifica la contraseña contra el hash almacenado"""
        return check_password_hash(self.password, raw_password)

    @property
    def tiene_perfil(self) -> bool:
        """True si el usuario ya tiene el perfil que corresponde a su rol"""
        if self.rol == 'medico':
            return self.medico is not None
        if self.rol == 'paciente':
            return self.paciente is not None
        return True  # admin no necesita perfil extra

    def __repr__(self):
        return f'<Usuario {self.username} [{self.rol}]>'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
