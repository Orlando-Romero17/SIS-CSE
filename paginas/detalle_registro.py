"""
detalle_registro.py
Ventana para ver, editar, desactivar, eliminar e imprimir un ciudadano.
Si se abre sin ID funciona como formulario de "Nuevo ciudadano".
Todas las operaciones usan el ORM (repositorio.py).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from Estilos.css import CONFIGURACION
from utilidades import confirmar_y_eliminar, ESTILO_PELIGRO
from repositorio import (
    obtener_ciudadano, existe_cedula, crear_ciudadano, actualizar_ciudadano,
    eliminar_ciudadano
)

# (nombre de la columna en la BD, etiqueta que ve el usuario)
CAMPOS = [
    ("cedula", "Cédula"),
    ("nombres", "Nombres"),
    ("apellidos", "Apellidos"),
    ("fecha_nacimiento", "Fecha nacimiento (AAAA-MM-DD)"),
    ("genero", "Género"),
    ("departamento", "Departamento"),
    ("municipio", "Municipio"),
    ("direccion", "Dirección"),
    ("telefono", "Teléfono"),
    ("correo", "Correo"),
]
# Fondo gris para los campos cuando solo se están consultando
RO_STYLE = "background-color:#eef1f4;"


class DetalleRegistro(QDialog):
    def __init__(self, id_ciudadano=None, parent=None):
        super().__init__(parent)
        self.id_ciudadano = id_ciudadano
        self.creando = id_ciudadano is None   # True = formulario de nuevo ciudadano
        self.editando = False
        self.setWindowTitle("Nuevo ciudadano" if self.creando else "Detalle de registro")
        self.setStyleSheet(CONFIGURACION)
        self.setMinimumSize(760, 520)
        self.setModal(True)

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(25, 20, 25, 20)
        contenido.setSpacing(8)

        titulo = QLabel("Nuevo ciudadano" if self.creando else "Detalle de registro")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)
        sub = QLabel("Complete los datos del ciudadano." if self.creando
                     else "Información completa del registro seleccionado.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        fila = QHBoxLayout()

        # ----- Izquierda: datos del ciudadano -----
        datos = QGroupBox("Información del ciudadano")
        form = QFormLayout(datos)
        self.campos = {}  # nombre de columna -> campo de texto
        for nombre, etiqueta in CAMPOS:
            w = QLineEdit()
            self.campos[nombre] = w
            form.addRow(etiqueta + ":", w)
        self.estado = QComboBox()
        self.estado.addItems(["Activo", "Inactivo"])
        form.addRow("Estado:", self.estado)
        fila.addWidget(datos, 3)

        # ----- Derecha: botones de acciones -----
        acciones = QGroupBox("Acciones")
        al = QVBoxLayout(acciones)
        self.btn_editar = QPushButton("Guardar registro" if self.creando else "Editar registro")
        self.btn_editar.setObjectName("principal")
        self.btn_editar.clicked.connect(self.alternar_edicion)
        self.btn_estado = QPushButton("Desactivar registro")
        self.btn_estado.setObjectName("principal")
        self.btn_estado.clicked.connect(self.cambiar_estado)
        self.btn_eliminar = QPushButton("Eliminar registro")
        self.btn_eliminar.setStyleSheet(ESTILO_PELIGRO)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_imprimir = QPushButton("Imprimir")
        self.btn_imprimir.setObjectName("secundario")
        self.btn_imprimir.clicked.connect(self.imprimir)
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setObjectName("secundario")
        self.btn_cerrar.clicked.connect(self.cerrar_o_cancelar)
        for b in (self.btn_editar, self.btn_estado, self.btn_eliminar,
                  self.btn_imprimir, self.btn_cerrar):
            al.addWidget(b)
        al.addStretch()
        fila.addWidget(acciones, 1)
        contenido.addLayout(fila)
        contenido.addStretch()

        if self.creando:
            # En modo "nuevo" solo tienen sentido Guardar y Cancelar
            for b in (self.btn_estado, self.btn_eliminar, self.btn_imprimir):
                b.hide()
            self.btn_cerrar.setText("Cancelar")
            self._set_editable(True)
        else:
            self.cargar_detalle()
            self._set_editable(False)

    # ---------- Utilidades internas ----------
    def _set_editable(self, editable):
        """Activa o desactiva la edición de los campos y ajusta los botones."""
        self.editando = editable
        for w in self.campos.values():
            w.setReadOnly(not editable)
            w.setStyleSheet("" if editable else RO_STYLE)
        self.estado.setEnabled(editable)
        if not self.creando:
            self.btn_editar.setText("Guardar cambios" if editable else "Editar registro")
            self.btn_cerrar.setText("Cancelar edición" if editable else "Cerrar")
            self.btn_estado.setEnabled(not editable)
            self.btn_eliminar.setEnabled(not editable)

    def _poner_estado(self, valor):
        """Muestra el estado y cambia el texto del botón Activar/Desactivar."""
        if self.estado.findText(valor) < 0:
            self.estado.addItem(valor)
        self.estado.setCurrentText(valor)
        self.btn_estado.setText(
            "Activar registro" if valor.lower().startswith("inact") else "Desactivar registro"
        )

    # ---------- READ ----------
    def cargar_detalle(self):
        """Trae el ciudadano desde la BD (ORM) y llena los campos."""
        try:
            d = obtener_ciudadano(self.id_ciudadano)
            if d:
                for nombre, _ in CAMPOS:
                    self.campos[nombre].setText(d[nombre])
                self._poner_estado(d["estado"] or "Activo")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el registro:\n{e}")

    # ---------- CREATE / UPDATE ----------
    def alternar_edicion(self):
        """Primer clic: habilita la edición. Segundo clic: guarda los cambios."""
        if self.creando or self.editando:
            self.guardar()
        else:
            self._set_editable(True)

    def cerrar_o_cancelar(self):
        """Si se está editando, cancela y recarga; si no, cierra la ventana."""
        if self.editando and not self.creando:
            self.cargar_detalle()
            self._set_editable(False)
        else:
            self.reject()

    def guardar(self):
        """Valida (con MessageBox) y guarda: INSERT si es nuevo, UPDATE si existe."""
        valores = {n: self.campos[n].text().strip() for n, _ in CAMPOS}

        # ----- Validaciones -----
        if not valores["cedula"] or not valores["nombres"] or not valores["apellidos"]:
            QMessageBox.warning(self, "Datos incompletos",
                                "Cédula, nombres y apellidos son obligatorios.")
            return
        fecha = valores["fecha_nacimiento"]
        if fecha and not QDate.fromString(fecha, "yyyy-MM-dd").isValid():
            QMessageBox.warning(self, "Fecha inválida",
                                "Use el formato AAAA-MM-DD (ejemplo: 1990-05-23).")
            return
        if valores["correo"] and "@" not in valores["correo"]:
            QMessageBox.warning(self, "Correo inválido", "Revise el correo electrónico.")
            return

        estado = self.estado.currentText()
        datos = dict(valores)
        datos["estado"] = estado

        try:
            # La cédula no puede repetirse entre ciudadanos
            if existe_cedula(valores["cedula"], excluir_id=self.id_ciudadano):
                QMessageBox.warning(self, "Duplicado", "Ya existe un ciudadano con esa cédula.")
                return

            if self.creando:
                crear_ciudadano(datos)                              # CREATE
            else:
                actualizar_ciudadano(self.id_ciudadano, datos)      # UPDATE

            QMessageBox.information(self, "Registro", "Registro guardado correctamente")
            if self.creando:
                self.accept()
            else:
                self._poner_estado(estado)
                self._set_editable(False)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar:\n{e}")

    # ---------- Desactivar / activar ----------
    def cambiar_estado(self):
        """Alterna el estado del ciudadano entre Activo e Inactivo (UPDATE)."""
        nuevo = "Activo" if self.estado.currentText().lower().startswith("inact") else "Inactivo"
        try:
            actualizar_ciudadano(self.id_ciudadano, {"estado": nuevo})
            self._poner_estado(nuevo)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cambiar el estado:\n{e}")

    # ---------- DELETE ----------
    def eliminar(self):
        """Confirma y elimina el ciudadano; si se elimina, cierra la ventana."""
        nombre = f"{self.campos['nombres'].text()} {self.campos['apellidos'].text()}".strip()
        if confirmar_y_eliminar(
            self, lambda: eliminar_ciudadano(self.id_ciudadano), f"el registro de «{nombre}»"
        ):
            self.accept()

    # ---------- Imprimir ----------
    def imprimir(self):
        """Arma una versión imprimible de la ficha y abre el diálogo de impresión."""
        filas = "".join(
            f"<tr><td><b>{etiqueta}</b></td><td>{self.campos[n].text()}</td></tr>"
            for n, etiqueta in CAMPOS
        )
        html = (
            "<h2>Consejo Supremo Electoral - Detalle de registro</h2>"
            f"<table cellpadding='4'>{filas}"
            f"<tr><td><b>Estado</b></td><td>{self.estado.currentText()}</td></tr></table>"
        )
        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter()
        dialogo = QPrintDialog(printer, self)
        if dialogo.exec() == QDialog.Accepted:
            doc.print_(printer)


# Solo para probar esta ventana sola (ID 1)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = DetalleRegistro(1)
    ventana.exec()
