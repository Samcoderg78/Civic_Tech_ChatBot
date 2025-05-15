import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class EscapeCallTestCase(unittest.TestCase):
    """Test cases for emergency escape call functionality"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('twilio.rest.Client')
    def test_red_emergency_call(self, mock_client):
        """Test RED keyword triggers emergency call"""
        # Setup mock
        mock_calls = MagicMock()
        mock_client.return_value.calls = mock_calls
        
        # Test data
        test_data = {
            'Body': 'RED help me',
            'From': '+13175551234'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check call was initiated
        mock_calls.create.assert_called_once()
        
        # Check response
        self.assertIn(b'emergency call', response.data)
    
    @patch('twilio.rest.Client')
    def test_call_mom_fake_emergency(self, mock_client):
        """Test 'call mom' keyword triggers fake family emergency"""
        # Setup mock
        mock_calls = MagicMock()
        mock_client.return_value.calls = mock_calls
        
        # Test data
        test_data = {
            'Body': 'call mom',
            'From': '+13175551234'
        }
        
        # Make request
        response = self.app.post('/sms', data=test_data)
        
        # Check call was initiated
        mock_calls.create.assert_called_once()
        
        # Check response
        self.assertIn(b'family emergency call', response.data)
    
    def test_emergency_call_twiml(self):
        """Test emergency call TwiML generation"""
        response = self.app.post('/emergency_call')
        
        # Check TwiML content
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This is an emergency call', response.data)
        self.assertIn(b'<Response>', response.data)
    
    def test_family_call_twiml(self):
        """Test family emergency call TwiML generation"""
        response = self.app.post('/family_call')
        
        # Check TwiML content
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"it's mom", response.data)
        self.assertIn(b'<Response>', response.data)