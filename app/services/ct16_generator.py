import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _extract_val(obj: Any, attr: str, default: Any = "N/A") -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        val = obj.get(attr)
    else:
        val = getattr(obj, attr, None)
    return default if val is None else val


def _format_dt(dt: Any) -> str:
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    if isinstance(dt, str):
        return dt
    return "N/A"


def generate_form_ct16_pdf(
    ae_record: Any,
    patient_record: Any,
    trial_record: Any,
    interactions: Optional[List[Dict[str, Any]]] = None,
    meddra_terms: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
    )
    section_heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=6,
        spaceAfter=3,
    )
    cell_bold_style = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2D3748"),
    )
    cell_style = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1A202C"),
    )
    cell_warning_style = ParagraphStyle(
        "CellWarning",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#C53030"),
    )

    story = []

    story.append(Paragraph("CDSCO Form CT-16 — Serious Adverse Event Preliminary Report (NDCT Rules 2019)", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Central Drugs Standard Control Organization | National Pharmacovigilance Coordination Centre (NPvCC) — AIIA", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("1. Clinical Trial Identification", section_heading_style))
    trial_data = [
        [
            Paragraph("Protocol ID:", cell_bold_style),
            Paragraph(str(_extract_val(trial_record, "protocol_id")), cell_style),
            Paragraph("CTRI Registration ID:", cell_bold_style),
            Paragraph(str(_extract_val(trial_record, "ctri_registration_id", "Pending/Not Linked")), cell_style),
        ],
        [
            Paragraph("Study Title:", cell_bold_style),
            Paragraph(str(_extract_val(trial_record, "study_title")), cell_style),
            Paragraph("Trial Status:", cell_bold_style),
            Paragraph(str(_extract_val(trial_record, "status")), cell_style),
        ],
    ]
    trial_table = Table(trial_data, colWidths=[95, 175, 110, 160])
    trial_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(trial_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Subject Demographics & Phenotypic Markers", section_heading_style))
    patient_data = [
        [
            Paragraph("USUBJID:", cell_bold_style),
            Paragraph(str(_extract_val(patient_record, "usubjid")), cell_style),
            Paragraph("Age / Sex:", cell_bold_style),
            Paragraph(f"{_extract_val(patient_record, 'age', 'N/A')} / {_extract_val(patient_record, 'sex', 'N/A')}", cell_style),
        ],
        [
            Paragraph("Baseline Prakriti:", cell_bold_style),
            Paragraph(str(_extract_val(patient_record, "prakriti_type")), cell_style),
            Paragraph("Baseline Agni:", cell_bold_style),
            Paragraph(str(_extract_val(patient_record, "baseline_agni")), cell_style),
        ],
    ]
    patient_table = Table(patient_data, colWidths=[95, 175, 110, 160])
    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Incident Manifestation & Statutory 24-Hour SLA Clock", section_heading_style))
    severity_val = _extract_val(ae_record, "severity")
    if hasattr(severity_val, "value"):
        severity_val = severity_val.value
    sla_start = _format_dt(_extract_val(ae_record, "sae_clock_start", None))
    sla_end = _format_dt(_extract_val(ae_record, "sla_deadline", None))
    rec_date = _format_dt(_extract_val(ae_record, "recorded_at", None))

    incident_data = [
        [
            Paragraph("Event Severity:", cell_bold_style),
            Paragraph(f"<font color='#C53030'><b>{severity_val}</b></font>", cell_style),
            Paragraph("Event Date / Time:", cell_bold_style),
            Paragraph(rec_date, cell_style),
        ],
        [
            Paragraph("24-hr SLA Clock Start:", cell_bold_style),
            Paragraph(sla_start, cell_style),
            Paragraph("CDSCO Statutory Deadline:", cell_bold_style),
            Paragraph(f"<font color='#C53030'><b>{sla_end}</b></font>", cell_style),
        ],
        [
            Paragraph("Clinical Presentation:", cell_bold_style),
            Paragraph(str(_extract_val(ae_record, "clinical_notes", "None recorded")), cell_style),
            Paragraph("Reported By:", cell_bold_style),
            Paragraph(str(_extract_val(ae_record, "reported_by")), cell_style),
        ],
    ]
    incident_table = Table(incident_data, colWidths=[95, 175, 110, 160])
    incident_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF5F5")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FEB2B2")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FED7D7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(incident_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. NPvCC Pharmacovigilance & Causality Assessment", section_heading_style))
    ayur_intervention = str(_extract_val(ae_record, "ayurvedic_intervention", "None"))
    raw_concomitant = _extract_val(ae_record, "concomitant_drugs", [])
    concomitant_str = ", ".join(raw_concomitant) if isinstance(raw_concomitant, list) and raw_concomitant else "None"

    pharma_data = [
        [
            Paragraph("Ayurvedic Intervention:", cell_bold_style),
            Paragraph(ayur_intervention, cell_style),
            Paragraph("Concomitant Medications:", cell_bold_style),
            Paragraph(concomitant_str, cell_style),
        ],
    ]
    pharma_table = Table(pharma_data, colWidths=[95, 175, 110, 160])
    pharma_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(pharma_table)
    story.append(Spacer(1, 4))

    conflict_list = interactions if interactions is not None else _extract_val(ae_record, "herb_drug_conflicts", [])
    if conflict_list:
        story.append(Paragraph("Flagged Herb-Drug Interactions:", cell_warning_style))
        conflict_rows = [
            [
                Paragraph("Herb", cell_bold_style),
                Paragraph("Concomitant Drug", cell_bold_style),
                Paragraph("Severity", cell_bold_style),
                Paragraph("Clinical Mechanism / Description", cell_bold_style),
            ]
        ]
        for conf in conflict_list:
            conflict_rows.append([
                Paragraph(str(conf.get("herb", "")), cell_style),
                Paragraph(str(conf.get("drug", "")), cell_style),
                Paragraph(f"<font color='#C53030'><b>{conf.get('severity', '')}</b></font>", cell_style),
                Paragraph(str(conf.get("description", "")), cell_style),
            ])
        conflict_table = Table(conflict_rows, colWidths=[100, 110, 80, 250])
        conflict_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FED7D7")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFF5F5")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FEB2B2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FED7D7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(conflict_table)
        story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("Herb-Drug Interactions: <font color='#276749'><b>No contraindications flagged.</b></font>", cell_style))
        story.append(Spacer(1, 4))

    meddra_list = meddra_terms if meddra_terms is not None else _extract_val(ae_record, "coded_meddra_terms", [])
    if meddra_list:
        story.append(Paragraph("Standardized MedDRA Coding:", cell_bold_style))
        meddra_rows = [
            [
                Paragraph("Clinical Phrase", cell_bold_style),
                Paragraph("PT Code", cell_bold_style),
                Paragraph("Preferred Term (PT)", cell_bold_style),
                Paragraph("System Organ Class (SOC)", cell_bold_style),
            ]
        ]
        for term in meddra_list:
            meddra_rows.append([
                Paragraph(str(term.get("phrase", "")), cell_style),
                Paragraph(str(term.get("pt_code", "")), cell_style),
                Paragraph(str(term.get("preferred_term", "")), cell_style),
                Paragraph(str(term.get("soc", "")), cell_style),
            ])
        meddra_table = Table(meddra_rows, colWidths=[130, 80, 150, 180])
        meddra_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EBF8FF")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BEE3F8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(meddra_table)
        story.append(Spacer(1, 6))

    story.append(Paragraph("5. Regulatory Causality & Principal Investigator Sign-Off", section_heading_style))
    signoff_data = [
        [
            Paragraph("WHO-UMC Causality Assessment:", cell_bold_style),
            Paragraph("[  ] Certain    [  ] Probable    [  ] Possible    [  ] Unlikely    [  ] Unclassified", cell_style),
        ],
        [
            Paragraph("Ayush Doshic Correlation:", cell_bold_style),
            Paragraph("Vata [  ]    Pitta [  ]    Kapha [  ]    Sannipatika [  ]    Ama Involvement [  ]", cell_style),
        ],
        [
            Paragraph("Principal Investigator Signature:", cell_bold_style),
            Paragraph("_______________________________    Date: _______________", cell_style),
        ],
        [
            Paragraph("Clinical Trial Center & License:", cell_bold_style),
            Paragraph("All India Institute of Ayurveda (AIIA) | NPvCC Regulatory Portal", cell_style),
        ],
    ]
    signoff_table = Table(signoff_data, colWidths=[180, 360])
    signoff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(signoff_table)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
