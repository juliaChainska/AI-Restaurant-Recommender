import warnings
warnings.filterwarnings("ignore")
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class GooglePlacesTool:
    def __init__(self, api_key: str = GOOGLE_MAPS_API_KEY):
        self.api_key = api_key

    def search_places(self, query: str, location: str, radius: Optional[int] = None) -> List[Dict]:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "location": location,
            "radius": radius,
            "key": self.api_key
        }
        if radius:
            params["radius"] = radius
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"Google Maps API Error: {response.status_code}")
            return []

    def get_place_details(self, place_id: str) -> Dict:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,rating,review,user_ratings_total,formatted_address,opening_hours,price_level",
            "key": self.api_key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("result", {})
        else:
            print(f"Details API Error: {response.status_code}")
            return {}
