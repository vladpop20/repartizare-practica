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
    render_unit_header,
    render_option
)

st.set_page_config(
    page_title="Situația în timp real",
    layout="wide"
)

st_autorefresh(
    interval=10000,
    key="live_monitor"
)

load_css()

st.title("📊 Situația în timp real")

st.caption(
    "Actualizare automată la fiecare 10 secunde"
)

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
# Filtre
#

specializare = st.selectbox(
    "Specializare",
    list(monitor.keys())
)

cautare = st.text_input(
    "🔍 Caută elev"
).strip().lower()

#
# Unități
#

for unit_name, unit in monitor[specializare].items():

    #
    # dacă nu există niciun elev pe opțiune,
    # nu afișăm unitatea
    #

    if not (unit["option1"]["boys"] or unit["option1"]["girls"]):
        continue

    #
    # căutare elev
    #

    if cautare:

        gasit = False

        for student in (
            unit["option1"]["boys"] +
            unit["option1"]["girls"]
        ):

            nume = (
                student["last_name"] +
                " " +
                student["first_name"]
            ).lower()

            if cautare in nume:
                gasit = True
                break

        if not gasit:
            continue

    #
    # Card unitate
    #

    render_unit_header(
        unit_name,
        unit
    )

    render_option(
        unit,
        "option1",
        "Opțiuni exprimate",
        cautare
    )

    st.markdown("---")
