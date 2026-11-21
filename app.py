import streamlit as st
import pandas as pd

st.set_page_config(page_title="HWO Solar Neighborhood Exoplanet Catalogue", page_icon="🪐", layout="wide")

# Custom Deep-Space Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 50%, #3a506b 100%);
        padding: 2rem;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 1.5rem;
        border-left: 6px solid #5bc0be;
    }
    .main-header h1 { color: #ffffff; margin: 0; font-size: 2.2rem; }
    .main-header p { color: #cbd5e1; margin-top: 0.5rem; font-size: 1.05rem; }
    .publisher-footer {
        background-color: #0b132b;
        color: #ffffff;
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 2rem;
        border-top: 4px solid #5bc0be;
        font-size: 1.1rem;
    }
</style>
<div class="main-header">
    <h1>🪐 Solar Neighborhood Exoplanet Catalogue (Within 80 Light-Years)</h1>
    <p>Comprehensive Characterization of <b>420 Exoplanets Across 248 Host Star Systems</b> for NASA's Habitable Worlds Observatory (HWO) Target Selection</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 Introduction, Exoplanet Classes, Detection Methods & Habitable Worlds Observatory (HWO)", expanded=False):
    st.markdown("""
    ### What Are Exoplanets?
    An **exoplanet** (extrasolar planet) is any planet located outside our Solar System. While most orbit stars other than our Sun, some drift freely through space without a host star and are known as **rogue planets**. Astronomers have confirmed over 6,000 exoplanets across the Milky Way, grouped into four main categories:
    * **Gas Giants:** Massive worlds composed mostly of hydrogen and helium, similar to Jupiter and Saturn (including scorching close-in *"hot Jupiters"*).
    * **Neptunian Worlds:** Similar in size to Uranus and Neptune, featuring thick hydrogen-helium atmospheres surrounding rocky or heavy-element cores, alongside smaller *"mini-Neptunes"*.
    * **Super-Earths:** Worlds more massive than Earth yet lighter than ice giants like Neptune, composed of rock, gas, or a combination of both.
    * **Terrestrial Planets:** Roughly Earth-sized or smaller worlds composed primarily of rock, silicate, water, or carbon.

    ### How Astronomers Detect and Characterize Them
    * **The Transit Method:** Measuring the tiny, regular dimming of starlight as a planet passes in front of its star reveals its physical size and orbital period.
    * **Radial Velocity (The Wobble Method):** Tracking shifts in a star's light spectrum caused by an orbiting planet's gravitational tug reveals the planet's mass.
    * **Atmospheric Spectroscopy:** Studying starlight filtered through a transiting planet's atmosphere with telescopes like JWST identifies molecules like water vapor, carbon dioxide, or methane.
    * **Direct Imaging & Microlensing:** Coronagraphs and starshades block stellar glare to capture faint infrared images, while gravitational microlensing uses a passing star's gravity to magnify distant planetary systems.

    ### Habitable Worlds Observatory (HWO) & Scope of This Catalogue
    Proposed as a flagship priority of NASA's future astrophysics program, **HWO** will use an advanced coronagraph (and potentially a starshade) to directly image approximately **25 potentially habitable worlds** in the solar neighborhood and analyze their reflected light spectra for **biosignatures**. This catalogue characterizes **420 exoplanets across 248 host star systems within 80 light-years (24.5 parsecs)**, evaluating each world against conservative **Kopparapu et al. (2013, 2014)** Habitable Zone boundaries.
    """)

df = pd.read_csv("exoplanets.csv", on_bad_lines="skip").dropna(subset=["Planet Name"])
df["Distance (ly)"] = pd.to_numeric(df["Distance (ly)"], errors="coerce")
df = df[df["Distance (ly)"] <= 80.0].sort_values("Distance (ly)").reset_index(drop=True)
df["T_num"] = pd.to_numeric(df["Equilibrium Temp (K)"].astype(str).str.replace("~","",regex=False).str.replace(",","",regex=False), errors="coerce")
df["A_num"] = pd.to_numeric(df["Semimajor Axis (AU)"].astype(str).str.replace("~","",regex=False).str.replace(",","",regex=False), errors="coerce")

# Sidebar Filters
st.sidebar.markdown("## 🔭 Catalogue Filters")
v_opts = [v for v in ["Within HZ", "Interior to HZ", "Outside HZ", "Unknown"] if v in df["HZ Verdict"].dropna().unique()]
verdicts = st.sidebar.multiselect("Habitable Zone Classification", v_opts, default=v_opts)

status_opts = sorted(df["Detection Status"].dropna().unique().tolist())
statuses = st.sidebar.multiselect("Detection Status", status_opts, default=status_opts)

max_d = st.sidebar.slider("Max Distance from Sun (Light-Years)", 4.0, 80.0, 80.0)
q_str = st.sidebar.text_input("Search Host Star or Planet Name")

filt = df[
    (df["HZ Verdict"].isin(verdicts)) &
    (df["Detection Status"].isin(statuses)) &
    (df["Distance (ly)"] <= max_d)
]
if q_str:
    filt = filt[
        filt["Host Star"].astype(str).str.contains(q_str, case=False) |
        filt["Planet Name"].astype(str).str.contains(q_str, case=False)
    ]

# Top Metrics Bar
c1, c2, c3, c4 = st.columns(4)
c1.metric("🪐 Exoplanets Shown", len(filt))
c2.metric("🌱 Within Habitable Zone", len(filt[filt["HZ Verdict"] == "Within HZ"]))
c3.metric("⭐ Host Star Systems", filt["Host Star"].nunique())
c4.metric("🌡️ Avg Equilibrium Temp (K)", round(filt["T_num"].mean(), 1) if filt["T_num"].notna().any() else "N/A")

# Interactive Chart
st.subheader("📊 Orbital Distance (AU) vs. Equilibrium Temperature (K)")
p_df = filt[["A_num", "T_num", "HZ Verdict"]].dropna()
p_df = p_df[p_df["A_num"] < 50].rename(columns={"A_num": "Semimajor Axis (AU)", "T_num": "Equilibrium Temp (K)"})
if not p_df.empty:
    st.scatter_chart(p_df, x="Semimajor Axis (AU)", y="Equilibrium Temp (K)", color="HZ Verdict")

# Full Catalogue Table
st.subheader("📋 Complete 19-Parameter Solar Neighborhood Exoplanet Catalogue")
st.dataframe(filt.drop(columns=["T_num", "A_num"]), use_container_width=True, height=550)

# Data Notes & Methodology Expander
with st.expander("📝 Habitable Zone Equations, Data Notes & Literature Methodology"):
    st.markdown("""
    * **Scope:** Lists every confirmed exoplanet (plus candidate Proxima Centauri c) within **80 light-years** (**248 host stars, 420 planets**), ranked by distance from the Sun (`distance in ly = parsecs × 3.26156`).
    * **Habitable Zone Model:** Calculated using conservative **Kopparapu et al. (2013, 2014)** runaway-greenhouse (inner) and maximum-greenhouse (outer) limits from stellar luminosity and effective temperature (extrapolated at 2,600 K / 7,200 K boundaries where needed; omitted for brown-dwarf hosts).
    * **Estimated Values (`~`):** Marks approximate literature values or main-sequence / mass–radius / equilibrium temperature ($A_B = 0.3$) estimates where direct measurements are unavailable.
    * **Verdict Summary (Full 420 Sample):** **41** Within HZ, **282** Interior to HZ, **93** Outside HZ, and **4** Unknown.
    """)

# Bold Publisher Footer
st.markdown("""
<div class="publisher-footer">
    <b>Published By: Esmelealem Haddis Bezie (Citizen Scientist)</b>
</div>
""", unsafe_allow_html=True)
