from female_students import *

def get_gender(specialization, first_name, last_name):

    student_name = f"{first_name}, {last_name}"

    if specialization == "Comunicatii":
        return "F" if student_name in female_students_comunicatii else "B"

    if specialization == "Aparare Cibernetica":
        return "F" if student_name in female_students_aparare_cibernetica else "B"

    if specialization == "Securitate Militara":
        return "F" if student_name in female_students_securitate_militara else "B"

    if specialization == "Tehnologia Informatiei":
        return "F" if student_name in female_students_tehnologia_informatiei else "B"

    return "B"