
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QLineEdit, QComboBox
)
from conexion import conectar
from Estilos.css import CONFIGURACION


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

        # Menú interno de configuración
        menu = QGroupBox()
        ml = QVBoxLayout(menu)
        for texto in ["General", "Seguridad", "Respaldo", "Preferencias"]:
            b = QPushButton(texto)
            if texto == "General":
                b.setStyleSheet(
                    "text-align:left; color:white; background:#2476c7; "
                    "border:none; border-radius:4px; padding:10px 12px;"
                )
            else:
                b.setStyleSheet(
                    "text-align:left; color:#20252b; background:#f1f3f5; "
                    "border:none; border-radius:4px; padding:10px 12px;"
                )
            ml.addWidget(b)
        ml.addStretch()
        cuerpo.addWidget(menu, 1)

        # Opciones generales
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

    def cargar_configuracion(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT nombre_institucion, idioma, tema
                FROM configuracion
                LIMIT 1
            """)
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()

            if resultado:
                self.nombre.setText(resultado[0] or "")
                if resultado[1]:
                    self.idioma.setCurrentText(resultado[1])
                if resultado[2]:
                    self.tema.setCurrentText(resultado[2])

        except Exception as e:
            print("Error:", e)

    def guardar_configuracion(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE configuracion
                SET nombre_institucion=%s, idioma=%s, tema=%s
                WHERE id_configuracion = 1
            """, (
                self.nombre.text().strip(),
                self.idioma.currentText(),
                self.tema.currentText(),
            ))
            conexion.commit()
            filas = cursor.rowcount
            cursor.close()
            conexion.close()

            if filas == 0:
                self.mensaje.setText("No existe la fila con id_configuracion = 1")
            else:
                self.mensaje.setText("Configuración guardada")

        except Exception as e:
            self.mensaje.setText(f"Error: {e}")


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Configuracion()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())