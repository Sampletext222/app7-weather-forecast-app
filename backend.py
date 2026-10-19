import requests
import streamlit as st

# Reads from Streamlit Cloud Secrets first; falls back to your key for local testing
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = "57d7ad397f04d340e2a50e9f95f3b188"


@st.cache_data(ttl=600, show_spinner=False)
def get_data(place: str, forecast_days: int):
    """
    Fetches 3-hourly forecast data in metric units from OpenWeatherMap.
    Returns a tuple of (filtered_forecast_list, city_metadata_dict).
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={place}&appid={API_KEY}&units=metric"
    )
    response = requests.get(url, timeout=10)
    data = response.json()

    # Check if the API returned a valid 200 status
    if str(data.get("cod")) != "200":
        raise ValueError(data.get("message", "City not found"))

    nr_values = 8 * forecast_days
    filtered_data = data["list"][:nr_values]
    city_info = data["city"]

    return filtered_data, city_info


if __name__ == "__main__":
    forecasts, city = get_data(place="Adelaide", forecast_days=2)
    print(f"Loaded {len(forecasts)} intervals for {city['name']}, {city['country']}")