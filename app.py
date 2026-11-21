import streamlit as st
import pandas as pd

st.set_page_config(page_title="HWO Nearby Exoplanet Catalogue", layout="wide")
st.title("🪐 Solar Neighborhood Exoplanet Catalogue (HWO Target Sample)")
st.write("Complete 19-parameter characterization of 60 exoplanets across the 30 nearest host star systems.")

df = pd.read_csv("exoplanets.csv")
df["Temp_Numeric"] = df["Equilibrium Temp (K)"].astype(str).str.replace("~", "", regex=False).str.replace("*", "", regex=False).astype(float)

st.sidebar.header("Filter HWO Target Sample")
verdicts = st.sidebar.multiselect("Habitable Zone Verdict", ["Within HZ", "Interior to HZ", "Outside HZ"], default=["Within HZ", "Interior to HZ", "Outside HZ"])
max_dist = st.sidebar.slider("Max Distance (Light-Years)", 4.0, 22.0, 22.0)
search = st.sidebar.text_input("Search Star or Planet")

filtered = df[(df["HZ Verdict"].isin(verdicts)) & (df["Distance (ly)"] <= max_dist)]
if search:
    filtered = filtered[filtered["Host Star"].str.contains(search, case=False) | filtered["Planet Name"].str.contains(search, case=False)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Planets Shown", len(filtered))
c2.metric("Within Habitable Zone", len(filtered[filtered["HZ Verdict"] == "Within HZ"]))
c3.metric("Nearest System (ly)", round(filtered["Distance (ly)"].min(), 3) if not filtered.empty else "N/A")
c4.metric("Avg Temp (K)", round(filtered["Temp_Numeric"].mean(), 1) if not filtered.empty else "N/A")

st.subheader("Orbital Distance (AU) vs. Equilibrium Temperature (K)")
if not filtered.empty:
    st.scatter_chart(filtered.rename(columns={"Temp_Numeric": "Equilibrium Temperature (K)"}), x="Semimajor Axis (AU)", y="Equilibrium Temperature (K)", color="HZ Verdict")

st.subheader("Full 19-Parameter Exoplanet & Host Star Catalogue")
st.dataframe(filtered.drop(columns=["Temp_Numeric"]), use_container_width=True)
