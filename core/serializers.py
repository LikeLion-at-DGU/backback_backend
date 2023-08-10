from rest_framework import serializers
from .models import *
from accounts.models import *


class WriterSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(source="profile.id")
    nickname = serializers.CharField(source="profile.nickname")
    type = serializers.CharField(source="profile.type")

    class Meta:
        model = User
        fields = ["id", "profile_id", "nickname", "type"]
        read_only_field = fields
