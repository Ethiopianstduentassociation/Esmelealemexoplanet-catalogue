import streamlit as st
import pandas as pd
import numpy as np
import urllib.request

st.set_page_config(page_title="HWO Solar Neighborhood Exoplanet Catalogue", layout="wide")
st.title("🪐 Solar Neighborhood Exoplanet Catalogue (Within 80 Light-Years)")
st.markdown(
    "**Characterizing 400+ Confirmed & Candidate Exoplanets Within 80 Light-Years (24.53 Parsecs) "
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
    * **Scope of This Catalogue:** Combining **161 curated literature entries** (Systems 1–80) with live data queried directly from the **NASA Exoplanet Archive** out to **80 light-years (24.53 parsecs)**, this catalogue automatically computes stellar luminosity, equilibrium temperature, incident stellar flux, and conservative **Kopparapu et al. (2013, 2014)** Habitable Zone boundaries—marking incomplete literature parameters as `"Uncertain"`.
    """)

def kopparapu_hz(lum_solar, teff):
    if pd.isna(lum_solar) or lum_solar <= 0:
        return np.nan, np.nan
    t = 5780.0 if pd.isna(teff) else float(np.clip(teff, 2600.0, 7200.0))
    dt = t - 5780.0
    s_in = 1.107 + 1.332e-4 * dt + 1.580e-8 * (dt ** 2) - 8.308e-12 * (dt ** 3) - 1.931e-15 * (dt ** 4)
    s_out = 0.356 + 6.171e-5 * dt + 1.698e-9 * (dt ** 2) - 3.198e-12 * (dt ** 3) - 5.575e-16 * (dt ** 4)
    return round(float(np.sqrt(lum_solar / s_in)), 4), round(float(np.sqrt(lum_solar / s_out)), 4)

@st.cache_data(ttl=3600)
def build_full_catalogue():
    curated_df = pd.read_csv("exoplanets.csv")
    existing_planets = set(curated_df["Planet Name"].str.lower().str.strip())

    query = (
        "select+pl_name,hostname,sy_dist,st_spectype,st_mass,st_rad,st_lum,st_teff,"
        "pl_bmasse,pl_msinie,pl_rade,pl_orbsmax,pl_orbper,pl_orbeccen,pl_eqt,pl_insol+"
        "from+pscomppars+where+sy_dist<=24.53"
    )
    url = f"https://caltech.edu{query}&format=csv"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            nasa_raw = pd.read_csv(resp)
    except Exception:
        return curated_df
    new_rows = []
    for _, r in nasa_raw.iterrows():
        pname = str(r.get("pl_name", "")).strip()
        if not pname or pname.lower() in existing_planets:
            continue
        if any(pname.lower() in ex or ex in pname.lower() for ex in existing_planets if len(ex) > 6):
            continue

        dist_ly = round(float(r["sy_dist"]) * 3.26156, 3) if pd.notna(r.get("sy_dist")) else np.nan
        if pd.isna(dist_ly) or dist_ly > 80.0:
            continue

        st_rad = float(r["st_rad"]) if pd.notna(r.get("st_rad")) else np.nan
        st_teff = float(r["st_teff"]) if pd.notna(r.get("st_teff")) else np.nan
        if pd.notna(r.get("st_lum")):
            st_lum = round(10 ** float(r["st_lum"]), 5)
        elif pd.notna(st_rad) and pd.notna(st_teff):
            st_lum = round((st_rad ** 2) * ((st_teff / 5772.0) ** 4), 5)
        else:
            st_lum = np.nan

        hz_in, hz_out = kopparapu_hz(st_lum, st_teff)
        a_au = float(r["pl_orbsmax"]) if pd.notna(r.get("pl_orbsmax")) else np.nan

        if pd.notna(a_au) and pd.notna(hz_in) and pd.notna(hz_out):
            if a_au < hz_in:
                verdict = "Interior to HZ"
            elif a_au <= hz_out:
                verdict = "Within HZ"
            else:
                verdict = "Outside HZ"
        else:
            verdict = "Uncertain"

        if pd.notna(r.get("pl_bmasse")):
            mass_str = f"{round(float(r['pl_bmasse']), 2)}"
        elif pd.notna(r.get("pl_msinie")):
            mass_str = f">={round(float(r['pl_msinie']), 2)}"
        else:
            mass_str = "Uncertain"

        rad_str = f"{round(float(r['pl_rade']), 2)}" if pd.notna(r.get("pl_rade")) else "Uncertain"
        per_val = round(float(r["pl_orbper"]), 3) if pd.notna(r.get("pl_orbper")) else "Uncertain"
        ecc_str = f"{round(float(r['pl_orbeccen']), 3)}" if pd.notna(r.get("pl_orbeccen")) else "Uncertain"

        if pd.notna(r.get("pl_eqt")):
            eqt_str = f"{int(round(float(r['pl_eqt'])))}"
        elif pd.notna(st_lum) and pd.notna(a_au) and a_au > 0:
            eqt_calc = 278.5 * ((st_lum / (a_au ** 2)) ** 0.25) * ((1.0 - 0.3) ** 0.25)
            eqt_str = f"{int(round(eqt_calc))}"
        else:
            eqt_str = "Uncertain"

        if pd.notna(r.get("pl_insol")):
            flux_str = f"{round(float(r['pl_insol']), 3)}"
        elif pd.notna(st_lum) and pd.notna(a_au) and a_au > 0:
            flux_str = f"{round(st_lum / (a_au ** 2), 3)}"
        else:
            flux_str = "Uncertain"

        new_rows.append((
            str(r.get("hostname", "Uncertain")),
            dist_ly,
            str(r["st_spectype"]).strip() if pd.notna(r.get("st_spectype")) and str(r.get("st_spectype")).strip() else "Uncertain",
            round(float(r["st_mass"]), 3) if pd.notna(r.get("st_mass")) else "Uncertain",
            round(st_rad, 3) if pd.notna(st_rad) else "Uncertain",
            st_lum if pd.notna(st_lum) else "Uncertain",
            int(round(st_teff)) if pd.notna(st_teff) else "Uncertain",
            pname,
            "Confirmed (NASA)",
            mass_str,
            rad_str,
            round(a_au, 4) if pd.notna(a_au) else "Uncertain",
            per_val,
            ecc_str,
            eqt_str,
            flux_str,
            hz_in if pd.notna(hz_in) else "Uncertain",
            hz_out if pd.notna(hz_out) else "Uncertain",
            verdict
        ))

    nasa_df = pd.DataFrame(new_rows, columns=curated_df.columns)
    combined = pd.concat([curated_df, nasa_df], ignore_index=True)
    return combined.sort_values(by="Distance (ly)", ascending=True).reset_index(drop=True)

df = build_full_catalogue()
df["Temp_Numeric"] = pd.to_numeric(df["Equilibrium Temp (K)"].astype(str).str.replace("~", "", regex=False).str.replace("*", "", regex=False), errors="coerce")
df["Axis_Numeric"] = pd.to_numeric(df["Semimajor Axis (AU)"], errors="coerce")

st.sidebar.header("Filter HWO Target Sample (<= 80 ly)")
verdict_opts = [v for v in ["Within HZ", "Interior to HZ", "Outside HZ", "Uncertain"] if v in df["HZ Verdict"].unique()]
verdicts = st.sidebar.multiselect("Habitable Zone Verdict", verdict_opts, default=verdict_opts)
max_dist = st.sidebar.slider("Max Distance from Sun (Light-Years)", 4.0, 80.0, 80.0)
search = st.sidebar.text_input("Search Host Star or Planet")

filtered = df[(df["HZ Verdict"].isin(verdicts)) & (df["Distance (ly)"] <= max_dist)]
if search:
    filtered = filtered[filtered["Host Star"].str.contains(search, case=False) | filtered["Planet Name"].str.contains(search, case=False)]

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

st.subheader("Full 19-Parameter Exoplanet & Host Star Catalogue (Within 80 Light-Years)")
st.dataframe(filtered.drop(columns=["Temp_Numeric", "Axis_Numeric"]), use_container_width=True)

with st.expander("Habitable Zone Equations, Automated Pipeline & Citations"):
    st.markdown("""
    * **Automated Habitable Zone Pipeline:** For systems beyond the initial 80 curated literature systems out to 80.0 light-years (24.53 parsecs), stellar luminosity ($L/L_\\odot$), equilibrium temperature ($A_B = 0.3$), incident stellar flux ($S/S_\\oplus = L/a^2$), and conservative **Kopparapu et al. (2013, 2014)** runaway-greenhouse (inner) and maximum-greenhouse (outer) boundaries are computed directly in Python from NASA Exoplanet Archive TAP parameters. Missing parameters are labeled `"Uncertain"`.
    * **Mass Notation (`>=`):** Marks minimum mass ($M \\sin i$) from radial-velocity detections; values without `>=` represent true-mass solutions.
    * **Data Sources:** Curated literature synthesis (Systems 1–80) merged with live **NASA Exoplanet Archive (`pscomppars`)** records within 24.53 parsecs.
    """)
