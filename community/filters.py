from rest_framework.filters import BaseFilterBackend


class PostTypeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        post_type = request.query_params.get("type")
        if post_type in ["ORDINARY", "PRO"]:
            return queryset.filter(type=post_type)
        return queryset


class FollowingUserPostFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get("followers") == "true":
            queryset = queryset.filter(writer__profile__followers=request.user.profile)
        return queryset
