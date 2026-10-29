import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import QDate
from conexion import conectar
from Estilos.css import CONFIGURACION
from utilidades import exportar_tabla

# tipo de reporte -> (consulta base, columna de fecha para filtrar o None)
# Si su tabla tiene una columna de fecha (ej. "fecha_registro"), escríbala
# en lugar de None y el reporte respetará el rango de fechas.
REPORTES = {
    "Registros de ciudadanos": (
        "SELECT cedula, nombres, apellidos, municipio, estado FROM ciudadanos", None),
    "Trámites": ("SELECT * FROM tramites", None),
    "Usuarios del sistema": (
        "SELECT usuario, nombre_completo, correo, rol, estado FROM usuarios", None),
}


class Reportes(QWidget):
    def __init__(self):
        super().__init__()

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Reportes")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)

        sub = QLabel("Genere reportes de la información registrada en el sistema.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        grupo = QGroupBox("Generar reporte")
        l = QVBoxLayout(grupo)

        l.addWidget(QLabel("Tipo de reporte"))
        self.tipo = QComboBox()
        self.tipo.addItems(["Seleccione"] + list(REPORTES.keys()))
        l.addWidget(self.tipo)

        l.addWidget(QLabel("Fecha inicial"))
        self.inicio = QDateEdit()
        self.inicio.setCalendarPopup(True)
        self.inicio.setDate(QDate.currentDate())
        l.addWidget(self.inicio)

        l.addWidget(QLabel("Fecha final"))
        self.fin = QDateEdit()
        self.fin.setCalendarPopup(True)
        self.fin.setDate(QDate.currentDate())
        l.addWidget(self.fin)

        fila = QHBoxLayout()
        generar = QPushButton("Generar reporte")
        generar.setObjectName("principal")
        generar.clicked.connect(self.guardar_reporte)
        exportar = QPushButton("Exportar")
        exportar.setObjectName("secundario")
        exportar.clicked.connect(self.exportar)
        fila.addStretch()
        fila.addWidget(exportar)
        fila.addWidget(generar)
        l.addLayout(fila)
        contenido.addWidget(grupo)

        self.mensaje = QLabel("")
        contenido.addWidget(self.mensaje)

        resultado = QGroupBox("Vista previa del reporte")
        rl = QVBoxLayout(resultado)
        self.tabla = QTableWidget()
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        rl.addWidget(self.tabla)
        contenido.addWidget(resultado, 1)

    def guardar_reporte(self):
        if self.tipo.currentIndex() == 0:
            self.mensaje.setText("Seleccione un tipo de reporte")
            return

        if self.inicio.date() > self.fin.date():
            self.mensaje.setText("La fecha inicial no puede ser mayor que la final")
            return

        tipo = self.tipo.currentText()
        sql, col_fecha = REPORTES[tipo]
        params = ()
        if col_fecha:
            sql += f" WHERE DATE({col_fecha}) BETWEEN %s AND %s"
            params = (self.inicio.date().toString("yyyy-MM-dd"),
                      self.fin.date().toString("yyyy-MM-dd"))

        # 1) Obtener los datos y mostrarlos
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(sql, params)
            encabezados = [d[0].upper() for d in cursor.description]
            filas = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Exception as e:
            self.mensaje.setText(f"Error al generar el reporte: {e}")
            return

        self.tabla.setColumnCount(len(encabezados))
        self.tabla.setHorizontalHeaderLabels(encabezados)
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, v in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem("" if v is None else str(v)))

        # 2) Registrar que se generó el reporte
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO reportes (tipo_reporte, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s)
            """, (
                tipo,
                self.inicio.date().toString("yyyy-MM-dd"),
                self.fin.date().toString("yyyy-MM-dd"),
            ))
            conexion.commit()
            cursor.close()
            conexion.close()
            self.mensaje.setText(f"Reporte generado correctamente ({len(filas)} registros)")
        except Exception as e:
            self.mensaje.setText(f"Reporte mostrado, pero no se pudo registrar: {e}")

    def exportar(self):
        if self.tabla.rowCount() == 0:
            self.mensaje.setText("Primero genere un reporte para poder exportarlo")
            return
        exportar_tabla(self, self.tabla, self.tipo.currentText().replace(" ", "_").lower())


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Reportes()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())
