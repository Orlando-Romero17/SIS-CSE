"""Funciones compartidas por las páginas: exportar tablas y eliminar registros."""
import csv
import mysql.connector
from PySide6.QtWidgets import QFileDialog, QMessageBox
from conexion import conectar

ESTILO_PELIGRO = (
    "QPushButton{background-color:#c0392b;color:white;border:none;"
    "border-radius:4px;padding:9px 16px;min-height:18px;}"
    "QPushButton:hover{background-color:#a5301f;}"
)


def exportar_tabla(parent, tabla, nombre_base="exportacion"):
    """Exporta lo que muestra un QTableWidget a Excel (.xlsx) o CSV."""
    if tabla.rowCount() == 0:
        QMessageBox.information(parent, "Exportar", "No hay datos para exportar.")
        return False

    ruta, filtro = QFileDialog.getSaveFileName(
        parent, "Exportar", f"{nombre_base}.xlsx", "Excel (*.xlsx);;CSV (*.csv)"
    )
    if not ruta:
        return False

    low = ruta.lower()
    if not (low.endswith(".xlsx") or low.endswith(".csv")):
        ruta += ".csv" if "CSV" in filtro else ".xlsx"

    encabezados = []
    for c in range(tabla.columnCount()):
        h = tabla.horizontalHeaderItem(c)
        encabezados.append(h.text() if h else "")
    filas = []
    for f in range(tabla.rowCount()):
        filas.append([
            tabla.item(f, c).text() if tabla.item(f, c) else ""
            for c in range(tabla.columnCount())
        ])

    try:
        if ruta.lower().endswith(".csv"):
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                w = csv.writer(archivo)
                w.writerow(encabezados)
                w.writerows(filas)
        else:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.append(encabezados)
            for fila in filas:
                ws.append(fila)
            wb.save(ruta)
        QMessageBox.information(parent, "Exportar", f"Archivo guardado en:\n{ruta}")
        return True
    except ImportError:
        QMessageBox.warning(
            parent, "Exportar",
            "Falta la librería openpyxl para Excel.\nInstálela con: pip install openpyxl\n"
            "o exporte en formato CSV."
        )
    except Exception as e:
        QMessageBox.warning(parent, "Exportar", f"No se pudo guardar el archivo:\n{e}")
    return False


def confirmar_y_eliminar(parent, sql, params, descripcion):
    """Pide confirmación y ejecuta un DELETE. Devuelve True si se eliminó."""
    r = QMessageBox.question(
        parent, "Eliminar",
        f"¿Eliminar {descripcion}?\nEsta acción no se puede deshacer.",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    if r != QMessageBox.Yes:
        return False
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(sql, params)
        conexion.commit()
        borradas = cursor.rowcount
        cursor.close()
        conexion.close()
        return borradas > 0
    except mysql.connector.Error as e:
        if e.errno == 1451:
            msg = ("No se puede eliminar porque tiene datos relacionados "
                   "(por ejemplo trámites). Puede desactivarlo en su lugar.")
        else:
            msg = str(e)
        QMessageBox.warning(parent, "No se pudo eliminar", msg)
        return False