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

# Sidebar for global filters
with st.sidebar:
    st.title("Population Dashboard")
    
    st.markdown("---")
    
    # Population threshold filter
    st.subheader("Filters")
    with st.expander("Population Filters", expanded=True):
        min_pop = int(df["pop_overall"].min())
        max_pop = int(df["pop_overall"].max())
        pop_threshold = st.slider(
            "Minimum Population",
            min_value=min_pop,
            max_value=max_pop,
            value=min_pop,
            step=100
        )
        filtered_df = df[df["pop_overall"] >= pop_threshold]
        demo_options = [
            "Overall Population",
            "Male Population",
            "Female Population", 
            "Children (0-5)",
            "Youth (15-24)",
            "Elderly (60+)",
            "Women (15-49)"
        ]
        selected_demo = st.selectbox("Demographic Focus", demo_options)
        demo_mapping = {
            "Overall Population": "pop_overall",
            "Male Population": "pop_men",
            "Female Population": "pop_women",
            "Children (0-5)": "pop_0_5",
            "Youth (15-24)": "pop_15_24",
            "Elderly (60+)": "pop_60_plus",
            "Women (15-49)": "pop_women_15_49"
        }
        selected_col = demo_mapping[selected_demo]
    
    with st.expander("Geographic Filters", expanded=True):
        regions = sorted(df['region'].unique())
        selected_regions = st.multiselect("Regions", regions, default=regions)
        filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
    
    st.markdown("### Filtered Data Summary")
    st.info(f"Showing {len(filtered_df):,} out of {len(df):,} divisions")
    percentage = len(filtered_df) / len(df) * 100
    st.progress(percentage / 100)
    st.caption(f"{percentage:.1f}% of total data")
    st.markdown("---")
    st.caption("Data source: Census 2020")
    filtered_metrics = calculate_key_metrics(filtered_df)
    st.markdown(f"*Total Population:* {format_number(filtered_metrics['Overall'])}")
    percentage_of_total = filtered_metrics['Overall'] / metrics['Overall'] * 100
    st.caption(f"{percentage_of_total:.1f}% of total population")