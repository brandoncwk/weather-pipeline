from pathlib import Path

import duckdb
import plotly.express as px
import streamlit as st

DB_FILE = Path(__file__).resolve().parent.parent / "weather.duckdb"

st.set_page_config(page_title="Weather Pipeline Dashboard", layout="wide")


@st.cache_data(ttl=3600)
def load_data():
    con = duckdb.connect(str(DB_FILE), read_only=True)
    df = con.execute("""
        SELECT city, time, temperature_2m, precipitation
        FROM weather
        ORDER BY time
    """).df()
    con.close()
    return df


df = load_data()

st.title("Weather Pipeline Dashboard")
st.caption(f"Latest data point: {df['time'].max():%Y-%m-%d %H:%M} UTC")

all_cities = sorted(df["city"].unique())
selected = st.multiselect("Cities", all_cities, default=all_cities)

if not selected:
    st.warning("Select at least one city.")
    st.stop()

filtered = df[df["city"].isin(selected)]

columns = st.columns(len(selected))
for col, city in zip(columns, selected):
    city_data = filtered[filtered["city"] == city]
    col.metric(f"{city}: average temperature", f"{city_data['temperature_2m'].mean():.1f} °C")

st.subheader("Temperature")
st.plotly_chart(
    px.line(filtered, x="time", y="temperature_2m", color="city",
            labels={"temperature_2m": "Temperature (°C)", "time": "Time (UTC)"})
)

st.subheader("Precipitation")
st.plotly_chart(
    px.bar(filtered, x="time", y="precipitation", color="city", barmode="group",
           labels={"precipitation": "Precipitation (mm)", "time": "Time (UTC)"})
)

with st.expander("View raw data"):
    st.dataframe(filtered)