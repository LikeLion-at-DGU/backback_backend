from rest_framework import serializers
from .models import *


class ProfileSerializer(serializers.ModelSerializer):
    following_cnt = serializers.SerializerMethodField()
    follower_cnt = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "nickname",
            "intro",
            "following_cnt",
            "follower_cnt",
            "type",
            "user",
        )

    def get_following_cnt(self, instance):
        return instance.followings.count()

    def get_follower_cnt(self, instance):
        return instance.followers.count()
