from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    following_cnt = serializers.SerializerMethodField(read_only=True)
    follower_cnt = serializers.SerializerMethodField(read_only=True)
    joined_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "nickname",
            "intro",
            "info",
            "following_cnt",
            "follower_cnt",
            "completed_cnt",
            "type",
            "user_id",
            "joined_at",
        ]
        read_only_fields = [
            "id",
            "info",
            "following_cnt",
            "follower_cnt",
            "completed_cnt",
            "type",
            "user_id",
        ]

    def get_following_cnt(self, instance):
        return instance.following.count()

    def get_follower_cnt(self, instance):
        return instance.followers.count()

    def get_joined_at(self, instance):
        return instance.user.date_joined.strftime("%Y-%m")
