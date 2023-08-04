from django.shortcuts import render
from urllib.parse import urlparse
import requests, json


def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": "KakaoAK 6556fdbf5f3e592092dbd5678bb76f64"}
    api_json = json.loads(str(requests.get(url, headers=headers).text))
    address = api_json["documents"][0]["address"]
    latitude = float(address["x"])
    longitude = float(address["y"])
    return (latitude, longitude)


print(get_location("대구광역시 달서구 상화로 86"))
