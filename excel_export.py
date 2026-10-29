"""
excel_export.py - Modul pentru generarea și formatarea rapoartelor Excel (.xlsx)
cuprinzând rezultatele finale/parțiale ale repartizării stagiilor de practică.
"""

import io
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from monitor_utils import normalize_spec


# Paletă de culori profesionale pentru Excel (Coduri hex fără '#')
COLOR_NAVY_HEADER = "1E3A8A"      # Albastru marin profund pentru antet
COLOR_WHITE = "FFFFFF"
COLOR_BORDER = "CBD5E1"           # Gri deschis pentru margini celule

# Culori pastelate de distincție pentru Specializări
SPEC_COLORS = {
    "Aparare Cibernetica": {
        "fill": "E0F2FE",   # Cyan/Sky pastel
        "text": "0369A1",   # Dark cyan
        "label": "Apărare Cibernetică"
    },
    "Comunicatii": {
        "fill": "DCFCE7",   # Mint/Emerald pastel
        "text": "15803D",   # Dark green
        "label": "Comunicații"
    },
    "Tehnologia Informatiei": {
        "fill": "F3E8FF",   # Lavender/Purple pastel
        "text": "7E22CE",   # Dark purple
        "label": "Tehnologia Informației"
    },
    "Securitate Militara": {
        "fill": "FEF3C7",   # Amber/Sand pastel
        "text": "B45309",   # Dark amber
        "label": "Securitate Militară"
    },
}

# Culori de distincție pentru Gen
GENDER_COLORS = {
    "F": {
        "fill": "FCE7F3",   # Rose pastel
        "text": "9D174D",   # Deep magenta
        "label": "Feminin (F)"
    },
    "B": {
        "fill": "DBEAFE",   # Blue pastel
        "text": "1E40AF",   # Deep blue
        "label": "Masculin (B)"
    },
    "M": {
        "fill": "DBEAFE",
        "text": "1E40AF",
        "label": "Masculin (B)"
    }
}

# Stiluri pentru borduri
thin_border = Border(
    left=Side(style='thin', color=COLOR_BORDER),
    right=Side(style='thin', color=COLOR_BORDER),
    top=Side(style='thin', color=COLOR_BORDER),
    bottom=Side(style='thin', color=COLOR_BORDER)
)

thick_bottom_border = Border(
    left=Side(style='thin', color=COLOR_BORDER),
    right=Side(style='thin', color=COLOR_BORDER),
    top=Side(style='thin', color=COLOR_BORDER),
    bottom=Side(style='medium', color="1E3A8A")
)


def _apply_sheet_styling(ws, title_text: str, session_title: str, records: list[dict], subtitle_spec: str = None):
    """Formatează complet o foaie de calcul cu antet, sumar și tabelul elevilor."""
    
    # 1. Rând Titlu Principal
    ws.merge_cells("A1:G1")
    cell_t1 = ws["A1"]
    cell_t1.value = "MINISTERUL APĂRĂRII NAȚIONALE — SISTEM DE REPARTIZARE PRACTICĂ"
    cell_t1.font = Font(name="Calibri", size=13, bold=True, color="1E3A8A")
    cell_t1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 24

    # 2. Rând Titlu Raport / Sesiune
    ws.merge_cells("A2:G2")
    cell_t2 = ws["A2"]
    sub_title = f"{title_text} — {session_title}"
    if subtitle_spec:
        sub_title += f" [Specializarea: {subtitle_spec}]"
    cell_t2.value = sub_title
    cell_t2.font = Font(name="Calibri", size=11, bold=True, color="334155")
    cell_t2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    # 3. Rând Sumar & Data Export
    now_str = datetime.now().strftime("%d.%m.%Y, ora %H:%M")
    total = len(records)
    enrolled = len([r for r in records if r.get("has_option")])
    unenrolled = total - enrolled
    pct = (enrolled / total * 100) if total > 0 else 0

    ws.merge_cells("A3:G3")
    cell_t3 = ws["A3"]
    cell_t3.value = f"Data export: {now_str}  |  Total elevi: {total}  |  Repartizați: {enrolled} ({pct:.1f}%)  |  În așteptare: {unenrolled}"
    cell_t3.font = Font(name="Calibri", size=10, italic=True, color="64748B")
    cell_t3.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 18

    # Rând 4: Gol separator
    ws.row_dimensions[4].height = 8

    # 4. Cap de Tabel (Rândul 5)
    headers = [
        "Nr. Crt.",
        "Specializare",
        "Nume și Prenume Elev",
        "Gen",
        "Medie",
        "Unitate Militară Repartizată",
        "Status Repartiție"
    ]
    ws.row_dimensions[5].height = 28

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=5, column=col_idx, value=header)
        cell.font = Font(name="Calibri", size=11, bold=True, color=COLOR_WHITE)
        cell.fill = PatternFill(start_color=COLOR_NAVY_HEADER, end_color=COLOR_NAVY_HEADER, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thick_bottom_border

    # 5. Populare rânduri date (de la Rândul 6)
    start_row = 6
    for idx, r in enumerate(records, start=1):
        row_idx = start_row + idx - 1
        ws.row_dimensions[row_idx].height = 22

        spec_norm = r.get("norm_spec") or normalize_spec(r.get("specialization", ""))
        spec_cfg = SPEC_COLORS.get(spec_norm, {"fill": "F1F5F9", "text": "0F172A", "label": spec_norm})

        gender_code = str(r.get("gender", "B")).upper()
        if gender_code not in ("F", "B", "M"):
            gender_code = "B"
        gen_cfg = GENDER_COLORS.get(gender_code, GENDER_COLORS["B"])

        has_option = bool(r.get("has_option"))
        unit_text = r.get("option1") or "— Fără opțiune aleasă —"

        # Celula 1: Nr. Crt.
        c1 = ws.cell(row=row_idx, column=1, value=idx)
        c1.alignment = Alignment(horizontal="center", vertical="center")
        c1.font = Font(name="Calibri", size=10)
        c1.border = thin_border

        # Celula 2: Specializare (colorată specific pe profil)
        c2 = ws.cell(row=row_idx, column=2, value=spec_cfg["label"])
        c2.alignment = Alignment(horizontal="left", vertical="center")
        c2.font = Font(name="Calibri", size=10, bold=True, color=spec_cfg["text"])
        c2.fill = PatternFill(start_color=spec_cfg["fill"], end_color=spec_cfg["fill"], fill_type="solid")
        c2.border = thin_border

        # Celula 3: Nume și Prenume (Nume cu majuscule)
        last_name = r.get("last_name", "").upper()
        first_name = r.get("first_name", "").title()
        nume_formatat = f"{last_name} {first_name}".strip()
        c3 = ws.cell(row=row_idx, column=3, value=nume_formatat)
        c3.alignment = Alignment(horizontal="left", vertical="center")
        c3.font = Font(name="Calibri", size=10, bold=True, color="0F172A")
        c3.border = thin_border

        # Celula 4: Gen (colorat distinctiv: roz pentru fete, albastru pentru băieți)
        c4 = ws.cell(row=row_idx, column=4, value=gen_cfg["label"])
        c4.alignment = Alignment(horizontal="center", vertical="center")
        c4.font = Font(name="Calibri", size=9, bold=True, color=gen_cfg["text"])
        c4.fill = PatternFill(start_color=gen_cfg["fill"], end_color=gen_cfg["fill"], fill_type="solid")
        c4.border = thin_border

        # Celula 5: Medie
        avg_val = float(r.get("average", 0.0))
        c5 = ws.cell(row=row_idx, column=5, value=avg_val)
        c5.alignment = Alignment(horizontal="center", vertical="center")
        c5.font = Font(name="Calibri", size=10, bold=True, color="0F172A")
        c5.number_format = "0.00"
        c5.border = thin_border

        # Celula 6: Unitate Repartizată
        c6 = ws.cell(row=row_idx, column=6, value=unit_text)
        c6.alignment = Alignment(horizontal="left", vertical="center")
        if has_option:
            c6.font = Font(name="Calibri", size=10, bold=True, color="0F172A")
            c6.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        else:
            c6.font = Font(name="Calibri", size=9, italic=True, color="DC2626")
            c6.fill = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
        c6.border = thin_border

        # Celula 7: Status Repartiție
        if has_option:
            c7 = ws.cell(row=row_idx, column=7, value="Confirmat")
            c7.font = Font(name="Calibri", size=9, bold=True, color="065F46")
            c7.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        else:
            c7 = ws.cell(row=row_idx, column=7, value="În așteptare")
            c7.font = Font(name="Calibri", size=9, bold=True, color="92400E")
            c7.fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        c7.alignment = Alignment(horizontal="center", vertical="center")
        c7.border = thin_border

    # Fixare panou de sus (Freeze Panes sub capul de tabel)
    ws.freeze_panes = "A6"

    # Lățimi automate adaptate per coloană
    col_widths = {
        1: 9,    # Nr. Crt.
        2: 24,   # Specializare
        3: 32,   # Nume și Prenume
        4: 15,   # Gen
        5: 12,   # Medie
        6: 38,   # Unitate Militară
        7: 18,   # Status
    }
    for col_idx, width in col_widths.items():
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width


def generate_repartition_excel(session_title: str, records: list[dict], units_dict: dict = None) -> bytes:
    """
    Generează fișierul Excel binar (.xlsx) complet formatat, cu foi separate
    pentru sinteza generală și fiecare specializare în parte.
    """
    wb = Workbook()

    # Sortare primară pe specializare, descrescător pe medie, apoi alfabetic
    sorted_records = sorted(
        records,
        key=lambda x: (
            x.get("norm_spec") or normalize_spec(x.get("specialization", "")),
            -float(x.get("average", 0.0)),
            x.get("last_name", ""),
            x.get("first_name", "")
        )
    )

    # 1. FOAIA PRINCIPALĂ: Toate Specializările
    ws_all = wb.active
    ws_all.title = "Toate Specializările"
    _apply_sheet_styling(ws_all, "TABEL NOMINAL REPARTIZARE PRACTICĂ", session_title, sorted_records)

    # Grupăm elevii pe specializări
    spec_groups = {}
    for r in sorted_records:
        norm = r.get("norm_spec") or normalize_spec(r.get("specialization", ""))
        if norm not in spec_groups:
            spec_groups[norm] = []
        spec_groups[norm].append(r)

    # 2. FOI SEPARATE PENTRU FIECARE SPECIALIZARE
    spec_sheet_names = {
        "Aparare Cibernetica": "Apărare Cibernetică",
        "Comunicatii": "Comunicații",
        "Tehnologia Informatiei": "Tehnologia Informației",
        "Securitate Militara": "Securitate Militară"
    }

    for norm_spec, sheet_name in spec_sheet_names.items():
        sub_records = spec_groups.get(norm_spec, [])
        if sub_records:
            ws_spec = wb.create_sheet(title=sheet_name[:31])  # Excel max 31 chars per title
            _apply_sheet_styling(
                ws_spec,
                f"REPARTIZARE {sheet_name.upper()}",
                session_title,
                sub_records,
                subtitle_spec=sheet_name
            )

    # Salvare în flux binar de memorie
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()
