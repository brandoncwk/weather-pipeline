import requests
import pandas as pd

URL = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 51.5,
    "longitude": -0.12,
    "hourly": "temperature_2m,precipitation",
    "past_days": 1,
    "timezone": "UTC",
}

response = requests.get(URL, params=params, timeout=30)
response.raise_for_status()
data = response.json()

df = pd.DataFrame(data["hourly"])
print(df.head())
print(f"Rows: {len(df)}")