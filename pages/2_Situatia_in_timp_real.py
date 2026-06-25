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
    # dacă nu există niciun elev pe nicio opțiune,
    # nu afișăm unitatea
    #

    exista = False

    for option in (
        "option1",
        "option2",
        "option3"
    ):

        if unit[option]["boys"] or unit[option]["girls"]:
            exista = True
            break

    if not exista:
        continue

    #
    # căutare elev
    #

    if cautare:

        gasit = False

        for option in (
            "option1",
            "option2",
            "option3"
        ):

            for student in (
                unit[option]["boys"] +
                unit[option]["girls"]
            ):

                nume = (
                    student["last_name"] +
                    " " +
                    student["first_name"]
                ).lower()

                if cautare in nume:
                    gasit = True
                    break

            if gasit:
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

    #
    # Tabs
    #

    tab1, tab2, tab3 = st.tabs(
        [
            "🟩 Opțiunea 1",
            "🟨 Opțiunea 2",
            "🟧 Opțiunea 3"
        ]
    )

    with tab1:

        render_option(
            unit,
            "option1",
            "Opțiunea 1",
            cautare
        )

    with tab2:

        render_option(
            unit,
            "option2",
            "Opțiunea 2",
            cautare
        )

    with tab3:

        render_option(
            unit,
            "option3",
            "Opțiunea 3",
            cautare
        )

    st.markdown("---")
