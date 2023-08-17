import datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, mixins
from .models import (
    Post,
    Purpose,
    Exercise,
    Scrap,
    PostReport,
    Reaction,
    Completed,
    CompletedReport,
    Comment,
    CommentReport,
    Banner,
)
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PurposeSerializer,
    ExerciseSerializer,
    ScrapSerializer,
    CompletedListCreateSerializer,
    CompletedSerializer,
    CommentSerializer,
    BannerSerializer,
)
from .filters import (
    PostTypeFilter,
    FollowingUserPostFilter,
    PostExerciseFilter,
    PostPurposeFilter,
)
from .permissions import IsOwnerOrReadOnly
from .paginations import PostPagination, CompletedPagination
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Q, Count


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = PostPagination
    filter_backends = [
        SearchFilter,
        PostTypeFilter,
        FollowingUserPostFilter,
        PostExerciseFilter,
        PostPurposeFilter,
    ]
    search_fields = ["title", "content"]
    parser_classes = [MultiPartParser]

    queryset = Post.objects.annotate(
        likes_cnt=Count(
            "reactions", filter=Q(reactions__completed__isnull=True), distinct=True
        ),
    ).order_by("-pk")

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

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        instance.view_cnt += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
            Scrap.objects.create(user=request.user, post=post)
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
        paginator = PostPagination()
        page = paginator.paginate_queryset(scraps, request)
        serializer = (
            ScrapSerializer(page, many=True)
            if page is not None
            else ScrapSerializer(scraps, many=True)
        )
        return (
            paginator.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        parser_classes=[JSONParser],
    )
    def report(self, request, pk=None):
        post = self.get_object()
        if PostReport.objects.filter(writer=request.user, post=post).exists():
            return Response(
                {"detail": "이미 신고한 게시글입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        PostReport.objects.create(
            writer=request.user, post=post, reason=request.data.get("reason", "default")
        )
        return Response({"detail": "게시글이 신고되었습니다."}, status=status.HTTP_201_CREATED)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, pk=None):
        post = self.get_object()
        if reaction := Reaction.objects.filter(
            completed__isnull=True, user=request.user, post=post
        ).first():
            reaction.delete()
        else:
            Reaction.objects.create(post=post, user=request.user)
        return Response()

    @action(methods=["GET"], detail=False, url_path="hot-ord")
    def hot_ordinary(self, request):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        hot_ord_posts = (
            self.get_queryset()
            .filter(created_at__gte=yesterday, type="ORDINARY")
            .order_by("-likes_cnt")[:2]
        )
        hot_ord_posts_serializer = PostListSerializer(
            hot_ord_posts, many=True, context={"request": request}
        )
        return Response(hot_ord_posts_serializer.data)

    @action(methods=["GET"], detail=False, url_path="hot-pro")
    def hot_pro(self, request):
        now = timezone.now()
        today = now.date()  # 현재 날짜
        days_since_monday = (today.weekday()) % 7  # 월요일까지의 날짜 차이
        # 월요일을 기준으로 1주일 전과 오늘 사이의 범위 계산
        week_start = today - datetime.timedelta(days=days_since_monday)
        week_end = week_start + datetime.timedelta(days=7)
        hot_pro_posts = (
            self.get_queryset()
            .filter(created_at__range=(week_start, week_end), type="PRO")
            .order_by("-view_cnt")[:5]
        )
        hot_pro_posts_serializer = PostListSerializer(
            hot_pro_posts, many=True, context={"request": request}
        )
        return Response(hot_pro_posts_serializer.data)


class PurposeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Purpose.objects.all()
    serializer_class = PurposeSerializer


class ExerciseViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class CompletedViewSet(viewsets.ModelViewSet):
    pagination_class = CompletedPagination
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        if self.action == "list":
            queryset = Completed.objects.filter(is_private=False).order_by("-id")
            return queryset
        return Completed.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return CompletedListCreateSerializer
        return CompletedSerializer

    def get_permissions(self):
        if self.action in ["create", "report", "like"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return []

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        parser_classes=[JSONParser],
    )
    def report(self, request, pk=None):
        completed = self.get_object()
        if CompletedReport.objects.filter(
            completed=completed, writer=request.user
        ).exists():
            return Response(
                {"detail": "이미 신고한 게시글입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        CompletedReport.objects.create(
            completed=completed,
            writer=request.user,
            reason=request.data.get("reason", "default"),
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

    @action(methods=["PATCH"], detail=True)
    def private(self, request, pk=None):
        completed = self.get_object()
        completed.is_private = True if completed.is_private == False else False
        completed.save()
        return Response()


class PostCommentViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post).order_by("-pk")
        return queryset

    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, writer=request.user)
        return Response(serializer.data)


class CommentViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.action == "destroy":
            return [IsOwnerOrReadOnly()]
        elif self.action == "report":
            return [IsAuthenticated()]
        return []

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        comment = self.get_object()
        if CommentReport.objects.filter(writer=request.user, comment=comment).exists():
            return Response(
                {"detail": "이미 신고한 댓글입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        CommentReport.objects.create(
            writer=request.user,
            comment=comment,
            reason=request.data.get("reason", "default"),
        )
        return Response({"detail": "댓글이 신고되었습니다."}, status=status.HTTP_201_CREATED)


class BannerViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Banner.objects.all().order_by("priority")
    serializer_class = BannerSerializer
