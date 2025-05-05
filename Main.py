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

# Main dashboard content
st.title("Population Analytics Dashboard")
st.caption("Explore detailed demographic data across geographic divisions")

# Tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "👥 Demographics", 
    "🗺 Spatial Analysis",
    "📈 Advanced Analytics",
    "📋 Data Explorer"
])

# --------- TAB 1: OVERVIEW ---------
with tab1:
    st.header("National Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Total Population")
        st.markdown(f"<h2>{format_number(metrics['Overall'])}</h2>", unsafe_allow_html=True)
        male_percentage = metrics['Male'] / metrics['Overall'] * 100
        female_percentage = metrics['Female'] / metrics['Overall'] * 100
        gender_fig = go.Figure()
        gender_fig.add_trace(go.Bar(
            y=['Gender Ratio'],
            x=[male_percentage],
            name='Male',
            orientation='h',
            marker=dict(color='#007BFF'),
            hovertemplate='Male: %{x:.1f}%<extra></extra>'
        ))
        gender_fig.add_trace(go.Bar(
            y=['Gender Ratio'],
            x=[female_percentage],
            name='Female',
            orientation='h',
            marker=dict(color='#FF69B4'),
            hovertemplate='Female: %{x:.1f}%<extra></extra>'
        ))
        gender_fig.update_layout(
            barmode='stack',
            height=100,
            margin=dict(l=0, r=0, t=10, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showticklabels=False, showgrid=False, range=[0, 100])
        )
        st.plotly_chart(gender_fig, use_container_width=True)
        st.markdown(f"*Male:* {format_number(metrics['Male'])} ({male_percentage:.1f}%)")
        st.markdown(f"*Female:* {format_number(metrics['Female'])} ({female_percentage:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Age Distribution")
        children_percentage = metrics['Children (0–5)'] / metrics['Overall'] * 100
        youth_percentage = metrics['Youth (15–24)'] / metrics['Overall'] * 100
        elderly_percentage = metrics['Elderly (60+)'] / metrics['Overall'] * 100
        others_percentage = 100 - (children_percentage + youth_percentage + elderly_percentage)
        age_fig = go.Figure(data=[go.Pie(
            labels=['Children (0-5)', 'Youth (15-24)', 'Elderly (60+)', 'Others'],
            values=[children_percentage, youth_percentage, elderly_percentage, others_percentage],
            hole=.3,
            marker_colors=px.colors.qualitative.Pastel
        )])
        age_fig.update_layout(
            showlegend=True,
            height=220,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(age_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Key Demographics")
        women_rep_percentage = metrics['Women of reproductive age (15–49)'] / metrics['Overall'] * 100
        st.markdown(f"*Women (15-49):* {format_number(metrics['Women of reproductive age (15–49)'])} ({women_rep_percentage:.1f}%)")
        dependent_pop = metrics['Children (0–5)'] + metrics['Elderly (60+)']
        working_age_pop = metrics['Overall'] - dependent_pop
        dependency_ratio = (dependent_pop / working_age_pop) * 100
        st.markdown(f"*Dependency Ratio:* {dependency_ratio:.1f}%")
        st.caption("(Ratio of dependents to working-age population)")
        sri_lanka_area = 65610
        pop_density = metrics['Overall'] / sri_lanka_area
        st.markdown(f"*Population Density:* {pop_density:.1f}/km²")
        st.caption("(Average population per square kilometer)")
        st.markdown("---")
        st.markdown("See full demographic breakdown in the Demographics tab")
        st.markdown('</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Regional Population Distribution")
        region_stats = df.groupby('region').agg(
            total_population=('pop_overall', 'sum'),
            male_population=('pop_men', 'sum'),
            female_population=('pop_women', 'sum'),
            division_count=('pop_overall', 'count')
        ).reset_index()
        region_stats['percentage'] = region_stats['total_population'] / region_stats['total_population'].sum() * 100
        region_stats = region_stats.sort_values('total_population', ascending=False)
        region_fig = px.bar(
            region_stats,
            x='region',
            y='total_population',
            text=region_stats['percentage'].round(1).astype(str) + '%',
            color='region',
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={'total_population': 'Population', 'region': 'Region'},
            title='Population by Region'
        )
        region_fig.update_layout(
            xaxis_title="Region",
            yaxis_title="Population",
            yaxis=dict(title_standoff=25),
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        region_fig.update_traces(
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Population: %{y:,.0f}<br>Percentage: %{text}<extra></extra>'
        )
        st.plotly_chart(region_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Population by Demographic Group")
        demo_data = pd.DataFrame({
            'Group': list(metrics.keys()),
            'Population': list(metrics.values())
        })
        demo_data = demo_data[demo_data['Group'] != 'Overall']
        demo_data = demo_data.sort_values('Population')
        demo_fig = px.bar(
            demo_data,
            y='Group',
            x='Population',
            orientation='h',
            text=demo_data['Population'].apply(format_number),
            color='Group',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'Population': 'Population Count', 'Group': 'Demographic Group'}
        )
        demo_fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=20, t=20, b=20),
            xaxis_title="Population",
            yaxis_title="",
        )
        demo_fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>'
        )
        st.plotly_chart(demo_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Top Population Centers")
    top_divisions = df.nlargest(10, selected_col).copy()
    pop_columns = [col for col in top_divisions.columns if col.startswith('pop_')]
    for col in pop_columns:
        top_divisions[col] = top_divisions[col].apply(format_number)
    top_divisions = top_divisions[['latitude', 'longitude', 'pop_overall', 'pop_men', 'pop_women', 'region']]
    top_divisions.columns = ['Latitude', 'Longitude', 'Total Population', 'Male', 'Female', 'Region']
    st.dataframe(
        top_divisions,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total Population": st.column_config.NumberColumn(format="%d"),
            "Male": st.column_config.NumberColumn(format="%d"),
            "Female": st.column_config.NumberColumn(format="%d"),
        }
    )
    st.caption("Top 10 divisions by selected demographic: " + selected_demo)
    st.markdown('</div>', unsafe_allow_html=True)

# --------- TAB 2: DEMOGRAPHICS ---------
with tab2:
    st.header("Demographic Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Population Pyramid")
        pyramid_data = pd.DataFrame({
            'Age Group': ['0-5', '15-24', '25-59', '60+'],
            'Male': [
                -df['pop_men'].sum() * 0.1,
                -df['pop_men'].sum() * 0.2,
                -df['pop_men'].sum() * 0.6,
                -df['pop_men'].sum() * 0.1
            ],
            'Female': [
                df['pop_women'].sum() * 0.1,
                df['pop_women'].sum() * 0.2,
                df['pop_women'].sum() * 0.55,
                df['pop_women'].sum() * 0.15
            ]
        })
        pyramid_fig = go.Figure()
        pyramid_fig.add_trace(go.Bar(
            y=pyramid_data['Age Group'],
            x=pyramid_data['Male'],
            name='Male',
            orientation='h',
            marker=dict(color='#007BFF'),
            hovertemplate='Male: %{x:,.0f}<extra></extra>'
        ))
        pyramid_fig.add_trace(go.Bar(
            y=pyramid_data['Age Group'],
            x=pyramid_data['Female'],
            name='Female',
            orientation='h',
            marker=dict(color='#FF69B4'),
            hovertemplate='Female: %{x:,.0f}<extra></extra>'
        ))
        pyramid_fig.update_layout(
            title='Population Pyramid (Age & Gender Distribution)',
            barmode='relative',
            bargap=0.1,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(
                title='Population',
                tickvals=[-10000000, -7500000, -5000000, -2500000, 0, 2500000, 5000000, 7500000, 10000000],
                ticktext=['10M', '7.5M', '5M', '2.5M', '0', '2.5M', '5M', '7.5M', '10M'],
            ),
            yaxis=dict(title=''),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(pyramid_fig, use_container_width=True)
        st.caption("Note: This pyramid is an approximation based on available age groups")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gender Ratios by Region")
        gender_ratio = df.groupby('region').agg(male=('pop_men','sum'), female=('pop_women','sum')).reset_index()
        gender_ratio['male_percent'] = gender_ratio['male'] / (gender_ratio['male'] + gender_ratio['female']) * 100
        gender_ratio['female_percent'] = gender_ratio['female'] / (gender_ratio['male'] + gender_ratio['female']) * 100
        gender_fig = go.Figure()
        gender_fig.add_trace(go.Bar(
            x=gender_ratio['region'],
            y=gender_ratio['male_percent'],
            name='Male',
            marker_color='#007BFF',
            hovertemplate='<b>%{x}</b><br>Male: %{y:.1f}%<extra></extra>'
        ))
        gender_fig.add_trace(go.Bar(
            x=gender_ratio['region'],
            y=gender_ratio['female_percent'],
            name='Female',
            marker_color='#FF69B4',
            hovertemplate='<b>%{x}</b><br>Female: %{y:.1f}%<extra></extra>'
        ))
        gender_fig.update_layout(
            barmode='group',
            title='Gender Distribution by Region',
            xaxis=dict(title='Region'),
            yaxis=dict(title='Percentage', range=[0, 100]),
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(gender_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Age Group Distribution")
        age_data = pd.DataFrame({
            'Age Group': ['Children (0-5)', 'Youth (15-24)', 'Adults (25-59)', 'Elderly (60+)'],
            'Population': [
                df['pop_0_5'].sum(),
                df['pop_15_24'].sum(),
                df['pop_overall'].sum() - df['pop_0_5'].sum() - df['pop_15_24'].sum() - df['pop_60_plus'].sum(),
                df['pop_60_plus'].sum()
            ]
        })
        age_data['Percentage'] = age_data['Population'] / age_data['Population'].sum() * 100
        age_fig = px.pie(
            age_data,
            values='Population',
            names='Age Group',
            title='Population by Age Group',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hover_data=['Percentage'],
            labels={'Percentage': 'Percentage'}
        )
        age_fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Population: %{value:,.0f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
        )
        age_fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(age_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Dependency Ratio by Region")
        dependency_by_region = df.groupby('region').agg(children=('pop_0_5','sum'), elderly=('pop_60_plus','sum'), total=('pop_overall','sum')).reset_index()
        dependency_by_region['working_age'] = dependency_by_region['total'] - dependency_by_region['children'] - dependency_by_region['elderly']
        dependency_by_region['dependency_ratio'] = (dependency_by_region['children'] + dependency_by_region['elderly']) / dependency_by_region['working_age'] * 100
        dependency_by_region = dependency_by_region.sort_values('dependency_ratio')
        dep_fig = px.bar(
            dependency_by_region,
            x='region',
            y='dependency_ratio',
            color='region',
            labels={'dependency_ratio': 'Dependency Ratio (%)', 'region': 'Region'},
            title='Dependency Ratio by Region',
            text=dependency_by_region['dependency_ratio'].round(1).astype(str) + '%',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        dep_fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Region",
            yaxis_title="Dependency Ratio (%)",
        )
        dep_fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Dependency Ratio: %{y:.1f}%<extra></extra>'
        )
        st.plotly_chart(dep_fig, use_container_width=True)
        st.caption("Dependency ratio = (Children + Elderly) / Working Age Population × 100")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Demographic Distributions")
    demographic_options = {
        'pop_overall': 'Overall Population',
        'pop_men': 'Male Population',
        'pop_women': 'Female Population',
        'pop_0_5': 'Children (0-5)',
        'pop_15_24': 'Youth (15-24)',
        'pop_60_plus': 'Elderly (60+)',
        'pop_women_15_49': 'Women (15-49)'
    }
    selected_demo_key = selected_col
    selected_demo_name = demographic_options[selected_demo_key]
    hist_fig = px.histogram(
        filtered_df,
        x=selected_demo_key,
        nbins=50,
        title=f'Distribution of {selected_demo_name}',
        labels={selected_demo_key: selected_demo_name},
        opacity=0.7,
        marginal='box'
    )
    hist_fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title=selected_demo_name,
        yaxis_title="Number of Divisions",
    )
    st.plotly_chart(hist_fig, use_container_width=True)
    stats_col1, stats_col2, stats_col3, stats_col4, stats_col5 = st.columns(5)
    with stats_col1:
        st.metric("Minimum", format_number(filtered_df[selected_demo_key].min()))
    with stats_col2:
        st.metric("Maximum", format_number(filtered_df[selected_demo_key].max()))
    with stats_col3:
        st.metric("Mean", format_number(int(filtered_df[selected_demo_key].mean())))
    with stats_col4:
        st.metric("Median", format_number(int(filtered_df[selected_demo_key].median())))
    with stats_col5:
        st.metric("Total", format_number(filtered_df[selected_demo_key].sum()))
    st.markdown('</div>', unsafe_allow_html=True)