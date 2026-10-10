import streamlit as st

from parser_students import load_students
from parser_units import load_units
from student_utils import get_gender
from choices_manager import save_choice, get_choice
from students_db import (
    get_student,
    login,
)
from supabase_db import (
    get_all_choices,
    get_all_students,
)
from monitor_utils import normalize_spec

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

    st.subheader("Selectare unitate de practică")

    # Calculăm în timp real locurile ocupate de ALȚI elevi
    all_choices = get_all_choices()
    all_students = get_all_students()
    students_map = {s["id"]: s for s in all_students}

    norm_spec = normalize_spec(specializare)

    occupied_spots = {}
    for c in all_choices:
        # Opțiunea elevului curent nu îi blochează propriul loc
        if c["student_id"] == student_id:
            continue
        chosen_unit = c.get("option1")
        if not chosen_unit:
            continue
        other_student = students_map.get(c["student_id"])
        if not other_student:
            continue
        if (
            normalize_spec(other_student.get("specialization", "")) == norm_spec
            and other_student.get("gender") == gender
        ):
            occupied_spots[chosen_unit] = occupied_spots.get(chosen_unit, 0) + 1

    # Găsim unitățile pentru specializarea curentă
    spec_units = []
    for s_name, u_list in units.items():
        if normalize_spec(s_name) == norm_spec:
            spec_units = u_list
            break

    available_units = []
    remaining_spots = {}

    for unit in spec_units:
        unit_name = unit.get("display", unit.get("unit_name", ""))
        if not unit_name:
            continue

        if gender == "B":
            capacity = unit.get("boys", 0)
            if capacity <= 0:
                continue  # Nu are locuri alocate pentru băieți
            occupied = occupied_spots.get(unit_name, 0)
            rem = capacity - occupied
            if rem > 0:
                available_units.append(unit)
                remaining_spots[unit_name] = rem
        elif gender == "F":
            capacity = unit.get("girls", 0)
            if capacity <= 0:
                continue  # Nu are locuri alocate pentru fete
            occupied = occupied_spots.get(unit_name, 0)
            rem = capacity - occupied
            if rem > 0:
                available_units.append(unit)
                remaining_spots[unit_name] = rem

    if saved_choice and saved_choice.get("option1"):
        st.info(f"Opțiunea ta salvată în prezent: **{saved_choice['option1']}**")

    if not available_units:
        st.warning("Nu mai există locuri disponibile pentru profilul tău.")
        return

    unit_names = [
        unit.get("display", unit.get("unit_name", ""))
        for unit in available_units
    ]

    default_index = 0
    if saved_choice and saved_choice.get("option1") in unit_names:
        default_index = unit_names.index(saved_choice["option1"])

    selected_unit = st.selectbox(
        "Alege unitatea dorită",
        unit_names,
        index=default_index,
        format_func=lambda u: (
            f"{u} ({remaining_spots.get(u, 1)} loc disponibil)"
            if remaining_spots.get(u, 1) == 1
            else f"{u} ({remaining_spots.get(u, 1)} locuri disponibile)"
        ),
        key=f"{student_id}_selected_unit",
    )

    if st.button("Salvează opțiunea", key=f"{student_id}_save_choice", use_container_width=True):
        save_choice(
            student_id,
            selected_unit,
        )
        st.toast("Opțiunea a fost salvată cu succes!")
        st.rerun()


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
        format_func=lambda s: f"{s} ({len(students[s])} elevi)",
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

    username = (
        student_record.get("username")
        or f"{last_name.lower().strip()}.{first_name.lower().strip()}"
    )

    st.subheader("Autentificare")
    st.info(f"Username: {username}")

    with st.form(key=f"{student_id}_login_form"):
        password = st.text_input(
            "Parola (ultimele 6 cifre din CNP)",
            type="password",
            key=f"{student_id}_login_password",
        )

        if st.form_submit_button("Login", use_container_width=True):
            if login(
                student_id,
                username,
                password.strip(),
            ):
                st.session_state["authenticated"] = True
                st.session_state["student_id"] = student_id
                st.toast("Autentificat.")
                st.rerun()
            else:
                st.error("Parolă incorectă.")
