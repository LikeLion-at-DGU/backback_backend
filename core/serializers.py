from rest_framework import serializers
from .models import *


class WriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname", "type"]
        read_only_field = fields
