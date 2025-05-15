import redis
import json
from config import REDIS_URL

class RedisManager:
    """Manage Redis operations for scaling to 870k users"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis = redis.from_url(REDIS_URL)
    
    def cache_user_location(self, phone_number, latitude, longitude, ttl=3600):
        """Cache user location for faster lookups
        
        Args:
            phone_number (str): User's phone number (hashed for privacy)
            latitude (float): User's latitude
            longitude (float): User's longitude
            ttl (int): Time-to-live in seconds (default 1 hour)
        """
        # Hash the phone number for privacy
        hashed_number = self._hash_phone_number(phone_number)
        
        # Store location data
        location_data = {
            'lat': latitude,
            'lon': longitude,
            'updated_at': json.dumps({'$date': int(datetime.now().timestamp() * 1000)})
        }
        
        # Save to Redis with expiration
        self.redis.setex(
            f"user:location:{hashed_number}",
            ttl,
            json.dumps(location_data)
        )
    
    def get_users_in_area(self, latitude, longitude, radius_miles=1.0):
        """Get all users in a specific area (useful for emergency alerts)
        
        In a real implementation, this would use Redis geospatial commands.
        For simplicity, we're implementing a basic version here.
        """
        # In production, use Redis GEO commands:
        # GEOADD users:locations longitude latitude hashed_phone_number
        # GEORADIUS users:locations longitude latitude radius_miles mi
        
        # Simplified approach for this example:
        # This would scan the recent locations in Redis and filter by distance
        # For demo purposes only - not efficient for 870k users
        return []
    
    def _hash_phone_number(self, phone_number):
        """Hash phone number for privacy"""
        import hashlib
        # Remove any non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        # Create a hash
        return hashlib.sha256(clean_number.encode()).hexdigest()