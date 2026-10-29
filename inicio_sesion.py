"""
inicio_sesion.py
Pantalla de inicio de sesión. Valida las credenciales contra la tabla usuarios
(con ORM, en un hilo) y, si son correctas, abre la ventana principal.
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from Estilos.css import CONFIGURACION
from ventana_principal import VentanaPrincipal
from hilos.trabajador import ejecutar_en_hilo
from repositorio import validar_login


class InicioSesion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIS-CSE - Sistema de Gestión")
        self.resize(1050, 700)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(CONFIGURACION)
        self.crear_interfaz()

    def crear_interfaz(self):
        """Construye la pantalla: barra lateral azul a la izquierda y formulario a la derecha."""
        contenedor = QWidget()
        self.setCentralWidget(contenedor)
        principal = QHBoxLayout(contenedor)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        # ----- Barra lateral con el logo y la descripción de la institución -----
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

        # ----- Lado derecho: formulario de inicio de sesión -----
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
        self.contrasena.setEchoMode(QLineEdit.Password)  # oculta lo que se escribe
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

        # Etiqueta para mostrar el estado ("Conectando...")
        self.mensaje = QLabel("")
        self.mensaje.setAlignment(Qt.AlignCenter)
        form.addWidget(self.mensaje)

        layout.addWidget(formulario)
        principal.addWidget(sidebar)
        principal.addWidget(derecha, 1)

        # El botón y la tecla Enter en la contraseña inician el proceso de login
        self.boton.clicked.connect(self.iniciar_sesion)
        self.contrasena.returnPressed.connect(self.iniciar_sesion)

    def iniciar_sesion(self):
        """Valida que los campos no estén vacíos y consulta la base de datos en segundo plano."""
        usuario = self.usuario.text().strip()
        contrasena = self.contrasena.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Datos incompletos", "Complete todos los campos")
            return

        # Se desactiva el botón para evitar clics repetidos mientras consulta
        self.boton.setEnabled(False)
        self.mensaje.setText("Conectando...")
        ejecutar_en_hilo(
            validar_login, usuario, contrasena,
            al_terminar=self._login_terminado,
            al_error=self._login_error,
        )

    def _login_terminado(self, valido):
        """Se ejecuta al volver la consulta: abre el sistema o avisa del error."""
        self.boton.setEnabled(True)
        self.mensaje.setText("")
        if valido:
            self.ventana_principal = VentanaPrincipal()
            self.ventana_principal.show()
            self.close()
        else:
            QMessageBox.warning(self, "Acceso denegado", "Usuario o contraseña incorrectos")

    def _login_error(self, mensaje):
        """Error de conexión con la base de datos."""
        self.boton.setEnabled(True)
        self.mensaje.setText("")
        QMessageBox.critical(self, "Error de conexión", f"No se pudo conectar:\n{mensaje}")


# Punto de entrada: se ejecuta con "python inicio_sesion.py"
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = InicioSesion()
    ventana.show()
    sys.exit(app.exec())