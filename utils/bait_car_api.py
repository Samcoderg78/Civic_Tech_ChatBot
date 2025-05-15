
import requests
import json
import math
import random
from datetime import datetime
from config import BAIT_CAR_API_URL, BAIT_CAR_API_KEY
from database.models import log_bait_car_notification

# This is a mock implementation. In production, this would connect to the IMPD API
def get_nearby_bait_cars(user_lat, user_lon, radius_miles=0.5):
    """Check if there are any bait cars near the specified coordinates
    
    Args:
        user_lat (float): User's latitude
        user_lon (float): User's longitude
        radius_miles (float): Search radius in miles
    
    Returns:
        list: List of bait cars in the vicinity, or empty list if none found
    """
    try:
        # In a real implementation, this would make an API call to IMPD's bait car system
        # For example:
        # headers = {'Authorization': f'Bearer {BAIT_CAR_API_KEY}'}
        # params = {'latitude': user_lat, 'longitude': user_lon, 'radius': radius_miles}
        # response = requests.get(BAIT_CAR_API_URL, headers=headers, params=params)
        # data = response.json()
        
        # For this project, we'll generate mock data
        # Indianapolis downtown area roughly spans from 39.75 to 39.78 latitude
        # and -86.18 to -86.15 longitude
        
        # Define bait car hotspots (these would come from the API in production)
        bait_car_hotspots = [
            {"lat": 39.768, "lon": -86.158, "active": True},  # Near Monument Circle
            {"lat": 39.764, "lon": -86.173, "active": True},  # Near White River State Park
            {"lat": 39.779, "lon": -86.148, "active": False}, # Near Mass Ave
            {"lat": 39.754, "lon": -86.142, "active": True},  # Near Fountain Square
            {"lat": 39.773, "lon": -86.178, "active": True}   # Near IUPUI
        ]
        
        # Calculate which bait cars are within the radius
        nearby_cars = []
        for car in bait_car_hotspots:
            if car["active"] and calculate_distance(user_lat, user_lon, car["lat"], car["lon"]) <= radius_miles:
                # Add some randomized details to make it more realistic
                car_details = {
                    "latitude": car["lat"],
                    "longitude": car["lon"],
                    "timestamp": datetime.now().isoformat(),
                    "vehicle_type": random.choice(["Sedan", "SUV", "Pickup", "Compact"]),
                    "distance_miles": round(calculate_distance(user_lat, user_lon, car["lat"], car["lon"]), 2)
                }
                nearby_cars.append(car_details)
        
        # If we found nearby bait cars, log this notification
        if nearby_cars:
            log_bait_car_notification(user_lat, user_lon)
            
        return nearby_cars
        
    except Exception as e:
        print(f"Error fetching bait car data: {str(e)}")
        return []

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Radius of earth in miles
    radius = 3956
    
    # Calculate distance
    distance = radius * c
    
    return distance