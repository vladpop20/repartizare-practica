import streamlit as st
from streamlit_autorefresh import st_autorefresh

from supabase_db import (
    get_all_students,
    get_all_choices,
    get_all_units
)

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
# Date
#
students = get_all_students()
choices = get_all_choices()
units = get_all_units()

monitor = build_monitor(
    students,
    choices,
    units
)

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


