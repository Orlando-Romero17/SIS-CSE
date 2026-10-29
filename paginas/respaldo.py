import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import decimal
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFileDialog, QMessageBox
)
from conexion import conectar
from Estilos.css import CONFIGURACION

CABECERA = "-- Respaldo SIS-CSE"


def _literal(v):
    """Convierte un valor de Python a literal SQL."""
    if v is None:
        return "NULL"
    if isinstance(v, (bytes, bytearray)):
        return "0x" + bytes(v).hex() if v else "''"
    if isinstance(v, bool):
        return str(int(v))
    if isinstance(v, (int, float, decimal.Decimal)):
        return str(v)
    if isinstance(v, (datetime.datetime, datetime.date, datetime.time, datetime.timedelta)):
        return "'" + str(v) + "'"
    if isinstance(v, set):
        v = ",".join(sorted(v))
    s = (str(v).replace("\\", "\\\\").replace("'", "\\'")
         .replace("\n", "\\n").replace("\r", "\\r").replace("\0", "\\0"))
    return "'" + s + "'"


def generar_dump(ruta):
    """Escribe un .sql con estructura y datos. Una sentencia por línea."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
    tablas = [f[0] for f in cursor.fetchall()]

    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{CABECERA} - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write("SET FOREIGN_KEY_CHECKS=0;\n")
        for t in tablas:
            cursor.execute(f"SHOW CREATE TABLE `{t}`")
            create = cursor.fetchone()[1].replace("\r", " ").replace("\n", " ")
            f.write(f"DROP TABLE IF EXISTS `{t}`;\n{create};\n")
            cursor.execute(f"SELECT * FROM `{t}`")
            cols = ",".join(f"`{d[0]}`" for d in cursor.description)
            while True:
                bloque = cursor.fetchmany(500)
                if not bloque:
                    break
                for fila in bloque:
                    vals = ",".join(_literal(v) for v in fila)
                    f.write(f"INSERT INTO `{t}` ({cols}) VALUES ({vals});\n")
        f.write("SET FOREIGN_KEY_CHECKS=1;\n")

    cursor.close()
    conexion.close()
    return len(tablas)


def restaurar_dump(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.read().splitlines()
    if not lineas or not lineas[0].startswith(CABECERA):
        raise ValueError("El archivo no es un respaldo generado por este sistema.")

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        for linea in lineas:
            linea = linea.strip()
            if linea and not linea.startswith("--"):
                cursor.execute(linea)
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


class RespaldoInformacion(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Respaldo de información")
        self.setStyleSheet(CONFIGURACION)
        self.resize(780, 620)
        self.setModal(True)

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(25, 20, 25, 20)
        contenido.setSpacing(8)

        titulo = QLabel("Respaldo de información")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)
        sub = QLabel("Realice y restaure copias de seguridad de la base de datos.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        info = QGroupBox("Información del respaldo")
        il = QVBoxLayout(info)
        il.addWidget(QLabel("Base de datos"))
        self.base = QLineEdit(os.getenv("DB_NAME", "SIS_CSE"))
        self.base.setReadOnly(True)
        il.addWidget(self.base)
        il.addWidget(QLabel("Descripción (opcional)"))
        self.descripcion = QTextEdit()
        self.descripcion.setFixedHeight(80)
        il.addWidget(self.descripcion)

        botones = QHBoxLayout()
        botones.addStretch()
        restaurar = QPushButton("Restaurar respaldo...")
        restaurar.setObjectName("secundario")
        restaurar.clicked.connect(self.restaurar_respaldo)
        realizar = QPushButton("Realizar respaldo")
        realizar.setObjectName("principal")
        realizar.clicked.connect(self.guardar_respaldo)
        botones.addWidget(restaurar)
        botones.addWidget(realizar)
        il.addLayout(botones)
        contenido.addWidget(info)

        hist = QGroupBox("Historial de respaldos")
        hl = QVBoxLayout(hist)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["FECHA", "BASE DE DATOS", "DESCRIPCIÓN"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        hl.addWidget(self.tabla)
        contenido.addWidget(hist, 1)

        self.mensaje = QLabel("")
        contenido.addWidget(self.mensaje)

        cerrar = QPushButton("Cerrar")
        cerrar.setObjectName("secundario")
        cerrar.clicked.connect(self.accept)
        fila = QHBoxLayout()
        fila.addStretch()
        fila.addWidget(cerrar)
        contenido.addLayout(fila)

        self.cargar_historial()

    def cargar_historial(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT fecha_respaldo, nombre_bd, descripcion
                FROM respaldos ORDER BY fecha_respaldo DESC LIMIT 50
            """)
            filas = cursor.fetchall()
            cursor.close()
            conexion.close()
            self.tabla.setRowCount(len(filas))
            for i, fila in enumerate(filas):
                for j, v in enumerate(fila):
                    self.tabla.setItem(i, j, QTableWidgetItem("" if v is None else str(v)))
        except Exception as e:
            self.mensaje.setText(f"No se pudo cargar el historial: {e}")

    def guardar_respaldo(self):
        nombre_sugerido = f"respaldo_{self.base.text()}_{datetime.datetime.now():%Y%m%d_%H%M%S}.sql"
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar respaldo", nombre_sugerido, "Archivo SQL (*.sql)"
        )
        if not ruta:
            return
        if not ruta.lower().endswith(".sql"):
            ruta += ".sql"

        try:
            n = generar_dump(ruta)
            tam = os.path.getsize(ruta) / 1024

            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO respaldos (nombre_bd, descripcion, fecha_respaldo)
                VALUES (%s, %s, NOW())
            """, (self.base.text(), self.descripcion.toPlainText()))
            conexion.commit()
            cursor.close()
            conexion.close()

            self.descripcion.clear()
            self.mensaje.setText(f"Respaldo completado: {n} tablas, {tam:.1f} KB.")
            self.cargar_historial()
        except Exception as e:
            self.mensaje.setText(f"Error: {e}")

    def restaurar_respaldo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar respaldo", "", "Archivo SQL (*.sql)"
        )
        if not ruta:
            return
        r = QMessageBox.warning(
            self, "Restaurar respaldo",
            "Esto REEMPLAZARÁ todas las tablas actuales con el contenido del archivo.\n"
            "Los datos actuales se perderán. ¿Desea continuar?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if r != QMessageBox.Yes:
            return
        try:
            restaurar_dump(ruta)
            self.mensaje.setText("Respaldo restaurado correctamente.")
            self.cargar_historial()
        except Exception as e:
            self.mensaje.setText(f"Error al restaurar: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = RespaldoInformacion()
    ventana.exec()
