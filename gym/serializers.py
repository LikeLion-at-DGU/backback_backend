from rest_framework import serializers
from .models import *


class GymSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Gym
        fields = ["name", "square_feet", "machines", "address", "image"]


class GymListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Gym
        fields = ["name", "square_feet", "machines", "address", "image"]
