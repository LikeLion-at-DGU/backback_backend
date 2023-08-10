from django.urls import path, include
from .views import *
from . import views
from rest_framework import routers

post_router = routers.SimpleRouter(trailing_slash=False)
post_router.register("posts", PostViewSet, basename="posts")

completed_router = routers.SimpleRouter(trailing_slash=False)
completed_router.register("completions", CompletedViewSet, basename="completions")

comment_router = routers.SimpleRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments")

post_comment_router = routers.SimpleRouter(trailing_slash=False)
post_comment_router.register("comments", PostCommentViewSet, basename="comments")

banner_router = routers.SimpleRouter(trailing_slash=False)
banner_router.register("banners", BannerViewSet, basename="banners")

urlpatterns = [
    path("", include(post_router.urls)),
    path("", include(comment_router.urls)),
    path("", include(completed_router.urls)),
    path("posts/<int:post_id>/", include(post_comment_router.urls)),
    path("", include(banner_router.urls)),
]
