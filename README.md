# 🇱🇰 Population Analytics Dashboard - Sri Lanka

An interactive data analytics dashboard developed in **Streamlit** to explore Sri Lanka’s 2020 population distribution. This tool visualizes key demographic attributes across regions using maps, charts, and advanced metrics for data-driven decision-making.

## 📌 Project Overview

This project was completed as part of the `5DATA004W - Data Science Project Lifecycle` module. It uses real population data sourced from the **Humanitarian Data Exchange (HDX)** and transforms it into an interactive experience for policy planners, researchers, and the public.

The dashboard allows users to:
- Filter and explore demographic segments (e.g., gender, youth, elderly)
- Visualize population distribution on maps (heatmap, scatter, 3D)
- Analyze regional dependency, gender ratio, and fertility indicators
- Download filtered datasets and generate custom charts

---

## 📊 Features

- **Five Main Tabs**:
  1. **National Overview** – Total population, gender breakdown, region-wise stats
  2. **Demographics** – Population pyramid, age group analysis, dependency ratios
  3. **Spatial Analysis** – Heatmaps, 3D elevation maps, radar and region-wise comparisons
  4. **Advanced Analytics** – Correlation matrix, gender parity, child-woman ratio
  5. **Data Explorer** – Interactive filtering, custom plots, data download (CSV/Excel)

- 🔍 **Sidebar filters**: Region selector, minimum population filter, demographic focus
- 🗺️ **Map visualizations** using **Pydeck** and **Plotly**
- 📈 **Chart builder** for custom visualizations
- 📥 Export filtered data to CSV/Excel

---

## 🗃️ Dataset

- **Source**: [Humanitarian Data Exchange (HDX)](https://data.humdata.org/dataset/sri-lanka-high-resolution-population-density-maps-demographic-estimates)
- **Title**: Sri Lanka - Population Data by Administrative Division (2020)
- **Preprocessed File**: `cleaned_lka_2020_subset_50000.csv`  
- Columns include:
  - `pop_overall`, `pop_men`, `pop_women`, `pop_0_5`, `pop_15_24`, `pop_60_plus`, `pop_women_15_49`
  - `latitude`, `longitude`, `region` (manually assigned based on coordinates)

---

## 🚀 How to Run Locally

```bash
# Step 1: Clone the repo
git clone https://github.com/Anne0422/5DATA004W-CW.git
cd sri-lanka-population-dashboard

# Step 2: Create virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run Streamlit app
streamlit run Main.py