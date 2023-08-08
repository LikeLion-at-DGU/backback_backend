from django.urls import path, include
from .views import *
from . import views
from rest_framework import routers

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("posts", PostViewSet, basename="posts")

urlpatterns = [
    path("", include(default_router.urls)),
]
