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

# --------- TAB 3: SPATIAL ANALYSIS ---------
with tab3:
    st.header("Spatial Distribution Analysis")
    map_options = st.columns([3, 1])
    with map_options[0]:
        map_type = st.radio("Map Type", options=["Heat Map", "Scatter Plot", "3D Elevation"], horizontal=True)
    with map_options[1]:
        map_height = st.slider("Map Height", 400, 800, 600, 50)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    demo_col = selected_col
    demo_name = selected_demo
    if map_type == "Heat Map":
        heat_layer = pdk.Layer(
            "HeatmapLayer",
            data=filtered_df,
            opacity=0.8,
            get_position=["longitude", "latitude"],
            get_weight=demo_col,
            threshold=0.1,
            aggregation="SUM",
            pickable=True
        )
        view_state = pdk.ViewState(
            latitude=filtered_df["latitude"].mean(),
            longitude=filtered_df["longitude"].mean(),
            zoom=8,
            pitch=0,
        )
        heat_map = pdk.Deck(
            layers=[heat_layer],
            initial_view_state=view_state,
            tooltip={"text": f"{demo_name}: {{{demo_col}}}"},
            height=map_height
        )
        st.subheader(f"Heat Map of {demo_name}")
        st.pydeck_chart(heat_map, use_container_width=True)
    elif map_type == "Scatter Plot":
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position=["longitude", "latitude"],
            get_radius=f"{demo_col} / 20",
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=2,
            radius_min_pixels=3,
            radius_max_pixels=30,
            line_width_min_pixels=1,
        )
        view_state = pdk.ViewState(
            latitude=filtered_df["latitude"].mean(),
            longitude=filtered_df["longitude"].mean(),
            zoom=8,
            pitch=0,
        )
        scatter_map = pdk.Deck(
            layers=[scatter_layer],
            initial_view_state=view_state,
            tooltip={...},
            height=map_height
        )
        st.subheader(f"Population Density of {demo_name}")
        st.pydeck_chart(scatter_map, use_container_width=True)
    else:  # 3D Elevation
        elevation_layer = pdk.Layer(
            "HexagonLayer",
            data=filtered_df,
            get_position=["longitude", "latitude"],
            get_elevation=f"{demo_col} / 50",
            elevation_scale=50,
            pickable=True,
            elevation_range=[0, 3000],
            extruded=True,
            coverage=1,
        )
        view_state = pdk.ViewState(
            latitude=filtered_df["latitude"].mean(),
            longitude=filtered_df["longitude"].mean(),
            zoom=7.5,
            pitch=40,
        )
        elevation_map = pdk.Deck(
            layers=[elevation_layer],
            initial_view_state=view_state,
            tooltip={"text": f"Elevation represents {demo_name}"},
            height=map_height
        )
        st.subheader(f"3D Elevation Map of {demo_name}")
        st.pydeck_chart(elevation_map, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Regional Population Analysis")
    col1, col2 = st.columns(2)
    with col1:
        region_data = df.groupby('region').agg(
            latitude=('latitude', 'mean'),
            longitude=('longitude', 'mean'),
            population=('pop_overall', 'sum'),
            population_selected=(selected_col, 'sum')
        ).reset_index()
        region_map = px.scatter_mapbox(
            region_data,
            lat="latitude",
            lon="longitude",
            size="population",
            color="region",
            hover_name="region",
            hover_data=["population", "population_selected"],
            zoom=7,
            height=400,
            mapbox_style="carto-positron",
            title=f"Regional Distribution of {demo_name}"
        )
        region_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(region_map, use_container_width=True)
    with col2:
        radar_data = df.groupby('region').agg(
            total=('pop_overall', 'sum'),
            male=('pop_men', 'sum'),
            female=('pop_women', 'sum'),
            children=('pop_0_5', 'sum'),
            youth=('pop_15_24', 'sum'),
            elderly=('pop_60_plus', 'sum'),
            women_reproductive=('pop_women_15_49', 'sum')
        ).reset_index()
        cols_to_normalize = radar_data.columns.difference(['region'])
        for col in cols_to_normalize:
            max_val = radar_data[col].max()
            radar_data[f'{col}_norm'] = radar_data[col] / max_val
        radar_fig = go.Figure()
        categories = ['Total', 'Male', 'Female', 'Children', 'Youth', 'Elderly', 'Women (15-49)']
        for i, region in enumerate(radar_data['region']):
            radar_fig.add_trace(go.Scatterpolar(
                r=[
                    radar_data.loc[i, 'total_norm'],
                    radar_data.loc[i, 'male_norm'],
                    radar_data.loc[i, 'female_norm'],
                    radar_data.loc[i, 'children_norm'],
                    radar_data.loc[i, 'youth_norm'],
                    radar_data.loc[i, 'elderly_norm'],
                    radar_data.loc[i, 'women_reproductive_norm']
                ],
                theta=categories,
                fill='toself',
                name=region
            ))
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title="Regional Demographic Comparison",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(radar_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --------- TAB 4: ADVANCED ANALYTICS ---------
with tab4:
    st.header("Advanced Population Analytics")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Demographic Correlation Analysis")
    demographic_cols = [
        'pop_overall', 'pop_men', 'pop_women',
        'pop_0_5', 'pop_15_24', 'pop_60_plus', 'pop_women_15_49'
    ]
    correlation = df[demographic_cols].corr()
    corr_fig = px.imshow(
        correlation,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        title="Correlation between Demographic Variables"
    )
    corr_fig.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
    better_labels = {
        'pop_overall': 'Total',
        'pop_men': 'Male',
        'pop_women': 'Female',
        'pop_0_5': 'Children',
        'pop_15_24': 'Youth',
        'pop_60_plus': 'Elderly',
        'pop_women_15_49': 'Women 15-49'
    }
    corr_fig.update_xaxes(ticktext=list(better_labels.values()), tickvals=list(range(len(better_labels))))
    corr_fig.update_yaxes(ticktext=list(better_labels.values()), tickvals=list(range(len(better_labels))))
    st.plotly_chart(corr_fig, use_container_width=True)
    st.markdown("""
    This correlation matrix shows the relationship between different demographic variables. Values close to 1 indicate 
    strong positive correlation, while values close to -1 indicate strong negative correlation. A value of 0 means no correlation.
    
    *Insights:*
    - All population segments show strong correlation with overall population, as expected
    - Male and female populations are strongly correlated with each other
    - Children (0-5) show moderate to strong correlation with women of reproductive age (15-49)
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Gender Ratio Analysis")
    df['gender_ratio'] = df['pop_men'] / df['pop_women'] * 100
    gender_hist = px.histogram(
        df,
        x='gender_ratio',
        nbins=50,
        title="Distribution of Gender Ratios (Males per 100 Females)",
        opacity=0.7,
        marginal='box'
    )
    gender_hist.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20), xaxis_title="Gender Ratio (Males per 100 Females)", yaxis_title="Number of Divisions")
    gender_hist.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="Gender Parity")
    st.plotly_chart(gender_hist, use_container_width=True)
    region_gender = df.groupby('region').agg(male=('pop_men','sum'), female=('pop_women','sum')).reset_index()
    region_gender['gender_ratio'] = region_gender['male'] / region_gender['female'] * 100
    region_gender = region_gender.sort_values('gender_ratio')
    gender_bar = px.bar(
        region_gender,
        y='region',
        x='gender_ratio',
        orientation='h',
        title="Gender Ratio by Region (Males per 100 Females)",
        color_continuous_scale="RdBu_r",
        text=region_gender['gender_ratio'].round(1).astype(str)
    )
    gender_bar.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), xaxis_title="Gender Ratio", yaxis_title="Region")
    gender_bar.add_vline(x=100, line_dash="dash", line_color="black", annotation_text="Gender Parity")
    gender_bar.update_traces(textposition='outside', hovertemplate='<b>%{y}</b><br>Gender Ratio: %{x:.1f}<extra></extra>')
    st.plotly_chart(gender_bar, use_container_width=True)
    st.markdown("""
    The gender ratio is the number of males per 100 females in a population. A ratio of 100 indicates an equal number of males and females.
    - A ratio greater than 100 indicates more males than females
    - A ratio less than 100 indicates more females than males
    
    Variations in gender ratio can be influenced by biological factors, migration patterns, and socioeconomic factors.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Child-Woman Ratio Analysis")
    df['child_woman_ratio'] = (df['pop_0_5'] / df['pop_women_15_49']) * 1000
    cwr_hist = px.histogram(
        df,
        x='child_woman_ratio',
        nbins=50,
        title="Distribution of Child-Woman Ratios",
        opacity=0.7,
        marginal='box'
    )
    cwr_hist.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20), xaxis_title="Child-Woman Ratio (Children per 1000 Women)", yaxis_title="Number of Divisions")
    mean_cwr = df['child_woman_ratio'].mean()
    cwr_hist.add_vline(x=mean_cwr, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_cwr:.1f}")
    st.plotly_chart(cwr_hist, use_container_width=True)
    region_cwr = df.groupby('region').agg(children=('pop_0_5','sum'), women_reproductive=('pop_women_15_49','sum')).reset_index()
    region_cwr['child_woman_ratio'] = (region_cwr['children'] / region_cwr['women_reproductive']) * 1000
    region_cwr = region_cwr.sort_values('child_woman_ratio')
    cwr_bar = px.bar(
        region_cwr,
        y='region',
        x='child_woman_ratio',
        orientation='h',
        title="Child-Woman Ratio by Region",
        color_continuous_scale="Reds",
        text=region_cwr['child_woman_ratio'].round(1).astype(str)
    )
    cwr_bar.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), xaxis_title="Child-Woman Ratio (Children per 1000 Women)", yaxis_title="Region")
    cwr_bar.update_traces(textposition='outside', hovertemplate='<b>%{y}</b><br>Child-Woman Ratio: %{x:.1f}%<extra></extra>')
    st.plotly_chart(cwr_bar, use_container_width=True)
    st.markdown("""
    The Child-Woman Ratio (CWR) is a measure of fertility that shows the number of children under 5 years old 
    per 1,000 women of reproductive age (15-49 years). It serves as a simple fertility indicator when detailed birth data is unavailable.
    
    *Interpretation:*
    - Higher ratios indicate higher fertility rates
    - Lower ratios may indicate lower birth rates or smaller family sizes
    - Variations across regions can reflect differences in family planning, cultural practices, and socioeconomic factors
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Comparative Regional Analysis")
    scatter_data = df.groupby('region').agg(
        total=('pop_overall','sum'),
        male=('pop_men','sum'),
        female=('pop_women','sum'),
        children=('pop_0_5','sum'),
        youth=('pop_15_24','sum'),
        elderly=('pop_60_plus','sum')
    ).reset_index()
    for col in scatter_data.columns:
        if col != 'region':
            scatter_data[col] = scatter_data[col] / 1000
    scatter_matrix = px.scatter_matrix(
        scatter_data,
        dimensions=['total', 'male', 'female', 'children', 'youth', 'elderly'],
        color='region',
        title="Demographic Correlation by Region (in thousands)",
        height=700
    )
    scatter_matrix.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    scatter_matrix.update_traces(diagonal_visible=False)
    st.plotly_chart(scatter_matrix, use_container_width=True)
    st.markdown("""
    This scatter matrix shows relationships between different demographic variables across regions. Each point represents a region.
    
    *How to read this chart:*
    - Each cell shows the relationship between two demographic variables
    - Points are colored by region
    - Patterns in the scatter plots can reveal correlations and regional differences
    - Diagonal alignment of points suggests strong correlation between the variables
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# --------- TAB 5: DATA EXPLORER ---------
with tab5:
    st.header("Data Explorer")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Interactive Data Table")
    display_df = filtered_df.copy()
    display_df['gender_ratio'] = display_df['pop_men'] / display_df['pop_women'] * 100
    display_df['dependency_ratio'] = (display_df['pop_0_5'] + display_df['pop_60_plus']) / (display_df['pop_overall'] - display_df['pop_0_5'] - display_df['pop_60_plus']) * 100
    display_df['child_woman_ratio'] = (display_df['pop_0_5'] / display_df['pop_women_15_49']) * 1000
    columns_to_display = {
        'region': 'Region',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'pop_overall': 'Total Population',
        'pop_men': 'Male Population',
        'pop_women': 'Female Population',
        'pop_0_5': 'Children (0-5)',
        'pop_15_24': 'Youth (15-24)',
        'pop_60_plus': 'Elderly (60+)',
        'pop_women_15_49': 'Women (15-49)',
        'gender_ratio': 'Gender Ratio',
        'dependency_ratio': 'Dependency Ratio',
        'child_woman_ratio': 'Child-Woman Ratio'
    }
    display_df = display_df.rename(columns=columns_to_display)
    with st.expander("Select Columns to Display", expanded=False):
        selected_columns = st.multiselect(
            "Columns",
            options=list(columns_to_display.values()),
            default=['Region', 'Total Population', 'Male Population', 'Female Population', 'Gender Ratio']
        )
    if not selected_columns:
        selected_columns = ['Region', 'Total Population', 'Male Population', 'Female Population', 'Gender Ratio']
    st.dataframe(display_df[selected_columns], use_container_width=True, height=500, hide_index=True)
    st.caption(f"Showing {len(display_df)} records based on current filters")
    col1, col2 = st.columns(2)
    with col1:
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download as CSV", data=csv, file_name="population_data.csv", mime="text/csv")
    with col2:
        excel_buffer = io.BytesIO()
        display_df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_data = excel_buffer.getvalue()
        st.download_button(label="Download as Excel", data=excel_data, file_name="population_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Statistical Summary")
    stats_df = display_df.describe().T.reset_index().rename(columns={'index': 'Variable'})
    numeric_cols = stats_df.columns[1:]
    for col in numeric_cols:
        stats_df[col] = stats_df[col].map(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Custom Visualization")
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("X-Axis", options=list(columns_to_display.values()), index=list(columns_to_display.values()).index('Total Population'))
    with col2:
        y_axis = st.selectbox("Y-Axis", options=list(columns_to_display.values()), index=list(columns_to_display.values()).index('Gender Ratio'))
    col1, col2 = st.columns(2)
    with col1:
        color_by = st.selectbox("Color By", options=['Region', 'None'], index=0)
    with col2:
        chart_type = st.selectbox("Chart Type", options=['Scatter Plot', 'Bar Chart', 'Line Chart', 'Box Plot'], index=0)
    rev_columns = {v: k for k, v in columns_to_display.items()}
    if chart_type == 'Scatter Plot':
        if color_by == 'None':
            custom_fig = px.scatter(display_df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", opacity=0.7, size='Total Population', hover_name='Region')
        else:
            custom_fig = px.scatter(display_df, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} vs {x_axis} by {color_by}", opacity=0.7, size='Total Population', hover_name='Region')
    elif chart_type == 'Bar Chart':
        if x_axis == 'Region':
            grouped_df = display_df.groupby('Region').agg({y_axis: 'mean'}).reset_index()
            custom_fig = px.bar(grouped_df, x='Region', y=y_axis, title=f"{y_axis} by {x_axis}", color='Region' if color_by != 'None' else None)
        else:
            custom_fig = px.histogram(display_df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}", color='Region' if color_by != 'None' else None, histfunc='avg')
    elif chart_type == 'Line Chart':
        if x_axis != 'Region':
            sorted_df = display_df.sort_values(by=x_axis)
            custom_fig = px.line(sorted_df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", color='Region' if color_by != 'None' else None)
        else:
            grouped_df = display_df.groupby('Region').agg({y_axis: 'mean'}).reset_index()
            custom_fig = px.line(grouped_df, x='Region', y=y_axis, title=f"{y_axis} by {x_axis}", markers=True)
    elif chart_type == 'Box Plot':
        if color_by != 'None':
            custom_fig = px.box(display_df, x='Region' if x_axis == 'Region' else None, y=y_axis, title=f"Distribution of {y_axis}" + (f" by {x_axis}" if x_axis == 'Region' else ""), color='Region')
        else:
            custom_fig = px.box(display_df, y=y_axis, title=f"Distribution of {y_axis}")
    custom_fig.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(custom_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="footer">
        <p>💡 Developed by Anne Fernando • Data Source: WFP/OCHA via HDX • © 2025 Population Explorer</p>
    </div>
""", unsafe_allow_html=True)