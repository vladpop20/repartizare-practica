import streamlit as st


def load_css():
    st.markdown("""
<style>

.unit-card{
    background:#1b1b1b;
    border-radius:18px;
    padding:20px;
    margin-bottom:28px;
    border-left:6px solid #2196F3;
    box-shadow:0 6px 18px rgba(0,0,0,.35);
}

.unit-info{
    color:#bbbbbb;
    margin-top:8px;
    margin-bottom:15px;
    font-size:15px;
}

.option-title{
    font-size:20px;
    font-weight:bold;
    margin-top:8px;
    margin-bottom:10px;
}

.option-separator{
    height:1px;
    background:#444;
    margin-top:18px;
    margin-bottom:18px;
}

.student-card{
    border-radius:12px;
    padding:8px;
    margin-bottom:8px;
    text-align:center;
    font-weight:600;
    box-shadow:0 2px 5px rgba(0,0,0,.25);
}

.empty-card{
    border:2px dashed #666;
    border-radius:12px;
    padding:8px;
    margin-bottom:8px;
    text-align:center;
    color:#888;
}

.progress-text{
    font-size:18px;
    margin-bottom:8px;
    letter-spacing:1px;
}

</style>
""", unsafe_allow_html=True)


def render_unit_header(unit_name, unit):
    st.markdown(
        f"""
<div class="unit-card">
<h2>🏢 {unit_name}</h2>
<div class="unit-info">
👨 Capacitate băieți: <b>{unit["boys_capacity"]}</b>
&nbsp;&nbsp;&nbsp;
👩 Capacitate fete: <b>{unit["girls_capacity"]}</b>
</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_progress(occupied, capacity, icon):
    if capacity <= 0:
        return
    filled = min(occupied, capacity)
    empty = max(capacity - filled, 0)
    st.markdown(
        f'<div class="progress-text">{icon * filled}⬜{empty * "⬜"} {occupied}/{capacity}</div>'.replace("⬜0", ""),
        unsafe_allow_html=True,
    )


def render_student(student, gender, cautare=""):
    highlight = False

    if cautare:
        text = (
            student["last_name"] + " " + student["first_name"]
        ).lower()
        highlight = cautare in text

    if highlight:
        background = "#FFD54F"
        color = "black"
    elif gender == "B":
        background = "#1565C0"
        color = "white"
    else:
        background = "#C62828"
        color = "white"

    st.markdown(
        f"""
<div class="student-card"
style="background:{background};color:{color};">
{student["last_name"]}<br>
{student["first_name"]}<br>
{student["average"]}
</div>
""",
        unsafe_allow_html=True,
    )


def render_empty():
    st.markdown(
        """
<div class="empty-card">
Loc liber
</div>
""",
        unsafe_allow_html=True,
    )


def render_option(unit, option_key, title, cautare=""):
    badges = {
        "option1": "🟩",
        "option2": "🟨",
        "option3": "🟧",
    }

    st.markdown(
        f'<div class="option-title">{badges.get(option_key,"")} {title}</div>',
        unsafe_allow_html=True,
    )

    boys = unit[option_key]["boys"]
    girls = unit[option_key]["girls"]

    render_progress(len(boys), unit["boys_capacity"], "🟦")
    if unit["girls_capacity"] > 0:
        render_progress(len(girls), unit["girls_capacity"], "🟥")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🟦 Băieți")
        for student in boys:
            render_student(student, "B", cautare)
        for _ in range(max(unit["boys_capacity"] - len(boys), 0)):
            render_empty()

    with col2:
        st.markdown("#### 🟥 Fete")
        for student in girls:
            render_student(student, "F", cautare)
        for _ in range(max(unit["girls_capacity"] - len(girls), 0)):
            render_empty()

    st.markdown(
        '<div class="option-separator"></div>',
        unsafe_allow_html=True,
    )
