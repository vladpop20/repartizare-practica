from supabase_client import supabase


def get_all_choices():

    result = (
        supabase
        .table("choices")
        .select("*")
        .execute()
    )

    return result.data


def get_all_students():

    result = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    return result.data

def get_all_units():

    result = (
        supabase
        .table("units")
        .select("*")
        .execute()
    )

    return result.data