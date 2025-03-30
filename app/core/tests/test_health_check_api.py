"""
Test for checking api health
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


class TestApiHealth(TestCase):
    """Test for api health."""
    def test_api_health(self):
        """test api health."""
        self.client = APIClient()
        url = reverse('health-check')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)