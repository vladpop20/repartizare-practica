# upload_units.py

from parser_units import load_units
from supabase_client import supabase

units = load_units()

count = 0

for specialization, unit_list in units.items():

    for unit in unit_list:

        supabase.table("units").insert({
            "specialization": specialization,
            "unit_name": unit["display"],
            "boys": unit["boys"],
            "girls": unit["girls"]
        }).execute()

        count += 1

print(f"Uploaded {count} units")