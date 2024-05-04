import requests
import random
import os
from dotenv import load_dotenv

class Navigator:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")

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
        response = requests.post(f"{url}?key={self.api_key}", json=data, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            location_data = response.json()
            
            # Extract latitude and longitude
            latitude = location_data["location"]["lat"]
            longitude = location_data["location"]["lng"]
            
            return latitude, longitude
        else:
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
            'key': self.api_key
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

if __name__ == "__main__":
    navigator = Navigator()
    location = navigator.get_location()
    if location:
        print("User's location (latitude, longitude):", location)
        print(navigator.find_nearby_fuel_stations(location[0], location[1]))

    else:
        print("Failed to retrieve user's location.")
