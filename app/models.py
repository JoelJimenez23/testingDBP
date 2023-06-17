from flask_sqlalchemy import SQLAlchemy
from config.local import config
import uuid
from datetime import datetime

db = SQLAlchemy()

def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = config['DATABASE_URI'] if database_path is None else database_path
    app.debug = True  # Enable debug mode
    db.init_app(app)
    db.create_all()


class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(120), unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    cursoId = db.Column(db.String(36), db.ForeignKey('cursos.id'), nullable=False)
    files = db.relationship('File', backref='estudiante', lazy=True)

    def __init__(self, firstName, lastName, age, cursoId):
        self.firstName = firstName
        self.lastName = lastName
        self.age = age
        self.cursoId = cursoId

    def __repr__(self):
        return '<Estudiante %r %r>' % (self.firstName, self.lastName)

    def serialize(self):
        return {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'age': self.age,
            'image': self.image,
            'cursoId': self.cursoId,
        }


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(120), nullable=False)
    estudianteId = db.Column(db.String(36), db.ForeignKey('estudiantes.id'), nullable=False)
    
    def __init__(self, filename, estudianteId):
        self.filename = filename
        self.estudianteId = estudianteId

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    short_name = db.Column(db.String(20), nullable=False)
    estudiantes = db.relationship('Estudiante', backref='curso', lazy=True)

    def __init__(self, name, short_name):
        self.name = name
        self.short_name = short_name
    
    def __repr__(self):
        return '<Curso %r %r>' % (self.name, self.short_name)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name
        }
