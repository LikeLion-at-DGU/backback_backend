from django.urls import include, path
from .views import *
from rest_framework import routers

app_name = "gym"

default_router = routers.SimpleRouter()
default_router.register("gyms", GymViewSet, basename="gyms")

urlpatterns = [
    path("api/", include(default_router.urls)),
]
