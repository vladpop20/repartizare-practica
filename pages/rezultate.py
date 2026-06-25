import streamlit as st
import pandas as pd

from supabase_db import get_allocations

st.title("Rezultate simulare")

allocations = get_allocations()

df = pd.DataFrame(allocations)

st.dataframe(
    df,
    use_container_width=True
)