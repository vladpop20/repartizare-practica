def normalize_spec(spec: str) -> str:
    if not spec:
        return ""
    s = spec.strip().lower()
    s = s.replace("ă", "a").replace("â", "a").replace("î", "i").replace("ș", "s").replace("ş", "s").replace("ț", "t").replace("ţ", "t")
    s = s.replace(".", " ").replace("-", " ").strip()

    if s in ["ti", "it"] or any(k in s for k in ["teh", "info", "informat"]):
        return "Tehnologia Informatiei"
    if s in ["ac"] or any(k in s for k in ["ciber", "aparare"]):
        return "Aparare Cibernetica"
    if s in ["sm"] or "securitat" in s:
        return "Securitate Militara"
    if s in ["com"] or "comunic" in s:
        return "Comunicatii"

    mapping = {
        "comunicatii": "Comunicatii",
        "aparare cibernetica": "Aparare Cibernetica",
        "securitate militara": "Securitate Militara",
        "tehnologia informatiei": "Tehnologia Informatiei",
    }
    return mapping.get(s, spec.strip())


def build_monitor(
    students,
    choices,
    units
):
    monitor = {}

    #
    # Construim structura unităților
    #

    for unit in units:

        specialization = normalize_spec(unit["specialization"])

        if specialization not in monitor:

            monitor[specialization] = {}

        monitor[
            specialization
        ][
            unit["unit_name"]
        ] = {

            "boys_capacity":
                unit["boys"],

            "girls_capacity":
                unit["girls"],

            "option1": {

                "boys": [],
                "girls": []

            }

        }

    #
    # id elev -> elev
    #

    students_map = {

        student["id"]: student

        for student in students

    }

    #
    # Introducem elevii
    #

    for choice in choices:

        student = students_map.get(

            choice["student_id"]

        )

        if student is None:

            continue

        specialization = normalize_spec(student["specialization"])

        if specialization not in monitor:

            continue

        raw_unit_name = choice.get("option1")
        if not raw_unit_name:
            continue

        target_unit = None
        if raw_unit_name in monitor[specialization]:
            target_unit = raw_unit_name
        else:
            canonical_u = raw_unit_name.replace("UM ", "UM_")
            display_u = raw_unit_name.replace("UM_", "UM ")
            if canonical_u in monitor[specialization]:
                target_unit = canonical_u
            elif display_u in monitor[specialization]:
                target_unit = display_u

        if not target_unit:
            continue

        gender = (
            "boys"
            if student["gender"] == "B"
            else "girls"
        )

        monitor[
            specialization
        ][
            target_unit
        ][
            "option1"
        ][
            gender
        ].append(student)

    return monitor