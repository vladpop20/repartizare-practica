import streamlit as st
import pandas as pd

import sessions_manager as sm
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
header_left, header_right = st.columns([5, 1.2], vertical_alignment="center")
with header_left:
    render_html("""
    <div style="margin-bottom: 8px;">
        <h1 style="margin: 0; padding: 0; font-size: 2.1rem; font-weight: 800; color: #ffffff; line-height: 1.2;">🛡️ Panou Administrare</h1>
        <div style="color: #94a3b8; font-size: 13.5px; margin-top: 4px;">Gestiune sesiuni de practică, import promoții și evidența alegerilor</div>
    </div>
    """)
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
tab_evidence, tab_config = st.tabs([
    "📋 Evidență & Alegeri în timp real",
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
# TAB 2: CONFIGURARE PROMOȚII & SESIUNI (IMPORT EXCEL)
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
        st.success(f"🟢 În prezent, repartizarea în pagina principală **App** este **DESCHISĂ** pentru sesiunea:\n\n**{active_session['title']}**")
    else:
        st.warning("🔒 În prezent, repartizarea în pagina principală **App** este **OPRITĂ**. Elevii nu pot alege opțiuni (pagina este blocată).")

    col_act1, col_act2 = st.columns([3, 2], vertical_alignment="center")
    with col_act1:
        sess_to_activate = st.selectbox(
            "Alege sesiunea pe care dorești să o activezi:",
            [s["title"] for s in all_sessions],
            index=default_idx,
            key="select_session_to_activate"
        )
    with col_act2:
        target_s = next(s for s in all_sessions if s["title"] == sess_to_activate)
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

        if st.button(f"💾 Salvează cei {len(students_to_preview)} elevi în «{target_sess_students['title']}»", type="primary", use_container_width=True):
            saved_cnt = sm.save_students_for_session(target_sess_students["id"], students_to_preview)
            st.session_state["temp_parsed_students"] = None
            st.success(f"🎉 {saved_cnt} elevi au fost salvați și înregistrați cu succes în sesiunea «{target_sess_students['title']}»!")
            st.rerun()

    st.write("---")

    # ------------------------------------------------------------
    # Secțiunea 4: Import Unități Militare (UM-uri) din Excel
    # ------------------------------------------------------------
    render_html("""
    <div class="config-section-card">
        <div class="config-section-title">🏢 4. Import Unități Militare (Locuri de Practică)</div>
        <div class="guide-box">
            <b>📌 Format coloane așteptat din Excel:</b><br>
            Tabelul copiat trebuie să conțină coloanele: <code>Unitate</code> (sau Denumire UM) | <code>Specializare</code> | <code>Locuri Băieți</code> | <code>Locuri Fete</code>.<br>
            <i>Poți da Copy la celulele din Excel și Paste mai jos, sau încarcă fișierul .xlsx / .csv direct.</i>
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

        if st.button(f"💾 Salvează unitățile în «{target_sess_units['title']}»", type="primary", use_container_width=True):
            saved_u = sm.save_units_for_session(target_sess_units["id"], units_to_preview)
            st.session_state["temp_parsed_units"] = None
            st.success(f"🎉 {saved_u} unități de practică au fost salvate cu succes în sesiunea «{target_sess_units['title']}»!")
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

        sess_summary_rows.append({
            "ID": s_id,
            "Denumire": s["title"],
            "Corp": s["category"],
            "Promoție": s["promotion"],
            "Tip Practică": s["practice_type"],
            "An": s["year"],
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