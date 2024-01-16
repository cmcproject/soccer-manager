import random

from django.conf import settings
from django.db import models

from .consts import PLAYER_INITIAL_MARKET_VALUE, TEAM_INITIAL_BUDGET, PositionChoices


class Team(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    country = models.CharField(max_length=50)
    budget = models.DecimalField(
        max_digits=len(str(TEAM_INITIAL_BUDGET)) + 2 + 2,
        decimal_places=2,
        default=TEAM_INITIAL_BUDGET,
    )  # max value = 999,999,999.99

    def __str__(self) -> str:
        return self.name


def get_random_age() -> int:
    """
    Generate player random age in interval [18, 40]
    :return: Age
    """
    return random.randint(18, 40)


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=50, choices=PositionChoices.choices)
    age = models.IntegerField(default=get_random_age)
    country = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    market_value = models.DecimalField(
        max_digits=len(str(PLAYER_INITIAL_MARKET_VALUE)) + 1 + 2,
        decimal_places=2,
        default=PLAYER_INITIAL_MARKET_VALUE,
    )  # max value = 99,999,999.99
    transferable = models.BooleanField(default=False)

    def __str__(self) -> str:
        return " ".join([self.first_name, self.last_name])
