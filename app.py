import streamlit as st
from parser_students import load_students
from parser_units import load_units
from student_utils import get_gender
from choices_manager import save_choice, get_choice
from students_db import (
    get_student,
    create_account,
    login
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

students = load_students()
# count = 0

# for specializare, elevi in students.items():
#     st.write(specializare, len(elevi))
#     count += len(elevi)

# st.write("TOTAL:", count)
# st.write(students.keys())
units = load_units()

st.title("Simulare repartizare practica")

specializare = st.selectbox(
    "Selecteaza specializarea",
    list(students.keys())
)

elevi = students[specializare]

nume_afisate = [
    f"{prenume} {nume} ({medie})"
    for nume, prenume, medie in elevi
]

elev_selectat = st.selectbox(
    "Selecteaza numele",
    nume_afisate
)

st.success(f"Ai selectat: {elev_selectat}")

selected_student = None

for nume, prenume, medie in elevi:

    if f"{prenume} {nume} ({medie})" == elev_selectat:
        selected_student = (
            nume,
            prenume,
            medie
        )
        break

last_name, first_name, average = selected_student

specialization_codes = {
    "Aparare Cibernetica": "AC",
    "Securitate Militara": "SM",
    "Comunicatii": "COM",
    "Tehnologia Informatiei": "TI"
}

student_id = (
    specialization_codes[specializare]
    + "_"
    + last_name.replace(" ", "_")
    + "_"
    + first_name.replace(" ", "_")
)

if (
    st.session_state.get("student_id")
    and st.session_state.get("student_id") != student_id
):
    st.session_state["authenticated"] = False
    st.session_state["student_id"] = None

# st.write(f"ID: {student_id}")

student_record = get_student(student_id)

# st.write(student_record)

saved_choice = get_choice(student_id)

gender = get_gender(
    specializare,
    first_name,
    last_name
)

st.info(f"Gen: {gender}")

st.subheader("Autentificare")

if not student_record["username"]:

    st.info("Nu ai cont. Creeaza unul.")

    generated_username = (
        last_name.lower()
        + "."
        + first_name.lower()
    )

    st.info(
        f"Username-ul tau va fi: {generated_username}"
    )


    password = st.text_input(
        "Parola",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirma parola",
        type="password"
    )

    if st.button("Creeaza cont"):

        if password != confirm_password:
            st.error("Parolele nu coincid")

        else:

            create_account(
                student_id,
                generated_username,
                password
            )

            st.success(
                "Cont creat!"
            )

else:

    st.info(
        f"Username: {student_record['username']}"
    )

    username = student_record["username"]

    password = st.text_input(
        "Parola",
        type="password"
    )

    if st.button("Login"):

        if login(
            student_id,
            username,
            password
        ):

            st.session_state["authenticated"] = True
            st.session_state["student_id"] = student_id

            st.success(
                "Autentificat!"
            )

        else:

            st.error(
                "Date incorecte"
            )

for index, (nume, prenume, medie) in enumerate(elevi, start=1):
    if f"{prenume} {nume} ({medie})" == elev_selectat:
        st.info(f"Pozitie in clasament: {index}")
        st.info(f"Media: {medie}")
        break

st.write(
    f"Numar elevi: {len(elevi)}"
)

if st.session_state["authenticated"]:

    st.subheader("Unitati disponibile")

    available_units = []

    for unit in units[specializare]:

        if gender == "B" and unit["boys"] > 0:
            available_units.append(unit)

        elif gender == "F" and unit["girls"] > 0:
            available_units.append(unit)

    unit_names = [
        unit["display"]
        for unit in available_units
    ]

    default1 = 0
    default2 = 0
    default3 = 0

    if saved_choice:

        if saved_choice["option1"] in unit_names:
            default1 = unit_names.index(
                saved_choice["option1"]
            )

        if saved_choice["option2"] in unit_names:
            default2 = unit_names.index(
                saved_choice["option2"]
            )

        if saved_choice["option3"] in unit_names:
            default3 = unit_names.index(
                saved_choice["option3"]
            )

    option1 = st.selectbox(
        "Optiunea 1",
        unit_names,
        index=default1
    )

    option2 = st.selectbox(
        "Optiunea 2",
        unit_names,
        index=default2,
        key="opt2"
    )

    option3 = st.selectbox(
        "Optiunea 3",
        unit_names,
        index=default3,
        key="opt3"
    )

    if st.button("Salveaza optiunile"):

        selected = {
            option1,
            option2,
            option3
        }

        if len(selected) != 3:

            st.error(
                "Trebuie sa alegi 3 unitati diferite."
            )

        else:

            save_choice(
                student_id,
                option1,
                option2,
                option3
            )

            st.success(
                "Optiunile au fost salvate!"
            )




