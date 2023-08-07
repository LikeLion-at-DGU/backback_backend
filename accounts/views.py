from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes
from django.shortcuts import render, get_object_or_404
from .models import Profile
from .serializers import *


class ProfileViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = Profile.objects.all()

    @action(["GET"], detail=False, url_path="me")
    @permission_classes([IsAuthenticated])
    def my_profile(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        serializers = ProfileSerializer(profile)
        return Response(serializers.data)
