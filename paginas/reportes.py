import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QComboBox, QDateEdit
)
from PySide6.QtCore import QDate
from conexion import conectar
from Estilos.css import CONFIGURACION


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
        self.tipo.addItems([
            "Seleccione",
            "Registros de ciudadanos",
            "Trámites",
            "Usuarios del sistema",
        ])
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
        fila.addStretch()
        fila.addWidget(exportar)
        fila.addWidget(generar)
        l.addLayout(fila)
        contenido.addWidget(grupo)

        self.mensaje = QLabel("")
        contenido.addWidget(self.mensaje)
        contenido.addStretch()

    def guardar_reporte(self):
        if self.tipo.currentIndex() == 0:
            self.mensaje.setText("Seleccione un tipo de reporte")
            return

        if self.inicio.date() > self.fin.date():
            self.mensaje.setText("La fecha inicial no puede ser mayor que la final")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO reportes (tipo_reporte, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s)
            """, (
                self.tipo.currentText(),
                self.inicio.date().toString("yyyy-MM-dd"),
                self.fin.date().toString("yyyy-MM-dd"),
            ))
            conexion.commit()
            cursor.close()
            conexion.close()

            self.mensaje.setText("Reporte generado correctamente")

        except Exception as e:
            self.mensaje.setText(f"Error: {e}")


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Reportes()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())
