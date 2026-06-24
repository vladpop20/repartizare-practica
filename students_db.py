from supabase_client import supabase


def get_student(student_id):

    result = (
        supabase
        .table("students")
        .select("*")
        .eq("id", student_id)
        .execute()
    )

    print(result)

    if len(result.data) == 0:
        return None

    return result.data[0]


def create_account(
    student_id,
    username,
    password
):

    supabase.table("students").update({
        "username": username,
        "password_hash": password
    }).eq("id", student_id).execute()


def login(
    student_id,
    username,
    password
):

    student = get_student(student_id)

    if not student:
        return False

    return (
        student["username"] == username
        and
        student["password_hash"] == password
    )