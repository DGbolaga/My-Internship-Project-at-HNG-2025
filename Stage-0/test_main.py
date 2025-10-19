import unittest
import json 
from unittest.mock import patch, Mock 
import os
import sys 
import requests

# adds current directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# set test environment variables, then import app
os.environ['USER_EMAIL'] = 'test@example.com'
os.environ['USER_NAME'] = 'Test User'
os.environ['USER_STACK'] = 'Python/Flask'

from main import app, get_cat_fact


# Test the Profile API
class TestProfileAPI(unittest.TestCase):
    """Test case to ensure Profile API is working"""

    def setUp(self):
        """set up test client and environement"""
        self.app = app.test_client()
        self.app.testing = True 

    def test_get_profile_success(self):
        """Test successful profile retrieval"""

        #Mock cat fact API to return a known response
        with patch('main.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"fact": "Cats are awesome!"}
            mock_response.raise_for_status.return_value = None 
            mock_get.return_value = mock_response 
            
            response = self.app.get("/me")

            #Check response status
            self.assertEqual(response.status_code, 200)

            #Check response content type
            self.assertEqual(response.content_type, 'application/json')

            #Parse/Format response data
            data = json.loads(response.data)

            #Check all required fields are present
            self.assertIn('status', data)
            self.assertIn('user', data)
            self.assertIn('timestamp', data)
            self.assertIn('fact', data)

            #check status
            self.assertEqual(data['status'], 'success')

            #check user information
            self.assertEqual(data['user']['email'], 'test@example.com')
            self.assertEqual(data['user']['name'], 'Test User')
            self.assertEqual(data['user']['stack'], 'Python/Flask')
            
            # Check timestamp format (must be ISO 8601)
            self.assertRegex(data['timestamp'], r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z')

            # Check cat fact
            self.assertEqual(data['fact'], 'Cats are awesome!')

    def test_get_profile_api_failure(self):
        """Test profile retrieval when cat api fails"""
        #Mock the cat fact api to raise an exception
        with patch('main.requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")

            response = self.app.get('/me')

            # Check response status (still should be 200)
            self.assertEqual(response.status_code, 200)

            # Format response data to json
            data = json.loads(response.data)

            #Check that a response is still gotten
            self.assertEqual(data['status'], 'success')
            self.assertIn('fact', data)

            #check that we get the fallback message
            self.assertEqual(data['fact'], 'Cats are amazing creatures with incredible agility.')

    def test_get_profile_timeout(self):
        """Test profile retrieval when cat api times out"""

        # Mock the cat fact API to timeout
        with patch('main.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

            response = self.app.get('/me')

            # check response status
            self.assertEqual(response.status_code, 200)

            #Parse response data
            data = json.loads(response.data)

            #Check that the get failback message is gotten
            self.assertEqual(data['fact'], 'Cats are amazing creatures with incredible agility.')

    def test_get_profile_http_error(self):
        """Test profile retrieval when cat api returns http error"""

        #Mock the cat fact api to return http  error
        with patch('main.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
            mock_get.return_value = mock_response

            response = self.app.get('/me')

            #Check response status
            self.assertEqual(response.status_code, 200)

            #Format response data to json
            data = json.loads(response.data)

            #check that the fallback message is gotten
            self.assertEqual(data['fact'], 'Cats are amazing creatures with incredible agility.')


# Test Cat Fact Function 
class TestCatFactFunction(unittest.TestCase):
    """Test cases to ensure get cat fact works correctly"""

    def test_get_cat_fact_success(self):
        """Test successful cat fact retrieval"""
        with patch("main.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"fact": "Cats have 32 muscles in eahc ear!"}
            mock_response.raise_for_status.return_value = None 
            mock_get.return_value = mock_response

            result = get_cat_fact()

            self.assertEqual(result, "Cats have 32 muscles in eahc ear!")

    def test_get_cat_fact_api_error(self):
        """Test cat fact retrieval when api fails"""
        with patch("main.requests.get") as mock_get:
            mock_get.side_effect = Exception("API Error")

            result = get_cat_fact()

            self.assertEqual(result, "Cats are amazing creatures with incredible agility.")

    def test_get_cat_fact_missing_fact_field(self):
        """Test cat fact retrieval when response doesn't have 'fact' field """
        with patch("main.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"message": "No fact here"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_cat_fact()

            self.assertEqual(result, "No cat fact available")

# Test Timestamp Format
class TestTimestampFunction(unittest.TestCase):
    """Test to ensure timestamp is formatted properly"""

    def test_timestamp_format(self):
        """Test that timestamp is in correct ISO 8601 format"""
        with patch("main.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"fact": "Test fact"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            app_test = app.test_client()
            response = app_test.get("/me")

            data = json.loads(response.data)
            timestamp = data['timestamp']

            #Check timestamp format
            self.assertRegex(timestamp, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z')

            #check that timestamp ends with Z (UTC)
            self.assertTrue(timestamp.endswith('Z'))



if __name__ == "__main__":
    unittest.main(verbosity=2)