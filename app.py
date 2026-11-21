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
    .priority-card-blue {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 6px solid #2563eb;
        padding: 1.3rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.2rem;
        color: #1e3a8a;
    }
    .priority-card-green {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-left: 6px solid #059669;
        padding: 1.3rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.2rem;
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

col_title, col_dl = st.columns([3, 1])
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

st.markdown("---")
st.subheader("🔭 HWO Observation Priority Rankings: Proximity & Biosignature Potential")
st.markdown(
    "Based on this 420-planet characterization, the **Habitable Worlds Observatory (HWO)** (alongside JWST transmission/emission follow-up for transiting systems such as **TRAPPIST-1**) will prioritize targets along two complementary axes: **(1) Distance from the Sun** (maximizing angular separation and photon flux) and **(2) Conservative Habitable-Zone & Biosignature Probability**."
)

col_prox, col_hab = st.columns(2)

with col_prox:
    st.markdown("""
    <div class="priority-card-blue">
        <h4>1. Priority by Distance from Sun (Angular Separation & Flux)</h4>
        <p>Closer planetary systems provide larger angular star–planet separation (<i>θ = a / d</i>) for coronagraphic starlight suppression and higher reflected-light photon rates.</p>
        <b>Top 10 Nearest Exoplanet Targets (4.24 – 10.72 ly):</b>
        <ol>
            <li><b>Proxima Centauri b</b> (4.244 ly — M5.5 V, Within HZ)</li>
            <li><b>Proxima Centauri c</b> (4.244 ly — M5.5 V, Candidate)</li>
            <li><b>Proxima Centauri d</b> (4.244 ly — M5.5 V, Sub-Earth)</li>
            <li><b>Barnard's Star b</b> (5.957 ly — M3.5–4 V)</li>
            <li><b>Barnard's Star c</b> (5.957 ly — M3.5–4 V)</li>
            <li><b>Barnard's Star d</b> (5.957 ly — M3.5–4 V)</li>
            <li><b>Barnard's Star e</b> (5.957 ly — M3.5–4 V)</li>
            <li><b>Luhman 16 A b</b> (6.500 ly — L7.5 Brown Dwarf)</li>
            <li><b>Epsilon Eridani b</b> (10.445 ly — K2 V, Wide Orbit)</li>
            <li><b>GJ 887 e</b> (10.720 ly — M1 V, Bright Red Dwarf)</li>
        </ol>
        <b>Top 50 Nearest Exoplanet Targets (Range: 4.244 – 18.201 ly):</b>
        <p>Spans the <b>50 closest confirmed & candidate exoplanets</b> across the <b>24 nearest host star systems</b>, beginning at <b>Proxima Centauri b (4.244 ly)</b> and extending outward through <i>Barnard's Star, Epsilon Eridani, GJ 887, Ross 128, GJ 725 A, GJ 15 A, Tau Ceti, Epsilon Indi A, GJ 1061, YZ Ceti, Teegarden's Star, Kapteyn, Wolf 1061, GJ 9066, GJ 674, GJ 687, GJ 876, GJ 1002, GJ 832, GJ 682, GJ 3323</i>, and concluding at <b>GJ 251 c (18.201 ly)</b>.</p>
    </div>
    """, unsafe_allow_html=True)

with col_hab:
st.markdown("""
<div class="publisher-footer">
    <b>Published By: Esmelealem Haddis Bezie (Citizen Scientist)</b>
</div>
""", unsafe_allow_html=True)

