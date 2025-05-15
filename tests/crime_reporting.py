import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class CrimeReportingTestCase(unittest.TestCase):
    """Test cases for crime reporting functionality"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('utils.image_processing.process_image')
    @patch('database.models.save_report')
    def test_report_with_image(self, mock_save_report, mock_process_image):
        """Test crime reporting with an image"""
        # Setup mocks
        mock_process_image.return_value = '/path/to/processed/image.jpg'
        mock_save_report.return_value = 12345
        
        # Test data
        test_data = {
            'Body': 'report Suspicious vehicle parked for 3 days',
            'From': '+13175551234',
            'NumMedia': '1',
            'MediaUrl0': 'https://example.com/image.jpg',
            'MediaContentType0': 'image/jpeg',
            'Latitude': '39.768',
            'Longitude': '-86.158'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check response
        self.assertIn(b'Thank you for your report', response.data)