from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    try:
        import streamlit as st
        if "SUPABASE_URL" in st.secrets:
            url = url or st.secrets["SUPABASE_URL"]
        if "SUPABASE_KEY" in st.secrets:
            key = key or st.secrets["SUPABASE_KEY"]
    except Exception:
        pass

if not url or not key:
    raise ValueError(
        "Lipsesc variabilele de configurare SUPABASE_URL sau SUPABASE_KEY! "
        "Asigură-te că le-ai configurat în fișierul .env (local) sau în Streamlit Cloud Secrets (online)."
    )

supabase = create_client(url, key)
print("Supabase connected!")