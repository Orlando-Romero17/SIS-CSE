"""
nuevo_usuario.py
Ventana emergente para CREAR un usuario nuevo o EDITAR uno existente.
Se abre desde Gestionar usuarios (botones "Nuevo usuario" y "Editar").
Guarda con el ORM (repositorio.py).
"""
import os
import sys
# Permite ejecutar este archivo solo, agregando la carpeta raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QLineEdit, QComboBox, QMessageBox, QFormLayout
)
from Estilos.css import CONFIGURACION
from repositorio import (
    obtener_usuario, existe_usuario, crear_usuario, actualizar_usuario
)


class NuevoUsuario(QDialog):
    """Si recibe 'usuario_editar' funciona como edición; si no, como creación."""

    def __init__(self, usuario_editar=None, parent=None):
        super().__init__(parent)
        self.usuario_original = usuario_editar
        self.editando = usuario_editar is not None
        self.setWindowTitle("Editar usuario" if self.editando else "Nuevo usuario")
        self.setStyleSheet(CONFIGURACION)
        self.setMinimumWidth(520)
        self.setModal(True)  # bloquea la ventana de atrás hasta cerrar esta

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(25, 20, 25, 20)
        contenido.setSpacing(8)

        # Título y subtítulo según el modo
        titulo = QLabel("Editar usuario" if self.editando else "Nuevo usuario")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)
        sub = QLabel(
            "Modifique los datos. Deje la contraseña vacía para conservar la actual."
            if self.editando else
            "Complete la información para crear un nuevo usuario."
        )
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        # Formulario con los campos del usuario
        grupo = QGroupBox()
        form = QFormLayout(grupo)
        self.nombre = QLineEdit()
        self.usuario = QLineEdit()
        self.correo = QLineEdit()
        self.rol = QComboBox()
        self.rol.addItems(["Administrador", "Operador", "Consulta"])
        self.estado = QComboBox()
        self.estado.addItems(["Activo", "Inactivo"])
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.confirmar = QLineEdit()
        self.confirmar.setEchoMode(QLineEdit.Password)

        form.addRow("Nombre completo", self.nombre)
        form.addRow("Nombre de usuario", self.usuario)
        form.addRow("Correo electrónico", self.correo)
        form.addRow("Rol", self.rol)
        form.addRow("Estado", self.estado)
        form.addRow("Contraseña", self.password)
        form.addRow("Confirmar contraseña", self.confirmar)
        contenido.addWidget(grupo)

        # Botones inferiores
        botones = QHBoxLayout()
        botones.addStretch()
        limpiar = QPushButton("Limpiar")
        limpiar.setObjectName("secundario")
        limpiar.clicked.connect(self.limpiar)
        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("secundario")
        cancelar.clicked.connect(self.reject)
        guardar = QPushButton("Guardar cambios" if self.editando else "Guardar usuario")
        guardar.setObjectName("principal")
        guardar.clicked.connect(self.guardar_usuario)
        botones.addWidget(limpiar)
        botones.addWidget(cancelar)
        botones.addWidget(guardar)
        contenido.addLayout(botones)

        # En modo edición se cargan los datos actuales del usuario
        if self.editando:
            self.cargar_usuario()

    def limpiar(self):
        """Vacía todos los campos del formulario."""
        for campo in (self.nombre, self.usuario, self.correo, self.password, self.confirmar):
            campo.clear()
        self.rol.setCurrentIndex(0)
        self.estado.setCurrentIndex(0)

    def cargar_usuario(self):
        """READ: trae los datos del usuario a editar y los muestra en el formulario."""
        try:
            d = obtener_usuario(self.usuario_original)
            if d:
                self.nombre.setText(d["nombre_completo"])
                self.usuario.setText(d["usuario"])
                self.correo.setText(d["correo"])
                self.rol.setCurrentText(d["rol"])
                self.estado.setCurrentText(d["estado"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el usuario:\n{e}")

    def guardar_usuario(self):
        """Valida los datos (con MessageBox) y crea o actualiza el usuario con el ORM."""
        nombre = self.nombre.text().strip()
        usuario = self.usuario.text().strip()
        correo = self.correo.text().strip()
        password = self.password.text()

        # ----- Validaciones -----
        if not nombre:
            QMessageBox.warning(self, "Validación", "Ingrese el nombre")
            return
        if not usuario:
            QMessageBox.warning(self, "Validación", "Ingrese el usuario")
            return
        if correo and "@" not in correo:
            QMessageBox.warning(self, "Validación", "El correo no es válido")
            return
        if not self.editando and not password:
            QMessageBox.warning(self, "Validación", "Ingrese una contraseña")
            return
        if password != self.confirmar.text():
            QMessageBox.warning(self, "Validación", "Las contraseñas no coinciden")
            return

        try:
            # No se permiten dos usuarios con el mismo nombre
            if existe_usuario(usuario, excluir=self.usuario_original):
                QMessageBox.warning(self, "Validación", "Ya existe un usuario con ese nombre")
                return

            datos = {
                "nombre_completo": nombre, "usuario": usuario, "correo": correo,
                "rol": self.rol.currentText(), "estado": self.estado.currentText(),
            }
            if password:  # en edición, contraseña vacía = conservar la actual
                datos["contrasena"] = password

            if self.editando:
                actualizar_usuario(self.usuario_original, datos)   # UPDATE
            else:
                crear_usuario(datos)                                # CREATE

            QMessageBox.information(self, "Usuarios", "Usuario guardado correctamente")
            self.accept()  # cierra la ventana indicando éxito

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")


# Solo para probar esta ventana sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = NuevoUsuario()
    ventana.exec()