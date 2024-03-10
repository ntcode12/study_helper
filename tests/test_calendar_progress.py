import os
import tempfile
import unittest
from flask import json
import datetime
from calendar_progress.calendar_progress import app, save_studied_day, load_studied_days

class FlaskStudyTrackerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Preparing a temporary file instead of the actual 'studied_days.txt'
        with open(app.config['DATABASE'], 'w') as f:
            f.write(f"{datetime.date.today()}\n")

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_get_index(self):
        """Test the index page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Study Tracker', response.get_data(as_text=True))

    def test_post_studied(self):
        """Test posting a studied day."""
        response = self.client.post('/', json={'studied': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'success'})
        # Check if the day was saved
        with open(app.config['DATABASE'], 'r') as f:
            lines = f.readlines()
            self.assertTrue(f"{datetime.date.today()}\n" in lines)

    def test_load_studied_days(self):
        """Test loading studied days."""
        app.config['DATABASE'] = 'studied_days.txt'  
        studied_days = load_studied_days()
        self.assertIn(datetime.date.today(), studied_days)

if __name__ == '__main__':
    unittest.main()
