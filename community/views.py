from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from .models import *
from .serializers import *
from .filters import *
from .permissions import IsOwnerOrReadOnly
from .paginations import PostPagination, CompletedPagination
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = PostPagination
    filter_backends = [SearchFilter, PostTypeFilter, FollowingUserPostFilter]
    search_fields = ["title", "content"]
    queryset = Post.objects.all().order_by("-pk")

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "list"]:
            return PostListSerializer
        return PostDetailSerializer

    def get_permissions(self):
        if self.action in ["partial_update", "destroy", "update"]:
            return [IsOwnerOrReadOnly()]
        elif self.action == "create":
            return [IsAuthenticated()]
        return []

    def get_object(self):
        obj = super().get_object()
        return obj

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def clip(self, request, pk=None):
        post = self.get_object()

        if request.method == "POST":
            if Scrap.objects.filter(user=request.user, post=post).exists():
                return Response(
                    {"detail": "이미 스크랩한 게시물입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            scrap = Scrap(user=request.user, post=post)
            scrap.save()
            return Response(
                {"detail": "게시물이 스크랩되었습니다."}, status=status.HTTP_201_CREATED
            )

        elif request.method == "DELETE":
            try:
                scrap = Scrap.objects.get(user=request.user, post=post)
            except Scrap.DoesNotExist:
                return Response(
                    {"detail": "스크랩한 기록이 없습니다."}, status=status.HTTP_404_NOT_FOUND
                )
            scrap.delete()
            return Response(
                {"detail": "게시물 스크랩이 해제되었습니다."}, status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def clips(self, request):
        user = request.user
        scraps = Scrap.objects.filter(user=user)
        serializer = ScrapSerializer(scraps, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reports(self, request, pk=None):
        post = self.get_object()
        if PostReport.objects.filter(writer=request.user, post=post).exists():
            return Response(
                {"detail": "이미 신고한 게시글입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        report = PostReport(writer=request.user, post=post)
        report.save()
        return Response({"detail": "게시글이 신고되었습니다."}, status=status.HTTP_201_CREATED)
