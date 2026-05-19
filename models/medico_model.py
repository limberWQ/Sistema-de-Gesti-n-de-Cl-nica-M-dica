from database import db


class Medico(db.Model):
    __tablename__ = 'medicos'

    id_medico    = db.Column(db.Integer, primary_key=True)
    especialidad = db.Column(db.String(100), nullable=False)
    telefono     = db.Column(db.String(20))
    correo       = db.Column(db.String(120))

    # FK a usuarios — unique=True garantiza la relación 1-to-1
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )

    # Relación 1-to-1 con Usuario
    usuario = db.relationship('Usuario', back_populates='medico')

    # Relación 1-to-N con Consulta
    consultas = db.relationship(
        'Consulta',
        back_populates='medico',
        cascade='all, delete-orphan',
        lazy='select'
    )

    def __repr__(self):
        return f'<Medico id={self.id_medico} especialidad={self.especialidad}>'
