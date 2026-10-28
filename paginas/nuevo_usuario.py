import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QMessageBox
)

from PySide6.QtCore import Qt
from conexion import conectar

STYLE = """
QWidget {
    background-color: #f7f8fa;
    color: #20252b;
    font-family: Arial;
    font-size: 12px;
}
QFrame#sidebar {
    background-color: #102b4a;
}
QLabel#logo {
    color: white;
    background-color: #173b63;
    border: 2px solid #6fa8dc;
    border-radius: 34px;
    font-size: 15px;
    font-weight: bold;
}
QLabel#marca {
    color: white;
    font-size: 19px;
    font-weight: bold;
}
QLabel#descripcion {
    color: #d8e0e8;
    font-size: 10px;
}
QPushButton#menu {
    text-align: left;
    background-color: transparent;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 12px;
    min-height: 18px;
}
QPushButton#menu:hover {
    background-color: #1d4772;
}
QPushButton#activo {
    text-align: left;
    background-color: #2476c7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 12px;
    min-height: 18px;
}
QLabel#titulo {
    font-size: 21px;
    font-weight: bold;
}
QLabel#subtitulo {
    color: #606a75;
    font-size: 12px;
}
QLineEdit, QComboBox, QTextEdit {
    background-color: white;
    border: 1px solid #d3d8de;
    border-radius: 4px;
    padding: 8px;
    min-height: 20px;
}
QGroupBox {
    background-color: white;
    border: 1px solid #d9dde2;
    border-radius: 5px;
    margin-top: 10px;
    padding: 14px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    background-color: #f7f8fa;
}
QPushButton#principal {
    background-color: #2476c7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 9px 16px;
    min-height: 18px;
}
QPushButton#principal:hover {
    background-color: #1c62a5;
}
QPushButton#secundario {
    background-color: #e7eaee;
    color: #30363d;
    border: none;
    border-radius: 4px;
    padding: 9px 16px;
}
QTableWidget {
    background-color: white;
    border: 1px solid #d9dde2;
    gridline-color: #e1e4e8;
}
QHeaderView::section {
    background-color: #eef1f4;
    padding: 7px;
    border: none;
    font-weight: bold;
}
"""

def crear_sidebar(activo):
    sidebar = QFrame()
    sidebar.setObjectName("sidebar")
    sidebar.setFixedWidth(265)

    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(20, 24, 20, 20)
    layout.setSpacing(5)

    encabezado = QHBoxLayout()
    encabezado.setSpacing(12)

    logo = QLabel("CSE")
    logo.setObjectName("logo")
    logo.setAlignment(Qt.AlignCenter)
    logo.setFixedSize(68, 68)

    textos = QVBoxLayout()
    textos.setSpacing(2)
    marca = QLabel("CSE")
    marca.setObjectName("marca")
    descripcion = QLabel("Consejo\nSupremo Electoral\nNicaragua")
    descripcion.setObjectName("descripcion")
    textos.addWidget(marca)
    textos.addWidget(descripcion)

    encabezado.addWidget(logo)
    encabezado.addLayout(textos)
    layout.addLayout(encabezado)
    layout.addSpacing(25)

    opciones = [
        ("⌂  Registrar usuario", "Registrar usuario"),
        ("⌕  Consultar registros", "Consultar registros"),
        ("♙  Gestionar usuarios", "Gestionar usuarios"),
        ("▥  Reportes", "Reportes"),
        ("⚙  Configuración", "Configuración"),
    ]

    for texto, nombre in opciones:
        boton = QPushButton(texto)
        boton.setObjectName("activo" if nombre == activo else "menu")
        layout.addWidget(boton)

    layout.addStretch()

    cerrar = QPushButton("↪  Cerrar sesión")
    cerrar.setObjectName("menu")
    layout.addWidget(cerrar)
    return sidebar

def crear_base(ventana, activo):
    ventana.setStyleSheet(STYLE)
    principal = QHBoxLayout(ventana)
    principal.setContentsMargins(0, 0, 0, 0)
    principal.setSpacing(0)
    principal.addWidget(crear_sidebar(activo))
    contenido = QVBoxLayout()
    contenido.setContentsMargins(30, 25, 30, 25)
    contenido.setSpacing(8)
    principal.addLayout(contenido, 1)
    return contenido

class NuevoUsuario(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIS-CSE - Sistema de Gestión")
        self.resize(1150, 700)
        contenido = crear_base(self, "Registrar usuario")

        titulo = QLabel("Nuevo usuario")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)
        sub = QLabel("Complete la información para crear un nuevo usuario.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        fila = QHBoxLayout()

        izquierda = QGroupBox()
        il = QVBoxLayout(izquierda)
        il.addWidget(QLabel("Nombre completo"))
        self.nombre = QLineEdit()
        il.addWidget(self.nombre)

        il.addWidget(QLabel("Nombre de usuario"))
        self.usuario = QLineEdit()
        il.addWidget(self.usuario)

        il.addWidget(QLabel("Correo electrónico"))
        self.correo = QLineEdit()
        il.addWidget(self.correo)
      
        il.addWidget(QLabel("Rol"))
        self.rol = QComboBox()
        self.rol.addItems([
        "Administrador",
        "Operador",
        "Consulta"
    ])
        il.addWidget(self.rol)
       
        il.addWidget(QLabel("Estado"))
        self.estado = QComboBox()
        self.estado.addItems([
        "Activo",
        "Inactivo"
     ])
        il.addWidget(self.estado)
        fila.addWidget(izquierda)

        derecha = QGroupBox()
        dl = QVBoxLayout(derecha)
        dl.addWidget(QLabel("Contraseña"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        dl.addWidget(self.password)

        dl.addWidget(QLabel("Confirmar contraseña"))
        self.confirmar = QLineEdit()
        self.confirmar.setEchoMode(QLineEdit.Password)
        dl.addWidget(self.confirmar)
        dl.addStretch()
        fila.addWidget(derecha)

        contenido.addLayout(fila)

        botones = QHBoxLayout()
        botones.addStretch()
        limpiar = QPushButton("Limpiar")
        limpiar.setObjectName("secundario")
        guardar = QPushButton("Guardar usuario")
        guardar.setObjectName("principal")
        guardar.clicked.connect(self.guardar_usuario)
        botones.addWidget(limpiar)
        botones.addWidget(guardar)
        contenido.addLayout(botones)
        self.mensaje = QLabel("")
        contenido.addWidget(self.mensaje)
        contenido.addStretch()

    def guardar_usuario(self):

        if self.nombre.text() == "":
            self.mensaje.setText("Ingrese el nombre")
            return

        if self.usuario.text() == "":
            self.mensaje.setText("Ingrese el usuario")
            return

        if self.password.text() != self.confirmar.text():
            self.mensaje.setText("Las contraseñas no coinciden")
            return

        try:

            conexion = conectar()
            cursor = conexion.cursor()

            sql = """
            INSERT INTO usuarios
            (
                nombre_completo,
                usuario,
                correo,
                contrasena,
                rol,
                estado
            )
            VALUES
            (%s,%s,%s,%s,%s,%s)
            """

            datos = (
                self.nombre.text(),
                self.usuario.text(),
                self.correo.text(),
                self.password.text(),
                self.rol.currentText(),
                self.estado.currentText()
            )

            cursor.execute(sql, datos)

            conexion.commit()

            self.mensaje.setText(
                "Usuario guardado correctamente"
            )

            cursor.close()
            conexion.close()

        except Exception as e:

            self.mensaje.setText(
                f"Error: {e}"
            )
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = NuevoUsuario()
    ventana.show()
    sys.exit(app.exec())
