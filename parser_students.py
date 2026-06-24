def load_students():
    students = {}

    with open("ListaEleviSortata.txt", "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("\n\n")

    for section in sections:

        section = section.strip()

        if not section:
            continue

        lines = section.split("\n")

        specialization = lines[0].replace(":", "").strip()

        students[specialization] = []

        all_students = " ".join(lines[1:])

        entries = all_students.split(";")

        for entry in entries:

            entry = entry.strip()

            if not entry:
                continue

            parts = [p.strip() for p in entry.split(",")]

            if len(parts) < 3:
                continue

            last_name = parts[0]
            first_name = parts[1]

            try:
                average = float(parts[2].replace(",", "."))
            except:
                continue

            students[specialization].append(
                (last_name, first_name, average)
            )

    return students