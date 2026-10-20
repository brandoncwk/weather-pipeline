import requests
import pandas as pd
import duckdb

URL = "https://api.open-meteo.com/v1/forecast"
DB_FILE = "weather.duckdb"
CITIES = {
    "London": (51.5, -0.12),
    "Tokyo": (35.68, 139.69),
    "New York": (40.71, -74.01),
    "Sydney": (-33.87, 151.21),
}


def fetch_city(city, lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation",
        "past_days": 1,
        "forecast_days": 1,
        "timezone": "UTC",
    }
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    df = pd.DataFrame(response.json()["hourly"])
    df["city"] = city
    df["time"] = pd.to_datetime(df["time"])
    return df


def save(df):
    con = duckdb.connect(DB_FILE)
    con.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            city VARCHAR,
            time TIMESTAMP,
            temperature_2m DOUBLE,
            precipitation DOUBLE,
            PRIMARY KEY (city, time)
        )
    """)
    con.register("new_data", df)
    con.execute("""
        INSERT OR REPLACE INTO weather
        SELECT city, time, temperature_2m, precipitation FROM new_data
    """)
    total = con.execute("SELECT COUNT(*) FROM weather").fetchone()[0]
    con.close()
    return total


def main():
    frames = [fetch_city(city, lat, lon) for city, (lat, lon) in CITIES.items()]
    all_data = pd.concat(frames, ignore_index=True)
    total = save(all_data)
    print(f"Fetched {len(all_data)} rows. Table now has {total} rows.")


if __name__ == "__main__":
    main()