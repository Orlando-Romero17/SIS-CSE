import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from conexion import conectar
from Estilos.css import CONFIGURACION


class ConsultarRegistros(QWidget):
    def __init__(self):
        super().__init__()

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Consultar registros")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)

        sub = QLabel("Busque y consulte información de ciudadanos registrados.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        busqueda = QGroupBox("Búsqueda")
        l = QHBoxLayout(busqueda)
        self.campo = QLineEdit()
        self.campo.setPlaceholderText("Cédula, nombre o apellido")
        self.campo.returnPressed.connect(self.buscar_ciudadanos)
        self.boton = QPushButton("Buscar")
        self.boton.setObjectName("principal")
        self.boton.clicked.connect(self.buscar_ciudadanos)
        l.addWidget(self.campo)
        l.addWidget(self.boton)
        contenido.addWidget(busqueda)

        grupo = QGroupBox("Resultados")
        l = QVBoxLayout(grupo)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["CÉDULA", "NOMBRE", "APELLIDO", "MUNICIPIO", "ESTADO"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.tabla)
        contenido.addWidget(grupo)

        self.cargar_ciudadanos()

    def _consultar(self, filtro=""):
        """Ejecuta la consulta y llena la tabla. Si filtro está vacío, trae todo."""
        try:
            conexion = conectar()
            cursor = conexion.cursor()

            if filtro:
                patron = f"%{filtro}%"
                cursor.execute("""
                    SELECT cedula, nombres, apellidos, municipio, estado
                    FROM ciudadanos
                    WHERE cedula LIKE %s OR nombres LIKE %s OR apellidos LIKE %s
                """, (patron, patron, patron))
            else:
                cursor.execute("""
                    SELECT cedula, nombres, apellidos, municipio, estado
                    FROM ciudadanos
                """)

            registros = cursor.fetchall()
            cursor.close()
            conexion.close()

            self.tabla.setRowCount(len(registros))
            for fila, registro in enumerate(registros):
                for columna, valor in enumerate(registro):
                    self.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

        except Exception as e:
            print("Error:", e)

    def cargar_ciudadanos(self):
        self._consultar()

    def buscar_ciudadanos(self):
        self._consultar(self.campo.text().strip())


# Solo para probar esta página sola (con su propio estilo)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ConsultarRegistros()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())