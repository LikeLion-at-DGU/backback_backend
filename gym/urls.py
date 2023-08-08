from django.urls import include, path
from rest_framework import routers


from gym.views import GymReviewViewSet, GymViewSet, ReviewViewSet

app_name = "gym"
gym_router = routers.SimpleRouter()
gym_router.register("gyms", GymViewSet, basename="gyms")

review_router = routers.SimpleRouter()
review_router.register("reviews", ReviewViewSet, basename="reviews")

gym_review_router = routers.SimpleRouter()
gym_review_router.register("reviews", GymReviewViewSet, basename="reviews")

urlpatterns = [
    path("", include(gym_router.urls)),
    path("", include(review_router.urls)),
    path("gyms/<int:gym_id>/", include(gym_review_router.urls)),
]
