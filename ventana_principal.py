"""
ventana_principal.py
Ventana principal del sistema: barra lateral de navegación y un QStackedWidget
que muestra una página a la vez (Panel, Consultar registros, Gestionar usuarios,
Reportes y Configuración).
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from Estilos.css import GENERAL
from paginas.configuracion import Configuracion
from paginas.consultar_registros import ConsultarRegistros
from paginas.gestionar_usuarios import GestionarUsuarios
from paginas.reportes import Reportes
from hilos.trabajador import ejecutar_en_hilo
from repositorio import contar_estadisticas, tramites_recientes


def crear_sidebar(stack, opciones, al_cerrar_sesion=None):
    """Crea la barra lateral con el logo, los botones del menú y 'Cerrar sesión'.
    Cada botón cambia la página visible del 'stack'."""
    sidebar = QFrame()
    sidebar.setObjectName("sidebar")
    sidebar.setFixedWidth(265)

    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(20, 24, 20, 20)
    layout.setSpacing(5)

    # Logo y nombre de la institución
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
        """Resalta el botón de la página que se está viendo."""
        for i, b in enumerate(botones):
            b.setObjectName("activo" if i == indice else "menu")
            b.style().unpolish(b)
            b.style().polish(b)

    # Un botón por cada opción del menú
    for i, texto in enumerate(opciones):
        boton = QPushButton(texto)
        boton.setObjectName("menu")
        boton.clicked.connect(lambda _=False, idx=i: stack.setCurrentIndex(idx))
        layout.addWidget(boton)
        botones.append(boton)

    stack.currentChanged.connect(marcar_activo)
    marcar_activo(stack.currentIndex())

    layout.addStretch()

    # Botón para cerrar sesión (al final de la barra)
    cerrar = QPushButton("↪  Cerrar sesión")
    cerrar.setObjectName("menu")
    if al_cerrar_sesion:
        cerrar.clicked.connect(al_cerrar_sesion)
    layout.addWidget(cerrar)
    return sidebar


class PaginaPanel(QWidget):
    """Página de inicio: tarjetas con totales y tabla de trámites recientes."""

    def __init__(self, al_buscar=None):
        super().__init__()
        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Panel principal")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)
        contenido.addWidget(QLabel("Resumen general del sistema"))

        # Buscador global: al presionar Enter envía el texto a Consultar registros
        buscar = QLineEdit()
        buscar.setPlaceholderText("Buscar ciudadano por cédula, nombre o apellido...")
        if al_buscar:
            buscar.returnPressed.connect(lambda: al_buscar(buscar.text().strip()))
        contenido.addWidget(buscar)

        # Tarjetas con los totales (se llenan desde la base de datos)
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

        # Tabla de trámites recientes (datos reales de la tabla tramites)
        grupo = QGroupBox("Trámites recientes")
        l = QVBoxLayout(grupo)
        self.tabla = QTableWidget(0, 0)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        l.addWidget(self.tabla)
        contenido.addWidget(grupo)

        self.cargar_estadisticas()

    def cargar_estadisticas(self):
        """Pide en segundo plano los totales y los trámites recientes."""
        ejecutar_en_hilo(
            contar_estadisticas,
            al_terminar=self._mostrar_estadisticas,
            al_error=lambda msg: print("Error:", msg),
        )
        ejecutar_en_hilo(
            tramites_recientes,
            al_terminar=self._mostrar_tramites,
            al_error=lambda msg: print("Error:", msg),
        )

    def _mostrar_estadisticas(self, datos):
        """Pone los totales en las tarjetas (se ejecuta en el hilo principal)."""
        self.lbl_usuarios.setText(str(datos.get("usuarios", 0)))
        self.lbl_ciudadanos.setText(str(datos.get("ciudadanos", 0)))
        self.lbl_tramites.setText(str(datos.get("tramites", 0)))

    def _mostrar_tramites(self, resultado):
        """Llena la tabla de trámites con las columnas que tenga la tabla de la BD."""
        encabezados, filas = resultado
        self.tabla.setColumnCount(len(encabezados))
        self.tabla.setHorizontalHeaderLabels(encabezados)
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem("" if valor is None else str(valor)))


class VentanaPrincipal(QWidget):
    """Contenedor principal: barra lateral + páginas intercambiables."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIS-CSE - Sistema de Gestión")
        self.resize(1150, 700)
        self.setMinimumSize(950, 620)
        self.setStyleSheet(GENERAL)

        # Páginas del sistema (el orden coincide con los botones del menú)
        self.pagina_consulta = ConsultarRegistros()
        self.stack = QStackedWidget()
        self.stack.addWidget(PaginaPanel(self._buscar_global))  # 0
        self.stack.addWidget(self.pagina_consulta)              # 1
        self.stack.addWidget(GestionarUsuarios())               # 2
        self.stack.addWidget(Reportes())                        # 3
        self.stack.addWidget(Configuracion())                   # 4

        # Al cambiar de página se recargan sus datos
        self.stack.currentChanged.connect(self._refrescar)

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
        principal.addWidget(crear_sidebar(self.stack, opciones, self.cerrar_sesion))
        principal.addWidget(self.stack, 1)

    def _refrescar(self, indice):
        """Recarga los datos de la página que se acaba de mostrar."""
        pagina = self.stack.widget(indice)
        for metodo in ("cargar_estadisticas", "cargar_ciudadanos", "cargar_usuarios"):
            if hasattr(pagina, metodo):
                getattr(pagina, metodo)()

    def _buscar_global(self, texto):
        """Búsqueda desde el panel: abre Consultar registros con ese texto."""
        self.stack.setCurrentIndex(1)
        self.pagina_consulta.campo.setText(texto)
        self.pagina_consulta.buscar_ciudadanos()

    def cerrar_sesion(self):
        """Pide confirmación y regresa a la pantalla de inicio de sesión."""
        r = QMessageBox.question(
            self, "Cerrar sesión", "¿Desea cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No
        )
        if r != QMessageBox.Yes:
            return
        from inicio_sesion import InicioSesion  # import aquí para evitar importación circular
        self.login = InicioSesion()
        self.login.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())