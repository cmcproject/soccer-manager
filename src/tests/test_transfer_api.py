"""
Tests for the transfer API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from soccer.consts import TEAM_INITIAL_BUDGET

TRANSFER_URL = reverse("soccer:transfer-list")
TEAM_URL = reverse("soccer:team")


def player_url(player_id):
    return reverse("soccer:player-detail", args=[player_id])


def transfer_player_url(player_id):
    return reverse("soccer:transfer-player", args=[player_id])


def create_user(email="user@example.com", password="pass123"):
    """Create and return user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTransferApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_transfer_list(self):
        res = self.client.get(TRANSFER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_transfer_player(self):
        url = transfer_player_url(player_id=5)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTransferApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user1 = create_user(email="user1@example.com")
        self.user2 = create_user(email="user@example.com")
        self.client1 = APIClient()
        self.client2 = APIClient()

    def login(self, client, user):
        client.force_authenticate(user)

    def test_add_player_to_transfer_list_and_buy(self):
        """
        Player is added to transfer list by TEAM1 and bought by TEAM2
        """
        # TEAM1
        # create team
        self.login(self.client1, self.user1)
        payload = {"name": "TEAM1", "country": "Spain"}
        res = self.client1.post(TEAM_URL, payload)

        # make player tansferable
        res = self.client1.get(TEAM_URL)
        player_id = res.data["players"][0]["id"]
        url = player_url(player_id=player_id)
        payload = {"transferable": True, "market_value": 1200000}
        res = self.client1.patch(url, payload)
        player_for_sale = res.data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["transferable"], True)
        self.assertEqual(res.data["market_value"], "1200000.00")

        res = self.client1.get(TEAM_URL)
        team_1_before_sale = res.data
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(float(team_1_before_sale["budget"]), TEAM_INITIAL_BUDGET)
        self.assertEqual(float(team_1_before_sale["team_value"]), 20200000)

        # TEAM2
        # create team
        self.login(self.client2, self.user2)
        payload = {"name": "TEAM2", "country": "Spain"}
        res = self.client2.post(TEAM_URL, payload)
        res = self.client2.get(TEAM_URL)
        team_2_before_sale = res.data
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(team_2_before_sale["players"]), 20)
        self.assertEqual(team_2_before_sale["team_value"], "20000000.00")
        self.assertEqual(team_2_before_sale["budget"], "5000000.00")

        # get transfer list
        res = self.client2.get(TRANSFER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], player_id)

        # buy player
        res = self.client2.post(transfer_player_url(player_id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        player_after_sale = res.data
        self.assertEqual(player_after_sale["id"], player_id)
        self.assertTrue((player_after_sale["market_value"]) > player_for_sale["market_value"])

        # check budget and team value updates
        res = self.client2.get(TEAM_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["players"]), 21)
        self.assertEqual(
            (float(res.data["team_value"])),
            float(team_2_before_sale["team_value"]) + float(player_after_sale["market_value"]),
        )
        self.assertEqual(
            (float(res.data["budget"])),
            float(team_2_before_sale["budget"]) - float(player_for_sale["market_value"]),
        )

        # TEAM1 - check budget and team value updates

        res = self.client1.get(TEAM_URL)
        self.assertEqual(len(res.data["players"]), 19)
        self.assertEqual(
            (float(res.data["team_value"])),
            float(team_1_before_sale["team_value"]) - float(player_for_sale["market_value"]),
        )
        self.assertEqual(
            (float(res.data["budget"])),
            float(team_1_before_sale["budget"]) + float(player_for_sale["market_value"]),
        )
