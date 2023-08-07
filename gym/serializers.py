from rest_framework import serializers
from .models import *


class GymSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = Gym
        fields = [
            "id",
            "name",
            "square_feet",
            "address",
            "info",
            "image",
            "created_at",
            "updated_at",
            "key",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "key",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "content",
            "id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ReviewListSerializer(serializers.ModelSerializer):
    key = serializers.CharField(max_length=10, write_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "content",
            "created_at",
            "updated_at",
            "key",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class GymListSerializer(serializers.ModelSerializer):
    exercises = serializers.CharField(source="info.exercises", read_only=True)

    class Meta:
        model = Gym
        fields = [
            "id",
            "name",
            "address",
            "exercises",
            "created_at",
            "updated_at",
        ]
        read_only_field = [
            "id",
            "created_at",
            "updated_at",
        ]
