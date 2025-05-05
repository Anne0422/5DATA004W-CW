import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Population Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data(path="cleaned_lka_2020_subset_50000.csv"):
    return pd.read_csv(path)

df = load_data()