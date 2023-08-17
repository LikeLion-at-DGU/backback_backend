from rest_framework import serializers
from .models import Gym, Review


class GymSerializer(serializers.ModelSerializer):
    review_cnt = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(use_url=True, required=False)

    def get_review_cnt(self, instance):
        return instance.reviews.count()

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
            "latitude",
            "longitude",
            "review_cnt",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "latitude",
            "longitude",
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
    class Meta:
        model = Review
        fields = [
            "id",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class GymListSerializer(serializers.ModelSerializer):
    exercises = serializers.CharField(source="info.exercises", read_only=True)
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Gym
        fields = [
            "id",
            "name",
            "address",
            "exercises",
            "created_at",
            "updated_at",
            "image",
            "latitude",
            "longitude",
        ]
        read_only_field = [
            "id",
            "created_at",
            "updated_at",
            "latitude",
            "longitude",
        ]
