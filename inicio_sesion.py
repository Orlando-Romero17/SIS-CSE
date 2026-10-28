
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt
from conexion import conectar
from  Estilos.css import CONFIGURACION
from ventana_principal import VentanaPrincipal


class InicioSesion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIS-CSE - Sistema de Gestión")
        self.resize(1050, 700)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(CONFIGURACION)
        self.crear_interfaz()

    def crear_interfaz(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)
        principal = QHBoxLayout(contenedor)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)
        barra = QVBoxLayout(sidebar)
        barra.setContentsMargins(35, 45, 35, 35)

        encabezado = QHBoxLayout()
        logo = QLabel("CSE")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(72, 72)
        textos = QVBoxLayout()
        marca = QLabel("CSE")
        marca.setObjectName("marca")
        desc = QLabel("Consejo\nSupremo Electoral\nNicaragua")
        desc.setObjectName("descripcion")
        textos.addWidget(marca)
        textos.addWidget(desc)
        encabezado.addWidget(logo)
        encabezado.addLayout(textos)
        barra.addLayout(encabezado)
        barra.addStretch()
        mensaje = QLabel("Sistema de Gestión\nde Registros y Trámites")
        mensaje.setStyleSheet("color:#d8e0e8; font-size:10px; background-color:transparent;")
        mensaje.setAlignment(Qt.AlignCenter)
        barra.addWidget(mensaje)

        derecha = QFrame()
        layout = QVBoxLayout(derecha)
        layout.setContentsMargins(55, 45, 55, 45)
        layout.setAlignment(Qt.AlignCenter)

        formulario = QGroupBox()
        formulario.setMaximumWidth(470)
        form = QVBoxLayout(formulario)
        titulo = QLabel("Inicio de Sesión")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        sub = QLabel("Ingrese sus credenciales para acceder al sistema")
        sub.setObjectName("subtitulo")
        sub.setAlignment(Qt.AlignCenter)
        form.addWidget(titulo)
        form.addWidget(sub)
        form.addSpacing(20)

        form.addWidget(QLabel("Nombre de usuario"))
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Ingrese su usuario")
        form.addWidget(self.usuario)
        form.addSpacing(8)

        form.addWidget(QLabel("Contraseña"))
        self.contrasena = QLineEdit()
        self.contrasena.setPlaceholderText("Ingrese su contraseña")
        self.contrasena.setEchoMode(QLineEdit.Password)
        form.addWidget(self.contrasena)
        form.addSpacing(12)

        fila = QHBoxLayout()
        recordar = QCheckBox("Recordarme")
        self.boton = QPushButton("Iniciar sesión")
        self.boton.setObjectName("principal")
        fila.addWidget(recordar)
        fila.addStretch()
        fila.addWidget(self.boton)
        form.addLayout(fila)

        self.mensaje = QLabel("")
        self.mensaje.setAlignment(Qt.AlignCenter)
        form.addWidget(self.mensaje)

        layout.addWidget(formulario)
        principal.addWidget(sidebar)
        principal.addWidget(derecha, 1)

        self.boton.clicked.connect(self.iniciar_sesion)
        self.contrasena.returnPressed.connect(self.iniciar_sesion)

    def iniciar_sesion(self):
        usuario = self.usuario.text().strip()
        contrasena = self.contrasena.text()

        if not usuario or not contrasena:
            self.mensaje.setText("Complete todos los campos")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT * FROM usuarios WHERE usuario=%s AND contrasena=%s",
                (usuario, contrasena)
            )
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()

            if resultado:
                self.ventana_principal = VentanaPrincipal()
                self.ventana_principal.show()
                self.close()
            else:
                self.mensaje.setText("Usuario o contraseña incorrectos")

        except Exception as e:
            self.mensaje.setText(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = InicioSesion()
    ventana.show()
    sys.exit(app.exec())