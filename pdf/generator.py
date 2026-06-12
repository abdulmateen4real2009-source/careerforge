from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def safe(text):
    """Prevents None crashing ReportLab"""
    return text if text else ""


def add_section(content, title, body, styles):
    content.append(Paragraph(title, styles["Heading2"]))
    content.append(Spacer(1, 6))
    content.append(Paragraph(safe(body), styles["Normal"]))
    content.append(Spacer(1, 14))


def add_contact_line(content, label, value, styles):
    if value:
        content.append(Paragraph(f"<b>{label}:</b> {value}", styles["Normal"]))


def generate_pdf(resume, filename):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    # =====================
    # HEADER (CLEAN & PROFESSIONAL)
    # =====================
    content.append(Paragraph(resume.full_name or "Unnamed User", styles["Title"]))
    content.append(Spacer(1, 8))

    add_contact_line(content, "Email", safe(resume.email), styles)
    add_contact_line(content, "Phone", safe(resume.phone), styles)
    add_contact_line(content, "Location", safe(resume.location), styles)

    content.append(Spacer(1, 15))

    # =====================
    # SUMMARY
    # =====================
    add_section(content, "Professional Summary", resume.bio, styles)

    # =====================
    # CORE SECTIONS
    # =====================
    add_section(content, "Education", resume.education, styles)
    add_section(content, "Skills", resume.skills, styles)
    add_section(content, "Projects", resume.projects, styles)

    # =====================
    # LINKS (CLEAN FORMAT)
    # =====================
    links = f"""
    GitHub: {safe(resume.github)}<br/>
    LinkedIn: {safe(resume.linkedin)}
    """

    add_section(content, "Links", links, styles)

    # =====================
    # FOOTER (BRANDING)
    # =====================
    content.append(Spacer(1, 25))
    content.append(Paragraph(
        "Generated with CareerForge • AI CV Builder",
        styles["Normal"]
    ))

    doc.build(content)