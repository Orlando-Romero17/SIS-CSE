import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QLineEdit, QComboBox, QMessageBox, QFormLayout
)
from conexion import conectar
from Estilos.css import CONFIGURACION


class NuevoUsuario(QDialog):
    """Diálogo para crear un usuario o, si recibe `usuario_editar`, para editarlo."""

    def __init__(self, usuario_editar=None, parent=None):
        super().__init__(parent)
        self.usuario_original = usuario_editar
        self.editando = usuario_editar is not None
        self.setWindowTitle("Editar usuario" if self.editando else "Nuevo usuario")
        self.setStyleSheet(CONFIGURACION)
        self.setMinimumWidth(520)
        self.setModal(True)

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(25, 20, 25, 20)
        contenido.setSpacing(8)

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

        self.mensaje = QLabel("")
        self.mensaje.setStyleSheet("color:#c0392b;")
        contenido.addWidget(self.mensaje)

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

        if self.editando:
            self.cargar_usuario()

    def limpiar(self):
        for campo in (self.nombre, self.usuario, self.correo, self.password, self.confirmar):
            campo.clear()
        self.rol.setCurrentIndex(0)
        self.estado.setCurrentIndex(0)
        self.mensaje.setText("")

    def cargar_usuario(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT nombre_completo, usuario, correo, rol, estado
                FROM usuarios WHERE usuario = %s
            """, (self.usuario_original,))
            r = cursor.fetchone()
            cursor.close()
            conexion.close()
            if r:
                self.nombre.setText(r[0] or "")
                self.usuario.setText(r[1] or "")
                self.correo.setText(r[2] or "")
                self.rol.setCurrentText(r[3] or "")
                self.estado.setCurrentText(r[4] or "")
        except Exception as e:
            self.mensaje.setText(f"Error: {e}")

    def guardar_usuario(self):
        nombre = self.nombre.text().strip()
        usuario = self.usuario.text().strip()
        correo = self.correo.text().strip()
        password = self.password.text()

        if not nombre:
            self.mensaje.setText("Ingrese el nombre")
            return
        if not usuario:
            self.mensaje.setText("Ingrese el usuario")
            return
        if correo and "@" not in correo:
            self.mensaje.setText("El correo no es válido")
            return
        if not self.editando and not password:
            self.mensaje.setText("Ingrese una contraseña")
            return
        if password != self.confirmar.text():
            self.mensaje.setText("Las contraseñas no coinciden")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # Evitar usuarios duplicados
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE usuario=%s AND usuario<>%s",
                (usuario, self.usuario_original or "")
            )
            if cursor.fetchone()[0] > 0:
                self.mensaje.setText("Ya existe un usuario con ese nombre")
                cursor.close()
                conexion.close()
                return

            if self.editando:
                if password:
                    cursor.execute("""
                        UPDATE usuarios
                        SET nombre_completo=%s, usuario=%s, correo=%s,
                            contrasena=%s, rol=%s, estado=%s
                        WHERE usuario=%s
                    """, (nombre, usuario, correo, password,
                          self.rol.currentText(), self.estado.currentText(),
                          self.usuario_original))
                else:
                    cursor.execute("""
                        UPDATE usuarios
                        SET nombre_completo=%s, usuario=%s, correo=%s,
                            rol=%s, estado=%s
                        WHERE usuario=%s
                    """, (nombre, usuario, correo,
                          self.rol.currentText(), self.estado.currentText(),
                          self.usuario_original))
            else:
                cursor.execute("""
                    INSERT INTO usuarios
                    (nombre_completo, usuario, correo, contrasena, rol, estado)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (nombre, usuario, correo, password,
                      self.rol.currentText(), self.estado.currentText()))

            conexion.commit()
            cursor.close()
            conexion.close()

            QMessageBox.information(self, "Usuarios", "Usuario guardado correctamente")
            self.accept()

        except Exception as e:
            self.mensaje.setText(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = NuevoUsuario()
    ventana.exec()