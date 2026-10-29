"""
configuracion.py
Página de configuración general del sistema (nombre de la institución,
idioma y tema). Lee y guarda en la tabla configuracion con el ORM, en hilos.
Desde el menú interno se abre la ventana de Respaldo.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QLineEdit, QComboBox, QMessageBox
)
from Estilos.css import CONFIGURACION
from paginas.respaldo import RespaldoInformacion
from hilos.trabajador import ejecutar_en_hilo
from repositorio import obtener_configuracion, guardar_configuracion as guardar_config_bd


class Configuracion(QWidget):
    def __init__(self):
        super().__init__()

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Configuración")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)

        sub = QLabel("Ajuste las opciones del sistema.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        cuerpo = QHBoxLayout()

        # ----- Menú interno de configuración -----
        menu = QGroupBox()
        ml = QVBoxLayout(menu)
        for texto in ["General", "Seguridad", "Respaldo", "Preferencias"]:
            b = QPushButton(texto)
            if texto == "General":  # sección activa
                b.setStyleSheet(
                    "text-align:left; color:white; background:#2476c7; "
                    "border:none; border-radius:4px; padding:10px 12px;"
                )
            else:
                b.setStyleSheet(
                    "text-align:left; color:#20252b; background:#f1f3f5; "
                    "border:none; border-radius:4px; padding:10px 12px;"
                )
            b.clicked.connect(lambda _=False, t=texto: self.abrir_seccion(t))
            ml.addWidget(b)
        ml.addStretch()
        cuerpo.addWidget(menu, 1)

        # ----- Opciones generales -----
        ajustes = QGroupBox("Opciones generales")
        al = QVBoxLayout(ajustes)

        al.addWidget(QLabel("Nombre de la institución"))
        self.nombre = QLineEdit()
        al.addWidget(self.nombre)

        al.addWidget(QLabel("Zona horaria"))
        self.zona = QComboBox()
        self.zona.addItems(["UTC-6 (Centroamérica)", "UTC-5", "UTC-4"])
        al.addWidget(self.zona)

        al.addWidget(QLabel("Idioma del sistema"))
        self.idioma = QComboBox()
        self.idioma.addItems(["Español", "English"])
        al.addWidget(self.idioma)

        al.addWidget(QLabel("Tema del sistema"))
        self.tema = QComboBox()
        self.tema.addItems(["Claro", "Oscuro"])
        al.addWidget(self.tema)

        fila = QHBoxLayout()
        self.mensaje = QLabel("")
        fila.addWidget(self.mensaje)
        fila.addStretch()
        guardar = QPushButton("Guardar cambios")
        guardar.setObjectName("principal")
        guardar.clicked.connect(self.guardar_configuracion)
        fila.addWidget(guardar)
        al.addLayout(fila)
        cuerpo.addWidget(ajustes, 3)

        contenido.addLayout(cuerpo)
        contenido.addStretch()

        self.cargar_configuracion()

    def abrir_seccion(self, nombre):
        """Abre la sección elegida del menú interno."""
        if nombre == "Respaldo":
            RespaldoInformacion(self).exec()
        elif nombre != "General":
            QMessageBox.information(
                self, nombre, f"La sección «{nombre}» estará disponible próximamente."
            )

    def cargar_configuracion(self):
        """READ: trae la configuración guardada (ORM) en segundo plano."""
        ejecutar_en_hilo(
            obtener_configuracion,
            al_terminar=self._mostrar_configuracion,
            al_error=lambda m: self.mensaje.setText(f"Error: {m}"),
        )

    def _mostrar_configuracion(self, c):
        """Coloca los valores guardados en los campos del formulario."""
        if c:
            self.nombre.setText(c["nombre"])
            if c["idioma"]:
                self.idioma.setCurrentText(c["idioma"])
            if c["tema"]:
                self.tema.setCurrentText(c["tema"])

    def guardar_configuracion(self):
        """UPDATE: guarda los cambios (ORM) en segundo plano."""
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Validación", "Ingrese el nombre de la institución")
            return
        self.mensaje.setText("Guardando...")
        ejecutar_en_hilo(
            guardar_config_bd,
            self.nombre.text().strip(), self.idioma.currentText(), self.tema.currentText(),
            al_terminar=self._guardado,
            al_error=lambda m: self.mensaje.setText(f"Error: {m}"),
        )

    def _guardado(self, ok):
        self.mensaje.setText(
            "Configuración guardada" if ok else "No existe la fila con id_configuracion = 1"
        )


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Configuracion()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())