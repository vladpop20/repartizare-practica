import streamlit as st
import pandas as pd

from supabase_db import (
    get_all_choices,
    get_all_students,
)
from monitor_utils import normalize_spec
from ui_utils import render_html

ADMIN_PASSWORD = "Practica2026"

st.set_page_config(
    page_title="Administrare - Repartizare",
    page_icon="🛡️",
    layout="wide",
)


def load_admin_css() -> None:
    render_html("""
<style>
/* Container principal */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}

/* Card autentificare */
.admin-login-box {
    background: #141824;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 32px 28px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    margin-top: 30px;
    text-align: center;
}

.admin-login-icon {
    font-size: 42px;
    margin-bottom: 12px;
}

.admin-login-title {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}

.admin-login-desc {
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 20px;
}

/* Header administrator conectat */
.admin-header {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 14px;
    margin-bottom: 20px;
}

.admin-header-title {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
}

.admin-header-sub {
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
}

/* Carduri KPI */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 22px;
}

.kpi-card {
    background: #141824;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 14px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
}

.kpi-blue { border-color: rgba(59, 130, 246, 0.35); }
.kpi-green { border-color: rgba(16, 185, 129, 0.35); }
.kpi-amber { border-color: rgba(245, 158, 11, 0.35); }
.kpi-purple { border-color: rgba(168, 85, 247, 0.35); }

.kpi-num {
    font-size: 26px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;
}

.kpi-blue .kpi-num { color: #60a5fa; }
.kpi-green .kpi-num { color: #34d399; }
.kpi-amber .kpi-num { color: #fbbf24; }
.kpi-purple .kpi-num { color: #c084fc; }

.kpi-lbl {
    font-size: 11px;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Container Tabel Alegeri */
.admin-table-container {
    background: #141824;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 20px;
    margin-top: 15px;
    margin-bottom: 25px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
    overflow-x: auto;
}

.admin-table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}

.admin-table-title {
    font-size: 17px;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
}

.admin-table-count {
    font-size: 13px;
    color: #94a3b8;
}

.admin-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13.5px;
    color: #e2e8f0;
}

.admin-table th {
    background: #1a2234;
    color: #94a3b8;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 11.5px;
    letter-spacing: 0.5px;
    padding: 12px 14px;
    text-align: left;
    border-bottom: 2px solid rgba(59, 130, 246, 0.35);
}

.admin-table th:first-child { border-top-left-radius: 8px; }
.admin-table th:last-child { border-top-right-radius: 8px; }

.admin-table td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: middle;
}

.admin-table tr:hover td {
    background: rgba(59, 130, 246, 0.06);
}

.admin-table tr:last-child td {
    border-bottom: none;
}

/* Badges */
.badge-grade {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-spec {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 11.5px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.spec-ac { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border-color: rgba(59, 130, 246, 0.35); }
.spec-sm { background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.35); }
.spec-com { background: rgba(168, 85, 247, 0.15); color: #c084fc; border-color: rgba(168, 85, 247, 0.35); }
.spec-ti { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border-color: rgba(245, 158, 11, 0.35); }

.badge-unit {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    color: #ffffff;
    background: rgba(30, 41, 59, 0.65);
    padding: 4px 10px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.badge-unit-none {
    color: #64748b;
    font-style: italic;
    font-size: 13px;
}

.badge-boy {
    color: #60a5fa;
    font-weight: 600;
}

.badge-girl {
    color: #f87171;
    font-weight: 600;
}

@media (max-width: 768px) {
    .kpi-row {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
""")


def get_spec_badge_html(spec: str) -> str:
    norm = normalize_spec(spec)
    if norm == "Aparare Cibernetica":
        return f'<span class="badge-spec spec-ac">{norm}</span>'
    elif norm == "Securitate Militara":
        return f'<span class="badge-spec spec-sm">{norm}</span>'
    elif norm == "Comunicatii":
        return f'<span class="badge-spec spec-com">{norm}</span>'
    elif norm == "Tehnologia Informatiei":
        return f'<span class="badge-spec spec-ti">{norm}</span>'
    return f'<span class="badge-spec">{norm}</span>'


def get_gender_html(gender: str) -> str:
    if gender == "B":
        return '<span class="badge-boy">👦 Băiat</span>'
    elif gender == "F":
        return '<span class="badge-girl">👧 Fată</span>'
    return '<span style="color: #94a3b8;">-</span>'


def get_unit_html(unit_name: str) -> str:
    if not unit_name:
        return '<span class="badge-unit-none">⏳ Nicio opțiune</span>'
    clean = unit_name.replace("UM_", "UM ").replace("_", " ")
    return f'<span class="badge-unit">🏢 {clean}</span>'


# ============================================================
# Autentificare
# ============================================================
load_admin_css()

if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
    col_l, col_center, col_r = st.columns([1, 1.8, 1])
    with col_center:
        render_html("""
        <div class="admin-login-box">
            <div class="admin-login-icon">🔒</div>
            <div class="admin-login-title">Panou Administrator</div>
            <div class="admin-login-desc">Introduceți parola de administrator pentru a accesa datele de repartizare.</div>
        </div>
        """)
        with st.form("admin_login_form"):
            password_input = st.text_input(
                "Parolă administrator",
                type="password",
                placeholder="Introduceți parola..."
            )
            submit = st.form_submit_button("Autentificare", use_container_width=True)
            if submit:
                if password_input == ADMIN_PASSWORD:
                    st.session_state["admin_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă!")
    st.stop()

# ============================================================
# Panou Admin Conectat
# ============================================================
header_left, header_right = st.columns([5, 1])
with header_left:
    st.title("🛡️ Panou Administrare")
    st.caption("Evidența opțiunilor exprimate și distribuția elevilor pe unități")
with header_right:
    st.write("")
    if st.button("Deconectare 🚪", use_container_width=True):
        st.session_state["admin_authenticated"] = False
        st.rerun()

#
# Încărcare date
#
choices = get_all_choices()
students = get_all_students()

choices_map = {c["student_id"]: c for c in choices}

all_records = []
for s in students:
    s_id = s["id"]
    choice = choices_map.get(s_id)
    opt1 = choice.get("option1") if choice else None

    all_records.append({
        "id": s_id,
        "first_name": s.get("first_name", ""),
        "last_name": s.get("last_name", ""),
        "nume_complet": f"{s.get('last_name', '')} {s.get('first_name', '')}",
        "average": float(s.get("average", 0.0)),
        "specialization": s.get("specialization", ""),
        "norm_spec": normalize_spec(s.get("specialization", "")),
        "gender": s.get("gender", ""),
        "option1": opt1,
        "has_option": bool(opt1),
    })

# Sortare implicită descrescătoare după medie
all_records.sort(key=lambda x: (x["average"], x["nume_complet"]), reverse=True)

#
# Statistici generale KPI
#
total_students = len(students)
enrolled_count = len([r for r in all_records if r["has_option"]])
unenrolled_count = max(total_students - enrolled_count, 0)
enrolled_pct = (enrolled_count / total_students * 100) if total_students > 0 else 0

render_html(f"""
<div class="kpi-row">
    <div class="kpi-card kpi-blue">
        <div class="kpi-num">{total_students}</div>
        <div class="kpi-lbl">Total elevi</div>
    </div>
    <div class="kpi-card kpi-green">
        <div class="kpi-num">{enrolled_count}</div>
        <div class="kpi-lbl">Opțiuni salvate</div>
    </div>
    <div class="kpi-card kpi-amber">
        <div class="kpi-num">{unenrolled_count}</div>
        <div class="kpi-lbl">Fără opțiune</div>
    </div>
    <div class="kpi-card kpi-purple">
        <div class="kpi-num">{enrolled_pct:.1f}%</div>
        <div class="kpi-lbl">Rată exprimare</div>
    </div>
</div>
""")

#
# Filtre superioare
#
col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 2])

with col_f1:
    specializari_options = ["Toate specializările"] + sorted(list({r["norm_spec"] for r in all_records if r["norm_spec"]}))
    sel_spec = st.selectbox("Specializare", specializari_options)

with col_f2:
    sel_status = st.selectbox(
        "Filtru opțiuni",
        ["Doar elevii cu opțiune salvată", "Toți elevii", "Doar fără opțiune"]
    )

with col_f3:
    cautare = st.text_input("🔍 Căutare", placeholder="Nume, prenume sau unitate...").strip().lower()

#
# Aplicare filtre
#
filtered_records = []
for r in all_records:
    # Filtru status
    if sel_status == "Doar elevii cu opțiune salvată" and not r["has_option"]:
        continue
    elif sel_status == "Doar fără opțiune" and r["has_option"]:
        continue

    # Filtru specializare
    if sel_spec != "Toate specializările" and r["norm_spec"] != sel_spec:
        continue

    # Filtru căutare
    if cautare:
        text_target = f"{r['nume_complet']} {r['option1'] or ''}".lower()
        if cautare not in text_target:
            continue

    filtered_records.append(r)

#
# Export CSV
#
export_data = []
for idx, r in enumerate(filtered_records, start=1):
    export_data.append({
        "Nr": idx,
        "Nume": r["last_name"],
        "Prenume": r["first_name"],
        "Gen": r["gender"],
        "Medie": r["average"],
        "Specializare": r["norm_spec"],
        "Unitate_Aleasa": (r["option1"] or "").replace("UM_", "UM "),
    })
df_export = pd.DataFrame(export_data)
csv_bytes = df_export.to_csv(index=False).encode("utf-8")

col_info, col_export = st.columns([4, 1.2])
with col_info:
    st.caption(f"Afișați **{len(filtered_records)}** din **{total_students}** elevi (sortați descrescător după medie).")
with col_export:
    st.download_button(
        label="📥 Descarcă CSV",
        data=csv_bytes,
        file_name=f"alegeri_practica_{sel_spec.replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

#
# Randare Tabel Contrastat (fără Optiunea 2 și 3)
#
if len(filtered_records) == 0:
    st.info("Niciun elev găsit conform filtrelor selectate.")
else:
    table_rows = []
    for idx, r in enumerate(filtered_records, start=1):
        spec_badge = get_spec_badge_html(r["specialization"])
        gender_badge = get_gender_html(r["gender"])
        unit_badge = get_unit_html(r["option1"])
        avg_formatted = f"{r['average']:.2f}"

        table_rows.append(f"""
        <tr>
            <td style="color: #64748b; font-weight: 600;">{idx}</td>
            <td style="font-weight: 700; color: #ffffff;">{r['last_name']} {r['first_name']}</td>
            <td>{gender_badge}</td>
            <td><span class="badge-grade">{avg_formatted}</span></td>
            <td>{spec_badge}</td>
            <td>{unit_badge}</td>
        </tr>
        """)

    table_html = f"""
    <div class="admin-table-container">
        <div class="admin-table-header">
            <div class="admin-table-title">📋 Alegeri detaliate</div>
            <div class="admin-table-count">Afișați <b>{len(filtered_records)}</b> elevi</div>
        </div>
        <table class="admin-table">
            <thead>
                <tr>
                    <th style="width: 50px;">#</th>
                    <th>Elev</th>
                    <th>Gen</th>
                    <th>Medie</th>
                    <th>Specializare</th>
                    <th>Unitate aleasă</th>
                </tr>
            </thead>
            <tbody>
                {"".join(table_rows)}
            </tbody>
        </table>
    </div>
    """
    render_html(table_html)