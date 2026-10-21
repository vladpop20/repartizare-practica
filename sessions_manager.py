import json
import re
from datetime import datetime, timezone
import pandas as pd
from supabase_client import supabase
from monitor_utils import normalize_spec

DEFAULT_SESSION_ID = "mm_2025_2027_p1"

DEFAULT_SESSION = {
    "id": DEFAULT_SESSION_ID,
    "name": "Maiștri Militari - Promoția 2025-2027 - Practica 1 (2026)",
    "category": "Maiștri Militari",
    "promotion": "2025-2027",
    "practice_type": "Practica 1",
    "year": 2026,
    "title": "Maiștri Militari - Promoția 2025-2027 - Practica 1 (2026)",
    "is_active": True,
    "created_at": "2026-06-24T12:00:00Z"
}


def is_default_session(session_id: str | None) -> bool:
    """Verifică dacă ID-ul reprezintă sesiunea de bază (fără prefixe în BD)."""
    return session_id in (DEFAULT_SESSION_ID, "mm_2024_2026_p1", None)


def _read_config(key: str, default=None):
    try:
        res = (
            supabase.table("allocations")
            .select("allocated_unit")
            .eq("student_id", key)
            .execute()
        )
        if res.data and len(res.data) > 0:
            val = res.data[0].get("allocated_unit")
            if val:
                return json.loads(val)
    except Exception as e:
        print(f"Error reading config key {key}: {e}")
    return default


def _write_config(key: str, data) -> bool:
    try:
        payload = {
            "student_id": key,
            "allocated_unit": json.dumps(data, ensure_ascii=False),
            "allocation_rank": 0
        }
        supabase.table("allocations").upsert(payload).execute()
        return True
    except Exception as e:
        print(f"Error writing config key {key}: {e}")
        return False


def get_all_sessions() -> list[dict]:
    """Returnează lista tuturor sesiunilor configurate, migrând automat la Promoția 2025-2027 dacă este necesar."""
    sessions = _read_config("__APP_CONFIG_SESSIONS__")
    updated = False
    if not sessions:
        sessions = [DEFAULT_SESSION]
        updated = True
    else:
        for s in sessions:
            if s.get("id") in ("mm_2024_2026_p1", DEFAULT_SESSION_ID):
                if s.get("promotion") != "2025-2027" or "2024-2026" in s.get("title", ""):
                    s["id"] = DEFAULT_SESSION_ID
                    s["promotion"] = "2025-2027"
                    s["name"] = "Maiștri Militari - Promoția 2025-2027 - Practica 1 (2026)"
                    s["title"] = "Maiștri Militari - Promoția 2025-2027 - Practica 1 (2026)"
                    updated = True
    if updated:
        _write_config("__APP_CONFIG_SESSIONS__", sessions)
    return sessions


def get_session_by_id(session_id: str) -> dict | None:
    sessions = get_all_sessions()
    for s in sessions:
        if s["id"] == session_id:
            return s
    return None


def get_active_session() -> dict | None:
    """Returnează sesiunea activă pentru selectare în app.py."""
    sessions = get_all_sessions()
    for s in sessions:
        if s.get("is_active"):
            return s
    return None


def set_active_session(session_id: str | None) -> bool:
    """Setează sesiunea activă (sau None pentru a opri repartizarea în app.py)."""
    sessions = get_all_sessions()
    for s in sessions:
        s["is_active"] = (s["id"] == session_id)
    return _write_config("__APP_CONFIG_SESSIONS__", sessions)


def create_session(category: str, promotion: str, practice_type: str, year: int) -> dict:
    """Creează o nouă sesiune de practică."""
    sessions = get_all_sessions()

    # Generăm un slug curat pentru ID
    cat_code = "mm" if "mai" in category.lower() else "so"
    promo_clean = re.sub(r"[^\w]", "_", promotion).strip("_").lower()
    promo_clean = re.sub(r"_+", "_", promo_clean)
    pract_clean = "p1" if "1" in str(practice_type) else "p2"
    base_id = f"{cat_code}_{promo_clean}_{pract_clean}"

    # Ne asigurăm de unicitate
    final_id = base_id
    counter = 1
    existing_ids = {s["id"] for s in sessions}
    while final_id in existing_ids:
        final_id = f"{base_id}_{counter}"
        counter += 1

    title = f"{category} - Promoția {promotion} - {practice_type} ({year})"

    new_sess = {
        "id": final_id,
        "category": category,
        "promotion": promotion,
        "practice_type": practice_type,
        "year": int(year),
        "title": title,
        "is_active": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    sessions.append(new_sess)
    _write_config("__APP_CONFIG_SESSIONS__", sessions)
    return new_sess


def delete_session(session_id: str) -> bool:
    """Șterge o sesiune (sesiunea implicită inițială nu poate fi ștearsă)."""
    if is_default_session(session_id):
        return False
    sessions = get_all_sessions()
    sessions = [s for s in sessions if s["id"] != session_id]
    _write_config("__APP_CONFIG_SESSIONS__", sessions)

    # Curățăm datele asociate din Supabase
    try:
        supabase.table("students").delete().like("id", f"{session_id}__%").execute()
        supabase.table("units").delete().like("specialization", f"{session_id}__%").execute()
        supabase.table("choices").delete().like("student_id", f"{session_id}__%").execute()
        supabase.table("allocations").delete().in_("student_id", [
            f"__SESSION_STUDENTS__{session_id}",
            f"__SESSION_UNITS__{session_id}"
        ]).execute()
    except Exception as e:
        print(f"Eroare curățare date sesiune {session_id}: {e}")

    return True


# ============================================================
# Elevi per Sesiune
# ============================================================
def get_students_for_session(session_id: str) -> list[dict]:
    """Returnează elevii pentru o sesiune specificată."""
    if is_default_session(session_id):
        # Sesiunea implicită folosește elevii fără prefix
        res = supabase.table("students").select("*").execute()
        students = [s for s in (res.data or []) if "__" not in s["id"]]
        return students

    # Pentru alte sesiuni: căutăm după prefixul sesiunii
    res = supabase.table("students").select("*").like("id", f"{session_id}__%").execute()
    students = res.data or []

    # Curățăm specializarea pentru afișare dacă are prefix
    for s in students:
        spec = s.get("specialization", "")
        if "__" in spec:
            s["specialization"] = spec.split("__", 1)[1]

    return students


def save_students_for_session(session_id: str, new_students: list[dict]) -> int:
    """Salvează sau actualizează elevii pentru o sesiune."""
    if not new_students:
        return 0

    records = []
    for s in new_students:
        raw_id = s.get("id")
        if not is_default_session(session_id):
            s_id = f"{session_id}__{raw_id}" if not raw_id.startswith(f"{session_id}__") else raw_id
            spec_val = f"{session_id}__{normalize_spec(s.get('specialization', ''))}"
        else:
            s_id = raw_id
            spec_val = normalize_spec(s.get("specialization", ""))

        records.append({
            "id": s_id,
            "specialization": spec_val,
            "last_name": s.get("last_name", "").strip(),
            "first_name": s.get("first_name", "").strip(),
            "average": float(s.get("average", 0.0)),
            "gender": (s.get("gender") or "B").strip().upper()[:1],
            "username": s.get("username", "").strip(),
            "password_hash": s.get("password_hash", "123456").strip()
        })

    # Ștergem eventualii elevi vechi ai sesiunii pentru reîncărcare curată dacă nu e default
    if not is_default_session(session_id):
        supabase.table("students").delete().like("id", f"{session_id}__%").execute()

    # Inserăm în batch-uri de 50
    inserted = 0
    batch_size = 50
    for i in range(0, len(records), batch_size):
        chunk = records[i:i + batch_size]
        supabase.table("students").upsert(chunk).execute()
        inserted += len(chunk)

    # Salvăm și copia cache în allocations
    _write_config(f"__SESSION_STUDENTS__{session_id}", records)

    return inserted


# ============================================================
# Unități per Sesiune
# ============================================================
def get_units_for_session(session_id: str) -> list[dict]:
    """Returnează unitățile de practică pentru o sesiune specificată."""
    if is_default_session(session_id):
        res = supabase.table("units").select("*").execute()
        units = [u for u in (res.data or []) if "__" not in u.get("specialization", "")]
        return units

    res = supabase.table("units").select("*").like("specialization", f"{session_id}__%").execute()
    units = res.data or []

    # Curățăm specializarea de prefix pentru UI
    for u in units:
        spec = u.get("specialization", "")
        if "__" in spec:
            u["specialization"] = spec.split("__", 1)[1]

    return units


def save_units_for_session(session_id: str, new_units: list[dict]) -> int:
    """Salvează unitățile pentru o sesiune."""
    if not new_units:
        return 0

    records = []
    for u in new_units:
        raw_spec = normalize_spec(u.get("specialization", ""))
        spec_val = f"{session_id}__{raw_spec}" if not is_default_session(session_id) else raw_spec

        records.append({
            "specialization": spec_val,
            "unit_name": u.get("unit_name", "").strip(),
            "boys": int(u.get("boys", 0)),
            "girls": int(u.get("girls", 0))
        })

    if not is_default_session(session_id):
        supabase.table("units").delete().like("specialization", f"{session_id}__%").execute()

    inserted = 0
    batch_size = 50
    for i in range(0, len(records), batch_size):
        chunk = records[i:i + batch_size]
        supabase.table("units").insert(chunk).execute()
        inserted += len(chunk)

    _write_config(f"__SESSION_UNITS__{session_id}", records)
    return inserted


# ============================================================
# Alegeri per Sesiune
# ============================================================
def get_choices_for_session(session_id: str) -> list[dict]:
    """Returnează alegerile salvate pentru o sesiune."""
    if is_default_session(session_id):
        res = supabase.table("choices").select("*").execute()
        choices = [c for c in (res.data or []) if "__" not in c.get("student_id", "")]
        return choices

    res = supabase.table("choices").select("*").like("student_id", f"{session_id}__%").execute()
    return res.data or []


# ============================================================
# Parser inteligent pentru tabele Excel (Paste & File)
# ============================================================
def clean_header_name(h: str) -> str:
    s = h.lower().strip()
    s = s.replace("ă", "a").replace("â", "a").replace("î", "i").replace("ș", "s").replace("ş", "s").replace("ț", "t").replace("ţ", "t")
    return s


def parse_students_text(raw_text: str) -> list[dict]:
    """Parsează text copiat din Excel cu elevi."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return []

    # Detectăm separatorul
    first_line = lines[0]
    if "\t" in first_line:
        sep = "\t"
    elif ";" in first_line:
        sep = ";"
    elif "," in first_line:
        sep = ","
    else:
        sep = r"\s{2,}"

    import io
    df = pd.read_csv(io.StringIO(raw_text), sep=sep, engine="python")
    return process_students_dataframe(df)


def process_students_dataframe(df: pd.DataFrame) -> list[dict]:
    """Extrage și normalizează elevii dintr-un DataFrame."""
    col_map = {}
    for col in df.columns:
        c_clean = clean_header_name(str(col))
        if any(w in c_clean for w in ["last_name", "nume_familie", "nume"]) and "prenume" not in c_clean and "complet" not in c_clean:
            col_map["last_name"] = col
        elif any(w in c_clean for w in ["first_name", "prenume"]):
            col_map["first_name"] = col
        elif any(w in c_clean for w in ["nume_complet", "nume si prenume", "elev"]):
            col_map["full_name"] = col
        elif any(w in c_clean for w in ["medie", "average", "nota"]):
            col_map["average"] = col
        elif any(w in c_clean for w in ["specializ", "spec", "profil"]):
            col_map["specialization"] = col
        elif any(w in c_clean for w in ["gen", "sex"]):
            col_map["gender"] = col
        elif any(w in c_clean for w in ["user", "username", "cont"]):
            col_map["username"] = col

    students = []
    used_usernames = set()

    for _, row in df.iterrows():
        # Nume / Prenume
        if "last_name" in col_map and "first_name" in col_map:
            last_name = str(row[col_map["last_name"]]).strip()
            first_name = str(row[col_map["first_name"]]).strip()
        elif "full_name" in col_map:
            parts = str(row[col_map["full_name"]]).strip().split(" ", 1)
            last_name = parts[0]
            first_name = parts[1] if len(parts) > 1 else ""
        else:
            continue

        if not last_name or last_name.lower() == "nan":
            continue

        # Medie
        raw_avg = str(row.get(col_map.get("average", ""), "0.0")).replace(",", ".")
        try:
            average = float(raw_avg)
        except ValueError:
            average = 0.0

        # Specializare
        spec = normalize_spec(str(row.get(col_map.get("specialization", ""), "Aparare Cibernetica")))

        # Gen
        raw_gender = str(row.get(col_map.get("gender", "B"))).strip().upper()
        if raw_gender.startswith("F") or "FEM" in raw_gender or "FAT" in raw_gender:
            gender = "F"
        else:
            gender = "B"

        # Username generat sau specificat
        if "username" in col_map and str(row[col_map["username"]]).strip() not in ["", "nan"]:
            base_user = str(row[col_map["username"]]).strip().lower()
        else:
            clean_l = re.sub(r"[^\w]", "", clean_header_name(last_name))
            clean_f = re.sub(r"[^\w]", "", clean_header_name(first_name.split()[0] if first_name else "elev"))
            base_user = f"{clean_l}.{clean_f}"

        username = base_user
        idx = 1
        while username in used_usernames:
            username = f"{base_user}{idx}"
            idx += 1
        used_usernames.add(username)

        # ID elev
        spec_prefix = "".join([w[0] for w in spec.split()]).upper()
        s_id = f"{spec_prefix}_{last_name.replace(' ', '_')}_{first_name.replace(' ', '_')}"

        students.append({
            "id": s_id,
            "last_name": last_name,
            "first_name": first_name,
            "specialization": spec,
            "average": average,
            "gender": gender,
            "username": username,
            "password_hash": "123456"
        })

    return students


def parse_units_text(raw_text: str) -> list[dict]:
    """Parsează text copiat din Excel cu unități militare."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return []

    first_line = lines[0]
    if "\t" in first_line:
        sep = "\t"
    elif ";" in first_line:
        sep = ";"
    elif "," in first_line:
        sep = ","
    else:
        sep = r"\s{2,}"

    import io
    df = pd.read_csv(io.StringIO(raw_text), sep=sep, engine="python")
    return process_units_dataframe(df)


def process_units_dataframe(df: pd.DataFrame) -> list[dict]:
    """Extrage și normalizează unitățile dintr-un DataFrame."""
    col_map = {}
    for col in df.columns:
        c_clean = clean_header_name(str(col))
        if any(w in c_clean for w in ["unitate", "um", "denumire"]):
            col_map["unit_name"] = col
        elif any(w in c_clean for w in ["specializ", "spec"]):
            col_map["specialization"] = col
        elif any(w in c_clean for w in ["baieti", "barbati", "b"]):
            col_map["boys"] = col
        elif any(w in c_clean for w in ["fete", "femei", "f"]):
            col_map["girls"] = col

    units = []
    for _, row in df.iterrows():
        unit_name = str(row.get(col_map.get("unit_name", ""), "")).strip()
        if not unit_name or unit_name.lower() == "nan":
            continue

        spec = normalize_spec(str(row.get(col_map.get("specialization", ""), "Aparare Cibernetica")))

        try:
            boys = int(float(str(row.get(col_map.get("boys", 0), 0)).strip() or 0))
        except (ValueError, TypeError):
            boys = 0

        try:
            girls = int(float(str(row.get(col_map.get("girls", 0), 0)).strip() or 0))
        except (ValueError, TypeError):
            girls = 0

        clean_name = unit_name.replace(" ", "_") if not unit_name.startswith("UM_") else unit_name

        units.append({
            "unit_name": clean_name,
            "specialization": spec,
            "boys": boys,
            "girls": girls
        })

    return units


def get_session_students_dict(session_id: str) -> dict:
    """Returnează elevii sesiunii în formatul dict[specializare] = [(last_name, first_name, average), ...]"""
    students_list = get_students_for_session(session_id)
    out = {}
    for s in students_list:
        spec = s["specialization"]
        if spec not in out:
            out[spec] = []
        out[spec].append((s["last_name"], s["first_name"], s["average"]))
    for spec in out:
        out[spec].sort(key=lambda x: x[2], reverse=True)
    return out


def get_session_units_dict(session_id: str) -> dict:
    """Returnează unitățile sesiunii în formatul dict[specializare] = [{'display': ..., 'unit_name': ..., 'boys': ..., 'girls': ...}, ...]"""
    units_list = get_units_for_session(session_id)
    out = {}
    for u in units_list:
        spec = u["specialization"]
        if spec not in out:
            out[spec] = []
        clean_name = u["unit_name"].replace("UM_", "UM ")
        out[spec].append({
            "display": clean_name,
            "unit_name": u["unit_name"],
            "boys": u.get("boys", 0),
            "girls": u.get("girls", 0)
        })
    return out
