from supabase_client import supabase

def update_students_credentials():
    print("Preia lista de elevi din Supabase...")
    response = supabase.table("students").select("id, last_name, first_name").execute()
    students = response.data

    print(f"S-au gasit {len(students)} elevi. Se actualizeaza credentialele...")

    updated_count = 0
    for student in students:
        student_id = student["id"]
        last_name = student["last_name"]
        first_name = student["first_name"]

        username = f"{last_name.lower().strip()}.{first_name.lower().strip()}"
        password_hash = "123456"

        supabase.table("students").update({
            "username": username,
            "password_hash": password_hash
        }).eq("id", student_id).execute()

        updated_count += 1
        if updated_count % 25 == 0 or updated_count == len(students):
            print(f"Progres: {updated_count}/{len(students)} elevi actualizati...")

    print(f"Finalizat cu succes! {updated_count} elevi au primit username si parola '123456'.")

if __name__ == "__main__":
    update_students_credentials()

