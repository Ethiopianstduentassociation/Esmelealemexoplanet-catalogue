import streamlit as st
import pandas as pd
import urllib.request

st.set_page_config(page_title="Exoplanet Catalogue", layout="wide")
st.title("🪐 Interactive Exoplanet Catalogue")
st.write("Live astronomical data queried from the NASA Exoplanet Archive.")

@st.cache_data(ttl=3600)
def load_data():
    url = "https://caltech.edu"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            return pd.read_csv(response)
    except Exception:
        rows = [
            ("Proxima Cen b", "Proxima Cen", "Radial Velocity", 2016, 1.03, 1.07, 234.0, 1.30),
            ("TRAPPIST-1 e", "TRAPPIST-1", "Transit", 2017, 0.92, 0.69, 251.0, 12.43),
            ("Kepler-186 f", "Kepler-186", "Transit", 2014, 1.17, 1.71, 188.0, 178.5),
            ("51 Peg b", "51 Peg", "Radial Velocity", 1995, 14.3, 150.0, 1284.0, 15.47),
            ("HD 209458 b", "HD 209458", "Transit", 1999, 15.6, 220.0, 1449.0, 48.3),
            ("Kepler-452 b", "Kepler-452", "Transit", 2015, 1.63, 3.29, 265.0, 561.0),
            ("TOI-700 d", "TOI-700", "Transit", 2020, 1.19, 1.72, 269.0, 31.1),
            ("LHS 1140 b", "LHS 1140", "Transit", 2017, 1.73, 5.60, 235.0, 14.99),
            ("GJ 1214 b", "GJ 1214", "Transit", 2009, 2.74, 8.17, 596.0, 14.65),
            ("K2-18 b", "K2-18", "Transit", 2015, 2.61, 8.63, 255.0, 38.0)
        ]
        cols = ["pl_name", "hostname", "discoverymethod", "disc_year", "pl_rade", "pl_bmasse", "pl_eqt", "sy_dist"]
        return pd.DataFrame(rows, columns=cols)

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Planets")
available_methods = df["discoverymethod"].dropna().unique().tolist()
default_methods = ["Transit"] if "Transit" in available_methods else available_methods
methods = st.sidebar.multiselect("Discovery Method", available_methods, default=default_methods)
max_radius = st.sidebar.slider("Max Planet Radius (Earth Radii)", 0.5, 25.0, 15.0)

filtered_df = df[(df["discoverymethod"].isin(methods)) & (df["pl_rade"] <= max_radius)]

# Key metrics
col1, col2, col3 = st.columns(3)
col1.metric("Matching Exoplanets", len(filtered_df))
col2.metric("Closest Planet (Parsecs)", round(filtered_df["sy_dist"].min(), 2) if not filtered_df.empty else "N/A")
col3.metric("Avg Equilibrium Temp (K)", round(filtered_df["pl_eqt"].mean(), 1) if not filtered_df.empty else "N/A")

# Scatter plot & Data Table
st.subheader("Planet Radius vs. Mass")
plot_df = filtered_df.dropna(subset=["pl_rade", "pl_bmasse"])
if not plot_df.empty:
    st.scatter_chart(plot_df, x="pl_rade", y="pl_bmasse")

st.subheader("Catalogue Data")
st.dataframe(filtered_df, use_container_width=True)
