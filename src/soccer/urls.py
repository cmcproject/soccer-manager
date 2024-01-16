"""
URL mappings for the soccer API
"""
from django.urls import path

from soccer import views

app_name = "soccer"

urlpatterns = [
    path("team/", views.TeamSetupAPIView.as_view(), name="team"),
    path(
        "player/<int:pk>",
        views.PlayerDetailsAPIView.as_view(),
        name="player-detail",
    ),
    path("transfer/", views.TransferPlayerListAPIView.as_view(), name="transfer-list"),
    path(
        "transfer/<int:pk>",
        views.TransferPlayerAPIView.as_view(),
        name="transfer-player",
    ),
]
