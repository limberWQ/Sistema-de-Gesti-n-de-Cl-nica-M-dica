import os


class Config:

    # Clave secreta para sesiones y seguridad
    # Si existe una variable de entorno SECRET_KEY la usa,
    # caso contrario usa la clave por defecto
    SECRET_KEY = (os.environ.get('SECRET_KEY') or 'clinica-secret-key-2024')

    # Configuración de la base de datos
    # Si existe DATABASE_URL la usa,
    # caso contrario usa SQLite local
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or 'sqlite:///clinica.db')

    # Desactiva notificaciones innecesarias de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False