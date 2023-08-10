from django.shortcuts import get_object_or_404
from haversine import haversine
from rest_framework import viewsets, mixins, status
from community.permissions import IsOwnerOrReadOnly
from gym.paginations import Pagination
from .models import Gym, GymReport, Review, ReviewReport
from .serializers import (
    GymListSerializer,
    GymSerializer,
    ReviewListSerializer,
    ReviewSerializer,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter


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
    mixins.RetrieveModelMixin,
):
    pagination_class = Pagination
    queryset = Gym.objects.all().order_by("-created_at")
    filter_backends = [SearchFilter]
    search_fields = ["address"]  # 지역 헬스장 검색

    def get_serializer_class(self):
        if self.action == "list":
            return GymListSerializer
        return GymSerializer

    @action(
        ["POST"],
        detail=True,
        url_path="reports",
        permission_classes=[IsAuthenticated],
    )  # 신고
    def report(self, request, pk):
        gym = self.get_object()
        if not gym.reports.filter(writer=request.user).exists():
            GymReport.objects.create(
                writer=request.user,
                gym=gym,
                reason=request.data.get("reason", "default"),
            )
            return Response({"detail": "게시글이 신고되었습니다."}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "이미 신고한 게시글입니다."}, status=status.HTTP_400_BAD_REQUEST
        )


    @action(["POST"], detail=False, url_path="use-location")  # 내 주변 헬스장
    def use_location(self, request):
        latitude = float(request.data.get("latitude"))
        longitude = float(request.data.get("longitude"))

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

    @action(
        ["POST"],
        detail=True,
        url_path="reports",
        permission_classes=[IsAuthenticated],
    )  # 신고
    def report(self, request, pk):
        review = self.get_object()
        if not review.reports.filter(writer=request.user).exists():
            ReviewReport.objects.create(
                writer=request.user,
                review=review,
                reason=request.data.get("reason", "default"),
            )
            return Response({"detail": "게시글이 신고되었습니다."}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "이미 신고한 게시글입니다."}, status=status.HTTP_400_BAD_REQUEST
        )


class GymReviewViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action == "list":
            return ReviewListSerializer
        return ReviewSerializer

    def get_queryset(self):
        gym = self.kwargs.get("gym_id")
        queryset = Review.objects.filter(gym_id=gym).order_by("-created_at")
        return queryset

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return []

    def create(self, request, gym_id):  # 헬스장 리뷰 작성
        gym = get_object_or_404(Gym, pk=gym_id)
        if gym.key == request.data.get("key"):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(writer=request.user, gym=gym)
            return Response(serializer.data)
        return Response(
            {"detail": "올바른 key를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST
        )
