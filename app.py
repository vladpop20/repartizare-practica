import streamlit as st

st.set_page_config(
    page_title="Repartizare Practică",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

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
from ui_utils import render_html

SPECIALIZATION_CODES = {
    "Aparare Cibernetica": "AC",
    "Securitate Militara": "SM",
    "Comunicatii": "COM",
    "Tehnologia Informatiei": "TI",
}


def load_app_css() -> None:
    render_html("""
<style>
/* Centrare și limitare lățime container pe laptop/desktop, adaptiv pe mobil */
.block-container {
    max-width: 680px !important;
    padding-top: 2rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    margin: 0 auto !important;
}

/* Card profil elev conectat */
.student-profile-header {
    background: linear-gradient(135deg, #1e293b 0%, #172554 100%);
    border: 1px solid rgba(59, 130, 246, 0.4);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}

.profile-greeting {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}

.profile-spec-badge {
    display: inline-block;
    background: rgba(59, 130, 246, 0.25);
    color: #93c5fd;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 20px;
    border: 1px solid rgba(59, 130, 246, 0.35);
}

/* Banner opțiune salvată */
.saved-choice-banner {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.08) 100%);
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 12px;
    padding: 14px 18px;
    margin-top: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.saved-choice-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #6ee7b7;
    margin-bottom: 4px;
}

.saved-choice-val {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
}

/* Butoane primare */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease-in-out !important;
}

/* Formulare și carduri */
div[data-testid="stForm"] {
    background: rgba(35, 42, 53, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    padding: 22px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
}

/* Responsivitate pentru telefoane (>= 6.5 inchi) */
@media (max-width: 640px) {
    .block-container {
        padding-top: 1.25rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    h1 {
        font-size: 1.7rem !important;
    }
    .profile-greeting {
        font-size: 1.05rem;
    }
    div[data-testid="stForm"] {
        padding: 16px !important;
    }
}
</style>
""")


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
    left, right = st.columns([4, 1])

    with left:
        render_html(
            f"""
<div class="student-profile-header">
    <div class="profile-greeting">👋 Salut, {student_record['first_name']} {student_record['last_name']}!</div>
    <span class="profile-spec-badge">Specializare: {student_record['specialization']}</span>
</div>
"""
        )

    with right:
        st.write("")
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
        render_html(
            f"""
<div class="saved-choice-banner">
    <div class="saved-choice-label">Opțiunea ta salvată în prezent</div>
    <div class="saved-choice-val">✅ {saved_choice['option1']}</div>
</div>
"""
        )

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
load_app_css()

students = load_students()
units = load_units()

st.title("🎓 Repartizare practică")
st.caption("Sistem de simulare și alocare a stagiilor de practică")

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
