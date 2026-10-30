"""
css.py
Estilo visual único (hoja de estilos Qt) de todo el sistema SIS-CSE.
Cada ventana lo aplica con: self.setStyleSheet(GENERAL)
Los widgets se estilizan por su nombre de objeto (setObjectName), por ejemplo
el botón con setObjectName("principal") toma el estilo QPushButton#principal.
"""

GENERAL = """
/* ============ BASE ============ */
QWidget {
    background-color: #f7f8fa;
    color: #20252b;
    font-family: Arial;
    font-size: 12px;
}
QLabel, QCheckBox {
    background-color: transparent;
}
QDialog, QMessageBox {
    background-color: #f7f8fa;
}

/* ============ BARRA LATERAL ============ */
QFrame#sidebar {
    background-color: #102b4a;
}
QFrame#sidebar QLabel {
    background-color: transparent;
}
QLabel#logo {
    color: white;
    background-color: #173b63;
    border: 2px solid #6fa8dc;
    border-radius: 34px;
    font-size: 15px;
    font-weight: bold;
}
QLabel#marca {
    color: white;
    font-size: 19px;
    font-weight: bold;
}
QLabel#descripcion {
    color: #d8e0e8;
    font-size: 10px;
}
QLabel#lema {
    color: #d8e0e8;
    font-size: 10px;
    background-color: transparent;
}
QPushButton#menu {
    text-align: left;
    background-color: transparent;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 12px;
    min-height: 18px;
}
QPushButton#menu:hover {
    background-color: #1d4772;
}
QPushButton#activo {
    text-align: left;
    background-color: #2476c7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 12px;
    min-height: 18px;
}

/* ============ TEXTOS ============ */
QLabel#titulo {
    font-size: 21px;
    font-weight: bold;
}
QLabel#subtitulo {
    color: #606a75;
    font-size: 12px;
}
QLabel#cifra {
    font-size: 25px;
    font-weight: bold;
    color: #2476c7;
}

/* ============ CAMPOS DE ENTRADA ============ */
QLineEdit, QComboBox, QTextEdit, QDateEdit {
    background-color: white;
    border: 1px solid #d3d8de;
    border-radius: 4px;
    padding: 8px;
    min-height: 20px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {
    border: 1px solid #2476c7;
}
QLineEdit:read-only {
    background-color: #eef1f4;
}
QComboBox QAbstractItemView {
    background-color: white;
    selection-background-color: #2476c7;
    selection-color: white;
}

/* ============ CAJAS (GROUPBOX) ============ */
QGroupBox {
    background-color: white;
    border: 1px solid #d9dde2;
    border-radius: 5px;
    margin-top: 10px;
    padding: 14px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    background-color: #f7f8fa;
}

/* ============ BOTONES ============ */
QPushButton {
    background-color: #e7eaee;
    color: #30363d;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #d9dde2;
}
QPushButton:disabled {
    background-color: #eceef1;
    color: #9aa3ad;
}
QPushButton#principal {
    background-color: #2476c7;
    color: white;
    padding: 9px 16px;
    min-height: 18px;
}
QPushButton#principal:hover {
    background-color: #1c62a5;
}
QPushButton#principal:disabled {
    background-color: #9dbfe0;
    color: white;
}
QPushButton#secundario {
    background-color: #e7eaee;
    color: #30363d;
    padding: 9px 16px;
}
QPushButton#secundario:hover {
    background-color: #d9dde2;
}
QPushButton#peligro {
    background-color: #c0392b;
    color: white;
    padding: 9px 16px;
    min-height: 18px;
}
QPushButton#peligro:hover {
    background-color: #a5301f;
}

/* Menú interno de Configuración */
QPushButton#submenu {
    text-align: left;
    background-color: #f1f3f5;
    color: #20252b;
    padding: 10px 12px;
}
QPushButton#submenu:hover {
    background-color: #e3e7eb;
}
QPushButton#submenu_activo {
    text-align: left;
    background-color: #2476c7;
    color: white;
    padding: 10px 12px;
}

/* ============ TABLAS ============ */
QTableWidget {
    background-color: white;
    border: 1px solid #d9dde2;
    gridline-color: #e1e4e8;
    selection-background-color: #dbe9f7;
    selection-color: #20252b;
}
QHeaderView::section {
    background-color: #eef1f4;
    padding: 7px;
    border: none;
    font-weight: bold;
}
"""