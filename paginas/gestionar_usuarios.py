import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from conexion import conectar
from Estilos.css import CONFIGURACION
from utilidades import exportar_tabla, confirmar_y_eliminar, ESTILO_PELIGRO
from paginas.nuevo_usuario import NuevoUsuario


class GestionarUsuarios(QWidget):
    def __init__(self):
        super().__init__()

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Gestionar usuarios")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)

        sub = QLabel("Administre los usuarios que tienen acceso al sistema.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        acciones = QHBoxLayout()
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar usuario...")
        self.buscar.textChanged.connect(self.buscar_usuarios)

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

        grupo = QGroupBox("Usuarios registrados")
        l = QVBoxLayout(grupo)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["USUARIO", "NOMBRE", "ROL", "ESTADO"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.cellDoubleClicked.connect(lambda r, c: self.editar_usuario())
        l.addWidget(self.tabla)
        contenido.addWidget(grupo)

        self.cargar_usuarios()

    def _consultar(self, filtro=""):
        """Llena la tabla. Si hay filtro, busca por usuario, nombre o rol."""
        try:
            conexion = conectar()
            cursor = conexion.cursor()

            if filtro:
                patron = f"%{filtro}%"
                cursor.execute("""
                    SELECT usuario, nombre_completo, rol, estado
                    FROM usuarios
                    WHERE usuario LIKE %s OR nombre_completo LIKE %s OR rol LIKE %s
                """, (patron, patron, patron))
            else:
                cursor.execute("""
                    SELECT usuario, nombre_completo, rol, estado
                    FROM usuarios
                """)

            registros = cursor.fetchall()
            cursor.close()
            conexion.close()

            self.tabla.setRowCount(len(registros))
            for fila, registro in enumerate(registros):
                for columna, valor in enumerate(registro):
                    self.tabla.setItem(
                        fila, columna,
                        QTableWidgetItem("" if valor is None else str(valor))
                    )

        except Exception as e:
            print("Error:", e)

    def cargar_usuarios(self):
        self._consultar()

    def buscar_usuarios(self):
        self._consultar(self.buscar.text().strip())

    def _usuario_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Usuarios", "Seleccione un usuario de la tabla.")
            return None
        return self.tabla.item(fila, 0).text()

    def nuevo_usuario(self):
        NuevoUsuario(parent=self).exec()
        self.buscar_usuarios()

    def editar_usuario(self):
        usuario = self._usuario_seleccionado()
        if usuario:
            NuevoUsuario(usuario_editar=usuario, parent=self).exec()
            self.buscar_usuarios()

    def eliminar_usuario(self):
        usuario = self._usuario_seleccionado()
        if usuario and confirmar_y_eliminar(
            self, "DELETE FROM usuarios WHERE usuario=%s", (usuario,),
            f"el usuario «{usuario}»"
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
