import re

def load_units():

    units = {}

    with open("Unitati.txt", "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("\n\n")

    for section in sections:

        section = section.strip()

        if not section:
            continue

        lines = section.split("\n")

        specialization = lines[0].replace(":", "").strip()

        units[specialization] = []

        all_units = " ".join(lines[1:])

        entries = all_units.split(";")

        for entry in entries:

            entry = entry.strip()

            if not entry:
                continue

            boys = 0
            girls = 0

            boys_match = re.search(r'(\d+)B', entry)
            girls_match = re.search(r'(\d+)F', entry)

            if boys_match:
                boys = int(boys_match.group(1))

            if girls_match:
                girls = int(girls_match.group(1))

            clean_entry = re.sub(r'\d+B', '', entry)
            clean_entry = re.sub(r'\d+F', '', clean_entry)
            clean_entry = " ".join(clean_entry.split())

            units[specialization].append({
                "display": clean_entry,
                "boys": boys,
                "girls": girls
            })

    return units