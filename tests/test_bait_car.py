import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils.bait_car_api import get_nearby_bait_cars, calculate_distance

class BaitCarTestCase(unittest.TestCase):
    """Test cases for bait car functionality"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_calculate_distance(self):
        """Test distance calculation function"""
        # Monument Circle to White River State Park (about 0.9 miles)
        distance = calculate_distance(39.768, -86.158, 39.764, -86.173)
        self.assertTrue(0.8 < distance < 1.0)
        
        # Close points (should be near zero)
        distance = calculate_distance(39.768, -86.158, 39.768, -86.158)
        self.assertAlmostEqual(distance, 0, delta=0.01)
    
    @patch('utils.bait_car_api.get_nearby_bait_cars')
    def test_bait_car_nearby(self, mock_get_nearby_bait_cars):
        """Test bait car detection when one is nearby"""
        # Setup mock
        mock_get_nearby_bait_cars.return_value = [{
            "latitude": 39.768,
            "longitude": -86.158,
            "timestamp": "2023-08-10T15:30:00.000Z",
            "vehicle_type": "Sedan",
            "distance_miles": 0.25
        }]
        
        # Test data
        test_data = {
            'Body': 'bait cars',
            'From': '+13175551234',
            'Latitude': '39.768',
            'Longitude': '-86.158'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check response
        self.assertIn(b'Police bait car active near you', response.data)
    
    @patch('utils.bait_car_api.get_nearby_bait_cars')
    def test_no_bait_car_nearby(self, mock_get_nearby_bait_cars):
        """Test bait car detection when none are nearby"""
        # Setup mock
        mock_get_nearby_bait_cars.return_value = []
        
        # Test data
        test_data = {
            'Body': 'bait cars',
            'From': '+13175551234',
            'Latitude': '39.768',
            'Longitude': '-86.158'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check response
        self.assertIn(b'No active bait cars', response.data)
    
    def test_bait_car_no_location(self):
        """Test bait car request without location data"""
        # Test data
        test_data = {
            'Body': 'bait cars',
            'From': '+13175551234'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check response
        self.assertIn(b'Location information is needed', response.data)