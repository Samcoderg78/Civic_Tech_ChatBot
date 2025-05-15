import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils.ocr import extract_vin, validate_vin
from utils.stolen_vehicle_api import check_stolen_status

class StolenVehicleCheckTestCase(unittest.TestCase):
    """Test cases for stolen vehicle check functionality"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_validate_vin(self):
        """Test VIN validation"""
        # Valid VIN
        self.assertTrue(validate_vin("1HGCM82633A123456"))
        
        # Invalid VIN (wrong length)
        self.assertFalse(validate_vin("1HGCM82633A"))
        
        # Invalid VIN (contains invalid characters)
        self.assertFalse(validate_vin("1HGCM82633A12345I"))
    
    @patch('utils.ocr.extract_vin')
    @patch('utils.stolen_vehicle_api.check_stolen_status')
    def test_check_vin_stolen(self, mock_check_stolen, mock_extract_vin):
        """Test stolen vehicle check with stolen vehicle"""
        # Setup mocks
        mock_extract_vin.return_value = "1HGCM82633A123456"
        mock_check_stolen.return_value = {
            'is_stolen': True,
            'vin': "1HGCM82633A123456",
            'report_date': '2023-05-15',
            'vehicle_details': {
                'make': 'Honda',
                'model': 'Accord',
                'year': 2020,
                'color': 'Black'
            }
        }
        
        # Test data
        test_data = {
            'Body': 'check vin',
            'From': '+13175551234',
            'NumMedia': '1',
            'MediaUrl0': 'https://example.com/vin_image.jpg',
            'MediaContentType0': 'image/jpeg'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check response
        self.assertIn(b'REPORTED STOLEN', response.data)
    
    @patch('utils.ocr.extract_vin')
    @patch('utils.stolen_vehicle_api.check_stolen_status')
    def test_check_vin_not_stolen(self, mock_check_stolen, mock_extract_vin):
        """Test stolen vehicle check with non-stolen vehicle"""
        # Setup mocks
        mock_extract_vin.return_value = "1HGCM82633A123456"
        mock_check_stolen.return_value = {
            'is_stolen': False,
            'vin': "1HGCM82633A123456",
            'vehicle_details': {
                'make': 'Honda',
                'model': 'Accord',
                'year': 2020,
                'color': 'Black'
            }
        }
        
        # Test data
        test_data = {
            'Body': 'check vin',
            'From': '+13175551234',
            'NumMedia': '1',
            'MediaUrl0': 'https://example.com/vin_image.jpg',
            'MediaContentType0': 'image/jpeg'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check response
        self.assertIn(b'not reported stolen', response.data)
    
    @patch('utils.ocr.extract_vin')
    def test_check_vin_no_vin_detected(self, mock_extract_vin):
        """Test stolen vehicle check when no VIN can be detected"""
        # Setup mock
        mock_extract_vin.return_value = None
        
        # Test data
        test_data = {
            'Body': 'check vin',
            'From': '+13175551234',
            'NumMedia': '1',
            'MediaUrl0': 'https://example.com/vin_image.jpg',
            'MediaContentType0': 'image/jpeg'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check response
        self.assertIn(b'Could not detect a VIN', response.data)