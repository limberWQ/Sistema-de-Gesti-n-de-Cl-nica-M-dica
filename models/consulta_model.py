from database import db
from datetime import date


class Consulta(db.Model):
    __tablename__ = 'consultas'

    id_consulta = db.Column(db.Integer, primary_key=True)
    fecha       = db.Column(db.Date, nullable=False, default=date.today)
    diagnostico = db.Column(db.Text, nullable=False)
    tratamiento = db.Column(db.Text)
    # FKs — ondelete='CASCADE' como respaldo a nivel DB (SQLAlchemy ya maneja esto con cascade)
    id_medico   = db.Column(
        db.Integer,
        db.ForeignKey('medicos.id_medico', ondelete='CASCADE'),
        nullable=False
    )
    id_paciente = db.Column(
        db.Integer,
        db.ForeignKey('pacientes.id_paciente', ondelete='CASCADE'),
        nullable=False
    )

    # Relaciones N-to-1
    medico   = db.relationship('Medico',   back_populates='consultas')
    paciente = db.relationship('Paciente', back_populates='consultas')

    def __repr__(self):
        return f'<Consulta id={self.id_consulta} fecha={self.fecha}>'
