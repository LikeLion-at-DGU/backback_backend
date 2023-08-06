from django.urls import path, include
from rest_framework import routers
from .views import *
from . import views

app_name = "accounts"

default_router = routers.SimpleRouter()
default_router.register("profiles", ProfileViewSet, basename="profiles")

urlpatterns = [path("", include(default_router.urls))]
