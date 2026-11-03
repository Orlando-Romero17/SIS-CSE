"""
utilidades.py
Funciones compartidas por varias páginas:
  - exportar_tabla: guarda lo que muestra una tabla en Excel o CSV.
  - confirmar_y_eliminar: pide confirmación y ejecuta un borrado.
"""
import csv
from PySide6.QtWidgets import QFileDialog, QMessageBox
from sqlalchemy.exc import IntegrityError

# Estilo (rojo) del botón Eliminar
ESTILO_PELIGRO = (
    "QPushButton{background-color:#c0392b;color:white;border:none;"
    "border-radius:4px;padding:9px 16px;min-height:18px;}"
    "QPushButton:hover{background-color:#a5301f;}"
)


def exportar_tabla(parent, tabla, nombre_base="exportacion"):
    """Exporta el contenido de un QTableWidget a un archivo Excel (.xlsx) o CSV."""
    # Si la tabla está vacía no hay nada que exportar
    if tabla.rowCount() == 0:
        QMessageBox.information(parent, "Exportar", "No hay datos para exportar.")
        return False

    # Ventana para elegir dónde guardar y en qué formato
    ruta, filtro = QFileDialog.getSaveFileName(
        parent, "Exportar", f"{nombre_base}.xlsx", "Excel (*.xlsx);;CSV (*.csv)"
    )
    if not ruta:
        return False

    # Si el usuario no escribió extensión, se agrega según el filtro elegido
    low = ruta.lower()
    if not (low.endswith(".xlsx") or low.endswith(".csv")):
        ruta += ".csv" if "CSV" in filtro else ".xlsx"

    # Se leen los encabezados y las filas desde la tabla de la interfaz
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
            # utf-8-sig para que Excel muestre bien las tildes
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                w = csv.writer(archivo)
                w.writerow(encabezados)
                w.writerows(filas)
        else:
            from openpyxl import Workbook  # librería para crear archivos Excel
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


def confirmar_y_eliminar(parent, funcion_eliminar, descripcion):
    """Pregunta si desea eliminar y, si acepta, ejecuta funcion_eliminar().
    funcion_eliminar es una función del repositorio (ORM) que devuelve True/False.
    Devuelve True si se eliminó."""
    r = QMessageBox.question(
        parent, "Eliminar",
        f"¿Eliminar {descripcion}?\nEsta acción no se puede deshacer.",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    if r != QMessageBox.Yes:
        return False
    try:
        return bool(funcion_eliminar())
    except IntegrityError:
        # Error de llave foránea: el registro tiene datos relacionados (ej. trámites)
        QMessageBox.warning(
            parent, "No se pudo eliminar",
            "No se puede eliminar porque tiene datos relacionados "
            "(por ejemplo trámites). Puede desactivarlo en su lugar."
        )
    except Exception as e:
        QMessageBox.warning(parent, "No se pudo eliminar", str(e))
    return False