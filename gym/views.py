from django.shortcuts import get_object_or_404
import requests, json
from haversine import haversine
from rest_framework import viewsets, mixins
from .models import Gym, GymReport, Review
from .serializers import GymListSerializer, GymSerializer, ReviewSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


# def find_gym(my_coor):
#     near = []
#     gym = Gym.objects.all()
#     for g in gym:
#         if haversine(my_coor, (g.latitude, g.longitude)) <= 3:
#             near.append(g.name)
#     return near


# class GymViewSet(
#     viewsets.GenericViewSet,
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
#     mixins.RetrieveModelMixin,
# ):
#     queryset = Gym.objects.all()
#
#     def create(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         gym = serializer.instance
#         self.get_location(gym)
#         return Response(serializer.data)
#
#     def get_location(self, gym):
#         url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + gym.address
#         headers = {"Authorization": "KakaoAK 6556fdbf5f3e592092dbd5678bb76f64"}
#         api_json = json.loads(str(requests.get(url, headers=headers).text))
#         address = api_json["documents"][0]["address"]
#         gym.latitude = float(address["y"])
#         gym.longitude = float(address["x"])
#         gym.save()
#
#     def get_serializer_class(self):
#         if self.action == "list":
#             return GymListSerializer
#         return GymSerializer
#
#     @action(["POST"], detail=True, url_path="reports")
#     def report(self, request):
#         gym = self.get_object()
#         GymReport.objects.create(
#             writer=request.user, gym=gym, reason=request.POST["reason"]
#         )
#         return Response()
