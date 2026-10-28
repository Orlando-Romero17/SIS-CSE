import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from conexion import conectar
from Estilos.css import CONFIGURACION


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
        self.buscar.returnPressed.connect(self.buscar_usuarios)
        self.buscar.textChanged.connect(self.buscar_usuarios)
        nuevo = QPushButton("Nuevo usuario")
        nuevo.setObjectName("principal")
        acciones.addWidget(self.buscar)
        acciones.addWidget(nuevo)
        contenido.addLayout(acciones)

        grupo = QGroupBox("Usuarios registrados")
        l = QVBoxLayout(grupo)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["USUARIO", "NOMBRE", "ROL", "ESTADO"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
                    self.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

        except Exception as e:
            print("Error:", e)

    def cargar_usuarios(self):
        self._consultar()

    def buscar_usuarios(self):
        self._consultar(self.buscar.text().strip())


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = GestionarUsuarios()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())
