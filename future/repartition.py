import streamlit as st
import pandas as pd

from supabase_db import (
    get_all_students,
    get_all_choices,
    get_all_units,
    save_allocation,
    clear_allocations
)

from supabase_db import (
    get_all_students,
    get_all_choices,
    get_all_units
)

st.title("Simulare repartizare")

students = get_all_students()
choices = get_all_choices()
units = get_all_units()

unit_capacity = {}

for unit in units:

    unit_capacity[
        unit["unit_name"]
    ] = {
        "boys": unit["boys"],
        "girls": unit["girls"]
    }

students_sorted = sorted(
    students,
    key=lambda s: s["average"],
    reverse=True
)

choices_map = {}

for choice in choices:

    choices_map[
        choice["student_id"]
    ] = choice


results = []

clear_allocations()

for student in students_sorted:

    student_id = student["id"]

    if student_id not in choices_map:
        continue

    choice = choices_map[student_id]

    allocated = "NEREPARTIZAT"
    allocation_rank = 0

    options = [
        choice["option1"],
        choice["option2"],
        choice["option3"]
    ]

    for rank, option in enumerate(
        options,
        start = 1
    ):

        if option not in unit_capacity:
            continue

        if student["gender"] == "B":

            if unit_capacity[option]["boys"] > 0:

                unit_capacity[option]["boys"] -= 1

                allocated = option
                allocation_rank = rank

                break

        else:

            if unit_capacity[option]["girls"] > 0:

                unit_capacity[option]["girls"] -= 1

                allocated = option
                allocation_rank = rank

                break

    results.append(
        {
            "Elev":
                student["first_name"]
                + " "
                + student["last_name"],

            "Medie":
                student["average"],

            "Specializare":
                student["specialization"],

            "Optiunea 1":
                choice["option1"],

            "Optiunea 2":
                choice["option2"],

            "Optiunea 3":
                choice["option3"],

            "Repartizat":
                allocated
        }
    )

df = pd.DataFrame(results)

st.dataframe(
    df,
    use_container_width=True
)

st.subheader(
    "Locuri ramase"
)

remaining = []

for unit_name, capacity in unit_capacity.items():

    remaining.append(
        {
            "Unitate": unit_name,
            "Locuri baieti": capacity["boys"],
            "Locuri fete": capacity["girls"]
        }
    )

df_remaining = pd.DataFrame(
    remaining
)

st.dataframe(
    df_remaining,
    use_container_width=True
)