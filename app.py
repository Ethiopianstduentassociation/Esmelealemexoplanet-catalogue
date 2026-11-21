import streamlit as st
import pandas as pd

st.set_page_config(page_title="HWO Exoplanet Catalogue", layout="wide")
st.title("🪐 Solar Neighborhood Exoplanet Catalogue (Within 80 Light-Years)")
st.markdown("**Characterizing Confirmed & Candidate Exoplanets Within 80 Light-Years (24.53 Parsecs) for Habitable Worlds Observatory (HWO) Target Selection**")

with st.expander("📖 Read Full Introduction, Detection Methods & Habitable Worlds Observatory (HWO) Context", expanded=False):
    st.markdown("""
    * **Exoplanet Categories:** Over 6,000 confirmed exoplanets span **Gas Giants** (including hot Jupiters), **Neptunian Worlds** (including mini-Neptunes), **Super-Earths**, and rocky **Terrestrial Planets**.
    * **Detection & Characterization:** **Transit** (radius & period), **Radial Velocity** (mass via Doppler wobble), **Atmospheric Spectroscopy** (JWST biosignature gases like $H_2O$, $CO_2$, $CH_4$), and **Direct Imaging / Microlensing**.
    * **Habitable Worlds Observatory (HWO):** NASA's flagship direct-imaging mission designed to suppress host-star glare with a coronagraph/starshade and obtain atmospheric spectra for **~25 potentially habitable Earth-sized exoplanets** in the solar neighborhood.
    * **Methodology:** Uses conservative **Kopparapu et al. (2013, 2014)** runaway-greenhouse (inner) and maximum-greenhouse (outer) Habitable Zone limits; incomplete literature parameters are marked `"Uncertain"`.
    """)

df = pd.read_csv("exoplanets.csv", on_bad_lines="skip").dropna(subset=["Planet Name"])
df["Distance (ly)"] = pd.to_numeric(df["Distance (ly)"], errors="coerce")
df = df[df["Distance (ly)"] <= 80.0].drop_duplicates(subset=["Planet Name"]).sort_values("Distance (ly)").reset_index(drop=True)
df["T_num"] = pd.to_numeric(df["Equilibrium Temp (K)"].astype(str).str.replace("~","",regex=False).str.replace("*","",regex=False), errors="coerce")
df["A_num"] = pd.to_numeric(df["Semimajor Axis (AU)"], errors="coerce")

st.sidebar.header("Filter HWO Sample (<= 80 ly)")
v_opts = [v for v in ["Within HZ", "Interior to HZ", "Outside HZ", "Uncertain"] if v in df["HZ Verdict"].dropna().unique()]
verdicts = st.sidebar.multiselect("Habitable Zone Verdict", v_opts, default=v_opts)
max_d = st.sidebar.slider("Max Distance (Light-Years)", 4.0, 80.0, 80.0)
q_str = st.sidebar.text_input("Search Star or Planet")

filt = df[(df["HZ Verdict"].isin(verdicts)) & (df["Distance (ly)"] <= max_d)]
if q_str:
    filt = filt[filt["Host Star"].astype(str).str.contains(q_str, case=False) | filt["Planet Name"].astype(str).str.contains(q_str, case=False)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Planets Shown (<= 80 ly)", len(filt))
c2.metric("Within Habitable Zone", len(filt[filt["HZ Verdict"] == "Within HZ"]))
c3.metric("Host Star Systems", filt["Host Star"].nunique())
c4.metric("Avg Temp (K)", round(filt["T_num"].mean(), 1) if filt["T_num"].notna().any() else "N/A")

st.subheader("Orbital Distance (AU) vs. Equilibrium Temperature (K)")
p_df = filt.dropna(subset=["A_num", "T_num"])
p_df = p_df[p_df["A_num"] < 50]
if not p_df.empty:
    st.scatter_chart(p_df.rename(columns={"A_num": "Semimajor Axis (AU)", "T_num": "Equilibrium Temp (K)"}), x="Semimajor Axis (AU)", y="Equilibrium Temp (K)", color="HZ Verdict")

st.subheader("Full 19-Parameter Exoplanet Catalogue (Strictly <= 80 Light-Years)")
st.dataframe(filt.drop(columns=["T_num", "A_num"]), use_container_width=True)
