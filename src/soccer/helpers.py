import logging
import random
from decimal import Decimal

from faker import Faker

from soccer.consts import TEAM_POSITIONS
from soccer.models import Player, Team

LOG = logging.getLogger(__name__)


class TeamMixin:
    def get_current_team(self, user):
        current_team = Team.objects.filter(user=user).first()
        return current_team


def create_team(team, name, country):
    """
    Create new team
    :param team: Current team
    :param name: Team name
    :param country: Team country
    """
    team.name = name
    team.country = country
    team.save()

    fake = Faker()

    for position in TEAM_POSITIONS:
        player = Player.objects.create(
            first_name=fake.first_name_male(),
            last_name=fake.last_name_male(),
            country=fake.country(),
            team=team,
            position=position,
        )
        team.players.add(player)

    LOG.info(f"Team {team.name} was created.")


def get_increzed_market_value(market_value: Decimal) -> Decimal:
    """
    Get new market value increazed by random percent [10, 100]
    :param market_value: Current market value
    :return: New market value
    """
    increaze_percent = Decimal(random.randint(10, 100) / 100)
    new_market_value = market_value * (1 + increaze_percent)

    return new_market_value
