from django.test import Client, TestCase

import os
import pytest
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'piazza.settings')
import django

django.setup()
client = Client()

class TestBase(TestCase):
    def test_zero_returns_nothing(self):
        client.login(email='amir@gmail.com', password='abcd')
        response = client.get('/soren/courses/')
        self.assertEqual(json.loads(response.content).get('results'), [])




