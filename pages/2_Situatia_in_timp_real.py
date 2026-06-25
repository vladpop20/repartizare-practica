import streamlit as st

from supabase_db import (
    get_all_students,
    get_all_choices,
    get_all_units
)

from monitor_utils import (
    build_monitor
)

st.set_page_config(
    page_title="Situația în timp real",
    layout="wide"
)

st.title("Situația în timp real")

st.caption(
    "Actualizare automată la fiecare 10 secunde"
)

specializare = st.selectbox(
    "Specializare",
    [
        "Comunicatii",
        "Aparare Cibernetica",
        "Securitate Militara",
        "Tehnologia Informatiei"
    ]
)

cautare = st.text_input(
    "🔍 Caută elev"
)

students = get_all_students()

choices = get_all_choices()

units = get_all_units()

st.write(units[0])

monitor = build_monitor(
    students,
    choices,
    units
)

st.write(type(monitor))

st.write(monitor)

st.stop()

# st.write(monitor.keys())

students_map = {}

for student in students:

    students_map[
        student["id"]
    ] = student

for unit_name, unit in monitor[specializare].items():

    exista = False

    for option in [
        "option1",
        "option2",
        "option3"
    ]:

        for student in unit[option]["boys"]:

            if (
                student["specialization"]
                ==
                specializare
            ):

                exista = True

        for student in unit[option]["girls"]:

            if (
                student["specialization"]
                ==
                specializare
            ):

                exista = True

    if not exista:
        continue

    st.divider()

    st.header(unit_name)

    #
    # OPTIUNEA 1
    #

    st.subheader("Opțiunea 1")

    boys = unit["option1"]["boys"]
    girls = unit["option1"]["girls"]

    st.write(
        f"Băieți: {len(boys)}/{unit['boys_capacity']}"
    )

    st.progress(
        min(
            len(boys) / max(unit["boys_capacity"], 1),
            1.0
        )
    )

    st.write(
        f"Fete: {len(girls)}/{unit['girls_capacity']}"
    )

    if unit["girls_capacity"] > 0:

        st.progress(
            min(
                len(girls) / unit["girls_capacity"],
                1.0
            )
        )

    st.markdown("### Băieți")

    for student in boys:

        st.info(
            f"🟦 {student['last_name']} {student['first_name']} ({student['average']})"
        )

    st.markdown("### Fete")

    for student in girls:

        st.error(
            f"🟥 {student['last_name']} {student['first_name']} ({student['average']})"
        )

# st.write("Monitor construit!")
# st.write(len(monitor))

# st.write(monitor)