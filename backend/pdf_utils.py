import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import inch
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def add_footer(canvas, doc):
    """
    Dibuja el pie de página en cada hoja.
    """
    canvas.saveState()
    footer_text = "Desarrollado por Pelayo Quirós&Ramón Codesido | MPAD1 by SDC"
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(doc.pagesize[0] - 40, 20, footer_text)
    canvas.restoreState()

def generar_pdf_simple(titulo, subtitulo, figuras, logo_path, comentarios_por_figura=None):
    """
    Genera un PDF con encabezado personalizado (logo y título), y una figura por página con su comentario.
    Es compatible con figuras matplotlib y mplsoccer. Devuelve un buffer listo para st.download_button.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TituloPDF', fontSize=14, alignment=TA_RIGHT, textColor=colors.black, spaceAfter=6))
    styles.add(ParagraphStyle(name='SubtituloPDF', fontSize=10, alignment=TA_RIGHT, textColor=colors.grey, spaceAfter=12))
    styles.add(ParagraphStyle(name='ComentarioFigura', fontSize=11, alignment=TA_CENTER, textColor=colors.black, spaceAfter=10))
    styles.add(ParagraphStyle(name='ComentarioInferiorDerecha', fontSize=10, alignment=TA_RIGHT, textColor=colors.black, spaceAfter=4))
    styles.add(ParagraphStyle(name='ComentarioTituloCentrado', fontSize=12, alignment=TA_CENTER, textColor=colors.black, spaceAfter=12))

    elements = []

    for idx, fig in enumerate(figuras):
        # Encabezado (logo + título/subtítulo)
        header_table_data = []

        # Logo (si existe)
        if logo_path:
            try:
                with open(logo_path, 'rb') as img_file:
                    logo_img = io.BytesIO(img_file.read())
                logo = ReportLabImage(logo_img, width=0.7*inch, height=0.7*inch)
                header_table_data.append([logo, Paragraph(f"<b>RP Scouting</b><br/>{titulo}", styles['TituloPDF'])])
            except Exception as e:
                print(f"⚠️ Error cargando logo: {e}")
                header_table_data.append(['', Paragraph(f"<b>RP Scouting</b><br/>{titulo}", styles['TituloPDF'])])
        else:
            header_table_data.append(['', Paragraph(f"<b>RP Scouting</b><br/>{titulo}", styles['TituloPDF'])])

        header_table = Table(header_table_data, colWidths=[0.9*inch, 9.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        elements.append(header_table)

        # Subtítulo
        elements.append(Paragraph(subtitulo, styles['SubtituloPDF']))

        # Comentario
        if comentarios_por_figura and idx < len(comentarios_por_figura):
            comentario = comentarios_por_figura[idx]
            if isinstance(comentario, dict) and 'titulo' in comentario and 'alineado_derecha' in comentario:
                # Comentario especial tipo interpretación de clustering
                elements.append(Paragraph(comentario['titulo'], styles['ComentarioTituloCentrado']))
                for linea in comentario['alineado_derecha']:
                    elements.append(Paragraph(linea, styles['ComentarioInferiorDerecha']))
            else:
                # Comentario normal
                elements.append(Paragraph(comentario, styles['ComentarioFigura']))

        # Figura a imagen
        fig.patch.set_facecolor('white')  # Forzar fondo blanco
        canvas = FigureCanvas(fig)
        canvas.draw()

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)

        imagen = ReportLabImage(img_buffer, width=7.5 * inch, height=4.5 * inch)
        imagen.hAlign = 'CENTER'
        elements.append(imagen)

        # Salto de página si no es la última
        if idx < len(figuras) - 1:
            elements.append(PageBreak())

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer
