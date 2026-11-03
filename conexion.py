"""
conexion.py
Conexión directa a MySQL con mysql-connector.
En el sistema se usa solo para el respaldo y la restauración de la base de datos
(que necesitan SQL crudo). El resto del sistema usa el ORM (modelos.py).
"""
import os
import mysql.connector
from dotenv import load_dotenv

# Lee las credenciales desde el archivo .env (así no quedan escritas en el código)
load_dotenv()


def conectar():
    """Abre y devuelve una nueva conexión a la base de datos SIS_CSE."""
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "SIS_CSE"),
    )
    return conexion