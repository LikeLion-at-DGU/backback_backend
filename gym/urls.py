from django.urls import include, path
from .views import *
from rest_framework import routers

app_name = "gym"

default_router = routers.SimpleRouter()
default_router.register("gyms", GymViewSet, basename="gyms")

review_router = routers.SimpleRouter()
review_router.register("reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    path("", include(default_router.urls)),
    path("gyms/<int:gym_id>/", include(review_router.urls)),
]
