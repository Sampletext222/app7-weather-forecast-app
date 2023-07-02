import requests


API_KEY = "57d7ad397f04d340e2a50e9f95f3b188"


def get_data(place, forecast_days, type,):
    url= f"http://api.openweathermap.org/data/2.5/forecast?q={place}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    filtered_data = data["list"]
    nr_values = 8 * forecast_days
    filtered_data = filtered_data[:nr_values]
    if type == "Temperature":
        filtered_data = [dict["main"]["temp"] for dict in filtered_data]
    if type == "Sky":
        filtered_data = [dict["weather"][0]["main"] for dict in filtered_data]

    return filtered_data

if __name__ == "__main__"
    get_data(place="tokyo")