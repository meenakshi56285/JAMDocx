from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(text, filename):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>Document Comparison Report</b>", styles["Title"]))
    story.append(Paragraph(text.replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(story)