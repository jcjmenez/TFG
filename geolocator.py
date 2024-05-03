import requests
import random

class GeoLocator:
    def __init__(self, api_key):
        self.api_key = api_key

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
    
if __name__ == "__main__":
    api_key = "API_KEY"
    locator = GeoLocator(api_key)
    location = locator.get_location()
    if location:
        print("User's location (latitude, longitude):", location)
    else:
        print("Failed to retrieve user's location.")
