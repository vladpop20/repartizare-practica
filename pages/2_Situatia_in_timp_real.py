import streamlit as st
from streamlit_autorefresh import st_autorefresh

import sessions_manager as sm

from monitor_utils import (
    build_monitor
)

from ui_utils import (
    load_css,
    render_html,
    render_unit_card,
    render_stats_sidebar
)

st.set_page_config(
    page_title="Situația în timp real",
    page_icon="📊",
    layout="wide"
)

st_autorefresh(
    interval=10000,
    key="live_monitor"
)

load_css()

#
# Titlu și info banner
#
st.title("📊 Situația în timp real")
st.caption("Actualizare automată la fiecare 10 secunde")

render_html("""
<div class="info-alert-banner">
    ℹ️ Fiecare casetă reprezintă un loc disponibil. <b>Albastru = băieți</b> | <b>Roșu = fete</b> | <b>Punctat = loc liber</b>
</div>
<div class="order-alert-banner">
    ✅ Ordinea elevilor în fiecare unitate este descrescătoare după medie.
</div>
""")

#
# Sesiune de practică / Promoție
#
all_sessions = sm.get_all_sessions()
active_session = sm.get_active_session()

default_sess_idx = 0
if active_session:
    for idx, s in enumerate(all_sessions):
        if s["id"] == active_session["id"]:
            default_sess_idx = idx
            break

col_s1, col_s2 = st.columns([4, 1.5], vertical_alignment="center")
with col_s1:
    session_title = st.selectbox(
        "Sesiune de practică / Promoție:",
        [s["title"] for s in all_sessions],
        index=default_sess_idx,
        key="live_monitor_session_select"
    )

selected_session = next((s for s in all_sessions if s["title"] == session_title), all_sessions[0])

with col_s2:
    if selected_session.get("is_active"):
        render_html('<div style="margin-top: 25px;"><span class="status-active-badge">🟢 În direct (Live)</span></div>')
    else:
        render_html('<div style="margin-top: 25px;"><span class="status-inactive-badge">📁 Consultare arhivă</span></div>')

#
# Date pentru sesiunea selectată
#
students = sm.get_students_for_session(selected_session["id"])
choices = sm.get_choices_for_session(selected_session["id"])
units = sm.get_units_for_session(selected_session["id"])

monitor = build_monitor(
    students,
    choices,
    units
)

if not monitor:
    st.info(f"Nu există încă unități de practică configurate pentru sesiunea «{selected_session['title']}». Administratorul poate adăuga unități din Panoul Admin.")
    st.stop()

#
# Filtre superioare
#
col_f1, col_f2 = st.columns([1, 1])

with col_f1:
    specializare = st.selectbox(
        "Specializare",
        list(monitor.keys())
    )

with col_f2:
    cautare = st.text_input(
        "🔍 Caută elev",
        placeholder="Nume sau prenume..."
    ).strip().lower()

# Indicator Mod Real și elev aflat la rând
if sm.get_session_mode(selected_session["id"]) == "real":
    turn_st_mon = sm.get_turn_student_for_spec(selected_session["id"], specializare)
    if turn_st_mon:
        st.info(f"⚖️ **Mod REAL activ (strict pe bază de medii):** În acest moment este la rând elevul **{turn_st_mon['last_name']} {turn_st_mon['first_name']}** (Medie: **{float(turn_st_mon.get('average', 0.0)):.2f}**)")
    else:
        st.success(f"🎉 **Mod REAL:** Toți elevii de la specializarea **{specializare}** și-au exprimat opțiunea!")


#
# Layout principal cu 2 coloane: Stânga (Unități de practică) | Dreapta (Statistici generale)
#
col_left, col_right = st.columns([7, 3])

with col_left:
    st.subheader("Unități de practică")

    units_dict = monitor.get(specializare, {})
    rendered_units = 0

    for unit_name, unit in units_dict.items():

        # Filtrare în caz de căutare activă
        if cautare:
            all_students_in_unit = (
                unit["option1"]["boys"] +
                unit["option1"]["girls"]
            )
            gasit = any(
                cautare in f"{s['last_name']} {s['first_name']}".lower()
                for s in all_students_in_unit
            )
            if not gasit:
                continue

        render_unit_card(
            unit_name,
            unit,
            cautare
        )
        rendered_units += 1

    if rendered_units == 0:
        if cautare:
            st.info(f"Niciun elev găsit pentru căutarea '{cautare}' în specializarea {specializare}.")
        else:
            st.info("Nu există unități de afișat pentru această specializare.")

with col_right:
    render_stats_sidebar(
        specializare,
        monitor,
        students,
        choices
    )


