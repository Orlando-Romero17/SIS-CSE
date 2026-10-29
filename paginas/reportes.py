"""
reportes.py
Página para generar reportes: muestra una vista previa en tabla, permite
exportar a Excel/CSV y generar el PDF (ReportLab) con un botón.
Los datos se obtienen con el ORM en un hilo.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog, QMessageBox
)
from PySide6.QtCore import QDate, QUrl
from PySide6.QtGui import QDesktopServices
from Estilos.css import CONFIGURACION
from utilidades import exportar_tabla
from hilos.trabajador import ejecutar_en_hilo
from repositorio import datos_reporte, registrar_reporte
from reporte_pdf import generar_pdf

# Tipos de reporte disponibles en la lista desplegable
TIPOS = ["Registros de ciudadanos", "Trámites", "Usuarios del sistema"]


class Reportes(QWidget):
    def __init__(self):
        super().__init__()
        self._ultimo = None  # (tipo, inicio, fin) del último reporte generado

        contenido = QVBoxLayout(self)
        contenido.setContentsMargins(30, 25, 30, 25)
        contenido.setSpacing(8)

        titulo = QLabel("Reportes")
        titulo.setObjectName("titulo")
        contenido.addWidget(titulo)

        sub = QLabel("Genere reportes de la información registrada en el sistema.")
        sub.setObjectName("subtitulo")
        contenido.addWidget(sub)

        # Formulario: tipo de reporte y rango de fechas
        grupo = QGroupBox("Generar reporte")
        l = QVBoxLayout(grupo)

        l.addWidget(QLabel("Tipo de reporte"))
        self.tipo = QComboBox()
        self.tipo.addItems(["Seleccione"] + TIPOS)
        l.addWidget(self.tipo)

        l.addWidget(QLabel("Fecha inicial"))
        self.inicio = QDateEdit()
        self.inicio.setCalendarPopup(True)
        self.inicio.setDate(QDate.currentDate())
        l.addWidget(self.inicio)

        l.addWidget(QLabel("Fecha final"))
        self.fin = QDateEdit()
        self.fin.setCalendarPopup(True)
        self.fin.setDate(QDate.currentDate())
        l.addWidget(self.fin)

        # Botones: Exportar (Excel/CSV), Generar PDF y Generar reporte
        fila = QHBoxLayout()
        generar = QPushButton("Generar reporte")
        generar.setObjectName("principal")
        generar.clicked.connect(self.guardar_reporte)
        pdf = QPushButton("Generar PDF")
        pdf.setObjectName("principal")
        pdf.clicked.connect(self.generar_pdf_reporte)
        exportar = QPushButton("Exportar")
        exportar.setObjectName("secundario")
        exportar.clicked.connect(self.exportar)
        fila.addStretch()
        fila.addWidget(exportar)
        fila.addWidget(pdf)
        fila.addWidget(generar)
        l.addLayout(fila)
        contenido.addWidget(grupo)

        self.mensaje = QLabel("")
        contenido.addWidget(self.mensaje)

        # Vista previa del reporte generado
        resultado = QGroupBox("Vista previa del reporte")
        rl = QVBoxLayout(resultado)
        self.tabla = QTableWidget()
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        rl.addWidget(self.tabla)
        contenido.addWidget(resultado, 1)

    def guardar_reporte(self):
        """Valida los datos y consulta el reporte (ORM) en segundo plano."""
        if self.tipo.currentIndex() == 0:
            QMessageBox.warning(self, "Validación", "Seleccione un tipo de reporte")
            return
        if self.inicio.date() > self.fin.date():
            QMessageBox.warning(self, "Validación",
                                "La fecha inicial no puede ser mayor que la final")
            return

        tipo = self.tipo.currentText()
        inicio = self.inicio.date().toPython()   # QDate -> datetime.date
        fin = self.fin.date().toPython()

        self.mensaje.setText("Generando reporte...")
        ejecutar_en_hilo(
            datos_reporte, tipo, inicio, fin,
            al_terminar=lambda r: self._mostrar_reporte(r, tipo, inicio, fin),
            al_error=lambda m: self.mensaje.setText(f"Error al generar el reporte: {m}"),
        )

    def _mostrar_reporte(self, resultado, tipo, inicio, fin):
        """Llena la tabla con el resultado y registra el reporte en la BD."""
        encabezados, filas = resultado
        self.tabla.setColumnCount(len(encabezados))
        self.tabla.setHorizontalHeaderLabels(encabezados)
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, v in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem("" if v is None else str(v)))

        self._ultimo = (tipo, inicio, fin)
        total = len(filas)

        # Se deja constancia del reporte en la tabla reportes (también en segundo plano)
        ejecutar_en_hilo(
            registrar_reporte, tipo, inicio, fin,
            al_terminar=lambda _: self.mensaje.setText(
                f"Reporte generado correctamente ({total} registros)"),
            al_error=lambda m: self.mensaje.setText(
                f"Reporte mostrado, pero no se pudo registrar: {m}"),
        )

    def generar_pdf_reporte(self):
        """Genera el PDF del reporte que se ve en la tabla y lo abre al terminar."""
        if self.tabla.rowCount() == 0 or self._ultimo is None:
            QMessageBox.information(self, "PDF", "Primero genere un reporte para crear el PDF.")
            return

        tipo, inicio, fin = self._ultimo
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte PDF",
            f"reporte_{tipo.replace(' ', '_').lower()}.pdf", "PDF (*.pdf)"
        )
        if not ruta:
            return
        if not ruta.lower().endswith(".pdf"):
            ruta += ".pdf"

        # Se leen los datos de la tabla (en el hilo principal, donde vive la interfaz)
        encabezados = [self.tabla.horizontalHeaderItem(c).text()
                       for c in range(self.tabla.columnCount())]
        filas = [[self.tabla.item(f, c).text() if self.tabla.item(f, c) else ""
                  for c in range(self.tabla.columnCount())]
                 for f in range(self.tabla.rowCount())]

        self.mensaje.setText("Generando PDF...")
        # La creación del PDF corre en un hilo para no congelar la ventana
        ejecutar_en_hilo(
            generar_pdf, ruta, f"Reporte: {tipo}",
            f"Período: {inicio:%d/%m/%Y} al {fin:%d/%m/%Y}", encabezados, filas,
            al_terminar=lambda r: self._pdf_listo(r),
            al_error=lambda m: self.mensaje.setText(f"Error al generar el PDF: {m}"),
        )

    def _pdf_listo(self, ruta):
        """Avisa que el PDF se creó y lo abre con el visor del sistema."""
        self.mensaje.setText(f"PDF generado: {ruta}")
        QMessageBox.information(self, "PDF", f"El PDF se generó correctamente en:\n{ruta}")
        QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))

    def exportar(self):
        """Exporta la vista previa a Excel o CSV."""
        if self.tabla.rowCount() == 0:
            QMessageBox.information(self, "Exportar", "Primero genere un reporte para exportarlo")
            return
        exportar_tabla(self, self.tabla, self.tipo.currentText().replace(" ", "_").lower())


# Solo para probar esta página sola
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Reportes()
    ventana.setStyleSheet(CONFIGURACION)
    ventana.resize(900, 650)
    ventana.show()
    sys.exit(app.exec())
