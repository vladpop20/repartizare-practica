import streamlit as st
import pandas as pd

from supabase_db import (
    get_all_choices,
    get_all_students
)

st.title("Admin")

choices = get_all_choices()

students = get_all_students()

df = pd.DataFrame(choices)

st.dataframe(
    df,
    use_container_width=True
)

st.subheader(
    "Alegeri detaliate"
)

rows = []

for choice in choices:

    student_id = choice["student_id"]

    student = next(
        (
            s
            for s in students
            if s["id"] == student_id
        ),
        None
    )

    if student is None:
        continue

    rows.append(
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
                choice["option3"]
        }
    )

df2 = pd.DataFrame(rows)

st.dataframe(
    df2,
    use_container_width=True
)