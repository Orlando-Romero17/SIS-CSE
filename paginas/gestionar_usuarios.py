"""
gestionar_usuarios.py
Página para administrar los usuarios del sistema (CRUD completo):
buscar, crear, editar, eliminar y exportar. La lista se carga en un hilo.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from Estilos.css import CONFIGURACION
from utilidades import exportar_tabla, confirmar_y_eliminar, ESTILO_PELIGRO
from paginas.nuevo_usuario import NuevoUsuario
from hilos.trabajador import ejecutar_en_hilo
from repositorio import listar_usuarios, eliminar_usuario


class GestionarUsuarios(QWidget):
    def __init__(self):
        super().__init__()
        # Contador para ignorar respuestas viejas si el usuario escribe rápido
        self._peticion = 0

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Gestionar usuarios")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)

        sub = QLabel("Administre los usuarios que tienen acceso al sistema.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        # Barra superior: buscador + botones de acción
        acciones = QHBoxLayout()
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar usuario...")
        self.buscar.textChanged.connect(self.buscar_usuarios)  # busca mientras escribe

        nuevo = QPushButton("Nuevo usuario")
        nuevo.setObjectName("principal")
        nuevo.clicked.connect(self.nuevo_usuario)
        editar = QPushButton("Editar")
        editar.setObjectName("secundario")
        editar.clicked.connect(self.editar_usuario)
        eliminar = QPushButton("Eliminar")
        eliminar.setStyleSheet(ESTILO_PELIGRO)
        eliminar.clicked.connect(self.eliminar_usuario)
        exportar = QPushButton("Exportar")
        exportar.setObjectName("secundario")
        exportar.clicked.connect(lambda: exportar_tabla(self, self.tabla, "usuarios"))

        acciones.addWidget(self.buscar, 1)
        for b in (nuevo, editar, eliminar, exportar):
            acciones.addWidget(b)
        contenido.addLayout(acciones)

        # Tabla de usuarios
        grupo = QGroupBox("Usuarios registrados")
        l = QVBoxLayout(grupo)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["USUARIO", "NOMBRE", "ROL", "ESTADO"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)   # selecciona fila completa
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)    # tabla de solo lectura
        self.tabla.cellDoubleClicked.connect(lambda r, c: self.editar_usuario())
        l.addWidget(self.tabla)
        contenido.addWidget(grupo)

        # Mensaje de estado ("Cargando..." / errores)
        self.estado = QLabel("")
        contenido.addWidget(self.estado)

        self.cargar_usuarios()

    # ---------- Carga de datos en segundo plano ----------
    def _consultar(self, filtro=""):
        """Lanza la consulta (ORM) en un hilo para no congelar la ventana."""
        self._peticion += 1
        numero = self._peticion
        self.estado.setText("Cargando...")
        ejecutar_en_hilo(
            listar_usuarios, filtro,
            al_terminar=lambda datos, n=numero: self._mostrar(datos, n),
            al_error=self._mostrar_error,
        )

    def _mostrar(self, registros, numero):
        """Pinta los resultados en la tabla (si no llegó una respuesta más nueva)."""
        if numero != self._peticion:
            return
        self.tabla.setRowCount(len(registros))
        for fila, registro in enumerate(registros):
            for columna, valor in enumerate(registro):
                self.tabla.setItem(
                    fila, columna, QTableWidgetItem("" if valor is None else str(valor))
                )
        self.estado.setText("")

    def _mostrar_error(self, mensaje):
        self.estado.setText(f"Error: {mensaje}")

    def cargar_usuarios(self):
        """Recarga la lista respetando el texto escrito en el buscador."""
        self._consultar(self.buscar.text().strip())

    def buscar_usuarios(self):
        self._consultar(self.buscar.text().strip())

    # ---------- Acciones del CRUD ----------
    def _usuario_seleccionado(self):
        """Devuelve el usuario de la fila seleccionada (o avisa si no hay ninguna)."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Usuarios", "Seleccione un usuario de la tabla.")
            return None
        return self.tabla.item(fila, 0).text()

    def nuevo_usuario(self):
        """CREATE: abre la ventana de nuevo usuario y luego refresca la tabla."""
        NuevoUsuario(parent=self).exec()
        self.buscar_usuarios()

    def editar_usuario(self):
        """UPDATE: abre la ventana en modo edición con el usuario seleccionado."""
        usuario = self._usuario_seleccionado()
        if usuario:
            NuevoUsuario(usuario_editar=usuario, parent=self).exec()
            self.buscar_usuarios()

    def eliminar_usuario(self):
        """DELETE: confirma y elimina el usuario seleccionado."""
        usuario = self._usuario_seleccionado()
        if usuario and confirmar_y_eliminar(
            self, lambda: eliminar_usuario(usuario), f"el usuario «{usuario}»"
        ):
            self.buscar_usuarios()


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = GestionarUsuarios()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())