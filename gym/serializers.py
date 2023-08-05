from rest_framework import serializers
from .models import *


class GymSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = Gym
        fields = [
            "name",
            "square_feet",
            "machines",
            "address",
            "image",
        ]
        read_only_field = ["created_at", "updated_at"]


class GymListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Gym
        fields = [
            "name",
            "square_feet",
            "machines",
            "address",
            "image",
        ]
        read_only_field = ["created_at", "updated_at"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["writer", "content"]
        read_only_field = ["created_at", "updated_at"]
