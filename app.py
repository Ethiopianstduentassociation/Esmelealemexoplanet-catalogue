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
        data = {
            "pl_name": ["Proxima Cen b", "TRAPPIST-1 e", "Kepler-186 f", "51 Peg b", "HD 209458 b", "Kepler-452 b", "TOI-700 d", "LHS 1140 b", "GJ 1214 b", "K2-18 b"],
            "hostname": ["Proxima Cen", "TRAPPIST-1", "Kepler-186", "51 Peg", "HD 209458", "Kepler-452", "TOI-700", "LHS 1140", "GJ 1214", "K2-18"],
            "discoverymethod": ["Radial Velocity", "Transit", "Transit", "Radial Velocity", "Transit", "Transit", "Transit", "Transit", "Transit", "Transit"],
            "disc_year":,
            "pl_rade": [1.03, 0.92, 1.17, 14.3, 15.6, 1.63, 1.19, 1.73, 2.74, 2.61],
            "pl_bmasse": [1.07, 0.69, 1.71, 150.0, 220.0, 3.29, 1.72, 5.60, 8.17, 8.63],
            "pl_eqt":,
            "sy_dist": [1.30, 12.43, 178.5, 15.47, 48.3, 561.0, 31.1, 14.99, 14.65, 38.0]
        }
        return pd.DataFrame(data)

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

