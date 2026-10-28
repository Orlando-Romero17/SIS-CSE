import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget,QMessageBox
)
from PySide6.QtCore import Qt
from conexion import conectar
from paginas.configuracion import Configuracion
from Estilos.css import CONFIGURACION
from paginas.consultar_registros import ConsultarRegistros
from paginas.gestionar_usuarios import GestionarUsuarios
from paginas.reportes import Reportes
def crear_sidebar(stack, opciones, al_cerrar_sesion=None):
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

    botones = []

    def marcar_activo(indice):
        for i, b in enumerate(botones):
            b.setObjectName("activo" if i == indice else "menu")
            b.style().unpolish(b)
            b.style().polish(b)

    for i, texto in enumerate(opciones):
        boton = QPushButton(texto)
        boton.setObjectName("menu")
        boton.clicked.connect(lambda _=False, idx=i: stack.setCurrentIndex(idx))
        layout.addWidget(boton)
        botones.append(boton)

    stack.currentChanged.connect(marcar_activo)
    marcar_activo(stack.currentIndex())

    layout.addStretch()

    cerrar = QPushButton("↪  Cerrar sesión")
    cerrar.setObjectName("menu")
    if al_cerrar_sesion:
        cerrar.clicked.connect(al_cerrar_sesion)
    layout.addWidget(cerrar)
    return sidebar

def pagina_vacia(titulo_texto, subtitulo_texto):
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    layout.setContentsMargins(30, 25, 30, 25)
    layout.setSpacing(8)
    titulo = QLabel(titulo_texto)
    titulo.setObjectName("titulo")
    subtitulo = QLabel(subtitulo_texto)
    subtitulo.setObjectName("subtitulo")
    layout.addWidget(titulo)
    layout.addWidget(subtitulo)
    layout.addStretch()
    return pagina


class PaginaPanel(QWidget):
    def __init__(self):
        super().__init__()
        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Panel principal")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)
        contenido.addWidget(QLabel("Resumen general del sistema"))

        buscar = QLineEdit()
        buscar.setPlaceholderText("Buscar ciudadano, trámite, expediente...")
        contenido.addWidget(buscar)

        tarjetas = QHBoxLayout()
        self.lbl_usuarios = QLabel("0")
        self.lbl_ciudadanos = QLabel("0")
        self.lbl_tramites = QLabel("0")

        for titulo_tarjeta, etiqueta in [
            ("USUARIOS", self.lbl_usuarios),
            ("CIUDADANOS", self.lbl_ciudadanos),
            ("TRÁMITES", self.lbl_tramites),
        ]:
            caja = QGroupBox(titulo_tarjeta)
            l = QVBoxLayout(caja)
            etiqueta.setAlignment(Qt.AlignCenter)
            etiqueta.setStyleSheet("font-size:25px;font-weight:bold;color:#2476c7;")
            l.addWidget(etiqueta)
            tarjetas.addWidget(caja)

        contenido.addLayout(tarjetas)

        grupo = QGroupBox("Trámites recientes")
        l = QVBoxLayout(grupo)
        tabla = QTableWidget(3, 4)
        tabla.setHorizontalHeaderLabels(["EXPEDIENTE", "CIUDADANO", "ESTADO", "FECHA"])
        datos = [
            ["EXP-00125", "Juan Pérez", "En proceso", "26/08"],
            ["EXP-00126", "María López", "Completado", "27/08"],
            ["EXP-00127", "Carlos Gómez", "Pendiente", "28/08"],
        ]
        for f, fila in enumerate(datos):
            for c, dato in enumerate(fila):
                tabla.setItem(f, c, QTableWidgetItem(dato))
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(tabla)
        contenido.addWidget(grupo)

        self.cargar_estadisticas()

    def cargar_estadisticas(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            self.lbl_usuarios.setText(str(cursor.fetchone()[0]))
            cursor.close()
            conexion.close()
        except Exception as e:
            print("Error:", e)


class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIS-CSE - Sistema de Gestión")
        self.resize(1150, 700)
        self.setMinimumSize(950, 620)
        self.setStyleSheet(CONFIGURACION)

        self.stack = QStackedWidget()
        self.stack.addWidget(PaginaPanel())                                              # 0
        self.stack.addWidget(ConsultarRegistros())   # 1
        self.stack.addWidget(GestionarUsuarios())  # 2
        self.stack.addWidget(Reportes())                # 3
        self.stack.addWidget(Configuracion())                                            # 4

        opciones = [
            "⌂  Panel principal",
            "⌕  Consultar registros",
            "♙  Gestionar usuarios",
            "▥  Reportes",
            "⚙  Configuración",
        ]

        principal = QHBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)
        principal.addWidget(crear_sidebar(self.stack, opciones,self.cerrar_sesion))
        principal.addWidget(self.stack, 1)

    def cerrar_sesion(self):
        r = QMessageBox.question(
            self, "Cerrar sesión", "¿Desea cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No
        )
        if r != QMessageBox.Yes:
            return
        from inicio_sesion import InicioSesion
        self.login = InicioSesion()
        self.login.show()
        self.close()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())