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
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser


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
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    def get_permissions(self):
        if self.action in ["partial_update", "destroy", "update"]:
            return [IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

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
                scrap.delete()
                return Response(
                    {"detail": "게시물 스크랩이 해제되었습니다."}, status=status.HTTP_204_NO_CONTENT
                )
            except Scrap.DoesNotExist:
                return Response(
                    {"detail": "스크랩한 기록이 없습니다."}, status=status.HTTP_404_NOT_FOUND
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

    @action(methods=["POST"], detail=True, url_path="like")
    def like(self, request, pk=None):
        post = self.get_object()
        if reaction := Reaction.objects.filter(
            completed__isnull=True, user=request.user, post=post
        ).first():
            reaction.delete()
        else:
            Reaction.objects.create(post=post, user=request.user)
        return Response()


class CompletedViewSet(viewsets.ModelViewSet):
    queryset = Completed.objects.all()
    pagination_class = CompletedPagination
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return CompletedListSerializer
        elif self.action in ["retrieve", "create"]:
            return CompletedRetrieveCreateSerializer
        return CompletedEditSerializer

    def get_permissions(self):
        if self.action in ["create", "reports", "likes"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return []

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

    @action(methods=["POST"], detail=True, url_path="reports")
    def reports(self, request, pk=None):
        completed = self.get_object()
        if CompletedReport.objects.filter(completed=completed, writer=request.user):
            return Response(
                {"detail": "이미 신고한 게시글입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        CompletedReport.objects.create(
            completed=completed, writer=request.user, reason=request.POST["reason"]
        )
        return Response()

    @action(methods=["POST"], detail=True, url_path="like")
    def like(self, request, pk=None):
        completed = self.get_object()
        if reaction := Reaction.objects.filter(
            post__isnull=True, user=request.user, completed=completed
        ).first():
            reaction.delete()
        else:
            Reaction.objects.create(completed=completed, user=request.user)
        return Response()
