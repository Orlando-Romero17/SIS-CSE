import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt
from conexion import conectar
from Estilos.css import CONFIGURACION
from utilidades import exportar_tabla, confirmar_y_eliminar, ESTILO_PELIGRO
from paginas.detalle_registro import DetalleRegistro


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

        barra = QHBoxLayout()
        nuevo = QPushButton("Nuevo ciudadano")
        nuevo.setObjectName("principal")
        nuevo.clicked.connect(lambda: self.abrir_detalle(None))
        ver = QPushButton("Ver / Editar")
        ver.setObjectName("secundario")
        ver.clicked.connect(self.ver_detalle)
        eliminar = QPushButton("Eliminar")
        eliminar.setStyleSheet(ESTILO_PELIGRO)
        eliminar.clicked.connect(self.eliminar_ciudadano)
        exportar = QPushButton("Exportar")
        exportar.setObjectName("secundario")
        exportar.clicked.connect(lambda: exportar_tabla(self, self.tabla, "ciudadanos"))
        barra.addStretch()
        for b in (nuevo, ver, eliminar, exportar):
            barra.addWidget(b)
        contenido.addLayout(barra)

        grupo = QGroupBox("Resultados")
        l = QVBoxLayout(grupo)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["CÉDULA", "NOMBRE", "APELLIDO", "MUNICIPIO", "ESTADO"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.cellDoubleClicked.connect(lambda r, c: self.ver_detalle())
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
                    SELECT id_ciudadano, cedula, nombres, apellidos, municipio, estado
                    FROM ciudadanos
                    WHERE cedula LIKE %s OR nombres LIKE %s OR apellidos LIKE %s
                """, (patron, patron, patron))
            else:
                cursor.execute("""
                    SELECT id_ciudadano, cedula, nombres, apellidos, municipio, estado
                    FROM ciudadanos
                """)

            registros = cursor.fetchall()
            cursor.close()
            conexion.close()

            self.tabla.setRowCount(len(registros))
            for fila, registro in enumerate(registros):
                for columna, valor in enumerate(registro[1:]):
                    item = QTableWidgetItem("" if valor is None else str(valor))
                    if columna == 0:
                        item.setData(Qt.UserRole, registro[0])  # id oculto
                    self.tabla.setItem(fila, columna, item)

        except Exception as e:
            print("Error:", e)

    def cargar_ciudadanos(self):
        self._consultar()

    def buscar_ciudadanos(self):
        self._consultar(self.campo.text().strip())

    def _id_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Registros", "Seleccione un registro de la tabla.")
            return None
        return self.tabla.item(fila, 0).data(Qt.UserRole)

    def abrir_detalle(self, id_ciudadano):
        DetalleRegistro(id_ciudadano, self).exec()
        self.buscar_ciudadanos()

    def ver_detalle(self):
        id_ciudadano = self._id_seleccionado()
        if id_ciudadano is not None:
            self.abrir_detalle(id_ciudadano)

    def eliminar_ciudadano(self):
        id_ciudadano = self._id_seleccionado()
        if id_ciudadano is None:
            return
        fila = self.tabla.currentRow()
        nombre = f"{self.tabla.item(fila, 1).text()} {self.tabla.item(fila, 2).text()}"
        if confirmar_y_eliminar(
            self, "DELETE FROM ciudadanos WHERE id_ciudadano=%s",
            (id_ciudadano,), f"el registro de «{nombre}»"
        ):
            self.buscar_ciudadanos()


# Solo para probar esta página sola (con su propio estilo)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ConsultarRegistros()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())