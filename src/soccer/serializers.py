from django.db.models import Sum
from rest_framework import serializers

from .models import Player, Team


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "id",
            "first_name",
            "last_name",
            "position",
            "age",
            "country",
            "market_value",
            "transferable",
            "team",
        ]
        read_only_fields = ["id", "age", "team"]


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, required=False)
    team_value = serializers.SerializerMethodField(method_name="get_team_value")

    class Meta:
        model = Team
        fields = ["name", "country", "budget", "team_value", "players"]

    @staticmethod
    def get_team_value(obj) -> str:
        sum_dict = obj.players.all().aggregate(Sum("market_value"))
        return str(sum_dict.get("market_value__sum"))


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "country"]
