import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="HWO Solar Neighborhood Exoplanet Catalogue", layout="wide")
st.title("🪐 Solar Neighborhood Exoplanet Catalogue")
st.markdown(
    "**Characterizing 400+ Confirmed & Candidate Exoplanets Across the Solar Neighborhood "
    "for Future Habitable Worlds Observatory (HWO) Target Selection**"
)

with st.expander("📖 Read Full Introduction, Detection Methods & Habitable Worlds Observatory (HWO) Context", expanded=True):
    st.markdown("""
    ### What Are Exoplanets?
    An **exoplanet** (extrasolar planet) is any planet located outside our Solar System. While most orbit stars other than our Sun, some drift freely through space without a host star and are known as **rogue planets**. Astronomers have confirmed over 6,000 exoplanets across the Milky Way, revealing a vast diversity of worlds grouped into four main categories:
    * **Gas Giants:** Massive worlds composed mostly of hydrogen and helium, similar to Jupiter and Saturn (including scorching close-in *"hot Jupiters"*).
    * **Neptunian Worlds:** Similar in size to Uranus and Neptune, featuring thick hydrogen-helium atmospheres surrounding rocky or heavy-element cores, alongside smaller *"mini-Neptunes"*.
    * **Super-Earths:** Worlds more massive than Earth yet lighter than ice giants like Neptune, composed of rock, gas, or a combination of both.
    * **Terrestrial Planets:** Roughly Earth-sized or smaller worlds composed primarily of rock, silicate, water, or carbon.

    ### How Astronomers Detect and Characterize Them
    * **The Transit Method:** Measuring the tiny, regular dimming of starlight as a planet passes in front of its star reveals its physical radius and orbital period.
    * **Radial Velocity (The Wobble Method):** Tracking Doppler shifts in a star's light spectrum caused by an orbiting planet's gravitational tug reveals the planet's mass.
    * **Atmospheric Spectroscopy:** Studying starlight filtered through a transiting planet's atmosphere with telescopes like JWST identifies molecules such as water vapor, carbon dioxide, and methane.
    * **Direct Imaging & Microlensing:** Coronagraphs and starshades block stellar glare to capture faint infrared light from planets, while gravitational microlensing uses a foreground star's gravity to magnify a distant planetary system.

    ### Why Studying Exoplanets & the Habitable Worlds Observatory (HWO) Matter
    * **Planetary Formation & Habitability:** Observing diverse star systems tests how planets form and identifies worlds inside the **Habitable Zone (Goldilocks Zone)**, where temperatures allow liquid water to exist on a planetary surface.
    * **Habitable Worlds Observatory (HWO):** Proposed as a flagship priority of NASA's astrophysics program, HWO will use an advanced coronagraph (and potentially a starshade) to directly image approximately **25 potentially habitable Earth-sized exoplanets** around nearby stars and search their reflected light spectra for **biosignatures**.
    * **Scope of This Catalogue:** Combining curated literature entries (Systems 1–80) with confirmed exoplanets across the wider solar neighborhood, this interactive catalogue computes stellar luminosity, equilibrium temperature, incident stellar flux, and conservative **Kopparapu et al. (2013, 2014)** Habitable Zone boundaries—marking incomplete literature parameters as `"Uncertain"`.
    """)

df = pd.read_csv("exoplanets.csv", on_bad_lines="skip")
df = df.dropna(subset=["Planet Name"]).drop_duplicates(subset=["Planet Name"], keep="first").reset_index(drop=True)
df["Distance (ly)"] = pd.to_numeric(df["Distance (ly)"], errors="coerce")
df["Temp_Numeric"] = pd.to_numeric(df["Equilibrium Temp (K)"].astype(str).str.replace("~", "", regex=False).str.replace("*", "", regex=False), errors="coerce")
df["Axis_Numeric"] = pd.to_numeric(df["Semimajor Axis (AU)"], errors="coerce")

st.sidebar.header("Filter HWO Target Sample")
verdict_opts = [v for v in ["Within HZ", "Interior to HZ", "Outside HZ", "Uncertain"] if v in df["HZ Verdict"].dropna().unique()]
verdicts = st.sidebar.multiselect("Habitable Zone Verdict", verdict_opts, default=verdict_opts)

max_available_dist = float(np.ceil(df["Distance (ly)"].max())) if df["Distance (ly)"].notna().any() else 2500.0
max_dist = st.sidebar.slider("Max Distance from Sun (Light-Years)", 4.0, max_available_dist, max_available_dist)
search = st.sidebar.text_input("Search Host Star or Planet")

filtered = df[
    (df["HZ Verdict"].isin(verdicts)) &
    (df["Distance (ly)"].isna() | (df["Distance (ly)"] <= max_dist))
]
if search:
    filtered = filtered[
        filtered["Host Star"].astype(str).str.contains(search, case=False) |
        filtered["Planet Name"].astype(str).str.contains(search, case=False)
    ]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Planets Shown", len(filtered))
c2.metric("Within Habitable Zone", len(filtered[filtered["HZ Verdict"] == "Within HZ"]))
c3.metric("Host Star Systems", filtered["Host Star"].nunique())
c4.metric("Avg Equilibrium Temp (K)", round(filtered["Temp_Numeric"].mean(), 1) if filtered["Temp_Numeric"].notna().any() else "N/A")

st.subheader("Orbital Distance (AU) vs. Equilibrium Temperature (K)")
plot_df = filtered.dropna(subset=["Axis_Numeric", "Temp_Numeric"])
plot_df = plot_df[plot_df["Axis_Numeric"] < 50]
if not plot_df.empty:
    chart_df = plot_df.rename(columns={"Axis_Numeric": "Semimajor Axis (AU) [Excl. >50 AU]", "Temp_Numeric": "Equilibrium Temperature (K)"})
    st.scatter_chart(chart_df, x="Semimajor Axis (AU) [Excl. >50 AU]", y="Equilibrium Temperature (K)", color="HZ Verdict")

st.subheader("Full 19-Parameter Exoplanet & Host Star Catalogue")
st.dataframe(filtered.drop(columns=["Temp_Numeric", "Axis_Numeric"]), use_container_width=True)

with st.expander("Habitable Zone Equations, Data Notes & Citations"):
    st.markdown("""
    * **Habitable Zone Boundaries:** Calculated from the conservative Kopparapu et al. (2013, 2014) runaway-greenhouse (inner) and maximum-greenhouse (outer) limits using stellar luminosity and effective temperature. Incomplete literature parameters are labeled `"Uncertain"`.
    * **Mass Notation (`>=`):** Marks minimum mass ($M \\sin i$) from radial-velocity detections; values without `>=` represent true-mass solutions.
    * **Equilibrium Temperature:** Calculated assuming a Bond albedo of 0.3 and full heat redistribution (`*` denotes measured internal-heat temperature).
    * **Data Sources:** Curated literature synthesis (Systems 1–80) merged with **NASA Exoplanet Archive (`pscomppars`)** records.
    """)
