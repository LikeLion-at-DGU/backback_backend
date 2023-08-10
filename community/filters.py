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


class PostPurposeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        post_purpose = request.query_params.get("purpose")
        if post_purpose in ["체중 증가", "체중 감량", "재활", "체형 개선", "대회 준비", "체력 증진"]:
            queryset = queryset.filter(purpose__name=post_purpose)
        return queryset


class PostExerciseFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        post_exercise = request.query_params.get("exercise")
        if post_exercise in ["헬스", "필라테스", "요가", "복싱", "골프", "수영", "축구", "사이클", "농구"]:
            queryset = queryset.filter(exercise__name=post_exercise)
        return queryset
