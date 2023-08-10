from django.urls import path, include
from rest_framework import routers
from .views import *
from . import views

app_name = "accounts"

profile_router = routers.SimpleRouter(trailing_slash=False)
profile_router.register("profiles", ProfileViewSet, basename="profiles")

urlpatterns = [
    path("", include(profile_router.urls)),
    path("me/", MeViewSet.as_view(), name="me"),
]
