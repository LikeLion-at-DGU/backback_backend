import random
import string
from django.shortcuts import get_object_or_404
import requests, json
from haversine import haversine
from rest_framework import viewsets, mixins

from community.permissions import IsOwnerOrReadOnly
from .models import Gym, GymReport, Review, ReviewReport
from .serializers import (
    GymListSerializer,
    GymSerializer,
    ReviewListSerializer,
    ReviewSerializer,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter


def generate_random_string(length=10):  # 헬스장 key 생성
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def find_gym(my_coor):
    near = []
    gym = Gym.objects.all()
    for g in gym:
        if haversine(my_coor, (g.latitude, g.longitude)) <= 3:
            near.append(g.id)
    return near


class GymViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Gym.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ["address", "^address"]  # 지역 헬스장 검색

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAdminUser()]
        return []

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        gym = serializer.instance
        gym.key = generate_random_string()
        self.get_location(gym)
        return Response(serializer.data)

    def get_location(self, gym):  # 경도,위도 저장
        url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + gym.address
        headers = {"Authorization": "KakaoAK 6556fdbf5f3e592092dbd5678bb76f64"}
        api_json = json.loads(str(requests.get(url, headers=headers).text))
        address = api_json["documents"][0]["address"]
        gym.latitude = float(address["y"])
        gym.longitude = float(address["x"])
        gym.save()

    def get_serializer_class(self):
        if self.action == "list":
            return GymListSerializer
        return GymSerializer

    @action(["POST"], detail=True, url_path="reports")  # 신고
    def report(self, request, pk):
        if IsAuthenticated:
            gym = get_object_or_404(Gym, pk=pk)
            reason = request.data.get("reason")
            GymReport.objects.create(writer=request.user, gym=gym, reason=reason)
            return Response()

    @action(["POST"], detail=False, url_path="use-location")  # 내 주변 헬스장
    def use_location(self, request):
        latitude = float(request.data.get("latitude"))
        longitude = float(request.data.get("longitude"))
        print("latitude", latitude)
        print("longitude", longitude)

        near = find_gym((latitude, longitude))
        gym = Gym.objects.filter(id__in=near)
        serializer = GymListSerializer(gym, many=True)
        return Response(serializer.data)


class ReviewViewSet(
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ["update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return []

    @action(["POST"], detail=True, url_path="reports")  # 신고
    def report(self, request, pk):
        if IsAuthenticated:
            review = get_object_or_404(Review, pk=pk)
            reason = request.data.get("reason")
            ReviewReport.objects.create(
                writer=request.user, review=review, reason=reason
            )
            return Response()


class GymReviewViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    def get_serializer_class(self):
        if self.action == "list":
            return ReviewListSerializer
        return ReviewSerializer

    def get_queryset(self):
        gym = self.kwargs.get("gym_id")
        queryset = Review.objects.filter(gym_id=gym)
        return queryset

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return []

    def list(self, request, gym_id):  # 헬스장 리뷰 리스트
        gym = get_object_or_404(Gym, pk=gym_id)
        reviews = gym.reviews.all()
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    def create(self, request, gym_id):  # 헬스장 리뷰 작성
        print(request.data)
        gym = get_object_or_404(Gym, pk=gym_id)
        if gym.key == request.data.get("key"):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(writer=request.user, gym=gym)
            return Response(serializer.data)
