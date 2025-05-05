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

def calculate_key_metrics(df):
    return {
        "Overall": int(df["pop_overall"].sum()),
        "Male": int(df["pop_men"].sum()),
        "Female": int(df["pop_women"].sum()),
        "Children (0–5)": int(df["pop_0_5"].sum()),
        "Youth (15–24)": int(df["pop_15_24"].sum()),
        "Elderly (60+)": int(df["pop_60_plus"].sum()),
        "Women of reproductive age (15–49)": int(df["pop_women_15_49"].sum()),
    }

def format_number(num):
    return f"{num:,.0f}" if isinstance(num, (int, float)) else num

metrics = calculate_key_metrics(df)

df['region'] = 'Central'
df.loc[df['latitude'] > 8.0, 'region'] = 'Northern'
df.loc[(df['latitude'] <= 8.0) & (df['latitude'] > 7.5) & (df['longitude'] < 80.5), 'region'] = 'Western'
df.loc[(df['latitude'] <= 7.5) & (df['longitude'] > 80.5), 'region'] = 'Eastern'
df.loc[(df['latitude'] <= 7.5) & (df['longitude'] < 80.5), 'region'] = 'Southern'