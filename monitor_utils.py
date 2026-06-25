# raise Exception("SE EXECUTA MONITOR_UTILS")

def build_monitor(
    students,
    choices,
    units
):

    monitor = {}

    #
    # Construim structura:
    #
    # monitor
    #   └── specializare
    #         └── unitate
    #

    for unit in units:

        specialization = unit["specialization"]

        if specialization not in monitor:

            monitor[specialization] = {}

        monitor[specialization][
            unit["unit_name"]
        ] = {

            "boys_capacity": unit["boys"],

            "girls_capacity": unit["girls"],

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

    students_map = {}

    for student in students:

        students_map[
            student["id"]
        ] = student

    #
    # completăm monitorul
    #

    for choice in choices:

        student = students_map.get(
            choice["student_id"]
        )

        if student is None:
            continue

        specialization = student["specialization"]

        options = [

            ("option1", choice["option1"]),

            ("option2", choice["option2"]),

            ("option3", choice["option3"])

        ]

        for option_name, unit_name in options:

            if (
                specialization
                not in monitor
            ):
                continue

            if (
                unit_name
                not in monitor[specialization]
            ):
                continue

            if student["gender"] == "B":

                monitor[
                    specialization
                ][
                    unit_name
                ][
                    option_name
                ][
                    "boys"
                ].append(student)

            else:

                monitor[
                    specialization
                ][
                    unit_name
                ][
                    option_name
                ][
                    "girls"
                ].append(student)

    print("CHEI MONITOR:")
    print(monitor.keys())

    return monitor