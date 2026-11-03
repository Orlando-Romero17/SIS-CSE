"""
reporte_pdf.py
Genera reportes en PDF con ReportLab: encabezado institucional, tabla con
estilo (TableStyle), total de registros y número de página.
Se llama desde el botón "Generar PDF" de la página Reportes.
"""
from datetime import datetime
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _pie_de_pagina(canvas, doc):
    """Dibuja en cada página el pie con la institución y el número de página."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#606a75"))
    canvas.drawString(doc.leftMargin, 1.1 * cm, "SIS-CSE - Consejo Supremo Electoral")
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 1.1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def generar_pdf(ruta, titulo, subtitulo, encabezados, filas):
    """Crea el archivo PDF en 'ruta' con los encabezados y filas recibidos."""
    # Si hay muchas columnas se usa la hoja en horizontal para que quepan
    tamano = landscape(letter) if len(encabezados) > 5 else letter
    margen = 1.5 * cm
    doc = SimpleDocTemplate(ruta, pagesize=tamano, leftMargin=margen, rightMargin=margen,
                            topMargin=1.8 * cm, bottomMargin=2 * cm, title=titulo)

    # Estilos de texto
    base = getSampleStyleSheet()
    st_inst = ParagraphStyle("inst", parent=base["Title"], fontSize=16,
                             textColor=colors.HexColor("#102b4a"))
    st_titulo = ParagraphStyle("tit", parent=base["Heading2"], alignment=1)
    st_sub = ParagraphStyle("sub", parent=base["Normal"], alignment=1, fontSize=9,
                            textColor=colors.HexColor("#606a75"))
    st_cab = ParagraphStyle("cab", parent=base["Normal"], fontName="Helvetica-Bold",
                            fontSize=9, textColor=colors.white)
    st_cel = ParagraphStyle("cel", parent=base["Normal"], fontSize=8, leading=10)

    # Contenido del documento
    contenido = [
        Paragraph("Consejo Supremo Electoral - Nicaragua", st_inst),
        Paragraph(escape(titulo), st_titulo),
        Paragraph(escape(subtitulo), st_sub),
        Paragraph(f"Generado: {datetime.now():%d/%m/%Y %H:%M} | Total de registros: {len(filas)}",
                  st_sub),
        Spacer(1, 0.5 * cm),
    ]

    # Datos de la tabla (cada celda es un Paragraph para que el texto largo se ajuste)
    datos = [[Paragraph(escape(str(h)), st_cab) for h in encabezados]]
    for fila in filas:
        datos.append([Paragraph(escape("" if v is None else str(v)), st_cel) for v in fila])

    # Columnas de igual ancho ocupando toda la página
    ancho_total = tamano[0] - 2 * margen
    tabla = Table(datos, colWidths=[ancho_total / len(encabezados)] * len(encabezados),
                  repeatRows=1)  # repeatRows: repite el encabezado en cada página

    # TableStyle: colores, bordes y filas alternadas
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102b4a")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9ced4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f3f5")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    contenido.append(tabla)

    doc.build(contenido, onFirstPage=_pie_de_pagina, onLaterPages=_pie_de_pagina)
    return ruta