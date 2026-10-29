import streamlit as st
import pandas as pd

import importlib
import sessions_manager as sm
importlib.reload(sm)
from monitor_utils import normalize_spec
from ui_utils import render_html, render_theme_toggle, get_theme_css
from student_utils import get_gender
import excel_export

ADMIN_PASSWORD = "Practica2026"

st.set_page_config(
    page_title="Administrare - Repartizare",
    page_icon="🛡️",
    layout="wide",
)


def load_admin_css() -> None:
    render_html("""
<style>
/* Container principal - spațiu generos pentru a preveni suprapunerea cu bara superioară Streamlit */
.block-container {
    padding-top: 4.25rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1400px !important;
}

/* Buton deconectare admin */
.logout-btn-container button {
    background: rgba(239, 68, 68, 0.12) !important;
    border: 1px solid rgba(239, 68, 68, 0.35) !important;
    color: #fca5a5 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
}

.logout-btn-container button:hover {
    background: rgba(239, 68, 68, 0.25) !important;
    border-color: rgba(239, 68, 68, 0.6) !important;
    color: #ffffff !important;
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

/* Carduri Configurare Tab 2 */
.config-section-card {
    background: #141824;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
}

.config-section-title {
    font-size: 17px;
    font-weight: 700;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 10px;
    margin-bottom: 16px;
}

.guide-box {
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 13px;
    color: #93c5fd;
    line-height: 1.5;
}

.status-active-badge {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34d399;
    font-weight: 700;
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-block;
}

.status-inactive-badge {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #f87171;
    font-weight: 700;
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-block;
}

.badge-gender-m {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.4);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
    display: inline-block;
}

.badge-gender-f {
    background: rgba(236, 72, 153, 0.15);
    color: #f472b6;
    border: 1px solid rgba(236, 72, 153, 0.4);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
    display: inline-block;
}

.badge-confirmed {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
    display: inline-block;
}

.badge-waiting {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.4);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
    display: inline-block;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 4.75rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .kpi-row {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
""")
    theme_css = get_theme_css()
    if theme_css:
        render_html(theme_css)


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
header_left, header_mid, header_right = st.columns([3.6, 1.4, 1.2], vertical_alignment="center")
with header_left:
    render_html("""
    <div style="margin-bottom: 8px;">
        <h1 style="margin: 0; padding: 0; font-size: 2.1rem; font-weight: 800; color: #ffffff; line-height: 1.2;">🛡️ Panou Administrare</h1>
        <div style="color: #94a3b8; font-size: 13.5px; margin-top: 4px;">Gestiune sesiuni de practică, import promoții și evidența alegerilor</div>
    </div>
    """)
with header_mid:
    render_theme_toggle("admin")
with header_right:
    render_html('<div class="logout-btn-container">')
    if st.button("🚪 Deconectare", use_container_width=True, key="admin_logout_btn"):
        st.session_state["admin_authenticated"] = False
        st.rerun()
    render_html("</div>")

#
# Sesiuni disponibile
#
all_sessions = sm.get_all_sessions()
active_session = sm.get_active_session()

#
# TABURI PRINCIPALE ADMIN
#
tab_evidence, tab_results, tab_edit, tab_config = st.tabs([
    "📋 Evidență & Alegeri în timp real",
    "📑 Rezultate Finale & Export Excel",
    "✏️ Editare Date (Elevi & Unități)",
    "⚙️ Configurare Promoții & Sesiuni (Import Excel)"
])

# ============================================================
# TAB 1: EVIDENȚĂ & ALEGERI
# ============================================================
with tab_evidence:
    # Selector sesiune pentru vizualizare
    session_titles = [s["title"] for s in all_sessions]
    default_idx = 0
    if active_session:
        for idx, s in enumerate(all_sessions):
            if s["id"] == active_session["id"]:
                default_idx = idx
                break

    col_s1, col_s2 = st.columns([4, 1.5], vertical_alignment="center")
    with col_s1:
        selected_session_title = st.selectbox(
            "Selectează sesiunea / promoția de analizat",
            session_titles,
            index=default_idx,
            key="evidence_session_select"
        )
    with col_s2:
        selected_session = next((s for s in all_sessions if s["title"] == selected_session_title), all_sessions[0])
        if selected_session.get("is_active"):
            render_html('<div style="margin-top: 25px;"><span class="status-active-badge">🟢 Repartizare Activă în App</span></div>')
        else:
            render_html('<div style="margin-top: 25px;"><span class="status-inactive-badge">📁 Sesiune Închisă / Arhivată</span></div>')

    current_sess_id = selected_session["id"]

    # Date sesiune
    choices = sm.get_choices_for_session(current_sess_id)
    students = sm.get_students_for_session(current_sess_id)

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

    all_records.sort(key=lambda x: (x["average"], x["nume_complet"]), reverse=True)

    # Carduri KPI
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

    # Filtre
    col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 2])
    with col_f1:
        specializari_options = ["Toate specializările"] + sorted(list({r["norm_spec"] for r in all_records if r["norm_spec"]}))
        sel_spec = st.selectbox("Specializare", specializari_options, key="evidence_spec_filter")

    with col_f2:
        sel_status = st.selectbox(
            "Filtru opțiuni",
            ["Doar elevii cu opțiune salvată", "Toți elevii", "Doar fără opțiune"],
            key="evidence_status_filter"
        )

    with col_f3:
        cautare = st.text_input("🔍 Căutare", placeholder="Nume, prenume sau unitate...", key="evidence_search_input").strip().lower()

    # Filtrare
    filtered_records = []
    for r in all_records:
        if sel_status == "Doar elevii cu opțiune salvată" and not r["has_option"]:
            continue
        elif sel_status == "Doar fără opțiune" and r["has_option"]:
            continue

        if sel_spec != "Toate specializările" and r["norm_spec"] != sel_spec:
            continue

        if cautare:
            text_target = f"{r['nume_complet']} {r['option1'] or ''}".lower()
            if cautare not in text_target:
                continue

        filtered_records.append(r)

    # Export CSV
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
            file_name=f"alegeri_{current_sess_id}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv_tab1"
        )

    # Tabel HTML
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
                <div class="admin-table-title">📋 Alegeri detaliate - {selected_session['title']}</div>
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


# ============================================================
# TAB 2: REZULTATE FINALE & EXPORT EXCEL
# ============================================================
with tab_results:
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">📑 Raport Oficial Rezultate & Export Excel</div>
        <div class="guide-box">
            📄 <b>Generare & Export Tabel Nominal:</b> Previzualizează situația centralizată a repartizării elevilor pe unități
            și descarcă raportul oficial formatat în Excel (<code>.xlsx</code>). Documentul generat conține <b>încadrare grafică completă,
            distincție coloristică pe specializări, nume și gen</b>, precum și foi de calcul dedicate pentru fiecare armă militară în parte.
        </div>
    </div>
    """)

    # Selector sesiune
    res_session_titles = [s["title"] for s in all_sessions]
    res_default_idx = 0
    if active_session:
        for idx, s in enumerate(all_sessions):
            if s["id"] == active_session["id"]:
                res_default_idx = idx
                break

    col_res_s1, col_res_s2 = st.columns([4, 1.5], vertical_alignment="center")
    with col_res_s1:
        res_selected_title = st.selectbox(
            "Selectează sesiunea pentru raportul de rezultate:",
            res_session_titles,
            index=res_default_idx,
            key="results_session_select"
        )
    with col_res_s2:
        res_session = next((s for s in all_sessions if s["title"] == res_selected_title), all_sessions[0])
        if res_session.get("is_active"):
            render_html('<div style="margin-top: 25px;"><span class="status-active-badge">🟢 Sesiune Activă</span></div>')
        else:
            render_html('<div style="margin-top: 25px;"><span class="status-inactive-badge">📁 Sesiune Închisă</span></div>')

    res_sess_id = res_session["id"]
    res_students = sm.get_students_for_session(res_sess_id)
    res_choices = sm.get_choices_for_session(res_sess_id)
    res_units = sm.get_session_units_dict(res_sess_id)
    res_choices_map = {c["student_id"]: c for c in res_choices}

    res_records = []
    for s in res_students:
        s_id = s["id"]
        c = res_choices_map.get(s_id)
        opt1 = c.get("option1") if c else None
        spec = s.get("specialization", "")
        norm = normalize_spec(spec)
        first_n = s.get("first_name", "")
        last_n = s.get("last_name", "")
        gen = s.get("gender") or get_gender(spec, first_n, last_n)

        res_records.append({
            "id": s_id,
            "first_name": first_n,
            "last_name": last_n,
            "nume_complet": f"{last_n} {first_n}".strip(),
            "average": float(s.get("average", 0.0)),
            "specialization": spec,
            "norm_spec": norm,
            "gender": gen,
            "option1": opt1,
            "has_option": bool(opt1),
        })

    # Sortare primară pe specializare, descrescător pe medie, apoi alfabetic
    res_records.sort(key=lambda x: (x["norm_spec"], -x["average"], x["last_name"], x["first_name"]))

    # Carduri KPI
    res_total = len(res_students)
    res_enrolled = len([r for r in res_records if r["has_option"]])
    res_unenrolled = max(res_total - res_enrolled, 0)
    res_pct = (res_enrolled / res_total * 100) if res_total > 0 else 0

    render_html(f"""
    <div class="kpi-row">
        <div class="kpi-card kpi-blue">
            <div class="kpi-num">{res_total}</div>
            <div class="kpi-lbl">Total elevi înscriși</div>
        </div>
        <div class="kpi-card kpi-green">
            <div class="kpi-num">{res_enrolled}</div>
            <div class="kpi-lbl">Repartizați ({res_pct:.1f}%)</div>
        </div>
        <div class="kpi-card kpi-amber">
            <div class="kpi-num">{res_unenrolled}</div>
            <div class="kpi-lbl">În așteptare (fără loc)</div>
        </div>
        <div class="kpi-card kpi-purple">
            <div class="kpi-num">{len(res_units)}</div>
            <div class="kpi-lbl">Unități disponibile</div>
        </div>
    </div>
    """)

    # Buton principal mare de descărcare Excel
    excel_bytes = excel_export.generate_repartition_excel(
        session_title=res_session["title"],
        records=res_records,
        units_dict=res_units
    )
    safe_slug = res_session["title"].replace(" ", "_").replace("—", "-").replace("(", "").replace(")", "").replace(".", "")

    col_btn_export, col_info_export = st.columns([2.5, 2], vertical_alignment="center")
    with col_btn_export:
        st.download_button(
            label=f"📥 Descarcă Tabel Excel Formatat (.xlsx) — {res_total} elevi",
            data=excel_bytes,
            file_name=f"Rezultate_Repartizare_{safe_slug}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
            key="btn_download_results_excel"
        )
    with col_info_export:
        st.caption("📊 Fișierul conține 5 foi de calcul Excel (Sinteză + Foi separate pe fiecare armă militară), cu formatare și culori pe profil, nume și gen.")

    st.write("---")
    st.subheader("👁️ Previzualizare tabelară rezultate")

    # Filtre interactive pentru previzualizare
    f_c1, f_c2, f_c3, f_c4 = st.columns([1.5, 1.2, 1, 2])
    with f_c1:
        spec_opts = ["Toate Specializările"] + sorted(list(set(r["norm_spec"] for r in res_records)))
        sel_spec_filter = st.selectbox("Filtrează după armă:", spec_opts, key="res_filter_spec")
    with f_c2:
        status_opts = ["Toți elevii", "Doar cei repartizați", "Doar în așteptare"]
        sel_status_filter = st.selectbox("Filtrează după status:", status_opts, key="res_filter_status")
    with f_c3:
        gender_opts = ["Toate", "Băieți (B)", "Fete (F)"]
        sel_gender_filter = st.selectbox("Gen:", gender_opts, key="res_filter_gender")
    with f_c4:
        search_query = st.text_input("Caută elev după nume:", "", key="res_filter_search", placeholder="Tastați numele sau prenumele...")

    # Aplicare filtre
    filtered_results = res_records
    if sel_spec_filter != "Toate Specializările":
        filtered_results = [r for r in filtered_results if r["norm_spec"] == sel_spec_filter]
    if sel_status_filter == "Doar cei repartizați":
        filtered_results = [r for r in filtered_results if r["has_option"]]
    elif sel_status_filter == "Doar în așteptare":
        filtered_results = [r for r in filtered_results if not r["has_option"]]
    if sel_gender_filter == "Băieți (B)":
        filtered_results = [r for r in filtered_results if r["gender"] in ("B", "M")]
    elif sel_gender_filter == "Fete (F)":
        filtered_results = [r for r in filtered_results if r["gender"] == "F"]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_results = [r for r in filtered_results if q in r["nume_complet"].lower()]

    # Construire rânduri tabel HTML stilat
    res_table_rows = []
    for idx, r in enumerate(filtered_results, start=1):
        spec_badge = get_spec_badge_html(r["specialization"])
        gender_badge = '<span class="badge-gender-f">👩 Fată</span>' if r["gender"] == "F" else '<span class="badge-gender-m">👨 Băiat</span>'

        if r["has_option"]:
            status_badge = '<span class="badge-confirmed">✅ Confirmat</span>'
            unit_disp = f"<b>{r['option1']}</b>"
        else:
            status_badge = '<span class="badge-waiting">⏳ În așteptare</span>'
            unit_disp = '<span style="color: #ef4444; font-style: italic;">— Fără opțiune aleasă —</span>'

        res_table_rows.append(f"""
        <tr>
            <td style="text-align: center; font-weight: 600; color: #94a3b8;">{idx}</td>
            <td><b>{r['last_name'].upper()}</b> {r['first_name']}</td>
            <td style="text-align: center;">{gender_badge}</td>
            <td style="text-align: center; font-weight: 700;">{r['average']:.2f}</td>
            <td>{spec_badge}</td>
            <td>{unit_disp}</td>
            <td style="text-align: center;">{status_badge}</td>
        </tr>
        """)

    res_table_html = f"""
    <div class="admin-table-container">
        <div class="admin-table-header">
            <div class="admin-table-title">📑 Tabel Rezultate — {res_session['title']}</div>
            <div class="admin-table-count">Afișați <b>{len(filtered_results)}</b> din {res_total} elevi</div>
        </div>
        <table class="admin-table">
            <thead>
                <tr>
                    <th style="width: 60px; text-align: center;">Nr.</th>
                    <th>Nume și Prenume Elev</th>
                    <th style="text-align: center;">Gen</th>
                    <th style="text-align: center;">Medie</th>
                    <th>Specializare</th>
                    <th>Unitate Repartizată</th>
                    <th style="text-align: center;">Status</th>
                </tr>
            </thead>
            <tbody>
                {"".join(res_table_rows) if res_table_rows else '<tr><td colspan="7" style="text-align: center; padding: 24px; color: #94a3b8;">Niciun elev nu corespunde criteriilor de filtrare selectate.</td></tr>'}
            </tbody>
        </table>
    </div>
    """
    render_html(res_table_html)


# ============================================================
# TAB 3: EDITARE DATE REALE (ELEVI & UNITĂȚI)
# ============================================================
with tab_edit:
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">✏️ Modificare Date Reale (Baza de Date)</div>
        <div class="guide-box">
            💡 <b>Panou de editare granulară:</b> Modifică direct în baza de date Supabase datele oricărui <b>elev</b> 
            (nume, prenume, medie, armă, unitatea militară aleasă) sau ale <b>unităților militare</b> (denumire, locuri alocate pe fiecare armă).<br>
            Fiecare operațiune de salvare este însoțită de o <b>previzualizare a diferențelor</b> și de un <b>pas de confirmare obligatorie</b> pentru a preveni modificările accidentale.
        </div>
    </div>
    """)

    edit_session_titles = [s["title"] for s in all_sessions]
    edit_default_idx = 0
    if active_session:
        for idx, s in enumerate(all_sessions):
            if s["id"] == active_session["id"]:
                edit_default_idx = idx
                break

    col_es1, col_es2 = st.columns([4, 1.5], vertical_alignment="center")
    with col_es1:
        target_edit_title = st.selectbox(
            "Selectează sesiunea pe care dorești să o editezi:",
            edit_session_titles,
            index=edit_default_idx,
            key="select_session_to_edit"
        )
    target_edit_sess = next((s for s in all_sessions if s["title"] == target_edit_title), all_sessions[0])
    edit_sid = target_edit_sess["id"]

    with col_es2:
        if target_edit_sess.get("is_active"):
            render_html('<div style="margin-top: 25px;"><span class="status-active-badge">🟢 Repartizare Activă</span></div>')
        else:
            render_html('<div style="margin-top: 25px;"><span class="status-inactive-badge">📁 Sesiune Închisă</span></div>')

    subtab_edit_students, subtab_edit_units = st.tabs([
        "👨‍🎓 Editare Elevi & Alegeri",
        "🏢 Editare Unități Militare & Locuri"
    ])

    # ------------------------------------------------------------
    # SUBTAB 1: EDITARE ELEVI & ALEGERI
    # ------------------------------------------------------------
    with subtab_edit_students:
        raw_students_list = sm.get_students_for_session(edit_sid)
        raw_choices_list = sm.get_choices_for_session(edit_sid)
        st_choices_map = {c["student_id"]: c.get("option1") for c in raw_choices_list}

        if not raw_students_list:
            st.info(f"ℹ️ Sesiunea «{target_edit_sess['title']}» nu are elevi înregistrați.")
        else:
            st_list = sorted(raw_students_list, key=lambda s: (s.get("last_name", "").upper(), s.get("first_name", "").upper()))

            def format_st_picker(idx):
                s = st_list[idx]
                c = st_choices_map.get(s["id"])
                c_txt = f" ➔ 🏢 {c.replace('UM_', 'UM ')}" if c else " (fără alegere)"
                return f"{s.get('last_name', '')} {s.get('first_name', '')} | {s.get('specialization', '')} | Medie: {float(s.get('average', 0.0)):.2f}{c_txt}"

            selected_st_idx = st.selectbox(
                "🔍 Caută și alege elevul de modificat:",
                range(len(st_list)),
                format_func=format_st_picker,
                key=f"picker_student_{edit_sid}"
            )
            curr_s = st_list[selected_st_idx]
            curr_sid = curr_s["id"]
            curr_choice = st_choices_map.get(curr_sid) or ""

            st.write(f"#### 👤 Modificare Date: {curr_s.get('last_name')} {curr_s.get('first_name')} `[{curr_sid}]`")

            col_e1, col_e2, col_e3 = st.columns([1.5, 1.5, 1])
            with col_e1:
                new_last_name = st.text_input("Nume de familie", value=curr_s.get("last_name", ""), key=f"e_ln_{curr_sid}")
            with col_e2:
                new_first_name = st.text_input("Prenume", value=curr_s.get("first_name", ""), key=f"e_fn_{curr_sid}")
            with col_e3:
                new_avg = st.number_input("Medie absolvire", min_value=1.0, max_value=10.0, value=float(curr_s.get("average", 0.0)), step=0.01, format="%.2f", key=f"e_avg_{curr_sid}")

            col_eg, col_esp = st.columns([1, 1.5])
            with col_eg:
                curr_g_idx = 0 if curr_s.get("gender") == "B" else 1
                new_gender = st.selectbox("Gen", ["B", "F"], index=curr_g_idx, format_func=lambda g: "👦 Băiat (B)" if g == "B" else "👧 Fată (F)", key=f"e_gen_{curr_sid}")
            with col_esp:
                spec_options = ["Aparare Cibernetica", "Tehnologia Informatiei", "Comunicatii", "Securitate Militara"]
                norm_curr_spec = normalize_spec(curr_s.get("specialization", ""))
                curr_spec_idx = spec_options.index(norm_curr_spec) if norm_curr_spec in spec_options else 0
                new_spec = st.selectbox("Specializare militară", spec_options, index=curr_spec_idx, key=f"e_spec_{curr_sid}")

            # Selector Unitate Aleasă
            sess_units = sm.get_units_for_session(edit_sid)
            norm_new_spec = normalize_spec(new_spec)
            matching_units = sorted(list(set(u["unit_name"] for u in sess_units if normalize_spec(u.get("specialization", "")) == norm_new_spec)))

            choice_dropdown_options = ["(Fără opțiune / Șterge alegerea)"] + matching_units
            if curr_choice and curr_choice not in choice_dropdown_options:
                choice_dropdown_options.append(curr_choice)

            curr_choice_index = choice_dropdown_options.index(curr_choice) if curr_choice in choice_dropdown_options else 0

            new_choice_selection = st.selectbox(
                "🏢 Unitate militară aleasă (Opțiunea 1 a elevului):",
                choice_dropdown_options,
                index=curr_choice_index,
                format_func=lambda x: f"🏢 {x.replace('UM_', 'UM ')}" if not x.startswith("(") else x,
                key=f"e_choice_{curr_sid}"
            )

            # Detecție diferențe (Diff)
            st_changes = []
            if new_last_name.strip() != curr_s.get("last_name", "").strip():
                st_changes.append(f"**Nume de familie:** `{curr_s.get('last_name')}` ➔ `{new_last_name.strip()}`")
            if new_first_name.strip() != curr_s.get("first_name", "").strip():
                st_changes.append(f"**Prenume:** `{curr_s.get('first_name')}` ➔ `{new_first_name.strip()}`")
            if abs(new_avg - float(curr_s.get("average", 0.0))) > 0.001:
                st_changes.append(f"**Medie:** `{float(curr_s.get('average', 0.0)):.2f}` ➔ `{new_avg:.2f}`")
            if new_gender != curr_s.get("gender"):
                st_changes.append(f"**Gen:** `{curr_s.get('gender')}` ➔ `{new_gender}`")
            if normalize_spec(new_spec) != norm_curr_spec:
                st_changes.append(f"**Specializare:** `{norm_curr_spec}` ➔ `{new_spec}`")

            clean_curr_c = curr_choice.strip() if curr_choice else ""
            clean_new_c = new_choice_selection.strip() if not new_choice_selection.startswith("(") else ""
            if clean_new_c != clean_curr_c:
                old_c_lbl = clean_curr_c.replace("UM_", "UM ") if clean_curr_c else "(Fără opțiune)"
                new_c_lbl = clean_new_c.replace("UM_", "UM ") if clean_new_c else "(Fără opțiune - ștearsă)"
                st_changes.append(f"**Unitate aleasă:** `{old_c_lbl}` ➔ `{new_c_lbl}`")

            if not st_changes:
                st.info("ℹ️ Nu ai modificat niciun câmp pentru acest elev. Datele sunt identice cu cele din baza de date.")
            else:
                st.warning("⚠️ **Modificări detectate ce urmează a fi salvate:**\n\n" + "\n\n".join(f"• {c}" for c in st_changes))
                confirm_save_st = st.checkbox(
                    f"⚠️ **Ești sigur că vrei să salvezi aceste modificări pentru elevul {curr_s.get('last_name')} {curr_s.get('first_name')}?**",
                    key=f"chk_confirm_st_save_{curr_sid}"
                )
                if st.button("💾 Salvează modificările elevului în baza de date", type="primary", disabled=not confirm_save_st, key=f"btn_save_st_edit_{curr_sid}", use_container_width=True):
                    updates = {
                        "last_name": new_last_name,
                        "first_name": new_first_name,
                        "average": new_avg,
                        "gender": new_gender,
                        "specialization": new_spec,
                        "chosen_unit": clean_new_c
                    }
                    if sm.update_student(edit_sid, curr_sid, updates):
                        st.success(f"🎉 Datele elevului {new_last_name} {new_first_name} au fost actualizate cu succes!")
                        st.rerun()
                    else:
                        st.error("A apărut o eroare la salvarea modificărilor în baza de date.")

            # Secțiune de resetare parolă elev
            st.write("")
            with st.expander("🔑 Resetare Parolă Cont Elev (la '123456')", expanded=False):
                st_username = curr_s.get("username") or f"{curr_s.get('last_name', '').lower().strip()}.{curr_s.get('first_name', '').lower().strip()}"
                st.write(
                    f"Această opțiune resetează parola contului pentru elevul **{curr_s.get('last_name')} {curr_s.get('first_name')}** "
                    f"(Username de conectare: ` {st_username} `)."
                )
                st.info("💡 Noua parolă a elevului va deveni parola inițială: **`123456`**")

                confirm_pwd = st.checkbox(
                    f"⚠️ **Confirm că sunt sigur că doresc să resetez parola elevului {curr_s.get('last_name')} {curr_s.get('first_name')} la '123456'.**",
                    key=f"chk_reset_pwd_{curr_sid}"
                )
                if st.button("🔑 Resetează Parola la «123456»", type="secondary", disabled=not confirm_pwd, key=f"btn_reset_pwd_{curr_sid}", use_container_width=True):
                    if sm.reset_student_password(curr_sid, "123456"):
                        st.success(f"🎉 Parola pentru elevul {curr_s.get('last_name')} {curr_s.get('first_name')} a fost resetată cu succes la «123456»!")
                        st.rerun()
                    else:
                        st.error("A apărut o eroare la resetarea parolei în baza de date.")

    # ------------------------------------------------------------
    # SUBTAB 2: EDITARE UNITĂȚI MILITARE & LOCURI
    # ------------------------------------------------------------
    with subtab_edit_units:
        raw_units_list = sm.get_units_for_session(edit_sid)

        if not raw_units_list:
            st.info(f"ℹ️ Sesiunea «{target_edit_sess['title']}» nu are unități militare înregistrate.")
        else:
            sorted_units = sorted(raw_units_list, key=lambda u: (u.get("unit_name", ""), u.get("specialization", "")))

            def format_u_picker(idx):
                u = sorted_units[idx]
                disp_u = u.get("unit_name", "").replace("UM_", "UM ")
                return f"{disp_u} | {u.get('specialization', '')} (Locuri: {u.get('boys', 0)} Băieți, {u.get('girls', 0)} Fete)"

            selected_u_idx = st.selectbox(
                "🔍 Caută și alege unitatea militară de modificat:",
                range(len(sorted_units)),
                format_func=format_u_picker,
                key=f"picker_unit_{edit_sid}"
            )
            curr_u = sorted_units[selected_u_idx]
            curr_uid = curr_u["id"]

            st.write(f"#### 🏢 Modificare Intrare Unitate: {curr_u.get('unit_name')} — {curr_u.get('specialization')} `[ID: {curr_uid}]`")

            col_un1, col_un2 = st.columns([2, 1.5])
            with col_un1:
                new_u_name = st.text_input("Denumire Unitate Militară", value=curr_u.get("unit_name", "").replace("UM_", "UM "), key=f"e_uname_{curr_uid}")
            with col_un2:
                u_spec_options = ["Aparare Cibernetica", "Tehnologia Informatiei", "Comunicatii", "Securitate Militara"]
                norm_curr_u_spec = normalize_spec(curr_u.get("specialization", ""))
                curr_u_spec_idx = u_spec_options.index(norm_curr_u_spec) if norm_curr_u_spec in u_spec_options else 0
                new_u_spec = st.selectbox("Specializare militară", u_spec_options, index=curr_u_spec_idx, key=f"e_uspec_{curr_uid}")

            col_ub, col_ug = st.columns([1, 1])
            with col_ub:
                new_u_boys = st.number_input("Locuri alocate Băieți", min_value=0, max_value=100, value=int(curr_u.get("boys", 0)), step=1, key=f"e_uboys_{curr_uid}")
            with col_ug:
                new_u_girls = st.number_input("Locuri alocate Fete", min_value=0, max_value=100, value=int(curr_u.get("girls", 0)), step=1, key=f"e_ugirls_{curr_uid}")

            # Detecție diferențe
            u_changes = []
            clean_new_u = sm.clean_unit_name_str(new_u_name)
            if clean_new_u != curr_u.get("unit_name"):
                u_changes.append(f"**Denumire:** `{curr_u.get('unit_name')}` ➔ `{clean_new_u}`")
            if normalize_spec(new_u_spec) != norm_curr_u_spec:
                u_changes.append(f"**Specializare:** `{norm_curr_u_spec}` ➔ `{new_u_spec}`")
            if new_u_boys != int(curr_u.get("boys", 0)):
                u_changes.append(f"**Locuri Băieți:** `{curr_u.get('boys', 0)}` ➔ `{new_u_boys}`")
            if new_u_girls != int(curr_u.get("girls", 0)):
                u_changes.append(f"**Locuri Fete:** `{curr_u.get('girls', 0)}` ➔ `{new_u_girls}`")

            if not u_changes:
                st.info("ℹ️ Nu ai modificat niciun câmp pentru această unitate militară.")
            else:
                st.warning("⚠️ **Modificări detectate ce urmează a fi salvate:**\n\n" + "\n\n".join(f"• {c}" for c in u_changes))
                confirm_save_u = st.checkbox(
                    f"⚠️ **Ești sigur că vrei să salvezi modificările pentru unitatea {curr_u.get('unit_name')}?**",
                    key=f"chk_confirm_u_save_{curr_uid}"
                )
                if st.button("💾 Salvează modificările unității în baza de date", type="primary", disabled=not confirm_save_u, key=f"btn_save_u_edit_{curr_uid}", use_container_width=True):
                    updates = {
                        "unit_name": clean_new_u,
                        "specialization": new_u_spec,
                        "boys": new_u_boys,
                        "girls": new_u_girls
                    }
                    if sm.update_unit(edit_sid, curr_uid, updates):
                        st.success(f"🎉 Unitatea {clean_new_u} a fost actualizată cu succes!")
                        st.rerun()
                    else:
                        st.error("A apărut o eroare la salvarea unității în baza de date.")

            # Secțiune de ștergere unitate
            st.write("")
            with st.expander("🗑️ Ștergere intrare unitate militară"):
                st.warning(f"Atenție: Această acțiune va șterge definitiv din sesiune intrarea: **{curr_u.get('unit_name')} ({curr_u.get('specialization')})**.")
                confirm_del_u = st.checkbox(f"⚠️ Confirm ștergerea definitivă a intrării [ID: {curr_uid}]", key=f"chk_del_u_{curr_uid}")
                if st.button("🗑️ Șterge definitiv această unitate", type="secondary", disabled=not confirm_del_u, key=f"btn_del_u_{curr_uid}"):
                    if sm.delete_unit_entry(edit_sid, curr_uid):
                        st.success("Unitatea a fost ștearsă cu succes!")
                        st.rerun()
                    else:
                        st.error("Eroare la ștergerea unității.")

        # Secțiune de adăugare unitate nouă
        st.write("---")
        with st.expander("➕ Adaugă o unitate militară nouă în această sesiune"):
            st.write("Completează datele pentru noua unitate militară:")
            col_add1, col_add2 = st.columns([2, 1.5])
            with col_add1:
                add_u_name = st.text_input("Denumire Unitate (ex: UM 01234 Bucuresti)", key=f"add_uname_{edit_sid}")
            with col_add2:
                add_u_spec = st.selectbox("Specializare militară", ["Aparare Cibernetica", "Tehnologia Informatiei", "Comunicatii", "Securitate Militara"], key=f"add_uspec_{edit_sid}")

            col_addb, col_addg = st.columns([1, 1])
            with col_addb:
                add_u_boys = st.number_input("Locuri alocate Băieți", min_value=0, max_value=100, value=1, step=1, key=f"add_uboys_{edit_sid}")
            with col_addg:
                add_u_girls = st.number_input("Locuri alocate Fete", min_value=0, max_value=100, value=0, step=1, key=f"add_ugirls_{edit_sid}")

            confirm_add_u = st.checkbox("⚠️ **Confirm că sunt sigur că doresc să introduc această unitate nouă în baza de date.**", key=f"chk_confirm_add_{edit_sid}")
            if st.button("➕ Adaugă unitatea în sesiune", type="primary", disabled=not confirm_add_u or not add_u_name.strip(), key=f"btn_add_unit_{edit_sid}", use_container_width=True):
                if sm.add_unit_entry(edit_sid, add_u_name, add_u_spec, add_u_boys, add_u_girls):
                    st.success(f"🎉 Unitatea {add_u_name} a fost adăugată cu succes!")
                    st.rerun()
                else:
                    st.error("A apărut o eroare la adăugarea unității.")


# ============================================================
# TAB 4: CONFIGURARE PROMOȚII & SESIUNI (IMPORT EXCEL)
# ============================================================
with tab_config:
    # ------------------------------------------------------------
    # Secțiunea 1: Control Sesiune Activă în App
    # ------------------------------------------------------------
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">🚦 1. Control Sesiune Activă în Aplicația Elevilor (App)</div>
    </div>
    """)

    if active_session:
        active_mode = sm.get_session_mode(active_session["id"])
        mode_badge = "⚖️ REAL (În ordinea mediilor)" if active_mode == "real" else "🎮 SIMULARE (Liber)"
        st.success(f"🟢 În prezent, repartizarea în pagina principală **App** este **DESCHISĂ** pentru sesiunea:\n\n**{active_session['title']}**\n\n📌 **Mod repartiție curent:** `{mode_badge}`")
    else:
        st.warning("🔒 În prezent, repartizarea în pagina principală **App** este **OPRITĂ**. Elevii nu pot alege opțiuni (pagina este blocată).")

    col_act1, col_act2 = st.columns([3, 2], vertical_alignment="center")
    with col_act1:
        sess_to_activate = st.selectbox(
            "Alege sesiunea pe care dorești să o configurezi / activezi:",
            [s["title"] for s in all_sessions],
            index=default_idx,
            key="select_session_to_activate"
        )
    target_s = next(s for s in all_sessions if s["title"] == sess_to_activate)
    with col_act2:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🟢 Deschide în App", use_container_width=True, key="btn_activate_session"):
                sm.set_active_session(target_s["id"])
                st.toast(f"Sesiunea «{target_s['title']}» este acum ACTIVĂ în App!")
                st.rerun()
        with col_b2:
            if st.button("⏸️ Oprește Repartizarea", use_container_width=True, key="btn_deactivate_all"):
                sm.set_active_session(None)
                st.toast("Repartizarea a fost oprită! Pagina App este acum blocată.")
                st.rerun()

    # Comutator Mod de funcționare (Simulare vs Real)
    current_sess_mode = sm.get_session_mode(target_s["id"])
    mode_idx = 0 if current_sess_mode == "simulare" else 1

    st.write("")
    st.write(f"⚙️ **Modul de funcționare al repartiției pentru «{target_s['title']}»:**")

    mode_options = [
        "🎮 Mod Simulare (Liber — Primul venit, primul servit)",
        "⚖️ Mod Real (Strict în ordinea mediilor descrescătoare pe specializare)"
    ]

    selected_mode_radio = st.radio(
        "Alege modul de funcționare:",
        mode_options,
        index=mode_idx,
        help="În Modul Simulare, orice elev se poate autentifica și poate alege liber un loc rămas disponibil. În Modul Real, elevii pot alege STRICT în ordinea descrescătoare a mediilor de la aceeași armă (elevul cu media mai mică trebuie să aștepte până alege cel cu media imediat superioară).",
        key=f"radio_mode_{target_s['id']}"
    )

    new_mode_val = "simulare" if "Simulare" in selected_mode_radio else "real"
    if new_mode_val != current_sess_mode:
        sm.set_session_mode(target_s["id"], new_mode_val)
        st.toast(f"Modul de repartiție a fost setat la: {new_mode_val.upper()}!")
        st.rerun()

    if new_mode_val == "real":
        st.info("⚖️ **Modul REAL este activat:** În pagina principală **App**, elevii vor putea alege strict în ordinea mediilor. Elevul care nu este la rând va vedea un banner cu numele și media colegului care alege în acel moment.")
    else:
        st.caption("🎮 *Modul SIMULARE este activat: Selecție liberă fără prioritizare pe bază de rând.*")

    st.write("---")

    # ------------------------------------------------------------
    # Secțiunea 2: Creare Promoție / Sesiune Nouă
    # ------------------------------------------------------------
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">➕ 2. Adăugare Promoție / Sesiune Nouă de Practică</div>
    </div>
    """)

    with st.form("form_create_session"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            new_cat = st.radio("Corp Militar / Categorie", ["Maiștri Militari", "Subofițeri"], horizontal=True)
            new_promo = st.text_input("Promoție (ex: 2025 - 2027 sau 2026 - 2028)", placeholder="2025 - 2027")
        with col_c2:
            if new_cat == "Maiștri Militari":
                new_pract = st.selectbox("Tipul stagiului de practică", ["Practica 1 (Anul 1)", "Practica 2 (Anul 2)"])
            else:
                new_pract = st.selectbox("Tipul stagiului de practică", ["Practica 1 (Stagiu unic)"])
            new_year = st.number_input("Anul calendaristic al stagiului", min_value=2024, max_value=2035, value=2027)

        btn_create = st.form_submit_button("Creează Sesiunea", use_container_width=True)
        if btn_create:
            if not new_promo.strip():
                st.error("Te rugăm să introduci promoția!")
            else:
                p_type_clean = "Practica 1" if "1" in new_pract else "Practica 2"
                created = sm.create_session(new_cat, new_promo.strip(), p_type_clean, int(new_year))
                st.success(f"Sesiunea a fost creată cu succes: **{created['title']}**!")
                st.rerun()

    st.write("---")

    # ------------------------------------------------------------
    # Secțiunea 3: Import Elevi din Excel (Paste sau Upload)
    # ------------------------------------------------------------
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">👥 3. Import Elevi dintr-un tabel Excel</div>
        <div class="guide-box">
            <b>📌 Format coloane așteptat din Excel:</b><br>
            Tabelul copiat trebuie să conțină coloanele: <code>Nume</code> | <code>Prenume</code> | <code>Specializare</code> | <code>Medie</code> | <code>Gen (B / F)</code>.<br>
            <i>Poți da Copy direct la celulele dintr-un fișier Excel și Paste mai jos, sau poți încărca fișierul .xlsx / .csv direct.</i>
        </div>
    </div>
    """)

    target_sess_title_students = st.selectbox(
        "Selectează sesiunea țintă pentru care imporți elevii:",
        [s["title"] for s in all_sessions],
        key="target_sess_students"
    )
    target_sess_students = next(s for s in all_sessions if s["title"] == target_sess_title_students)

    tab_st_paste, tab_st_file = st.tabs(["📋 Paste din Excel", "📁 Încarcă fișier Excel (.xlsx / .csv)"])

    parsed_students = None

    with tab_st_paste:
        raw_students_text = st.text_area(
            "Lipește aici tabelul copiat din Excel (Ctrl+V):",
            placeholder="Nume\tPrenume\tSpecializare\tMedie\tGen\nPopescu\tVlad\tAparare Cibernetica\t9.50\tB\nIonescu\tMaria\tComunicatii\t9.80\tF",
            height=180,
            key="students_paste_area"
        )
        if st.button("🔍 Analizează tabelul lipit", key="btn_parse_students_text"):
            if raw_students_text.strip():
                parsed_students = sm.parse_students_text(raw_students_text)
                st.session_state["temp_parsed_students"] = parsed_students
            else:
                st.warning("Zona de text este goală.")

    with tab_st_file:
        uploaded_st_file = st.file_uploader("Încarcă fișierul cu elevi", type=["xlsx", "xls", "csv"], key="st_file_upload")
        if uploaded_st_file:
            try:
                if uploaded_st_file.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_st_file)
                else:
                    df_upload = pd.read_excel(uploaded_st_file)
                parsed_students = sm.process_students_dataframe(df_upload)
                st.session_state["temp_parsed_students"] = parsed_students
            except Exception as e:
                st.error(f"Eroare la citirea fișierului: {e}")
                if "openpyxl" in str(e).lower():
                    st.info("💡 **Notă:** Pachetul `openpyxl` a fost instalat. Te rugăm să reîmprospătezi pagina (F5) sau să repornești comanda Streamlit în consolă. Poți folosi de asemenea tab-ul **📋 Paste din Excel** de mai sus pentru import instant!")

    # Previzualizare elevi analizați
    students_to_preview = st.session_state.get("temp_parsed_students", parsed_students)
    if students_to_preview:
        st.write(f"### ✅ Previzualizare: {len(students_to_preview)} elevi detectați")

        # Numărătoare băieți / fete
        count_boys = len([s for s in students_to_preview if s["gender"] == "B"])
        count_girls = len([s for s in students_to_preview if s["gender"] == "F"])
        specs_found = set(s["specialization"] for s in students_to_preview)

        st.info(f"**Statistici:** {count_boys} băieți, {count_girls} fete | Specializări detectate: {', '.join(specs_found)}")

        df_preview_st = pd.DataFrame(students_to_preview)[["last_name", "first_name", "specialization", "average", "gender", "username", "password_hash"]]
        df_preview_st.columns = ["Nume", "Prenume", "Specializare", "Medie", "Gen", "Username Generat", "Parolă Inițială"]
        st.dataframe(df_preview_st, use_container_width=True)

        # Verificare date existente pentru prevenirea suprascrierii accidentale
        existing_st = sm.get_students_for_session(target_sess_students["id"])
        existing_ch = sm.get_choices_for_session(target_sess_students["id"])

        can_save_st = True
        if existing_st:
            st.error(
                f"⚠️ **ATENȚIE: Sesiunea «{target_sess_students['title']}» conține deja {len(existing_st)} elevi înregistrați!**\n\n"
                f"Salvarea va **suprascrie / înlocui** elevii existenți din această sesiune."
                + (f"\n\n🚨 **PERICOL MARE:** Există deja **{len(existing_ch)} opțiuni salvate de către elevi** în această sesiune! Suprascrierea elevilor va afecta alegerile făcute." if existing_ch else "")
            )
            confirm_st = st.checkbox(
                f"⚠️ **Confirm că sunt sigur că vreau să SUPRASCRIU cei {len(existing_st)} elevi existenți** din «{target_sess_students['title']}» cu această listă nouă de {len(students_to_preview)} elevi.",
                key=f"confirm_overwrite_st_{target_sess_students['id']}"
            )
            can_save_st = confirm_st

        col_save_st, col_clear_st = st.columns([3, 1])
        with col_save_st:
            if st.button(
                f"💾 Salvează cei {len(students_to_preview)} elevi în «{target_sess_students['title']}»",
                type="primary",
                use_container_width=True,
                disabled=not can_save_st,
                key="btn_save_students"
            ):
                saved_cnt = sm.save_students_for_session(target_sess_students["id"], students_to_preview)
                st.session_state["temp_parsed_students"] = None
                st.success(f"🎉 {saved_cnt} elevi au fost salvați și înregistrați cu succes în sesiunea «{target_sess_students['title']}»!")
                st.rerun()
            if not can_save_st:
                st.caption("🔒 *Butonul de salvare este blocat până când bifezi confirmarea de mai sus.*")
        with col_clear_st:
            if st.button("🗑️ Anulează previzualizarea", key="clear_preview_st", use_container_width=True):
                st.session_state["temp_parsed_students"] = None
                st.rerun()

    st.write("---")

    # ------------------------------------------------------------
    # Secțiunea 4: Import Unități Militare (UM-uri) din Excel
    # ------------------------------------------------------------
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">🏢 4. Import Unități Militare (Locuri de Practică)</div>
        <div class="guide-box">
            <b>📌 Formate acceptate din Excel:</b><br>
            • <b>Documentul oficial MApN:</b> fișierul original tipizat cu celule îmbinate (Unitatea militară, Specialitatea militară, Total, Băieți [B], Fete [F]).<br>
            • <b>Format tabelar simplu:</b> <code>Unitate</code> | <code>Specializare</code> | <code>Locuri Băieți</code> | <code>Locuri Fete</code>.<br>
            <i>Poți încărca fișierul .xlsx / .csv direct sau poți folosi Copy-Paste la celule în tab-ul alăturat.</i>
        </div>
    </div>
    """)

    target_sess_title_units = st.selectbox(
        "Selectează sesiunea țintă pentru care imporți locurile UM:",
        [s["title"] for s in all_sessions],
        key="target_sess_units"
    )
    target_sess_units = next(s for s in all_sessions if s["title"] == target_sess_title_units)

    tab_um_paste, tab_um_file = st.tabs(["📋 Paste din Excel", "📁 Încarcă fișier Excel (.xlsx / .csv)"])

    parsed_units = None

    with tab_um_paste:
        raw_units_text = st.text_area(
            "Lipește aici tabelul copiat din Excel cu unitățile (Ctrl+V):",
            placeholder="Unitate\tSpecializare\tLocuri Băieți\tLocuri Fete\nUM 01107 Brasov\tAparare Cibernetica\t2\t1\nUM 02499 Bucuresti\tComunicatii\t3\t2",
            height=180,
            key="units_paste_area"
        )
        if st.button("🔍 Analizează unitățile lipite", key="btn_parse_units_text"):
            if raw_units_text.strip():
                parsed_units = sm.parse_units_text(raw_units_text)
                st.session_state["temp_parsed_units"] = parsed_units
            else:
                st.warning("Zona de text este goală.")

    with tab_um_file:
        uploaded_um_file = st.file_uploader("Încarcă fișierul cu unități", type=["xlsx", "xls", "csv"], key="um_file_upload")
        if uploaded_um_file:
            try:
                if uploaded_um_file.name.endswith(".csv"):
                    df_u_upload = pd.read_csv(uploaded_um_file)
                else:
                    df_u_upload = pd.read_excel(uploaded_um_file)
                parsed_units = sm.process_units_dataframe(df_u_upload)
                st.session_state["temp_parsed_units"] = parsed_units
            except Exception as e:
                st.error(f"Eroare la citirea fișierului de unități: {e}")
                if "openpyxl" in str(e).lower():
                    st.info("💡 **Notă:** Pachetul `openpyxl` a fost instalat. Te rugăm să reîmprospătezi pagina (F5) sau să repornești comanda Streamlit în consolă. Poți folosi de asemenea tab-ul **📋 Paste din Excel** de mai sus pentru import instant!")

    units_to_preview = st.session_state.get("temp_parsed_units", parsed_units)
    if units_to_preview:
        tot_b = sum(u["boys"] for u in units_to_preview)
        tot_f = sum(u["girls"] for u in units_to_preview)
        st.write(f"### ✅ Previzualizare: {len(units_to_preview)} intrări unități detectate")
        st.info(f"**Total locuri disponibile:** {tot_b + tot_f} ({tot_b} Băieți, {tot_f} Fete)")

        df_u_preview = pd.DataFrame(units_to_preview)
        df_u_preview.columns = ["Unitate", "Specializare", "Locuri Băieți", "Locuri Fete"]
        st.dataframe(df_u_preview, use_container_width=True)

        # Verificare date existente pentru prevenirea suprascrierii accidentale
        existing_u = sm.get_units_for_session(target_sess_units["id"])
        can_save_u = True
        if existing_u:
            tot_ex_b = sum(u.get("boys", 0) for u in existing_u)
            tot_ex_f = sum(u.get("girls", 0) for u in existing_u)
            st.error(
                f"⚠️ **ATENȚIE: Sesiunea «{target_sess_units['title']}» conține deja {len(existing_u)} unități militare înregistrate** "
                f"(totalizând {tot_ex_b + tot_ex_f} locuri: {tot_ex_b} Băieți, {tot_ex_f} Fete)!\n\n"
                f"Salvarea noilor date va **suprascrie / înlocui** unitățile existente din această sesiune."
            )
            confirm_u = st.checkbox(
                f"⚠️ **Confirm că sunt sigur că vreau să SUPRASCRIU cele {len(existing_u)} unități existente** din «{target_sess_units['title']}» cu această listă nouă de {len(units_to_preview)} unități ({tot_b + tot_f} locuri).",
                key=f"confirm_overwrite_u_{target_sess_units['id']}"
            )
            can_save_u = confirm_u

        col_save, col_clear = st.columns([3, 1])
        with col_save:
            if st.button(
                f"💾 Salvează unitățile în «{target_sess_units['title']}»",
                type="primary",
                use_container_width=True,
                disabled=not can_save_u,
                key="btn_save_units"
            ):
                saved_u = sm.save_units_for_session(target_sess_units["id"], units_to_preview)
                st.session_state["temp_parsed_units"] = None
                st.success(f"🎉 {saved_u} unități de practică au fost salvate cu succes în sesiunea «{target_sess_units['title']}»!")
                st.rerun()
            if not can_save_u:
                st.caption("🔒 *Butonul de salvare este blocat până când bifezi confirmarea de mai sus.*")
        with col_clear:
            if st.button("🗑️ Anulează previzualizarea", key="clear_preview_u", use_container_width=True):
                st.session_state["temp_parsed_units"] = None
                st.rerun()

    st.write("---")

    # ------------------------------------------------------------
    # Secțiunea 5: Listă Sesiuni & Gestiune
    # ------------------------------------------------------------
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">📂 5. Toate Sesiunile Configurate</div>
    </div>
    """)

    sess_summary_rows = []
    for s in all_sessions:
        s_id = s["id"]
        s_elevi = len(sm.get_students_for_session(s_id))
        s_unitati = len(sm.get_units_for_session(s_id))
        s_status = "🟢 ACTIVĂ" if s.get("is_active") else "📁 Inactivă"
        s_mode = "⚖️ REAL" if s.get("allocation_mode") == "real" else "🎮 Simulare"

        sess_summary_rows.append({
            "ID": s_id,
            "Denumire": s["title"],
            "Corp": s["category"],
            "Promoție": s["promotion"],
            "Tip Practică": s["practice_type"],
            "An": s["year"],
            "Mod": s_mode,
            "Elevi": s_elevi,
            "Unități": s_unitati,
            "Stare": s_status
        })

    st.dataframe(pd.DataFrame(sess_summary_rows), use_container_width=True)

    # Posibilitate de ștergere pentru sesiuni custom
    deletable_sessions = [s for s in all_sessions if s["id"] != sm.DEFAULT_SESSION_ID]
    if deletable_sessions:
        with st.expander("🗑️ Ștergere sesiune"):
            st.warning("Atenție: Ștergerea unei sesiuni va elimina și elevii, unitățile și alegerile asociate acesteia!")
            to_delete_title = st.selectbox("Alege sesiunea pe care dorești să o ștergi:", [s["title"] for s in deletable_sessions])
            to_delete_sess = next(s for s in deletable_sessions if s["title"] == to_delete_title)
            if st.button(f"Confirmă ștergerea definitivă a sesiunii «{to_delete_sess['title']}»", type="secondary"):
                sm.delete_session(to_delete_sess["id"])
                st.toast("Sesiunea a fost ștearsă!")
                st.rerun()