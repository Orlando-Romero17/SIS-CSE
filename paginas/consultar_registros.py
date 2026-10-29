"""
consultar_registros.py
Página para buscar y administrar ciudadanos (CRUD): buscar, ver/editar,
crear, eliminar y exportar. La lista se carga en un hilo con el ORM.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt
from Estilos.css import CONFIGURACION
from utilidades import exportar_tabla, confirmar_y_eliminar, ESTILO_PELIGRO
from paginas.detalle_registro import DetalleRegistro
from hilos.trabajador import ejecutar_en_hilo
from repositorio import listar_ciudadanos, eliminar_ciudadano


class ConsultarRegistros(QWidget):
    def __init__(self):
        super().__init__()
        self._peticion = 0  # para descartar respuestas viejas

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Consultar registros")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)

        sub = QLabel("Busque y consulte información de ciudadanos registrados.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        # Cuadro de búsqueda (por cédula, nombre o apellido)
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

        # Botones de acción del CRUD
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

        # Tabla de resultados
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

        self.estado = QLabel("")
        contenido.addWidget(self.estado)

        self.cargar_ciudadanos()

    # ---------- Carga de datos en segundo plano ----------
    def _consultar(self, filtro=""):
        """Lanza la consulta ORM en un hilo."""
        self._peticion += 1
        numero = self._peticion
        self.estado.setText("Cargando...")
        self.boton.setEnabled(False)
        ejecutar_en_hilo(
            listar_ciudadanos, filtro,
            al_terminar=lambda datos, n=numero: self._mostrar(datos, n),
            al_error=self._mostrar_error,
        )

    def _mostrar(self, registros, numero):
        """Pinta los resultados. El id del ciudadano se guarda oculto en la 1ª celda."""
        if numero != self._peticion:
            return
        self.tabla.setRowCount(len(registros))
        for fila, registro in enumerate(registros):
            for columna, valor in enumerate(registro[1:]):  # registro[0] es el id
                item = QTableWidgetItem("" if valor is None else str(valor))
                if columna == 0:
                    item.setData(Qt.UserRole, registro[0])
                self.tabla.setItem(fila, columna, item)
        self.estado.setText("")
        self.boton.setEnabled(True)

    def _mostrar_error(self, mensaje):
        self.estado.setText(f"Error: {mensaje}")
        self.boton.setEnabled(True)

    def cargar_ciudadanos(self):
        """Recarga la lista respetando el texto del buscador."""
        self._consultar(self.campo.text().strip())

    def buscar_ciudadanos(self):
        self._consultar(self.campo.text().strip())

    # ---------- Acciones del CRUD ----------
    def _id_seleccionado(self):
        """Devuelve el id del ciudadano de la fila seleccionada (o avisa si no hay)."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Registros", "Seleccione un registro de la tabla.")
            return None
        return self.tabla.item(fila, 0).data(Qt.UserRole)

    def abrir_detalle(self, id_ciudadano):
        """Abre la ventana de detalle (o de nuevo ciudadano si el id es None)."""
        DetalleRegistro(id_ciudadano, self).exec()
        self.buscar_ciudadanos()

    def ver_detalle(self):
        id_ciudadano = self._id_seleccionado()
        if id_ciudadano is not None:
            self.abrir_detalle(id_ciudadano)

    def eliminar_ciudadano(self):
        """DELETE: confirma y elimina el ciudadano seleccionado."""
        id_ciudadano = self._id_seleccionado()
        if id_ciudadano is None:
            return
        fila = self.tabla.currentRow()
        nombre = f"{self.tabla.item(fila, 1).text()} {self.tabla.item(fila, 2).text()}"
        if confirmar_y_eliminar(
            self, lambda: eliminar_ciudadano(id_ciudadano), f"el registro de «{nombre}»"
        ):
            self.buscar_ciudadanos()


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ConsultarRegistros()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())