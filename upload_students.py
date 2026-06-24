from parser_students import load_students
from student_utils import get_gender
from supabase_client import supabase

students = load_students()

specialization_codes = {
    "Aparare Cibernetica": "AC",
    "Securitate Militara": "SM",
    "Comunicatii": "COM",
    "Tehnologia Informatiei": "TI"
}

count = 0

for specialization, elevi in students.items():

    for last_name, first_name, average in elevi:

        student_id = (
            specialization_codes[specialization]
            + "_"
            + last_name.replace(" ", "_")
            + "_"
            + first_name.replace(" ", "_")
        )

        gender = get_gender(
            specialization,
            first_name,
            last_name
        )

        response = supabase.table("students").upsert({
            "id": student_id,
            "specialization": specialization,
            "last_name": last_name,
            "first_name": first_name,
            "average": average,
            "gender": gender
        }).execute()

        count += 1

print(f"Uploaded {count} students")

total = 0

for specializare, elevi in students.items():
    print(specializare, len(elevi))
    total += len(elevi)

print("TOTAL =", total)