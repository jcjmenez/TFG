import os
from dotenv import load_dotenv
import requests

class WeatherGetter:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")

    def get_weather(self, lat, lon):
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        else:
            print("Failed to retrieve weather data:", response.status_code)
            return None

if __name__ == "__main__":
    lat = 40.4168
    lon = -3.7038
    weather_getter = WeatherGetter()
    weather = weather_getter.get_weather(lat, lon)
    if weather:
        print("Weather:", weather)
