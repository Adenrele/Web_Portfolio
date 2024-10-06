import os
import unittest
from flask import Flask
from flask_mail import Mail
from forms import ContactForm  # Import your ContactForm
from main import app  # Import your Flask app

class ContactFormTests(unittest.TestCase):
    def setUp(self):
        # Set up a test client
        app.config['TESTING'] = True
        app.config['MAIL_SUPPRESS_SEND'] = True  # Suppress sending actual emails
        self.client = app.test_client()
        self.app = app

    def test_contact_get(self):
        # Test GET request
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contact Me', response.data)  # Check for the title or any known text

    def test_contact_post_valid(self):
        # Test POST request with valid data
        response = self.client.post('/contact', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.',
            'submit': 'Send'  # Ensure this matches your form's submit button
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your message has been sent successfully!', response.data)

    def test_contact_post_invalid(self):
        # Test POST request with invalid data (missing fields)
        response = self.client.post('/contact', data={
            'name': '',  # Invalid: empty name
            'email': 'test@example.com',
            'subject': '',
            'message': '',
            'submit': 'Send'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All fields are required.', response.data)

if __name__ == '__main__':
    unittest.main()
