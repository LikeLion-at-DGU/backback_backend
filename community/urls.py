from django.urls import path, include
from .views import *
from . import views
from rest_framework import routers

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("posts", PostViewSet, basename="posts")

completed_router = routers.SimpleRouter(trailing_slash=False)
completed_router.register("completions", CompletedViewSet, basename="completions")

urlpatterns = [
    path("", include(default_router.urls)),
    path("", include(completed_router.urls)),
]
