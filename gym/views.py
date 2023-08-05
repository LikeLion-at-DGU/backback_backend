import requests, json
from haversine import haversine
from rest_framework import viewsets, mixins
from .models import Gym, GymReport
from .serializers import GymListSerializer, GymSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": "KakaoAK 6556fdbf5f3e592092dbd5678bb76f64"}
    api_json = json.loads(str(requests.get(url, headers=headers).text))
    address = api_json["documents"][0]["address"]
    latitude = float(address["x"])
    longitude = float(address["y"])
    return (latitude, longitude)


def get_location(my_coor):
    near = []
    gym = Gym.objects.all()
    for g in gym:
        if haversine(my_coor, (g.latitude, g.longitude)) <= 3:
            near.append(g.name)
    return near


class GymViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Gym.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return GymListSerializer
        return GymSerializer

    @action(["POST"], detail=True, url_path="reports")
    def report(self, request):
        gym = self.get_object()
        GymReport.objects.create(
            writer=request.user, gym=gym, reason=request.POST["reason"]
        )
        GymReport.save()
        return Response()
