import requests
import random
import os
from dotenv import load_dotenv

class Navigator:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")

    def get_location(self):
        # Google Maps Geolocation API endpoint
        url = "https://www.googleapis.com/geolocation/v1/geolocate"
        
        # Request body
        data = {
            "considerIp": "true"
        }
        
        # HTTP headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Send POST request to Google Maps Geolocation API
        response = requests.post(f"{url}?key={self.google_api_key}", json=data, headers=headers)
        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            location_data = response.json()
            # Extract latitude and longitude
            latitude = location_data["location"]["lat"]
            longitude = location_data["location"]["lng"]
            
            return latitude, longitude
        else:
            print(response.text)
            print("Error:", response.status_code)
            
            return self.generate_random_location()

    def generate_random_location(self):
        # Bounding box for roads in Spain
        min_lat, max_lat = 36.0, 43.5
        min_lng, max_lng = -9.3, 3.4
        
        # Generate random latitude and longitude within the bounding box
        random_lat = random.uniform(min_lat, max_lat)
        random_lng = random.uniform(min_lng, max_lng)
        
        return random_lat, random_lng
    
    def find_nearby_fuel_stations(self, latitude, longitude, radius=5000, fuel_type='gas_station'):
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f'{latitude},{longitude}',
            'radius': radius,
            'type': fuel_type,
            'key': self.google_api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        stations = []
        if 'results' in data:
            for station in data['results']:
                if 'opening_hours' in station.keys() and station['opening_hours']['open_now']:
                    name = station['name']
                    location = station['geometry']['location']
                    lat = location['lat']
                    lng = location['lng']
                    rating = station['rating']
                    stations.append({'name': name, 'lat': lat, 'lon': lng, 'rating': rating})
        else:
            print("Error: No results found.")
        
        return stations

    def get_weather(self, lat, lon):
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.weather_api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            weather_data = response.json()
            current_weather = weather_data['weather'][0]['main']
            return current_weather
        else:
            print("Failed to retrieve weather data:", response.status_code)
            return None
        
    def calculate_road_distance_from_latlon(self, origin_latitude, origin_longitude, destination_latitude, destination_longitude):
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
        params = {
            'origins': f'{origin_latitude},{origin_longitude}',
            'destinations': f'{destination_latitude},{destination_longitude}',
            'mode': 'driving',
            'units': 'metric',
            'key': self.google_api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        print(data)
        if 'rows' in data and len(data['rows']) > 0 and 'elements' in data['rows'][0] and len(data['rows'][0]['elements']) > 0:
            distance_text = data['rows'][0]['elements'][0].get('distance', {}).get('text', '')
            if distance_text:
                distance = float(distance_text.split()[0])
                print(distance)
                return distance
        return None
    
    def calculate_road_distance_from_address(self, origin_lat, origin_lon, destination_address):
        url = 'https://maps.googleapis.com/maps/api/directions/json'
        params = {
            'origin': f'{origin_lat},{origin_lon}',
            'destination': destination_address,
            'key': self.google_api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        if 'routes' in data and len(data['routes']) > 0 and 'legs' in data['routes'][0] and len(data['routes'][0]['legs']) > 0:
            distance_text = data['routes'][0]['legs'][0].get('distance', {}).get('text', '')
            if distance_text:
                distance = float(distance_text.split()[0])
                return distance
        return None

    def calculate_nearest_gas_station_distance(self, user_latitude, user_longitude):
            stations = self.find_nearby_fuel_stations(user_latitude, user_longitude)
            if stations:
                min_distance = float('inf')
                for station in stations:
                    station_latitude = station['lat']
                    station_longitude = station['lon']
                    distance = self.calculate_road_distance_from_latlon(user_latitude, user_longitude, station_latitude, station_longitude)
                    if distance < min_distance:
                        min_distance = distance
                return min_distance
            else:
                return None
    
    def get_time_in_traffic_from_latlon(self, origin_latitude, origin_longitude, destination_latitude, destination_longitude):
            url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
            params = {
                'origins': f'{origin_latitude},{origin_longitude}',
                'destinations': f'{destination_latitude},{destination_longitude}',
                'mode': 'driving',
                'traffic_model': 'best_guess',
                'departure_time': 'now',
                'key': self.google_api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            if 'rows' in data and len(data['rows']) > 0 and 'elements' in data['rows'][0] and len(data['rows'][0]['elements']) > 0:
                duration_in_traffic_text = data['rows'][0]['elements'][0].get('duration_in_traffic', {}).get('text', '')
                if duration_in_traffic_text:
                    duration_in_traffic = int(duration_in_traffic_text.split()[0])
                    if 'min' in duration_in_traffic_text.lower() and duration_in_traffic > 30:
                        return duration_in_traffic
            return 0
    
    def get_time_in_traffic_from_address(self, origin_lat, origin_lon, destination_address):
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
        params = {
            'origins': f'{origin_lat},{origin_lon}',
            'destinations': destination_address,
            'mode': 'driving',
            'traffic_model': 'best_guess',
            'departure_time': 'now',
            'key': self.google_api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        if 'rows' in data and len(data['rows']) > 0 and 'elements' in data['rows'][0] and len(data['rows'][0]['elements']) > 0:
            duration_in_traffic_text = data['rows'][0]['elements'][0].get('duration_in_traffic', {}).get('text', '')
            if duration_in_traffic_text:
                duration_in_traffic = int(duration_in_traffic_text.split()[0])
                return duration_in_traffic
        return 0

    
if __name__ == "__main__":
    navigator = Navigator()
    location = navigator.get_location()
    if location:
        #print("User's location (latitude, longitude):", location)
        #print(navigator.find_nearby_fuel_stations(location[0], location[1]))
        #weather = navigator.get_weather(location[0], location[1])
        #print("Weather:", weather)
        nearest_gas_station = navigator.find_nearby_fuel_stations(location[0], location[1])
        if nearest_gas_station:
            gas_station_location = nearest_gas_station[0]  # Assuming the first gas station found is the nearest
            time_in_traffic = navigator.get_time_in_traffic_from_latlon(location[0], location[1], gas_station_location['lat'], gas_station_location['lon'])
            if time_in_traffic > 0:
                print(f"There is a traffic jam on the way to the nearest gas station. Estimated time in traffic: {time_in_traffic} minutes.")
            else:
                print("There is no traffic jam on the way to the nearest gas station.")
        else:
            print("No gas station found nearby.")

        road_distance = navigator.calculate_road_distance_from_address(location[0], location[1], "Avenida de los artesanos 6, Tres Cantos, Madrid, Spain")
        if road_distance is not None:
            print(f"Distance to artesanos {road_distance} km.")
            time_in_traffic = navigator.get_time_in_traffic_from_address(location[0], location[1], "Avenida de los artesanos 6, Tres Cantos, Madrid, Spain")
            print(f"Time in traffic to artesanos: {time_in_traffic} minutes.")
        else:
            print("Failed to calculate road distance.")

    else:
        print("Failed to retrieve user's location.")
