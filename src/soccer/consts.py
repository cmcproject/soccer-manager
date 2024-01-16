from django.db import models

PLAYER_INITIAL_MARKET_VALUE = 1000000
TEAM_INITIAL_BUDGET = 5000000


class PositionChoices(models.TextChoices):
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    ATTACKER = "attacker"


TEAM_POSITIONS = (
    [PositionChoices.GOALKEEPER] * 3
    + [PositionChoices.DEFENDER] * 6
    + [PositionChoices.MIDFIELDER] * 6
    + [PositionChoices.ATTACKER] * 5
)
