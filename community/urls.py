from django.urls import path, include
from .views import *
from . import views

from rest_framework import routers

completed_router = routers.SimpleRouter(trailing_slash=False)
completed_router.register("completions", CompleletedViewSet, basename="completions")

app_name = "community"
urlpatterns = [
    path("", include(completed_router.urls)),
]
