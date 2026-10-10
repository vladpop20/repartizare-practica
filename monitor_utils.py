def normalize_spec(spec: str) -> str:
    if not spec:
        return ""
    mapping = {
        "comunicatii": "Comunicatii",
        "aparare cibernetica": "Aparare Cibernetica",
        "securitate militara": "Securitate Militara",
        "tehnologia informatiei": "Tehnologia Informatiei",
    }
    return mapping.get(spec.strip().lower(), spec.strip())


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

        unit_name = choice.get("option1")

        if not unit_name or unit_name not in monitor[specialization]:

            continue

        gender = (

            "boys"

            if student["gender"] == "B"

            else "girls"

        )

        monitor[
            specialization
        ][
            unit_name
        ][
            "option1"
        ][
            gender
        ].append(student)

    return monitor