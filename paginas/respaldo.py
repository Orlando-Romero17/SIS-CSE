"""
respaldo.py
Ventana de copias de seguridad de la base de datos:
  - Realizar respaldo: genera un archivo .sql con estructura y datos.
  - Restaurar respaldo: carga un .sql creado por este sistema.
  - Historial: lista los respaldos hechos (tabla respaldos, con ORM).
El respaldo y la restauración corren en un hilo para no congelar la ventana.
"""
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
from hilos.trabajador import ejecutar_en_hilo
from repositorio import listar_respaldos, registrar_respaldo

# Primera línea de todo respaldo: sirve para validar el archivo al restaurar
CABECERA = "-- Respaldo SIS-CSE"


def _literal(v):
    """Convierte un valor de Python a texto SQL (para escribir los INSERT)."""
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
    # Texto: se escapan comillas, barras y saltos de línea
    s = (str(v).replace("\\", "\\\\").replace("'", "\\'")
         .replace("\n", "\\n").replace("\r", "\\r").replace("\0", "\\0"))
    return "'" + s + "'"


def generar_dump(ruta):
    """Escribe en 'ruta' un archivo .sql con la estructura y los datos de todas
    las tablas. Cada sentencia ocupa una línea (así es fácil restaurarlo)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
    tablas = [f[0] for f in cursor.fetchall()]

    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{CABECERA} - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write("SET FOREIGN_KEY_CHECKS=0;\n")
        for t in tablas:
            # Estructura de la tabla
            cursor.execute(f"SHOW CREATE TABLE `{t}`")
            create = cursor.fetchone()[1].replace("\r", " ").replace("\n", " ")
            f.write(f"DROP TABLE IF EXISTS `{t}`;\n{create};\n")
            # Datos de la tabla, de 500 en 500 filas
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
    """Ejecuta un archivo .sql creado por este sistema, reemplazando las tablas."""
    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.read().splitlines()
    # Seguridad: solo se aceptan archivos generados por este sistema
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


def hacer_respaldo(ruta, base, descripcion):
    """Crea el archivo de respaldo y lo anota en el historial (ORM).
    Se ejecuta en un hilo. Devuelve (cantidad de tablas, tamaño en KB)."""
    n = generar_dump(ruta)
    tam = os.path.getsize(ruta) / 1024
    registrar_respaldo(base, descripcion)
    return n, tam


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

        # Datos del respaldo: base de datos y descripción opcional
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
        self.btn_restaurar = QPushButton("Restaurar respaldo...")
        self.btn_restaurar.setObjectName("secundario")
        self.btn_restaurar.clicked.connect(self.restaurar_respaldo)
        self.btn_realizar = QPushButton("Realizar respaldo")
        self.btn_realizar.setObjectName("principal")
        self.btn_realizar.clicked.connect(self.guardar_respaldo)
        botones.addWidget(self.btn_restaurar)
        botones.addWidget(self.btn_realizar)
        il.addLayout(botones)
        contenido.addWidget(info)

        # Historial de respaldos anteriores
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

    def _bloquear(self, bloqueado):
        """Desactiva los botones mientras hay un respaldo o restauración en curso."""
        self.btn_realizar.setEnabled(not bloqueado)
        self.btn_restaurar.setEnabled(not bloqueado)

    def cargar_historial(self):
        """READ: trae el historial de respaldos (ORM) en segundo plano."""
        ejecutar_en_hilo(
            listar_respaldos,
            al_terminar=self._mostrar_historial,
            al_error=lambda m: self.mensaje.setText(f"No se pudo cargar el historial: {m}"),
        )

    def _mostrar_historial(self, filas):
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, v in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem("" if v is None else str(v)))

    def guardar_respaldo(self):
        """Pide dónde guardar el archivo y lanza el respaldo en un hilo."""
        nombre_sugerido = (f"respaldo_{self.base.text()}_"
                           f"{datetime.datetime.now():%Y%m%d_%H%M%S}.sql")
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar respaldo", nombre_sugerido, "Archivo SQL (*.sql)"
        )
        if not ruta:
            return
        if not ruta.lower().endswith(".sql"):
            ruta += ".sql"

        self._bloquear(True)
        self.mensaje.setText("Realizando respaldo, espere...")
        ejecutar_en_hilo(
            hacer_respaldo, ruta, self.base.text(), self.descripcion.toPlainText(),
            al_terminar=self._respaldo_listo,
            al_error=self._respaldo_error,
        )

    def _respaldo_listo(self, resultado):
        n, tam = resultado
        self._bloquear(False)
        self.descripcion.clear()
        self.mensaje.setText(f"Respaldo completado: {n} tablas, {tam:.1f} KB.")
        self.cargar_historial()

    def _respaldo_error(self, mensaje):
        self._bloquear(False)
        self.mensaje.setText(f"Error: {mensaje}")

    def restaurar_respaldo(self):
        """Pide el archivo .sql, confirma y restaura en un hilo."""
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

        self._bloquear(True)
        self.mensaje.setText("Restaurando, espere...")
        ejecutar_en_hilo(
            restaurar_dump, ruta,
            al_terminar=self._restauracion_lista,
            al_error=self._respaldo_error,
        )

    def _restauracion_lista(self, _):
        self._bloquear(False)
        self.mensaje.setText("Respaldo restaurado correctamente.")
        self.cargar_historial()


# Solo para probar esta ventana sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = RespaldoInformacion()
    ventana.exec()
