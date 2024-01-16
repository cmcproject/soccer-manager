"""
Tests for the player API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from soccer.consts import PLAYER_INITIAL_MARKET_VALUE, PositionChoices

TEAM_URL = reverse("soccer:team")


def player_url(player_id):
    return reverse("soccer:player-detail", args=[player_id])


def create_user(email="user@example.com", password="pass123"):
    """Create and return user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicPlayerApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        url = player_url(player_id=1)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlayerApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_player(self):
        # create team
        payload = {"name": "Barcelona", "country": "Spain"}
        res = self.client.post(TEAM_URL, payload)
        res = self.client.get(TEAM_URL)
        player = res.data["players"][0]

        # retrive player
        url = player_url(player["id"])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], player["id"])
        self.assertEqual(res.data["first_name"], player["first_name"])
        self.assertEqual(res.data["last_name"], player["last_name"])
        self.assertEqual(res.data["age"], player["age"])
        self.assertEqual(res.data["position"], player["position"])
        self.assertEqual(float(res.data["market_value"]), float(PLAYER_INITIAL_MARKET_VALUE))

        # partial update
        payload = {"first_name": "Testname"}
        res = self.client.patch(url, payload)

        patched_player = player.copy()
        patched_player.update(payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, patched_player)

        # update
        payload = {
            "first_name": "Firstname",
            "last_name": "Lastname",
            "position": PositionChoices.DEFENDER,
            "country": "Italy",
            "market_value": "1200000.00",
            "transferable": True,
        }
        res = self.client.put(url, payload)

        put_player = player.copy()
        put_player.update(payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, put_player)
