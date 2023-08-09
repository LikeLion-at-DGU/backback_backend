from rest_framework import serializers
from .models import *
from accounts.models import *


class WriterSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(source="id")

    class Meta:
        model = Profile
        fields = ["profile_id", "nickname", "type"]
        read_only_field = fields
