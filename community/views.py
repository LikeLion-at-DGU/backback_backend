from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from .models import (
    Post,
    Scrap,
    PostReport,
    Reaction,
    Completed,
    CompletedReport,
    Comment,
    CommentReport,
)
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    ScrapSerializer,
    CompletedListCreateSerializer,
    CompletedSerializer,
    CommentSerializer,
)
from .filters import PostTypeFilter, FollowingUserPostFilter
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
    filter_backends = [SearchFilter, PostTypeFilter, FollowingUserPostFilter]
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
        serializer = ScrapSerializer(scraps, many=True)
        return Response(serializer.data)

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


class CompletedViewSet(viewsets.ModelViewSet):
    pagination_class = CompletedPagination
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        if self.action == 'list':
            queryset = Completed.objects.filter(is_private = False)
            return queryset
        return Completed.objects.all()

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
    
    @action(methods = ['PATCH'], detail = True)
    def private(self, request, pk = None):
        completed = self.get_object()
        completed.is_private= True if completed.is_private == False else False
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
        elif self.action == "reports":
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
