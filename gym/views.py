from django.shortcuts import render
from urllib.parse import urlparse
import requests, json
from haversine import haversine

from gym.models import Gym


def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": "KakaoAK 6556fdbf5f3e592092dbd5678bb76f64"}
    api_json = json.loads(str(requests.get(url, headers=headers).text))
    address = api_json["documents"][0]["address"]
    latitude = float(address["x"])
    longitude = float(address["y"])
    return (latitude, longitude)


print(get_location("대구광역시 달서구 상화로 86"))


def get_location(my_coor):
    near = []
    gym = Gym.objects.all()
    for g in gym:
        if haversine(my_coor, (g.latitude, g.longitude)) <= 3:
            near.append(g.name)
    return near
