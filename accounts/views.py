from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Profile, ProfileReport
from accounts.serializers import ProfileSerializer
from community.models import Post, Completed
from community.serializers import PostListSerializer, CompletedListCreateSerializer
from .paginations import AccountsPagination


class ProfileViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(["POST"], detail=True, url_path="follow")
    @permission_classes([IsAuthenticated])
    def follow(self, request, pk=None):
        user = request.user
        followed_user = self.get_object()
        if user.profile == followed_user:
            return Response(
                {"detail": "본인은 팔로우 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.profile in followed_user.followers.all():
            user.profile.following.remove(followed_user)
        else:
            user.profile.following.add(followed_user)
        return Response({}, status=status.HTTP_200_OK)

    @action(["POST"], detail=True, url_path="report")
    @permission_classes([IsAuthenticated])
    def report(self, request, pk=None):
        profile = self.get_object()
        if profile == request.user.profile:
            return Response(
                {"detail": "본인은 신고할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ProfileReport.objects.create(
            writer=request.user,
            reason=request.data.get("reason", "default"),
            profile=profile,
        )
        return Response({"detail": "이미 스크랩한 게시물입니다."})

    @action(["GET"], detail=True, url_path="posts")
    def posts(self, request, pk=None):
        posts = Post.objects.filter(writer__id=pk)
        paginator = AccountsPagination()
        page = paginator.paginate_queryset(posts, request)
        serializer = (
            PostListSerializer(page, many=True)
            if page is not None
            else PostListSerializer(posts, many=True)
        )
        return (
            paginator.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    @action(["GET"], detail=True, url_path="completions")
    def completions(self, request, pk=None):
        completions = Completed.objects.filter(writer__id=pk)
        paginator = AccountsPagination()
        page = paginator.paginate_queryset(completions, request)
        serializer = (
            CompletedListCreateSerializer(page, many=True)
            if page is not None
            else CompletedListCreateSerializer(completions, many=True)
        )
        return (
            paginator.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )


class MeViewSet(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch", "options"]

    def get_object(self):
        if not self.request.user.is_active:
            raise PermissionDenied
        return get_object_or_404(
            User.objects.select_related("profile"), id=self.request.user.id
        )

    def get(self, request, *args, **kwargs):
        instance: User = self.get_object()
        serializer = self.get_serializer(instance.profile)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance: User = self.get_object()
        nickname = request.data.get("nickname")
        intro = request.data.get("intro")

        profile = instance.profile
        profile.nickname = nickname
        profile.intro = intro
        profile.save()

        serializer = self.get_serializer(instance.profile)
        return Response(serializer.data)
