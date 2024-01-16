from django.contrib import admin

from soccer.models import Player, Team


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "team", "position", "market_value"]


class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "budget"]


admin.site.register(Player, PlayerAdmin)
admin.site.register(Team, TeamAdmin)
