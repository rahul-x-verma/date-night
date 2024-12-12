from date_night_api.settings import get_settings
import requests
import os
from langchain_core.tools import tool
from dotenv import load_dotenv


@tool
def find_restaurant(cuisine: str) -> str:
    """Returns the name of a restaurant near the application's address that serves the given cuisine.

    Args:
        cuisine: The type of cuisine to search for.
    """
    settings = get_settings()
    api_key = settings.google_maps_api_key
    address = settings.address
    lat, long = get_coordinates(api_key, address)
    restaurant = find_restaurants(api_key, lat, long, cuisine)
    return f'{restaurant['name']} at {restaurant['vicinity']}'

def get_coordinates(api_key, address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(geocode_url).json()
    location = response['results'][0]['geometry']['location']
    return location['lat'], location['lng']

def find_restaurants(api_key, lat, lng, cuisine):
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 1500,
        "type": "restaurant",
        "keyword": cuisine,
        "key": api_key
    }
    response = requests.get(places_url, params=params).json()
    results = response['results']
    return sorted(results, key=lambda x: x['rating'], reverse=True)[0]
