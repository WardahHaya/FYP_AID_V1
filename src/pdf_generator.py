import html
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from src.config import REPORTS_DIR

URDU_LABELS = {
    "title": "آٹزم پری اسکریننگ رپورٹ",
    "screening_score": "اسکریننگ اسکور",
    "risk_level": "خطرے کی سطح",
    "referral": "رہنمائی",
    "default_prediction": "ابتدائی ماڈل پیش گوئی",
    "screening_prediction": "اسکریننگ پیش گوئی",
    "class_probabilities": "درجہ بندی کے امکانات",
    "disclaimer": "⚠️ اہم نوٹ: یہ رپورٹ صرف ابتدائی اسکریننگ معاونت کے لیے ہے، کوئی طبی تشخیص نہیں۔ کسی بھی فیصلے سے پہلے ہمیشہ کسی ماہر سے مشورہ لیں۔",
    "quick_summary": "فوری خلاصہ",
    "about_score": "اسکور کا مطلب",
    "parent_guide": "والدین کے لیے رہنمائی",
}

EN_LABELS = {
    "title": "🧠 Autism Pre-Screening Risk Assessment",
    "screening_score": "Screening Score",
    "risk_level": "Risk Level",
    "referral": "Recommendation",
    "default_prediction": "ML Assessment",
    "class_probabilities": "Confidence Levels",
    "disclaimer": "⚠️ Important: This report supports early screening only and is NOT a medical diagnosis. Always consult a professional before making any decisions.",
    "quick_summary": "Quick Summary",
    "about_score": "What Your Score Means",
    "parent_guide": "Personalized Guidance",
}

RISK_COLORS = {
    "No Risk": colors.HexColor("#27AE60"),  # Green
    "Mild Risk": colors.HexColor("#F39C12"),  # Orange
    "Moderate Risk": colors.HexColor("#E74C3C"),  # Red
    "Severe Risk": colors.HexColor("#C0392B"),  # Dark Red
}

FONT_CACHE = {"regular": None, "bold": None}


def normalize_language(language: str | None, report_text: str = "") -> str:
    if str(language or "").strip().lower().startswith("ur"):
        return "ur"
    return "ur" if re.search(r"[\u0600-\u06FF]", report_text or "") else "en"


def register_unicode_fonts() -> tuple[str, str]:
    if FONT_CACHE["regular"] and FONT_CACHE["bold"]:
        return FONT_CACHE["regular"], FONT_CACHE["bold"]

    candidates = [
        (Path(r"C:\Windows\Fonts\tahoma.ttf"), Path(r"C:\Windows\Fonts\tahomabd.ttf")),
        (Path(r"C:\Windows\Fonts\segoeui.ttf"), Path(r"C:\Windows\Fonts\segoeuib.ttf")),
        (Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")),
    ]

    for regular_path, bold_path in candidates:
        if regular_path.exists() and bold_path.exists():
            regular_name = f"AID_{regular_path.stem}"
            bold_name = f"AID_{bold_path.stem}"
            if regular_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(regular_name, str(regular_path)))
            if bold_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(bold_name, str(bold_path)))
            FONT_CACHE["regular"] = regular_name
            FONT_CACHE["bold"] = bold_name
            return regular_name, bold_name

    FONT_CACHE["regular"] = "Helvetica"
    FONT_CACHE["bold"] = "Helvetica-Bold"
    return FONT_CACHE["regular"], FONT_CACHE["bold"]


def reshape_rtl_text(text: str) -> str:
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except Exception:
        return text

    return "\n".join(
        get_display(arabic_reshaper.reshape(line)) for line in str(text).splitlines()
    )


def format_paragraph_text(text: str, language: str) -> str:
    rendered = reshape_rtl_text(text) if language == "ur" else str(text)
    return html.escape(rendered).replace("\n", "<br/>")


def generate_pdf_report(
    inference_result: Dict[str, Any],
    report_text: str,
    filename_prefix: str = "autism_prescreen_report",
    language: str = "en",
) -> Path:
    """Generates a comprehensive, visually appealing PDF report and returns the saved file path."""

    language = normalize_language(language, report_text)
    labels = URDU_LABELS if language == "ur" else EN_LABELS
    regular_font, bold_font = register_unicode_fonts()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = REPORTS_DIR / f"{filename_prefix}_{timestamp}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    base_styles = getSampleStyleSheet()

    # Define comprehensive styles for a modern, appealing layout
    title_style = ParagraphStyle(
        "AidTitle",
        parent=base_styles["Heading1"],
        fontName=bold_font,
        fontSize=24,
        textColor=colors.HexColor("#1A5490"),  # Professional blue
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        "AidSubtitle",
        parent=base_styles["Heading2"],
        fontName=bold_font,
        fontSize=14,
        textColor=colors.HexColor("#2E5C8A"),
        spaceAfter=10,
        spaceBefore=12,
        borderPadding=8,
    )

    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=base_styles["Heading3"],
        fontName=bold_font,
        fontSize=12,
        textColor=colors.HexColor("#FFFFFF"),
        spaceAfter=8,
        spaceBefore=8,
    )

    body_style = ParagraphStyle(
        "AidBody",
        parent=base_styles["BodyText"],
        fontName=regular_font,
        fontSize=11,
        leading=18 if language == "ur" else 16,
        alignment=TA_RIGHT if language == "ur" else TA_LEFT,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "AidNormal",
        parent=base_styles["Normal"],
        fontName=regular_font,
        fontSize=10,
        leading=14,
        alignment=TA_RIGHT if language == "ur" else TA_LEFT,
        spaceAfter=6,
    )

    footer_style = ParagraphStyle(
        "AidFooter",
        parent=base_styles["Italic"],
        fontName=regular_font,
        fontSize=9,
        textColor=colors.HexColor("#E74C3C"),
        leading=12,
        alignment=TA_CENTER,
        spaceBefore=12,
    )

    story = []

    # 1. Title Section with Date
    story.append(Paragraph(format_paragraph_text(labels["title"], language), title_style))
    story.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>", normal_style))
    story.append(Spacer(1, 0.2 * inch))

    # Extract data
    score = inference_result.get("screening_score", "N/A")
    score_max = inference_result.get("screening_score_max", 24)
    score_risk = inference_result.get("score_risk_level", "N/A")
    referral = inference_result.get("referral_interpretation", "N/A")
    class_probs = inference_result.get("class_probabilities", {})

    # 2. Quick Summary Box with Color-Coded Risk Level
    risk_color = RISK_COLORS.get(score_risk, colors.grey)
    
    summary_data = [
        [
            Paragraph(f"<b>{labels['quick_summary']}</b>", section_header_style),
        ],
        [
            Paragraph(f"{labels['screening_score']}:", normal_style),
            Paragraph(f"<b>{score}/{score_max}</b>", normal_style),
        ],
        [
            Paragraph(f"{labels['risk_level']}:", normal_style),
            Paragraph(f"<b>{score_risk}</b>", normal_style),
        ],
        [
            Paragraph(f"{labels['referral']}:", normal_style),
            Paragraph(f"{referral}", normal_style),
        ],
    ]

    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2.5 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), risk_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 1), (-1, -1), regular_font),
                ("FONTSIZE", (0, 1), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F5F5F5"), colors.white]),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.15 * inch))

    # 3. Confidence Levels Visualization
    if class_probs:
        story.append(
            Paragraph(f"<b>{labels['class_probabilities']}</b>", subtitle_style)
        )
        probs_data = [[k, f"{v}"] for k, v in class_probs.items()]
        probs_table = Table(probs_data, colWidths=[3 * inch, 1.5 * inch])
        probs_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), regular_font),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#F9F9F9"), colors.white]),
                ]
            )
        )
        story.append(probs_table)
        story.append(Spacer(1, 0.2 * inch))

    # 4. Main Guidance Report - the LLM-generated content
    story.append(
        Paragraph(f"<b>{labels['parent_guide']}</b>", subtitle_style)
    )
    story.append(Paragraph(format_paragraph_text(report_text, language), body_style))
    story.append(Spacer(1, 0.15 * inch))

    # 5. Footer Disclaimer - clearly visible but not scary
    story.append(
        Paragraph(format_paragraph_text(labels["disclaimer"], language), footer_style)
    )

    # 6. Additional Information Section
    additional_info = (
        "<br/><br/><b>About This Screening:</b><br/>"
        "• Early screening helps identify when professional guidance might be helpful<br/>"
        "• Development varies naturally among children<br/>"
        "• This assessment is one tool among many in understanding child development<br/>"
        "• Professional consultation always provides the most comprehensive perspective<br/>"
        "<br/><i>For more information, please consult with your pediatrician or developmental specialist.</i>"
    ) if language == "en" else (
        "<br/><br/><b>اس اسکریننگ کے بارے میں:</b><br/>"
        "• ابتدائی اسکریننگ سے معلوم ہوتا ہے کہ پیشہ ورانہ رہنمائی کب مفید ہو سکتی ہے<br/>"
        "• بچوں میں ترقی قدرتی طور پر مختلف ہوتی ہے<br/>"
        "• یہ تقویم بچے کی ترقی کو سمجھنے کا ایک طریقہ ہے<br/>"
        "• پیشہ ور from سے رابطہ ہمیشہ بہترین ہے<br/>"
        "<br/><i>مزید معلومات کے لیے اپنے ڈاکٹر سے رابطہ کریں۔</i>"
    )
    story.append(Paragraph(additional_info, normal_style))

    doc.build(story)
    return pdf_path
