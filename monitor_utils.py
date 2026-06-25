def build_monitor(
    students,
    choices,
    units
):
    """
    Structura rezultată:

    monitor = {

        "Comunicatii": {

            "UM_01308 Bucuresti SMFT": {

                "boys_capacity": 1,
                "girls_capacity": 1,

                "option1": {
                    "boys": [],
                    "girls": []
                },

                "option2": {
                    "boys": [],
                    "girls": []
                },

                "option3": {
                    "boys": [],
                    "girls": []
                }

            }

        }

    }
    """

    monitor = {}

    #
    # Construim structura unităților
    #

    for unit in units:

        specialization = unit["specialization"]

        if specialization not in monitor:

            monitor[specialization] = {}

        #
        # IMPORTANT:
        #
        # Nu sortăm unitățile.
        #
        # Ordinea rămâne EXACT cea din baza de date,
        # adică aceeași ordine în care au fost încărcate
        # din Unitati.txt.
        #

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

            },

            "option2": {

                "boys": [],
                "girls": []

            },

            "option3": {

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

        specialization = student["specialization"]

        if specialization not in monitor:

            continue

        options = [

            ("option1", choice["option1"]),

            ("option2", choice["option2"]),

            ("option3", choice["option3"])

        ]

        for option_name, unit_name in options:

            if unit_name not in monitor[specialization]:

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
                option_name
            ][
                gender
            ].append(student)

    return monitor