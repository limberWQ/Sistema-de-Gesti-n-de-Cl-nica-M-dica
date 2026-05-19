from database import db


class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id_paciente = db.Column(db.Integer, primary_key=True)
    edad        = db.Column(db.Integer)
    direccion   = db.Column(db.String(200))
    telefono    = db.Column(db.String(20))

    # FK a usuarios — unique=True garantiza la relación 1-to-1
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )

    # Relación 1-to-1 con Usuario
    usuario = db.relationship('Usuario', back_populates='paciente')

    # Relación 1-to-N con Consulta
    consultas = db.relationship(
        'Consulta',
        back_populates='paciente',
        cascade='all, delete-orphan',
        lazy='select'
    )

    def __repr__(self):
        return f'<Paciente id={self.id_paciente}>'
