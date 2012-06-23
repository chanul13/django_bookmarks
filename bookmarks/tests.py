"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class ViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_register_page(self):
        data = {
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password1': 'pass123',
            'password2': 'pass123'
        }

        response = self.client.post('/register/', data)
        self.assertRedirects(response, '/register/success/')

    def test_bookmark_save(self):
        response = self.client.login(
            username = 'flaugher',
            password = 'flaugher'
        )
        self.assertTrue(response, msg = 'Failed to login.')

        data = {
            'url'  : 'http://www.example.com/',
            'title': 'Test URL',
            'tags' : 'test-tag'
        }
        response = self.client.post('/save/', data)
        self.assertRedirects(response, '/user/flaugher/')

        response = self.client.get('/user/flaugher/')
        self.assertContains(response, 'http://www.example.com/')
        self.assertContains(response, 'Test URL')
        self.assertContains(response, 'test-tag')
