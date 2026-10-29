"""
modelos.py
Capa ORM del sistema con SQLAlchemy.
Define la conexión (engine), la fábrica de sesiones y las clases Python que
representan las tablas de MySQL (mapeo objeto-relacional).

IMPORTANTE: nunca se llama a create_all(), así que SQLAlchemy NO crea ni
modifica tablas: solo lee y escribe en las que ya existen en MySQL Workbench.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# URL de conexión armada con los datos del .env (URL.create maneja bien
# contraseñas con caracteres especiales)
url = URL.create(
    "mysql+mysqlconnector",
    username=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "SIS_CSE"),
)

# Engine: administra un "pool" de conexiones reutilizables y seguras entre hilos.
# pool_pre_ping verifica que la conexión siga viva antes de usarla.
engine = create_engine(url, pool_pre_ping=True, pool_recycle=1800)

# Cada operación abre su propia sesión: with SessionLocal() as s: ...
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Clase base de la que heredan todos los modelos
Base = declarative_base()


class Usuario(Base):
    """Tabla usuarios: personas con acceso al sistema.
    Se usa 'usuario' como llave del objeto porque es un nombre único."""
    __tablename__ = "usuarios"
    usuario = Column(String(50), primary_key=True)
    nombre_completo = Column(String(100))
    correo = Column(String(100))
    contrasena = Column(String(255))
    rol = Column(String(30))
    estado = Column(String(20))


class Ciudadano(Base):
    """Tabla ciudadanos: registro de ciudadanos (el CRUD principal del sistema)."""
    __tablename__ = "ciudadanos"
    id_ciudadano = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(30))
    nombres = Column(String(100))
    apellidos = Column(String(100))
    fecha_nacimiento = Column(Date)
    genero = Column(String(20))
    departamento = Column(String(60))
    municipio = Column(String(60))
    direccion = Column(String(200))
    telefono = Column(String(30))
    correo = Column(String(100))
    estado = Column(String(20))


class Configuracion(Base):
    """Tabla configuracion: opciones generales del sistema (una sola fila)."""
    __tablename__ = "configuracion"
    id_configuracion = Column(Integer, primary_key=True)
    nombre_institucion = Column(String(150))
    idioma = Column(String(30))
    tema = Column(String(30))


class Reporte(Base):
    """Tabla reportes: bitácora de los reportes que se han generado."""
    __tablename__ = "reportes"
    tipo_reporte = Column(String(60), primary_key=True)
    fecha_inicio = Column(Date, primary_key=True)
    fecha_fin = Column(Date, primary_key=True)


class Respaldo(Base):
    """Tabla respaldos: historial de copias de seguridad realizadas."""
    __tablename__ = "respaldos"
    fecha_respaldo = Column(DateTime, primary_key=True)
    nombre_bd = Column(String(60), primary_key=True)
    descripcion = Column(Text)