from rest_framework import serializers
from .models import *


class ProfileSerializer(serializers.ModelSerializer):
    following_cnt = serializers.SerializerMethodField(read_only=True)
    follower_cnt = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "nickname",
            "intro",
            "info",
            "following_cnt",
            "follower_cnt",
            "type",
            "user_id",
        ]
        read_only_fields = [
            "id",
            "info",
            "following_cnt",
            "follower_cnt",
            "type",
            "user_id",
        ]

    def get_following_cnt(self, instance):
        return instance.following.count()

    def get_follower_cnt(self, instance):
        return instance.followers.count()


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile")
        profile = instance.profile

        profile.nickname = profile_data.get("nickname", profile.nickname)
        profile.intro = profile_data.get("intro", profile.intro)
        profile.save()

        return super().update(instance, validated_data)
