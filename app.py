import streamlit as st

from parser_students import load_students
from parser_units import load_units
from student_utils import get_gender
from choices_manager import save_choice, get_choice
from students_db import (
    get_student,
    create_account,
    login,
)

SPECIALIZATION_CODES = {
    "Aparare Cibernetica": "AC",
    "Securitate Militara": "SM",
    "Comunicatii": "COM",
    "Tehnologia Informatiei": "TI",
}


def init_session_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "student_id" not in st.session_state:
        st.session_state["student_id"] = None


def make_student_id(specializare: str, last_name: str, first_name: str) -> str:
    return (
        SPECIALIZATION_CODES[specializare]
        + "_"
        + last_name.replace(" ", "_")
        + "_"
        + first_name.replace(" ", "_")
    )


def render_logout_header(student_record: dict) -> None:
    left, right = st.columns([5, 1])

    with left:
        st.success(
            f"👋 Salut, {student_record['first_name']} {student_record['last_name']}!"
        )
        st.caption(
            f"Specializare: {student_record['specialization']}"
        )

    with right:
        if st.button("Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["student_id"] = None
            st.rerun()


def render_options(student_record: dict, units: dict) -> None:
    student_id = student_record["id"]
    specializare = student_record["specialization"]
    last_name = student_record["last_name"]
    first_name = student_record["first_name"]
    gender = student_record.get("gender") or get_gender(
        specializare,
        first_name,
        last_name,
    )

    saved_choice = get_choice(student_id)

    st.subheader("Unitati disponibile")

    available_units = []
    for unit in units.get(specializare, []):
        if gender == "B" and unit["boys"] > 0:
            available_units.append(unit)
        elif gender == "F" and unit["girls"] > 0:
            available_units.append(unit)

    if not available_units:
        st.warning("Nu exista unitati disponibile pentru specializarea ta.")
        return

    unit_names = [
        unit.get("display", unit.get("unit_name", ""))
        for unit in available_units
        if unit.get("display", unit.get("unit_name", ""))
    ]

    if not unit_names:
        st.warning("Nu exista unitati valide de afisat.")
        return

    default1 = 0
    default2 = 0
    default3 = 0

    if saved_choice:
        if saved_choice.get("option1") in unit_names:
            default1 = unit_names.index(saved_choice["option1"])
        if saved_choice.get("option2") in unit_names:
            default2 = unit_names.index(saved_choice["option2"])
        if saved_choice.get("option3") in unit_names:
            default3 = unit_names.index(saved_choice["option3"])

    option1 = st.selectbox(
        "Optiunea 1",
        unit_names,
        index=default1,
        key=f"{student_id}_option1",
    )

    option2 = st.selectbox(
        "Optiunea 2",
        unit_names,
        index=default2,
        key=f"{student_id}_option2",
    )

    option3 = st.selectbox(
        "Optiunea 3",
        unit_names,
        index=default3,
        key=f"{student_id}_option3",
    )

    if st.button("Salveaza optiunile", key=f"{student_id}_save_choices"):
        selected = {option1, option2, option3}

        if len(selected) != 3:
            st.error("Trebuie sa alegi 3 unitati diferite.")
        else:
            save_choice(
                student_id,
                option1,
                option2,
                option3,
            )
            st.toast("Optiunile au fost salvate.")


# ============================================================
# Init
# ============================================================
init_session_state()

students = load_students()
units = load_units()

st.title("Simulare repartizare practica")

# ============================================================
# Already authenticated: hide login entirely
# ============================================================
if st.session_state["authenticated"]:
    student_id = st.session_state.get("student_id")

    if not student_id:
        st.session_state["authenticated"] = False
        st.session_state["student_id"] = None
        st.rerun()

    student_record = get_student(student_id)

    if not student_record:
        st.error("Contul tau nu a fost gasit in baza de date. Te delogam.")
        st.session_state["authenticated"] = False
        st.session_state["student_id"] = None
        st.rerun()

    render_logout_header(student_record)
    render_options(student_record, units)

# ============================================================
# Not authenticated: create account / login
# ============================================================
else:
    specializare = st.selectbox(
        "Selecteaza specializarea",
        list(students.keys()),
    )

    elevi = students[specializare]

    nume_afisate = [
        f"{prenume} {nume} ({medie})"
        for nume, prenume, medie in elevi
    ]

    elev_selectat = st.selectbox(
        "Selecteaza numele",
        nume_afisate,
    )

    st.success(f"Ai selectat: {elev_selectat}")

    selected_student = None
    for nume, prenume, medie in elevi:
        if f"{prenume} {nume} ({medie})" == elev_selectat:
            selected_student = (nume, prenume, medie)
            break

    if selected_student is None:
        st.error("Elevul selectat nu a fost gasit.")
        st.stop()

    last_name, first_name, average = selected_student

    student_id = make_student_id(specializare, last_name, first_name)
    student_record = get_student(student_id)

    if not student_record:
        st.error("Elevul nu exista in baza de date students.")
        st.stop()

    saved_choice = get_choice(student_id)

    gender = student_record.get("gender") or get_gender(
        specializare,
        first_name,
        last_name,
    )

    st.info(f"Gen: {gender}")

    for index, (nume, prenume, medie) in enumerate(elevi, start=1):
        if f"{prenume} {nume} ({medie})" == elev_selectat:
            st.info(f"Pozitie in clasament: {index}")
            st.info(f"Media: {medie}")
            break

    st.write(f"Numar elevi: {len(elevi)}")

    st.subheader("Autentificare")

    if not student_record.get("username"):
        st.info("Nu ai cont. Creeaza unul.")

        generated_username = (
            last_name.lower()
            + "."
            + first_name.lower()
        )

        st.info(f"Username-ul tau va fi: {generated_username}")

        password = st.text_input(
            "Parola",
            type="password",
            key=f"{student_id}_create_password",
        )

        confirm_password = st.text_input(
            "Confirma parola",
            type="password",
            key=f"{student_id}_create_confirm_password",
        )

        if st.button("Creeaza cont", key=f"{student_id}_create_account"):
            if password != confirm_password:
                st.error("Parolele nu coincid")
            else:
                create_account(
                    student_id,
                    generated_username,
                    password,
                )
                st.session_state["authenticated"] = True
                st.session_state["student_id"] = student_id
                st.toast("Cont creat. Te autentificam...")
                st.rerun()

    else:
        st.info(f"Username: {student_record['username']}")

        password = st.text_input(
            "Parola",
            type="password",
            key=f"{student_id}_login_password",
        )

        if st.button("Login", key=f"{student_id}_login"):
            if login(
                student_id,
                student_record["username"],
                password,
            ):
                st.session_state["authenticated"] = True
                st.session_state["student_id"] = student_id
                st.toast("Autentificat.")
                st.rerun()
            else:
                st.error("Date incorecte")
