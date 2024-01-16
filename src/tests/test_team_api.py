"""
Tests for the team API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from soccer.consts import TEAM_POSITIONS

TEAM_URL = reverse("soccer:team")


def create_user(email="user@example.com", password="pass123"):
    """Create and return user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTeamsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TEAM_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTeamsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_team_not_created(self):
        res = self.client.get(TEAM_URL)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data, {"msg": "Create the soccer team first."})

    def test_create_and_retrieve_team(self):
        data = {"name": "Barcelona", "country": "Spain"}
        res = self.client.post(TEAM_URL, data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, data)

        res = self.client.get(TEAM_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], data["name"])
        self.assertEqual(res.data["country"], data["country"])
        self.assertEqual(res.data["budget"], "5000000.00")
        self.assertEqual(res.data["team_value"], "20000000.00")
        self.assertEqual(len(res.data["players"]), len(TEAM_POSITIONS))
