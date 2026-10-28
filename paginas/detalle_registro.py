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
    QFormLayout
    )


from PySide6.QtCore import Qt
from conexion import conectar
from Estilos.css import DETALLE_REGISTRO


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
    ventana.setStyleSheet(DETALLE_REGISTRO)
    principal = QHBoxLayout(ventana)
    principal.setContentsMargins(0, 0, 0, 0)
    principal.setSpacing(0)
    principal.addWidget(crear_sidebar(activo))
    contenido = QVBoxLayout()
    contenido.setContentsMargins(30, 25, 30, 25)
    contenido.setSpacing(8)
    principal.addLayout(contenido, 1)
    return contenido

class DetalleRegistro(QWidget):

    def __init__(self, id_ciudadano=1):
        super().__init__()
        self.id_ciudadano = id_ciudadano
        self.setWindowTitle("SIS-CSE - Sistema de Gestión")
        self.resize(1150, 700)
        contenido = crear_base(self, "Consultar registros")

        titulo = QLabel("Detalle de registro")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)
        sub = QLabel("Información completa del registro seleccionado.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        fila = QHBoxLayout()

        datos = QGroupBox("Información del ciudadano")
        self.form = QFormLayout(datos)
        self.lbl_cedula = QLabel()
        self.lbl_nombre = QLabel()
        self.lbl_apellidos = QLabel()
        self.lbl_fecha = QLabel()
        self.lbl_genero = QLabel()
        self.lbl_departamento = QLabel()
        self.lbl_municipio = QLabel()
        self.lbl_direccion = QLabel()
        self.lbl_telefono = QLabel()
        self.lbl_correo = QLabel()
        self.lbl_estado = QLabel()

        self.form.addRow("Cédula:", self.lbl_cedula)
        self.form.addRow("Nombre:", self.lbl_nombre)
        self.form.addRow("Apellidos:", self.lbl_apellidos)
        self.form.addRow("Fecha nacimiento:", self.lbl_fecha)
        self.form.addRow("Género:", self.lbl_genero)
        self.form.addRow("Departamento:", self.lbl_departamento)
        self.form.addRow("Municipio:", self.lbl_municipio)
        self.form.addRow("Dirección:", self.lbl_direccion)
        self.form.addRow("Teléfono:", self.lbl_telefono)
        self.form.addRow("Correo:", self.lbl_correo)
        self.form.addRow("Estado:", self.lbl_estado)

        fila.addWidget(datos, 3)
        acciones = QGroupBox("Acciones")
        al = QVBoxLayout(acciones)
        for texto, estilo in [
            ("Editar registro", "principal"),
            ("Desactivar registro", "principal"),
            ("Imprimir", "secundario"),
            ("Cerrar", "secundario")
        ]:
            b = QPushButton(texto)
            b.setObjectName(estilo)
            al.addWidget(b)
        al.addStretch()
        fila.addWidget(acciones, 1)

        contenido.addLayout(fila)
        contenido.addStretch()
        self.cargar_detalle()
    def cargar_detalle(self):
        print("Entró a cargar_detalle")
        try:

            conexion = conectar()
            cursor = conexion.cursor()
            print("ID recibido:", self.id_ciudadano)

            cursor.execute("""
                SELECT
                    cedula,
                    nombres,
                    apellidos,
                    fecha_nacimiento,
                    genero,
                    departamento,
                    municipio,
                    direccion,
                    telefono,
                    correo,
                    estado
                FROM ciudadanos
                WHERE id_ciudadano = %s
            """, (self.id_ciudadano,))

            resultado = cursor.fetchone()
            print("RESULTADO:", resultado)
           
            if resultado:

                self.lbl_cedula.setText(str(resultado[0]))
                self.lbl_nombre.setText(str(resultado[1]))
                self.lbl_apellidos.setText(str(resultado[2]))
                self.lbl_fecha.setText(str(resultado[3]))
                self.lbl_genero.setText(str(resultado[4]))
                self.lbl_departamento.setText(str(resultado[5]))
                self.lbl_municipio.setText(str(resultado[6]))
                self.lbl_direccion.setText(str(resultado[7]))
                self.lbl_telefono.setText(str(resultado[8]))
                self.lbl_correo.setText(str(resultado[9]))
                self.lbl_estado.setText(str(resultado[10]))

            cursor.close()
            conexion.close()

        except Exception as e:

            print("Error:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = DetalleRegistro()
    ventana.show()
    sys.exit(app.exec())
