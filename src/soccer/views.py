from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.tasks import do_something_task

from .helpers import TeamMixin, create_team, get_increzed_market_value
from .models import Player, Team
from .serializers import PlayerSerializer, TeamCreateSerializer, TeamSerializer


class TeamSetupAPIView(generics.GenericAPIView):
    """
    Team setup
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Team.objects.filter(user=user)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TeamCreateSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        """
        Get team information
        """
        qs = self.get_queryset()
        if qs:
            serializer = self.get_serializer(qs.first())
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(
            data={"msg": "Create the soccer team first."},
            status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        description="Create team",
        request=TeamCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=TeamCreateSerializer,
                examples=[
                    OpenApiExample(
                        "ex1",
                        {
                            "name": "Barcelona",
                            "country": "Spain",
                        },
                    ),
                ],
            ),
            400: OpenApiResponse(
                response=TeamCreateSerializer,
                examples=[
                    OpenApiExample(
                        "ex2",
                        {
                            "msg": "Soccer team has been already created.",
                        },
                    ),
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Create team by setting up name, country and automatically generating players
        """
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        team, created = Team.objects.get_or_create(user=request.user)
        if created:
            create_team(team, data.get("name"), data.get("country"))

            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            data={"msg": "Soccer team has been already created."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PlayerDetailsAPIView(generics.RetrieveUpdateAPIView, TeamMixin):
    """
    Retrieve and update player information
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PlayerSerializer

    def get_queryset(self):
        current_team = self.get_current_team(self.request.user)
        queryset = Player.objects.filter(team=current_team)

        return queryset


class TransferPlayerListAPIView(generics.ListAPIView, TeamMixin):
    """
    Get players available for transfer (except current team players)
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PlayerSerializer

    def get_queryset(self):
        current_team = self.get_current_team(self.request.user)
        queryset = Player.objects.filter(transferable=True).exclude(team=current_team)
        return queryset


class TransferPlayerAPIView(generics.CreateAPIView, TeamMixin):
    """
    Perform player transaction
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PlayerSerializer

    def get_queryset(self):
        player_id = self.kwargs["pk"]
        current_team = self.get_current_team(self.request.user)
        queryset = Player.objects.filter(id=player_id, transferable=True).exclude(team=current_team).first()
        return queryset

    @extend_schema(
        description="Buy player",
        request=None,
    )
    def post(self, request, *args, **kwargs):
        player = self.get_queryset()

        if not player:
            return Response(
                data={"msg": "You cannot buy a player from your own team."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        seller = Team.objects.get(id=player.team.id)
        buyer = Team.objects.get(user=request.user)

        if buyer.budget < player.market_value:
            return Response(
                data={"msg": "Not enough funds to buy a new player."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # update player
            initial_market_value = player.market_value
            player.market_value = get_increzed_market_value(initial_market_value)
            player.team = buyer
            player.transferable = False
            player.save()

            # update buyer
            buyer.budget = buyer.budget - initial_market_value
            buyer.save()

            # update seller
            seller.budget = seller.budget + initial_market_value
            seller.save()

            serializer = self.get_serializer(player)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


@cache_page(60 * 15)
def cached(request):
    user_model = get_user_model()
    all_users = user_model.objects.all()

    return HttpResponse(f"<html><body><h1>{len(all_users)} users...<h1></body></html>")


def cacheless(request):
    # trigger Celery task
    do_something_task.delay(3, 5)

    user_model = get_user_model()
    all_users = user_model.objects.all()
    return HttpResponse(f"<html><body><h1>{len(all_users)} users...<h1></body></html>")
