import streamlit as st

st.set_page_config(
    page_title="Repartizare Practică",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

import sessions_manager as sm
from student_utils import get_gender
from choices_manager import save_choice, get_choice
from students_db import (
    get_student,
    login,
)
from monitor_utils import normalize_spec
from ui_utils import render_html


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
    if "active_session_id" not in st.session_state:
        st.session_state["active_session_id"] = None


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
            st.session_state["active_session_id"] = None
            st.rerun()


def render_options(student_record: dict, units: dict, active_session_id: str) -> None:
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
    saved_canonical = None
    if saved_choice and saved_choice.get("option1"):
        saved_canonical = saved_choice["option1"].strip().replace("UM ", "UM_")

    st.subheader("Selectare unitate de practică")

    # Calculăm în timp real locurile ocupate de ALȚI elevi din sesiunea curentă
    all_choices = sm.get_choices_for_session(active_session_id)
    all_students = sm.get_students_for_session(active_session_id)
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
            canonical_chosen = chosen_unit.strip().replace("UM ", "UM_")
            occupied_spots[canonical_chosen] = occupied_spots.get(canonical_chosen, 0) + 1

    # Găsim unitățile pentru specializarea curentă
    spec_units = []
    for s_name, u_list in units.items():
        if normalize_spec(s_name) == norm_spec:
            spec_units = u_list
            break

    available_units = []
    remaining_spots = {}

    for unit in spec_units:
        raw_unit_name = unit.get("unit_name", "")
        if not raw_unit_name:
            continue
        canonical_unit_name = raw_unit_name.strip().replace("UM ", "UM_")

        if gender == "B":
            capacity = unit.get("boys", 0)
            if capacity <= 0:
                continue  # Nu are locuri alocate pentru băieți
            occupied = occupied_spots.get(canonical_unit_name, 0)
            rem = capacity - occupied
            if rem > 0:
                available_units.append(unit)
                remaining_spots[canonical_unit_name] = rem
        elif gender == "F":
            capacity = unit.get("girls", 0)
            if capacity <= 0:
                continue  # Nu are locuri alocate pentru fete
            occupied = occupied_spots.get(canonical_unit_name, 0)
            rem = capacity - occupied
            if rem > 0:
                available_units.append(unit)
                remaining_spots[canonical_unit_name] = rem

    if saved_canonical:
        disp_saved = saved_canonical.replace("UM_", "UM ")
        render_html(
            f"""
<div class="saved-choice-banner">
    <div class="saved-choice-label">Opțiunea ta salvată în prezent</div>
    <div class="saved-choice-val">✅ {disp_saved}</div>
</div>
"""
        )

    if not available_units:
        st.warning("Nu mai există locuri disponibile pentru profilul tău.")
        return

    unit_canonical_keys = [
        unit.get("unit_name", "").strip().replace("UM ", "UM_")
        for unit in available_units
    ]

    default_index = 0
    if saved_canonical and saved_canonical in unit_canonical_keys:
        default_index = unit_canonical_keys.index(saved_canonical)

    def format_unit_label(u_key: str) -> str:
        disp = u_key.replace("UM_", "UM ")
        rem = remaining_spots.get(u_key, 0)
        if rem == 1:
            return f"{disp} (1 loc disponibil)"
        else:
            return f"{disp} ({rem} locuri disponibile)"

    selected_canonical = st.selectbox(
        "Alege unitatea dorită",
        unit_canonical_keys,
        index=default_index,
        format_func=format_unit_label,
        key=f"{student_id}_selected_unit",
    )

    if st.button("Salvează opțiunea", key=f"{student_id}_save_choice", use_container_width=True):
        save_choice(
            student_id,
            selected_canonical,
        )
        st.toast("Opțiunea a fost salvată cu succes!")
        st.rerun()


# ============================================================
# Init
# ============================================================
init_session_state()
load_app_css()

st.title("🎓 Repartizare practică")
st.caption("Sistem de simulare și alocare a stagiilor de practică")

active_session = sm.get_active_session()

# Verificăm dacă există o sesiune activă deschisă pentru selecție
if not active_session:
    render_html("""
<div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 14px; padding: 28px 20px; text-align: center; margin-top: 20px;">
    <div style="font-size: 2.2rem; margin-bottom: 12px;">🔒</div>
    <div style="font-size: 1.25rem; font-weight: 700; color: #f87171; margin-bottom: 8px;">Repartizarea este în prezent OPRITĂ</div>
    <div style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; max-width: 480px; margin: 0 auto;">
        Nicio sesiune de repartiție nu este activă în acest moment pentru alegerea opțiunilor de către elevi.<br><br>
        Puteți consulta situația alocărilor și arhiva opțiunilor accesând pagina 
        <strong style="color: #60a5fa;">„Situatia in timp real”</strong> din meniul lateral.
    </div>
</div>
""")
    st.stop()

# Banner sesiune activă
render_html(f"""
<div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.08) 100%); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
    <div>
        <span style="color: #6ee7b7; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;">🟢 Sesiune Deschisă</span>
        <div style="color: #ffffff; font-weight: 700; font-size: 1.05rem; margin-top: 2px;">{active_session.get('title', active_session.get('name', 'Sesiune activă'))}</div>
    </div>
    <span style="background: rgba(16, 185, 129, 0.2); color: #a7f3d0; font-size: 0.8rem; padding: 4px 10px; border-radius: 16px; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.3);">
        {active_session.get('category', 'MM')} • {active_session.get('practice_type', '')} ({active_session.get('year', '')})
    </span>
</div>
""")

active_session_id = active_session["id"]
session_students = sm.get_students_for_session(active_session_id)
session_units = sm.get_session_units_dict(active_session_id)

# ============================================================
# Already authenticated: hide login entirely
# ============================================================
if st.session_state["authenticated"]:
    # Dacă sesiunea activă s-a schimbat între timp, resetăm autentificarea
    if st.session_state.get("active_session_id") != active_session_id:
        st.session_state["authenticated"] = False
        st.session_state["student_id"] = None
        st.session_state["active_session_id"] = active_session_id
        st.rerun()

    student_id = st.session_state.get("student_id")

    if not student_id:
        st.session_state["authenticated"] = False
        st.session_state["student_id"] = None
        st.rerun()

    student_record = get_student(student_id)

    if not student_record:
        st.error("Contul tău nu a fost găsit în baza de date. Te delogăm.")
        st.session_state["authenticated"] = False
        st.session_state["student_id"] = None
        st.rerun()

    render_logout_header(student_record)
    render_options(student_record, session_units, active_session_id)

# ============================================================
# Not authenticated: autentificare elev
# ============================================================
else:
    if not session_students:
        st.info("⚠️ Nu există elevi înregistrați pentru această sesiune de practică.")
        st.stop()

    # Grupăm elevii pe specializări
    students_by_spec = {}
    for s in session_students:
        spec_name = s.get("specialization", "General")
        if spec_name not in students_by_spec:
            students_by_spec[spec_name] = []
        students_by_spec[spec_name].append(s)

    for spec_name in students_by_spec:
        students_by_spec[spec_name].sort(key=lambda x: x.get("average", 0.0), reverse=True)

    specializare = st.selectbox(
        "Selectează specializarea",
        list(students_by_spec.keys()),
        format_func=lambda s: f"{s} ({len(students_by_spec[s])} elevi)",
    )

    elevi = students_by_spec[specializare]

    student_options_map = {
        f"{s['first_name']} {s['last_name']} ({s['average']:.2f})": s
        for s in elevi
    }

    elev_selectat = st.selectbox(
        "Selectează numele",
        list(student_options_map.keys()),
    )

    student_record = student_options_map[elev_selectat]
    student_id = student_record["id"]

    st.success(f"Ai selectat: {elev_selectat}")

    username = (
        student_record.get("username")
        or f"{student_record['last_name'].lower().strip()}.{student_record['first_name'].lower().strip()}"
    )

    st.subheader("Autentificare")
    st.info(f"Username: {username}")

    with st.form(key=f"{student_id}_login_form"):
        password = st.text_input(
            "Parola (implicit: 123456 sau ultimele 6 cifre CNP)",
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
                st.session_state["active_session_id"] = active_session_id
                st.toast("Autentificat cu succes!")
                st.rerun()
            else:
                st.error("Parolă incorectă.")
