import streamlit as st
import pandas as pd

st.set_page_config(page_title="HWO Solar Neighborhood Exoplanet Catalogue", page_icon="🪐", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 55%, #3a506b 100%);
        padding: 2.2rem;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 1.5rem;
        border: 1px solid #5bc0be;
        box-shadow: 0 4px 16px rgba(11, 19, 43, 0.25);
    }
    .main-header h1 { color: #ffffff; margin-bottom: 0.4rem; font-size: 2.1rem; }
    .main-header p { color: #e0fbfc; font-size: 1.08rem; margin: 0; }
    .spotlight-box {
        background-color: #f0fdf4;
        border-left: 5px solid #10b981;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: #064e3b;
    }
    .publisher-footer {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
        color: #5bc0be;
        padding: 1.3rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.15rem;
        margin-top: 2rem;
        border: 1px solid #3a506b;
    }
</style>
<div class="main-header">
    <h1>🪐 Solar Neighborhood Exoplanet Catalogue (Within 80 Light-Years)</h1>
    <p>Comprehensive Characterization of <b>420 Confirmed & Candidate Exoplanets Across 248 Host Star Systems</b> for NASA Habitable Worlds Observatory (HWO) Target Selection</p>
</div>
""", unsafe_allow_html=True)

st.subheader("📖 Scientific Introduction, Detection Methods & Habitable Worlds Observatory (HWO) Context")
st.markdown("""
### What Are Exoplanets?
An **exoplanet** (extrasolar planet) is any planet located outside our Solar System. While most orbit stars other than our Sun, some drift freely through space without a host star and are known as **rogue planets**. Astronomers have confirmed over 6,000 exoplanets across the Milky Way, grouped into four primary classes:
* **Gas Giants:** Massive worlds composed mostly of hydrogen and helium, similar to Jupiter and Saturn (including scorching close-in *"hot Jupiters"*).
* **Neptunian Worlds:** Similar in size to Uranus and Neptune, featuring thick hydrogen-helium atmospheres surrounding rocky or heavy-element cores, alongside smaller *"mini-Neptunes"*.
* **Super-Earths:** Worlds more massive than Earth yet lighter than ice giants like Neptune, composed of rock, gas, or a combination of both.
* **Terrestrial Planets:** Roughly Earth-sized or smaller worlds composed primarily of rock, silicate, water, or carbon.

### How Astronomers Detect and Characterize Them
* **The Transit Method:** Measuring tiny, regular dips in starlight as a planet crosses in front of its star reveals its physical radius (R⊕) and orbital period.
* **Radial Velocity (The Wobble Method):** Tracking Doppler shifts in a star's light spectrum caused by an orbiting planet's gravitational tug reveals planetary mass (M⊕).
* **Atmospheric Spectroscopy:** Analyzing starlight filtered through a transiting planet's atmosphere with telescopes like JWST identifies biosignature-relevant gases such as H₂O, CO₂, and CH₄.
* **Direct Imaging & Microlensing:** Coronagraphs and starshades suppress host-star glare to capture reflected or thermal light from planets, while gravitational microlensing uses a foreground star's gravity to magnify distant systems.

### Habitable Worlds Observatory (HWO) & Habitability Modeling
* **Habitable Worlds Observatory (HWO):** A flagship priority of NASA's astrophysics program designed to directly image approximately **25 potentially habitable Earth-sized exoplanets** around nearby stars and analyze their reflected light spectra for **biosignatures**.
* **Habitable Zone Boundaries:** Calculated from conservative **Kopparapu et al. (2013, 2014)** runaway-greenhouse (inner) and maximum-greenhouse (outer) limits using stellar luminosity (L☉) and effective temperature.
""")

df = pd.read_csv("exoplanets.csv", on_bad_lines="skip").dropna(subset=["Planet Name"])
df["Distance (ly)"] = pd.to_numeric(df["Distance (ly)"].astype(str).str.replace("~", "", regex=False).str.strip(), errors="coerce")
df = df[df["Distance (ly)"].isna() | (df["Distance (ly)"] <= 80.0)].sort_values("Distance (ly)").reset_index(drop=True)
df["T_num"] = pd.to_numeric(df["Equilibrium Temp (K)"].astype(str).str.replace("~", "", regex=False).str.replace("*", "", regex=False).str.replace(",", "", regex=False), errors="coerce")
df["A_num"] = pd.to_numeric(df["Semimajor Axis (AU)"].astype(str).str.replace("~", "", regex=False).str.replace(",", "", regex=False), errors="coerce")
df["R_num"] = pd.to_numeric(df["Radius (R_Earth)"].astype(str).str.replace("~", "", regex=False).str.replace(",", "", regex=False), errors="coerce")

st.sidebar.header("🔭 Filter HWO Target Sample")
verdict_opts = sorted(df["HZ Verdict"].dropna().unique())
verdicts = st.sidebar.multiselect("Habitable Zone Verdict", verdict_opts, default=verdict_opts)

def star_group(sp):
    s = str(sp).replace("~", "").strip()
    for ch in ["M", "K", "G", "F", "A", "L", "Y"]:
        if s.startswith(ch):
            return f"{ch}-Type"
    return "Other / Unknown"

df["Star Class"] = df["Spectral Type"].apply(star_group)
class_opts = sorted(df["Star Class"].unique())
star_classes = st.sidebar.multiselect("Host Star Spectral Class", class_opts, default=class_opts)

status_opts = sorted(df["Detection Status"].dropna().unique())
statuses = st.sidebar.multiselect("Detection Status", status_opts, default=status_opts)

max_d = st.sidebar.slider("Max Distance from Sun (Light-Years)", 4.0, 80.0, 80.0)
q_str = st.sidebar.text_input("Search Host Star or Planet Name")

filt = df[
    (df["HZ Verdict"].isin(verdicts)) &
    (df["Star Class"].isin(star_classes)) &
    (df["Detection Status"].isin(statuses)) &
    (df["Distance (ly)"].isna() | (df["Distance (ly)"] <= max_d))
].reset_index(drop=True)
if q_str:
    filt = filt[
        filt["Host Star"].astype(str).str.contains(q_str, case=False, na=False) |
        filt["Planet Name"].astype(str).str.contains(q_str, case=False, na=False)
    ].reset_index(drop=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Catalogued Exoplanets", len(filt))
c2.metric("Within Habitable Zone", len(filt[filt["HZ Verdict"] == "Within HZ"]))
c3.metric("Host Star Systems", filt["Host Star"].nunique())
c4.metric("Avg Equilibrium Temp (K)", round(filt["T_num"].mean(), 1) if filt["T_num"].notna().any() else "N/A")

st.subheader("🎯 Top Priority HWO Rocky Habitable-Zone Candidates (Radius ≤ 1.8 R⊕)")
st.markdown("""
<div class="spotlight-box">
    <b>Scientific Target Selection:</b> Filtering the 80 light-year solar neighborhood for planets orbiting <b>Within the Habitable Zone</b> with terrestrial/super-Earth radii (<b>≤ 1.8 R⊕</b>) isolates prime rocky candidates for future Habitable Worlds Observatory direct-imaging spectroscopy.
</div>
""", unsafe_allow_html=True)

hwo_top = filt[(filt["HZ Verdict"] == "Within HZ") & (filt["R_num"] <= 1.8)][
    ["Planet Name", "Host Star", "Distance (ly)", "Spectral Type", "Mass (M_Earth)", "Radius (R_Earth)", "Semimajor Axis (AU)", "Equilibrium Temp (K)", "Incident Flux (S_Earth)"]
].reset_index(drop=True)
if not hwo_top.empty:
    hwo_top.insert(0, "No.", range(1, len(hwo_top) + 1))
    st.dataframe(hwo_top, use_container_width=True, hide_index=True)
else:
    st.info("Adjust sidebar filters to display rocky Habitable Zone candidates (≤ 1.8 R⊕).")

st.subheader("📊 Orbital Distance (AU) vs. Equilibrium Temperature (K)")
p_df = filt[["A_num", "T_num", "HZ Verdict"]].dropna()
p_df = p_df[p_df["A_num"] < 50].rename(columns={"A_num": "Semimajor Axis (AU)", "T_num": "Equilibrium Temp (K)"})
if not p_df.empty:
    st.scatter_chart(p_df, x="Semimajor Axis (AU)", y="Equilibrium Temp (K)", color="HZ Verdict")

col_title, col_dl = st.columns([4, 1])
with col_title:
    st.subheader("🪐 Complete 19-Parameter Exoplanet & Host Star Catalogue")
with col_dl:
    clean_export = filt.drop(columns=["T_num", "A_num", "R_num", "Star Class"]).copy()
    clean_export.insert(0, "No.", range(1, len(clean_export) + 1))
    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=clean_export.to_csv(index=False).encode("utf-8"),
        file_name="HWO_Solar_Neighborhood_Exoplanet_Catalogue.csv",
        mime="text/csv",
    )

def style_verdict(val):
    v = str(val)
    if v == "Within HZ":
        return "background-color: #d1fae5; color: #065f46; font-weight: 700;"
    elif v == "Interior to HZ":
        return "background-color: #fef3c7; color: #92400e; font-weight: 600;"
    elif v == "Outside HZ":
        return "background-color: #e0f2fe; color: #075985; font-weight: 600;"
    return "background-color: #f3f4f6; color: #374151;"

display_table = filt.drop(columns=["T_num", "A_num", "R_num", "Star Class"]).copy()
display_table.insert(0, "No.", range(1, len(display_table) + 1))
st.dataframe(display_table.style.map(style_verdict, subset=["HZ Verdict"]), use_container_width=True, hide_index=True)

st.subheader("📚 Data Notes, Equations & Methodology")
st.markdown("""
* **Scope:** Every confirmed planet (plus candidate Proxima Centauri c) whose host star lies within **80 light-years** (248 host stars, 420 planets), ranked by distance from the Sun.
* **Habitable Zone Model:** Conservative **Kopparapu et al. (2013, 2014)** runaway-greenhouse (inner) and maximum-greenhouse (outer) limits using stellar luminosity and effective temperature.
* **Approximations (`~`):** Marks estimated or recalled literature values (main-sequence stellar relations after Pecaut & Mamajek; Chen & Kipping style planetary mass–radius relation).
* **Equilibrium Temperature & Flux:** Calculated via `S = L / a²` and `Teq = 255 K × S^0.25` (Bond albedo 0.3, full heat redistribution) where archive values were unavailable.
""")

st.markdown("""
<div class="publisher-footer">
    <b>Published By: Esmelealem Haddis Bezie (Citizen Scientist)</b>
</div>
""", unsafe_allow_html=True)
