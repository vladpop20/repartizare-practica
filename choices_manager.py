from supabase_client import supabase


def save_choice(
    student_id,
    option1,
    option2,
    option3
):

    supabase.table("choices").upsert({

        "student_id": student_id,
        "option1": option1,
        "option2": option2,
        "option3": option3

    }).execute()

def get_choice(student_id):

    result = (
        supabase
        .table("choices")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )

    if len(result.data) == 0:
        return None

    return result.data[0]