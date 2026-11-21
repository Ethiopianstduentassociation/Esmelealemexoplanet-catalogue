import streamlit as st
import pandas as pd

st.set_page_config(page_title="Exoplanet Catalogue", layout="wide")
st.title("🪐 Interactive Exoplanet Catalogue")
st.write("Live data queried directly from the NASA Exoplanet Archive.")

@st.cache_data
def load_data():
    url = "https://caltech.edu"
    return pd.read_csv(url)

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Planets")
methods = st.sidebar.multiselect("Discovery Method", df["discoverymethod"].dropna().unique(), default=["Transit"])
max_radius = st.sidebar.slider("Max Planet Radius (Earth Radii)", 0.5, 25.0, 15.0)

filtered_df = df[(df["discoverymethod"].isin(methods)) & (df["pl_rade"] <= max_radius)]

# Key metrics
col1, col2, col3 = st.columns(3)
col1.metric("Matching Exoplanets", len(filtered_df))
col2.metric("Closest Planet (Parsecs)", round(filtered_df["sy_dist"].min(), 2))
col3.metric("Avg Equilibrium Temp (K)", round(filtered_df["pl_eqt"].mean(), 1))

# Scatter plot & Data Table
st.subheader("Planet Radius vs. Mass")
st.scatter_chart(filtered_df.dropna(subset=["pl_rade", "pl_bmasse"]), x="pl_rade", y="pl_bmasse")

st.subheader("Catalogue Data")
st.dataframe(filtered_df, use_container_width=True)
