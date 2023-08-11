from rest_framework import serializers
from .models import *
from accounts.models import *


class WriterSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(source="profile.id")
    nickname = serializers.CharField(source="profile.nickname")
    type = serializers.CharField(source="profile.type")
    level = serializers.IntegerField(read_only=True)

    def get_level(self, instance):
        level = instance.profile.completed_cnt // 3 + 1
        level = 5 if (level > 5) else level
        return level

    class Meta:
        model = User
        fields = ["id", "profile_id", "nickname", "type", "level"]
        read_only_field = fields
